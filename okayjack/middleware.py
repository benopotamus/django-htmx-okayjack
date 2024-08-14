attrs_names = [
	'Location',
	'Push-Url',
	'Redirect',
	'Refresh',
	'Replace-Url',
	'Swap',
	'Target',
	'Trigger',
	'Trigger-After-Settle',
	'Trigger-After-Swap',
	'Block',
]


class OkayjackMiddleware:
	def __init__(self, get_response):
		self.get_response = get_response

	def __call__(self, request):
		request.hx = {
			'success': {},
			'error': {}
		}

		# Add Okayjack's custom hx-? attributes to request
		if 'HX-Block' in request.headers:
			request.hx['block'] = request.headers['HX-Block']
		if 'HX-Trigger-After-Receive' in request.headers:
			request.hx['trigger-after-receive'] = request.headers['HX-Trigger-After-Receive']
		if 'HX-Trigger-After-Settle' in request.headers:
			request.hx['trigger-after-settle'] = request.headers['HX-Trigger-After-Settle']
		if 'HX-Trigger-After-Swap' in request.headers:
			request.hx['trigger-after-swap'] = request.headers['HX-Trigger-After-Swap']

		# Add hx-success-* and hx-error-* attributes to request
		for attr_name in attrs_names:
			full_attr_name = 'HX-Success-'+attr_name
			if full_attr_name in request.headers:
				request.hx['success'][attr_name.lower()] = request.headers[full_attr_name]

			full_attr_name = 'HX-Error-'+attr_name
			if full_attr_name in request.headers:
				request.hx['error'][attr_name.lower()] = request.headers[full_attr_name]


		# For PATCH and PUT, process as a POST request, and then copy the values to request.[method]
		if request.method == 'PATCH' or request.method == 'PUT':
			'''	From https://thihara.github.io/Django-Req-Parsing/

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