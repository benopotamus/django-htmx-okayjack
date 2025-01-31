from django.template.loader import render_to_string
from render_block import render_block_to_string
from django.http import HttpResponse, HttpResponseRedirect

class HxDoNothing(HttpResponse):
	'''A HttpResponse that tells htmx to do nothing'''
	status_code = 204 # No content


class HxRedirect(HttpResponseRedirect):
	'''A HttpResponse that tells htmx to do a client side redirect to the provided URL
	E.g. HxRedirect(reverse('home'))
	'''
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self['HX-Redirect'] = self['Location']
	status_code = 200


class HxRefresh(HttpResponse):
	'''A HttpResponse that tells htmx to refresh the page'''
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self['HX-Refresh'] = "true"
	status_code = 200


class HxFire(HttpResponse):
	'''A HttpResponse that tells htmx to fire (aka trigger) an event - and do nothing else.
	https://htmx.org/headers/hx-trigger/
	
	Parameters
		fire: the name of the event to fire. Can also be JSON string, which allows for firing multiple events and/or passing data for the event
		fire_after_receive: same as fire, but after receive
		fire_after_swap: same as fire, but after swap
		fire_after_settle: same as fire, but after settle
	
		Usage
			HxFire('my-event')
			HxFire(fire='my-event')
			HxFire(fire_after_receive='my-event')
			HxFire(fire_after_swap='my-event')
			HxFire(fire_after_settle='my-event')
	'''
	def __init__(self, fire=None, *args, fire_after_receive=None, fire_after_swap=None, fire_after_settle=None, **kwargs):
		super().__init__(*args, **kwargs)

		# Two ways to define HX-Trigger (fire can be a positional or keyword argument)
		if fire:
			self['HX-Trigger'] = fire
		elif fire_after_receive:
			self['HX-Trigger'] = fire_after_receive

		if fire_after_swap:
			self['HX-Trigger-After-Swap'] = fire_after_swap
		if fire_after_swap:
			self['HX-Trigger-After-Settle'] = fire_after_settle


class BlockResponse(HttpResponse):
	'''Creates a TemplateResponse like object using django-render-block to render just a block in a template
	The format of block is "template_name#block_name"
	'''
	def __init__(self, request, block, context, **kwargs):
		template_name, block_name = block.split('#')
		super().__init__(render_block_to_string(template_name=template_name, block_name=block_name, context=context, request=request), **kwargs)


class HxResponse(HttpResponse):
	'''Returns a TemplateResponse-like object with HX headers like HX-Retarget for controlling htmx behaviour.

	Headers are based on request.hx.general object or supplied kwargs. kwargs get precedence.
	'''

	def __init__(self, request, *args, **kwargs):

		# If DoNothing or Refresh (the page), we don't need to process anything else about the request
		do_nothing = (
			kwargs.pop('do_nothing', None) or 
			('do-nothing' in request.hx['general']) or
			('do-nothing' in request.hx['success']) or
			('do-nothing' in request.hx['error']) or
			None
		)
		refresh = (
			kwargs.pop('refresh', None) or 
			('refresh' in request.hx['general']) or
			('refresh' in request.hx['success']) or
			('refresh' in request.hx['error']) or
			None
		)

		if do_nothing:
			super().__init__(status=204) # 204 is "No Content"
		elif refresh:
			super().__init__(status=204) # 204 is "No Content"
			self['HX-Refresh'] = "true"

		else:		
			# We shouldn't actually get HxResponses with no context supplied as there other classes to cover those edge cases (e.g. HxRefresh), but avoiding that error is best.
			try:
				context = args[0]
				# HttpResponse doesn't take a 'context' argument so we need to remove that before passing the remaining args to super (the HttpResponse __init__ method)
				args = args[1:]
			except IndexError:
				context = None
			
			# Get any values from hx.request.general or kwargs
			# kwargs take recedence, and we pop them here so we can just pass the kwargs variable to HttpResponse. This lets the user mix HxResponse and HttpResponse kwargs when creating a HxResponse.
			for attr in hx_attributes:
				attr['value'] = kwargs.pop(attr['kwarg'], None) or request.hx['general'].get(attr['request']) or None
				# e.g. trigger_after_receive = kwargs['trigger_after_receive'] or request.hx['general']['trigger-after-receive'] or None

			# HxSuccessResponse and HxErrorResponse will pass the block reference in kwargs
			# If the user is using hx-block, that will be in request.hx['general']['block']
			block = kwargs.pop('block', None) or request.hx['general'].get('block') or None

			# Render HTML from context and block reference (if supplied)
			if block:
				if '#' in block:
					template_name, block_name = block.split('#')
					html = render_block_to_string(template_name=template_name, block_name=block_name, context=context, request=request)
				else:
					html = render_to_string(template_name=block, context=context, request=request)
			else:
				# Sometimes we don't want any response body. An empty block (i.e. hx-block="") will end up here as well.
				html = ''

			# Create HttpResponse here so we can start adding headers below
			# HxSuccessResponse and HxErrorResponse pass in a status code via kwargs
			super().__init__(html, *args, **kwargs)

			for attr in hx_attributes:
				if attr['value']:
					self[attr['response']] = attr['value']
					# e.g. self['HX-Trigger'] = attr['trigger_after_receive']


