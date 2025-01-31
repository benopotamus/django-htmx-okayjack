from django.test import Client, TestCase
from django.urls import reverse
# from peek import peek
from urllib.parse import urlencode

# Help
# https://docs.djangoproject.com/en/5.1/topics/testing/advanced/#testing-reusable-applications
# https://docs.djangoproject.com/en/5.1/topics/testing/tools/


class MiddlewareFullChainTestCase(TestCase):
	def setUp(self):
		self.c = Client()

	# POST requests

	def post_success(self, headers):
		'''Creates a HxSuccess response with a POST request that used the supplied headers'''
		return self.c.post(reverse('state_form_view'), 
			content_type='application/x-www-form-urlencoded',
			data=urlencode({'testfield': 'hi'}),
			headers=headers,)
	
	def post_error(self, headers):
		'''Creates an HxError response with a POST request that used the supplied headers'''
		return self.c.post(reverse('state_form_view'), 
			content_type='application/x-www-form-urlencoded',
			data=urlencode({'something_other_than_testfield': 'oops'}),
			headers=headers,)
	
	def post_general(self, headers):
		'''
		Creates an HxResponse with a POST request that used the supplied headers. 
		This simulates using hx-* attributes rather than hx-success-* (or hx-error-*) attributes
		'''
		return self.c.post(reverse('general_form_view'), 
			content_type='application/x-www-form-urlencoded',
			data=urlencode({'testfield': 'hi'}),
			headers=headers,)
	
	def post_general_formless(self, headers):
		'''
		This is the same as post_general (returns a HxResponse) except there's no form involved. 
		
		This is an edge case as okayjack provides various HxResponse subclasses for returning a response that doesn't use a form (e.g. HxFire), so it's expected that users would use those subclasses instead.
		'''
		return self.c.post(reverse('general_formless_view'), 
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
		

	# General requests with views that set hx-trigger

	def hx_fire(self):
		'''Creates an HxFire response'''
		return self.c.post(reverse('hx_fire_view'))
	
	def hx_fire_after_swap(self):
		'''Creates an HxFire response'''
		return self.c.post(reverse('hx_fire_after_swap_view'))






	##################################### TESTS ########################################

	### Do-Nothing

	def test_do_nothing(self):
		response = self.post_general({'HX-Do-Nothing': ''})
		self.assertEquals(response.status_code, 204)

	def test_success_do_nothing(self):
		response = self.post_success({'HX-Success-Do-Nothing': ''})
		self.assertEquals(response.status_code, 204)

	def test_error_do_nothing(self):
		response = self.post_error({'HX-Error-Do-Nothing': ''})
		self.assertEquals(response.status_code, 204)


	### Fire-After-Receive

	def test_fire_after_receive(self):
		response = self.post_general({'HX-Fire-After-Receive': 'testevent'})
		self.assertEquals(response.status_code, 200)
		self.assertEquals(response.headers.get('HX-Trigger'), 'testevent')

	def test_success_fire_after_receive(self):
		response = self.post_success({'HX-Success-Fire-After-Receive': 'testevent'})
		self.assertEquals(response.status_code, 200)
		self.assertEquals(response.headers.get('HX-Trigger'), 'testevent')
	
	def test_error_fire_after_receive(self):
		response = self.post_error({'HX-Error-Fire-After-Receive': 'testevent'})
		self.assertEquals(response.status_code, 422)
		self.assertEquals(response.headers.get('HX-Trigger'), 'testevent')

	def test_error_fire_after_receive_precendence(self):
		# In this test, the HX-Error event should take precedence over the general one
		response = self.post_error({'HX-Fire-After-Receive': 'general-event'})
		response = self.post_error({'HX-Error-Fire-After-Receive': 'error-event'})
		self.assertEquals(response.status_code, 422)
		self.assertEquals(response.headers.get('HX-Trigger'), 'error-event')

	def test_fire(self):
		# 'fire' is a shorthand for hx-fire-after-receive (or success/error variants), we're testing that the shorthand works here
		response = self.post_general({'HX-Fire': 'testevent'})
		self.assertEquals(response.status_code, 200)
		self.assertEquals(response.headers.get('HX-Trigger'), 'testevent')


	### Fire-After-Settle

	def test_fire_after_settle(self):
		response = self.post_general({'HX-Fire-After-Settle': 'testevent'})
		self.assertEquals(response.status_code, 200)
		self.assertEquals(response.headers.get('HX-Trigger-After-Settle'), 'testevent')
		self.assertEquals(response.headers.get('HX-Trigger'), None)

	def test_success_fire_after_settle(self):
		response = self.post_success({'HX-Success-Fire-After-Settle': 'testevent'})
		self.assertEquals(response.status_code, 200)
		self.assertEquals(response.headers.get('HX-Trigger-After-Settle'), 'testevent')
		self.assertEquals(response.headers.get('HX-Trigger'), None)

	def test_error_fire_after_settle(self):
		response = self.post_error({'HX-Error-Fire-After-Settle': 'testevent'})
		self.assertEquals(response.status_code, 422)
		self.assertEquals(response.headers.get('HX-Trigger-After-Settle'), 'testevent')
		self.assertEquals(response.headers.get('HX-Trigger'), None)


	### Fire-After-Swap

	def test_fire_after_swap(self):
		response = self.post_general({'HX-Fire-After-Swap': 'testevent'})
		self.assertEquals(response.status_code, 200)
		self.assertEquals(response.headers.get('HX-Trigger-After-Swap'), 'testevent')
		self.assertEquals(response.headers.get('HX-Trigger'), None)

	def test_success_fire_after_swap(self):
		response = self.post_success({'HX-Success-Fire-After-Swap': 'testevent'})
		self.assertEquals(response.status_code, 200)
		self.assertEquals(response.headers.get('HX-Trigger-After-Swap'), 'testevent')
		self.assertEquals(response.headers.get('HX-Trigger'), None)

	def test_error_fire_after_swap(self):
		response = self.post_error({'HX-Error-Fire-After-Swap': 'testevent'})
		self.assertEquals(response.status_code, 422)
		self.assertEquals(response.headers.get('HX-Trigger-After-Swap'), 'testevent')
		self.assertEquals(response.headers.get('HX-Trigger'), None)


	### Fire via view
	# In these tests, we're simulating the user defining the fire/trigger behaviour in the view, rather than in the markup via headers
			
	def test_view_hx_fire(self):
		response = self.hx_fire() # No event passed, it is being set in the view
		self.assertEquals(response.status_code, 200)
		self.assertEquals(response.headers.get('HX-Trigger'), 'testevent')

	def test_view_hx_fire_after_swap(self):
		response = self.hx_fire_after_swap() # No event passed, it is being set in the view
		self.assertEquals(response.status_code, 200)
		self.assertEquals(response.headers.get('HX-Trigger-After-Swap'), 'testevent')


	### Location

	def test_location(self):
		response = self.post_general({'HX-Location': '{"path":"/test2", "target":"#testdiv"}'})
		self.assertEquals(response.status_code, 200)
		self.assertEquals(response.headers.get('HX-Location'), '{"path":"/test2", "target":"#testdiv"}')

	def test_success_location(self):
		response = self.post_success({'HX-Success-Location': '{"path":"/test2", "target":"#testdiv"}'})
		self.assertEquals(response.status_code, 200)
		self.assertEquals(response.headers.get('HX-Location'), '{"path":"/test2", "target":"#testdiv"}')

	def test_error_location(self):
		response = self.post_error({'HX-Error-Location': '{"path":"/test2", "target":"#testdiv"}'})
		self.assertEquals(response.status_code, 422)
		self.assertEquals(response.headers.get('HX-Location'), '{"path":"/test2", "target":"#testdiv"}')


	### Push-Url

	# No general tests for these as htmx handles those attributes directly

	def test_success_push_url(self):
		response = self.post_success({'HX-Success-Push-Url': '/yo'})
		self.assertEquals(response.status_code, 200)
		self.assertEquals(response.headers.get('HX-Push-Url'), '/yo')

	def test_success_push_url_true(self):
		response = self.post_success({'HX-Success-Push-Url': 'true'})
		self.assertEquals(response.status_code, 200)
		self.assertEquals(response.headers.get('HX-Push-Url'), reverse('state_form_view'))

	def test_error_push_url(self):
		response = self.post_error({'HX-Error-Push-Url': '/yo'})
		self.assertEquals(response.status_code, 422)
		self.assertEquals(response.headers.get('HX-Push-Url'), '/yo')

	def test_error_push_url_true(self):
		response = self.post_error({'HX-Error-Push-Url': 'true'})
		self.assertEquals(response.status_code, 422)
		self.assertEquals(response.headers.get('HX-Push-Url'), reverse('state_form_view'))


	### Redirect

	def test_redirect(self):
		response = self.post_general({'HX-Redirect': '/test2'})
		self.assertEquals(response.status_code, 200)
		self.assertEquals(response.headers.get('HX-Redirect'), '/test2')

	def test_success_redirect(self):
		response = self.post_success({'HX-Success-Redirect': '/test2'})
		self.assertEquals(response.status_code, 200)
		self.assertEquals(response.headers.get('HX-Redirect'), '/test2')

	def test_error_redirect(self):
		response = self.post_error({'HX-Error-Redirect': '/test2'})
		self.assertEquals(response.status_code, 422)
		self.assertEquals(response.headers.get('HX-Redirect'), '/test2')


	### Refresh

	def test_refresh(self):
		response = self.post_general({'HX-Refresh': 'true'})
		self.assertEquals(response.status_code, 204)
		self.assertEquals(response.headers.get('HX-Refresh'), 'true')

	def test_success_refresh(self):
		response = self.post_success({'HX-Success-Refresh': 'true'})
		self.assertEquals(response.status_code, 204)
		self.assertEquals(response.headers.get('HX-Refresh'), 'true')

	def test_error_refresh(self):
		response = self.post_error({'HX-Error-Refresh': 'true'})
		self.assertEquals(response.status_code, 204)
		self.assertEquals(response.headers.get('HX-Refresh'), 'true')

	# These last 2 test that the user can do hx-refresh attributes without a value
	def test_refresh_empty_string(self):
		response = self.post_general({'HX-Refresh': ''})
		self.assertEquals(response.status_code, 204)
		self.assertEquals(response.headers.get('HX-Refresh'), 'true')

	def test_success_refresh_empty_string(self):
		response = self.post_success({'HX-Success-Refresh': ''})
		self.assertEquals(response.status_code, 204)
		self.assertEquals(response.headers.get('HX-Refresh'), 'true')


	### Replace-Url

	# No general tests as htmx handles hx-replace-url directly

	def test_success_replace_url(self):
		response = self.post_success({'HX-Success-Replace-Url': '/test2'})
		self.assertEquals(response.status_code, 200)
		self.assertEquals(response.headers.get('HX-Replace-Url'), '/test2')

	def test_error_replace_url(self):
		response = self.post_error({'HX-Error-Replace-Url': '/test2'})
		self.assertEquals(response.status_code, 422)
		self.assertEquals(response.headers.get('HX-Replace-Url'), '/test2')


	### Swap

	# No general tests as htmx handles hx-swap directly

	def test_success_swap(self):
		response = self.post_success({'HX-Success-Swap': 'delete'})
		self.assertEquals(response.status_code, 200)
		self.assertEquals(response.headers.get('HX-Reswap'), 'delete')

	def test_error_swap(self):
		response = self.post_error({'HX-Error-Swap': 'afterend'})
		self.assertEquals(response.status_code, 422)
		self.assertEquals(response.headers.get('HX-Reswap'), 'afterend')


	### Target

	# No general tests as htmx handles hx-target directly

	def test_success_target(self):
		response = self.post_success({'HX-Success-Target': '#main'})
		self.assertEquals(response.status_code, 200)
		self.assertEquals(response.headers.get('HX-Retarget'), '#main')

	def test_error_target(self):
		response = self.post_error({'HX-Error-Target': '#errors'})
		self.assertEquals(response.status_code, 422)
		self.assertEquals(response.headers.get('HX-Retarget'), '#errors')


	### Block

	def test_block(self):
		response = self.post_general({'HX-Block': 'tests/index.html#main_area'})
		expected_html = '<div id="main">I am the main section 😎</div>'
		self.assertEquals(response.status_code, 200)
		self.assertEquals(response.content.decode(), expected_html)

	def test_success_block(self):
		response = self.post_success({'HX-Success-Block': 'tests/index.html#main_area'})
		expected_html = '<div id="main">I am the main section 😎</div>'
		self.assertEquals(response.status_code, 200)
		self.assertEquals(response.content.decode(), expected_html)

	def test_error_block(self):
		response = self.post_error({'HX-Error-Block': 'tests/index.html#errors_block'})
		expected_html = '<div id="errors"></div>'
		self.assertEquals(response.status_code, 422)
		self.assertEquals(response.content.decode(), expected_html)


	### hx-patch tests
	# We don't test much for these because post, patch, and put are treated the same way - okayjack is about hx attributes being turned into headers

	def test_success_patch_do_nothing(self):
		response = self.patch_success({'HX-Success-Do-Nothing': ''})
		self.assertEquals(response.status_code, 204)

	def test_patch_fire_after_receive(self):
		response = self.patch_general({'HX-Fire-After-Receive': 'testevent'})
		self.assertEquals(response.status_code, 200)
		self.assertEquals(response.headers.get('HX-Trigger'), 'testevent')

	def test_error_patch_swap(self):
		response = self.patch_error({'HX-Error-Swap': 'afterend'})
		self.assertEquals(response.status_code, 422)
		self.assertEquals(response.headers.get('HX-Reswap'), 'afterend')

	def test_error_patch_block(self):
		response = self.patch_error({'HX-Error-Block': 'tests/index.html#errors_block'})
		expected_html = '<div id="errors"></div>'
		self.assertEquals(response.status_code, 422)
		self.assertEquals(response.content.decode(), expected_html)


	### hx-delete tests
	# general_delete_view
	# success_delete_view
	# error_delete_view

	def test_delete_success_block(self):
		response = self.success_delete_view({'HX-Success-Block': 'tests/index.html#main_area'})
		expected_html = '<div id="main">I am the main section 😎</div>'
		self.assertEquals(response.status_code, 200)
		self.assertEquals(response.content.decode(), expected_html)

	def test_error_block(self):
		response = self.error_delete_view({'HX-Error-Block': 'tests/index.html#errors_block'})
		expected_html = '<div id="errors"></div>'
		self.assertEquals(response.status_code, 422)
		self.assertEquals(response.content.decode(), expected_html)
