from django.http import QueryDict

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

		# Add hx-block value to request
		if 'HX-Block' in request.headers:
			request.hx['block'] = request.headers['HX-Block']

		# Add hx-success-* and hx-error-* attributes to request
		for attr_name in attrs_names:
			full_attr_name = 'HX-Success-'+attr_name
			if full_attr_name in request.headers:
				request.hx['success'][attr_name.lower()] = request.headers[full_attr_name]

			full_attr_name = 'HX-Error-'+attr_name
			if full_attr_name in request.headers:
				request.hx['error'][attr_name.lower()] = request.headers[full_attr_name]


		# Copy PATCH method data to request
		if request.method == 'PATCH':
			request.PATCH = QueryDict(request.body, mutable=True)
			
			# Convert booleans from strings to Python booleans
			for key, value in request.PATCH.items():
				if value == 'true':
					request.PATCH[key] = True
				elif value == 'false':
					request.PATCH[key] = False

		response = self.get_response(request)
		return response
	