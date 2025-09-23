from urllib.parse import urlencode
from django.urls import reverse

'''These request types aim to simulate common requests made by clients (browsers) using htmx.

There's success, errror, and general versions for POST, PATCH, and DELETE

The POST requests have a `view` argument. This allows tests to change the view used.
Most tests use the default view as specified in these function definitions.
'''

# POST requests

def post_success(self, headers, view='state_form_view'):
	'''Creates a HxSuccess response with a POST request that used the supplied headers'''
	return self.c.post(reverse(view), 
		content_type='application/x-www-form-urlencoded',
		data=urlencode({'testfield': 'hi'}),
		headers=headers,)

def post_error(self, headers, view='state_form_view'):
	'''Creates an HxError response with a POST request that used the supplied headers'''
	return self.c.post(reverse(view), 
		content_type='application/x-www-form-urlencoded',
		data=urlencode({'something_other_than_testfield': 'oops'}),
		headers=headers,)

def post_general(self, headers, view='general_form_view'):
	'''
	Creates an HxResponse with a POST request that used the supplied headers. 
	This simulates using hx-* attributes rather than hx-success-* (or hx-error-*) attributes
	'''
	return self.c.post(reverse(view), 
		content_type='application/x-www-form-urlencoded',
		data=urlencode({'testfield': 'hi'}),
		headers=headers,)

def post_general_formless(self, headers, view='general_formless_view'):
	'''
	This is the same as post_general (returns a HxResponse) except there's no form involved. 
	
	This is an edge case as okayjack provides various HxResponse subclasses for returning a response that doesn't use a form (e.g. HxFire), so it's expected that users would use those subclasses instead.
	'''
	return self.c.post(reverse(view), 
		content_type='application/x-www-form-urlencoded',
		headers=headers,)

# PATCH requests

def patch_success(self, headers):
	'''Creates a HxSuccess response with a PATCH request that used the supplied headers'''
	return self.c.patch(reverse('state_form_view'), 
		content_type='application/x-www-form-urlencoded',
		data=urlencode({'testfield': 'hi'}),
		headers=headers,)

def patch_error(self, headers):
	'''Creates an HxError response with a PATCH request that used the supplied headers'''
	return self.c.patch(reverse('state_form_view'), 
		content_type='application/x-www-form-urlencoded',
		data=urlencode({'something_other_than_testfield': 'oops'}),
		headers=headers,)

def patch_general(self, headers):
	'''Creates a successful HttpResponse with a PATCH request that used the supplied headers.'''
	return self.c.patch(reverse('general_form_view'), 
		content_type='application/x-www-form-urlencoded',
		data=urlencode({'testfield': 'hi'}),
		headers=headers,)

# DELETE requests

def general_delete_view(self, headers):
	'''Creates a successful HttpResponse with a DELETE request that used the supplied headers.'''
	return self.c.delete(reverse('general_delete_view'), headers=headers,)

def success_delete_view(self, headers):
	'''Creates a successful HttpResponse with a DELETE request that used the supplied headers.'''
	return self.c.delete(reverse('success_delete_view'), headers=headers,)

def error_delete_view(self, headers):
	'''Creates a successful HttpResponse with a DELETE request that used the supplied headers.'''
	return self.c.delete(reverse('error_delete_view'), headers=headers,)
	