# The list of HTMX attributes that HxResponse recognises, and their header equivalent (for telling HTMX to do something different when it receives the response). kwarg is the kwarg name used when creating a HxResponse directly
hx_attributes = [
	# These attributes are native htmx ones. They don't come in request.hx.general - because htmx will process them by default. We wnly need to process them in request.hx.success/error situations.
	{ 'request': 'location', 'response': 'HX-Location', 'kwarg': 'location'},
	{ 'request': 'push-url', 'response': 'HX-Push-Url', 'kwarg': 'push_url'}, #core
	{ 'request': 'redirect', 'response': 'HX-Redirect', 'kwarg': 'redirect'},
	{ 'request': 'refresh', 'response': 'HX-Refresh', 'kwarg': 'refresh'},
	{ 'request': 'replace-url', 'response': 'HX-Replace-Url', 'kwarg': 'replace_url'}, #core
	{ 'request': 'swap', 'response': 'HX-Reswap', 'kwarg': 'swap'}, #core
	{ 'request': 'target', 'response': 'HX-Retarget', 'kwarg': 'target'}, #core

	# These attributes are pure okayjack ones - we need to process them for all of request.hx.*
	{ 'request': 'fire', 'response': 'HX-Trigger', 'kwarg': 'fire'},
	{ 'request': 'fire-after-receive', 'response': 'HX-Trigger', 'kwarg': 'fire_after_receive'},
	{ 'request': 'fire-after-settle', 'response': 'HX-Trigger-After-Settle', 'kwarg': 'fire_after_settle'},
	{ 'request': 'fire-after-swap', 'response': 'HX-Trigger-After-Swap', 'kwarg': 'fire_after_swap'},

	# There is also the "do_nothing" and "block" attributes, but we process them in special ways. (They don't do htmx overrides like the above attributes do)
]

class HxStateResponse(HxResponse):
	'''Creates a HxResponse class with htmx headers based on the request.hx.success or request.hx.error attribute. i.e. if state is 'success' headers are based on request.hx.success. Or request.hx.error for 'error' state.

	This doesn't process the request.hx.general values (except for block) - that is done in HxResponse. If the client is making a request that only uses request.hx.general attributes, it is expected the view will return a HxResponse (so processing needs to be done there). If the client sends a mix of request.hx.general and request.hx.success/error attributes, the request.hx.success/error attributes should take precedence, which is what will happen here as the headers for success/error are added after the HxResponse is created in this class.
	'''

	def __init__(self, request, *args, state=None, **kwargs):
		# If the user specified that htmx should do nothing with a response, we tell HxResponse to just create a HxDoNothing
		if 'do_nothing' in request.hx[state]:
			super().__init__(request, *args, do_nothing=True, **kwargs)
		
		else:
			# Create a HxResponse that we can attach headers to. HxResponse requires a block to create the HttpResponse object so we pass one here as well. None is fine for a block value because some requests are doing things like hx-success-swap=delete
			super().__init__(request, *args, block=request.hx[state].get('block', None), **kwargs)

			# Add headers for any okayjack attributes specified (e.g. hx-fire-after-swap or hx-success-fire-after-swap)
			for attr_header in hx_attributes:
				if attr_header['request'] in request.hx[state]:
					# Add the header with the correct htmx name with the value specified in the request
					self[attr_header['response']] = request.hx[state][attr_header['request']]

			# HX-Refresh can be passed in as an empty string, which we want to treat as "true", so we need to do that special assignment here because the for loop above just naively sends the passed in value back to the client (i.e. it would send an empty string, which htmx won't process)
			if 'HX-Refresh' in self and self['HX-Refresh'] == "":
				self['HX-Refresh'] = "true"



class HxSuccessResponse(HxStateResponse):
	'''A convenience class for creating a 'sucess' HxResponse. This is just done by adding the state='success' kwarg.'''
	def __init__(self, request, *args, **kwargs):
		super().__init__(request, *args, state='success', status=200, **kwargs)

class HxErrorResponse(HxStateResponse):
	'''A convenience class for creating an 'error' HxResponse. This is just done by adding the state='error' kwarg.
	
	422 (Unprocessable Content) is the error code we use for generic form submission errors'''
	def __init__(self, request, *args, **kwargs):
		super().__init__(request, *args, state='error', status=422, **kwargs)
