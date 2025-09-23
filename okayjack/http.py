from django.template.loader import render_to_string
from render_block import render_block_to_string
from django.http import HttpResponse, HttpResponseRedirect


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
		self['HX-Refresh'] = 'true'
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

	The values to return as HX headers can come from: hx-*, hx-success-*, or hx-error-* attributes in the HTML, or kwargs when creating a HxResponse, HxSuccessResponse, or HxErrorResponse in the View.
	
	It is valid for the values to come from a combination of the above sources, so this class determines which one to use based on an order of importance. 
	
	From most important to least:
	1. kwargs
	2. hx-success-* or hx-error-* attributes
	3. hx-* attrributes

	Values of higher importance supercede those of lower importance. The class then returns a response with the most important value for each attribute (target, swap, etc).
	'''

	def __init__(self, request, *args, **kwargs):

		state = kwargs.pop('state', None)
		status = kwargs.pop('status', None)

		# Processing shortcuts for DoNothing or Refresh. If either of these are present, none of the other hx attributes apply. so these checks allow the HxResponse to return without processing the block etc.
		
		if (kwargs.pop('do_nothing', None) or 
			(state and 'do-nothing' in request.hx[state]) or 
			('do-nothing' in request.hx['general'])):
				# Default to status 204 for do-nothing responses
				if status is None or status == 200:
					status = 204
				super().__init__(status=status)
				# We use this special response header to tell the JavaScript to not swap in the response body.
				# Vanilla htmx supports this through returning a 204 status code. We want to support more status codes than just 204 so we do it this way instead. This will allow the request status to be queried in analytics programs (e.g. django-silent-mammoth-whistle)
				self['HX-Do-Nothing'] = 'true'
		
		elif (kwargs.pop('refresh', None) or 
			(state and 'refresh' in request.hx[state]) or
			('refresh' in request.hx['general'])):
				super().__init__(status=status)
				self['HX-Refresh'] = 'true'

		else:
			# We shouldn't actually get HxResponses with no context supplied as there are other classes to cover those edge cases (e.g. HxRefresh), but avoiding that error is best.
			try:
				context = args[0]
				# HttpResponse doesn't take a 'context' argument so we need to remove that before passing the remaining args to super (the HttpResponse __init__ method)
				args = args[1:]
			except IndexError:
				context = None

			# HxSuccessResponse and HxErrorResponse will pass the block reference in kwargs
			# If the user is using hx-block, that will be in request.hx['general']['block']
			block = (kwargs.pop('block', None) or 
				(request.hx[state].get('block') if state else None) or 
				request.hx['general'].get('block') or 
				None)

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

			# Pop any special okayjack keyword args so the remaining kwargs can be sent to HttpResponse
			# While we're at it, we determine all the values which should be included in the HttpResponse
			response_values = {}
			for attr in hx_attributes:
				if value := (kwargs.pop(attr['kwarg'], None) or 
					(request.hx[state].get(attr['request']) if state else None) or
					request.hx['general'].get(attr['request'])):
						response_values[attr['response']] = value

			# Create HttpResponse
			# We need to do this before setting the headers to there's a response to set the headers on
			#
			# `status` kwarg is used by okayjack as well as HttpResponse. 
			# For okayjack usage, the value is in the request.state object so we need to explicitly include it as a kwarg to HttpResponse here.
			super().__init__(html, *args, status=status, **kwargs)

			# Set response headers
			for key, value in response_values.items():
				self[key] = value


class HxSuccessResponse(HxResponse):
	'''A convenience class for creating a 'sucess' HxResponse. This is just done by adding the state='success' kwarg.'''
	def __init__(self, request, *args, **kwargs):
		super().__init__(request, *args, state='success', status=200, **kwargs)

class HxErrorResponse(HxResponse):
	'''A convenience class for creating an 'error' HxResponse. This is just done by adding the state='error' kwarg.
	
	422 (Unprocessable Content) is the error code we use for generic form submission errors'''
	def __init__(self, request, *args, **kwargs):
		super().__init__(request, *args, state='error', status=422, **kwargs)
