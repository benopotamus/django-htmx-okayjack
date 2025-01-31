headerAttrs = [
	'Block',
	'Do-Nothing',
	'Fire-After-Receive',
	'Fire-After-Settle',
	'Fire-After-Swap',
	'Fire', # Fire is a shorthand for Fire-After-Receive
	'Location',
	'Redirect',
	'Refresh',
]

# These last 4 will never have general request headers (e.g. HX-Swap) because they're processed client side by htmx
# These should not be added to general otherwise it will confuse things (e.g. HX-Target doesn't have the '#' for the id)	
clientProcessedAttrs =[
	'Replace-Url',
	'Swap',
	'Target',
	#'Push-Url', # Special processing for this one
]


class OkayjackMiddleware:
	'''Modifies a request object so the request.method matches the one from the client, and populates the request.hx attribute.

	request.method:
		Adds PUT or PATCH objects to the Request (if the originating request used one of those methods). It does this by processing as a POST and then just changed the request.method value. POST already has lots of good form processing so this was the least custom way to implement that.

	request.hx
		This builds on the okayjack htmx extension (the JavaScript one). The extension put all okayjack attribute values into headers in the request so they can be processed in Django. This middleware then takes any okayjack headers and puts them into a request.hx object for later processing in okayjack.http.
	'''

	def __init__(self, get_response):
		self.get_response = get_response

	def __call__(self, request):
		request.hx = {
			'success': {},	# For hx-success-* attributes
			'error': {},	# For hx-error-* attributes
			'general': {}	# For hx-* attributes
		}

		# Copy request headers into the relevant place in request.hx
		for attr_name in headerAttrs:
			full_attr_name = f'HX-{attr_name}'
			if full_attr_name in request.headers:
				request.hx['general'][attr_name.lower()] = request.headers[full_attr_name]
				# e.g. request.hx['block'] = request.headers['HX-Block']

		for attr_name in headerAttrs + clientProcessedAttrs:
			full_attr_name = f'HX-Success-{attr_name}'
			if full_attr_name in request.headers:
				request.hx['success'][attr_name.lower()] = request.headers[full_attr_name]

			full_attr_name = f'HX-Error-{attr_name}'
			if full_attr_name in request.headers:
				request.hx['error'][attr_name.lower()] = request.headers[full_attr_name]

		# Special processing for Push-Url because it has a feature where if the value is "true", the client url should be changed to the requested url. Only applies to success and error headers as htmx handles the general one already
		if 'HX-Success-Push-Url' in request.headers:
			if request.headers['HX-Success-Push-Url'] == 'true':
				request.hx['success']['push-url'] = request.path
			else:
				request.hx['success']['push-url'] = request.headers['HX-Success-Push-Url']

		if 'HX-Error-Push-Url' in request.headers:
			if request.headers['HX-Error-Push-Url'] == 'true':
				request.hx['error']['push-url'] = request.path
			else:
				request.hx['error']['push-url'] = request.headers['HX-Error-Push-Url']


		# For PATCH and PUT, process as a POST request, and then copy the values to request.[method]
		if request.method == 'PATCH' or request.method == 'PUT':
			'''From https://thihara.github.io/Django-Req-Parsing/

			The try/except abominiation here is due to a bug
			in mod_python. This should fix it.
			
			Bug fix: if _load_post_and_files has already been called, for
			example by middleware accessing request.POST, the below code to
			pretend the request is a POST instead of a PUT will be too late
			to make a difference. Also calling _load_post_and_files will result
			in the following exception:

				AttributeError: You cannot set the upload handlers after the upload has been processed.	

			The fix is to check for the presence of the _post field which is set
			the first time _load_post_and_files is called (both by wsgi.py and
			modpython.py). If it's set, the request has to be 'reset' to redo
			the query value parsing in POST mode.
			'''
			original_method = request.method

			if hasattr(request, '_post'):
				del request._post
				del request._files
			try:
				request.method = "POST"
				request._load_post_and_files()
				request.method = original_method
			except AttributeError:
				request.META['REQUEST_METHOD'] = 'POST'
				request._load_post_and_files()
				request.META['REQUEST_METHOD'] = original_method
			
			setattr(request, request.method, request.POST) # equates to, e.g: request.PATCH = request.POST


		# Return response for next middleware
		response = self.get_response(request)
		return response