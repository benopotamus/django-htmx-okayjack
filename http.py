from http import HTTPStatus
from django.template.loader import render_to_string
from render_block import render_block_to_string
from django.http import HttpResponse, HttpResponseRedirect
from django.template.response import TemplateResponse


class HxDoNothing(HttpResponse):
	'''A HttpResponse that tells htmx to do nothing'''
	status_code = HTTPStatus.NO_CONTENT #204


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


class HxTrigger(HttpResponse):
	'''A HttpResponse that tells htmx to trigger an event - and do nothing else.
	https://htmx.org/headers/hx-trigger/
	
	trigger: the name of the event to trigger. Can also be JSON string, which allows for triggering multiple events and/or passing data for the event
	'''
	def __init__(self, trigger=None, trigger_after_swap=None, trigger_after_settle=None, *args, **kwargs):
		super().__init__(*args, **kwargs)
		if trigger:
			self['HX-Trigger'] = trigger
		if trigger_after_swap:
			self['HX-Trigger-After-Swap'] = trigger_after_swap
		if trigger_after_swap:
			self['HX-Trigger-After-Settle'] = trigger_after_settle


class BlockResponse(HttpResponse):
	'''Creates a TemplateResponse like object using django-render-block to render just a block in a template
	The format of block is "template_name:block_name"
	'''
	def __init__(self, request, block, context, **kwargs):
		template_name, block_name = block.split(':')
		super().__init__(render_block_to_string(template_name=template_name, block_name=block_name, context=context, request=request), **kwargs)


class HxResponse(HttpResponse):
	'''Creates a TemplateResponse-like object using django-render-block and HTMX header functions. It's main purpose is to make it easy to specify - on the server side - what HTMX should do with a response.

	Automatically gets the block name from HX-Block header, or it can be specified as a kwarg. The format of block should be "path/to/template.html:block_name"

	Uses django-render-block and the Okayjack HTMX extension."
	'''
	def __init__(self, request, *args, **kwargs):

		# Most instances will include a context, but some things like just triggering an event, or doing a refresh, doesn't need a context
		try:
			context = args[0]
		except IndexError:
			context=None

		# Remove extra kwargs before passing kwargs to HttpResponse
		swap = kwargs.pop('swap', None)
		target = kwargs.pop('target', None)
		trigger = kwargs.pop('trigger', None)
		trigger_after_settle = kwargs.pop('trigger_after_settle', None)
		trigger_after_swap = kwargs.pop('trigger_after_swap', None)

		# Render HTML from context and block reference
		html = None
		if 'block' in kwargs:
			block = kwargs.pop('block', None)
			if ':' in block:
				template_name, block_name = block.split(':')
				html = render_block_to_string(template_name=template_name, block_name=block_name, context=context, request=request)
			else:
				html = render_to_string(template_name=block, context=context, request=request)
		elif 'block' in request.hx:
			if ':' in request.hx['block']:
				template_name, block_name = request.hx['block'].split(':')
				html = render_block_to_string(template_name=template_name, block_name=block_name, context=context, request=request)
			else:
				html = render_to_string(template_name=request.hx['block'], context=context, request=request)
		else:
			# Sometimes we don't want any response body, such as when the response is just to instruct HTMX to do a client side refresh
			html = ''
		
		# Create response here so we can start adding headers below
		super().__init__(html, *args, **kwargs)

		# Swap
		if swap:
			self['HX-Reswap'] = swap

		# Target
		if target:
			self['HX-Retarget'] = target

		# Trigger
		if trigger:
			self['HX-Trigger'] = trigger
		if trigger_after_settle:
			self['HX-Trigger-After-Settle'] = trigger_after_settle
		if trigger_after_swap:
			self['HX-Trigger-After-Swap'] = trigger_after_swap


# The list of HTMX attributes that HxResponse recognises, and their header equivalent (for telling HTMX to do something different when it receives the response)
hx_attributes = [
	{ 'request': 'location', 'response': 'HX-Location'},
	{ 'request': 'push-url', 'response': 'HX-Push-Url'},
	{ 'request': 'redirect', 'response': 'HX-Redirect'},
	{ 'request': 'refresh', 'response': 'HX-Refresh'},
	{ 'request': 'replace-url', 'response': 'HX-Replace-Url'},
	{ 'request': 'swap', 'response': 'HX-Reswap'},
	{ 'request': 'target', 'response': 'HX-Retarget'},
	{ 'request': 'trigger', 'response': 'HX-Trigger'},
	{ 'request': 'trigger-after-settle', 'response': 'HX-Trigger-After-Settle'},
	{ 'request': 'trigger-after-swap', 'response': 'HX-Trigger-After-Swap'},
]

class HxStateResponse(HxResponse):
	'''A special HxResponse class that adds response headers (https://htmx.org/reference/#response_headers) for success and error states based on a list of HTMX attributes
	
	e.g. the request might have been made with a hx-success-target attribute and we use that to add the HX-Retarget response header'''

	def __init__(self, *args, **kwargs):
		state = kwargs.pop('state')
		request = args[0]

		# If there is a success/error block specified, pass that along as a kwarg.
		# This lets HxResponse create the request - with content from the block - before adding any extra headers to that request.
		if 'block' in request.hx[state]:
			kwargs['block'] = request.hx[state]['block']
		super().__init__(*args, **kwargs)

		# Add any success/error headers specified
		for attr in hx_attributes:
			if attr['request'] in request.hx[state]:
				self[attr['response']] = request.hx[state][attr['request']]

class HxSuccessResponse(HxStateResponse):
	'''A convenience class for creating a 'sucess' HxResponse. 
	The response will include any hx-success-* attributes specified in the request markup.'''
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs, state='success')

class HxErrorResponse(HxStateResponse):
	'''A convenience class for creating an 'error' HxResponse. 
	The response will include any hx-error-* attributes specified in the request markup.'''
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs, state='error')
