# from peek import peek
# peek.configure(show_line_number=True)

from django.test import Client, TestCase
from django.urls import reverse
from tests import test_requests

# Help
# https://docs.djangoproject.com/en/5.1/topics/testing/advanced/#testing-reusable-applications
# https://docs.djangoproject.com/en/5.1/topics/testing/tools/


class MiddlewareFullChainTestCase(TestCase):

	def setUp(self):
		self.c = Client()


	### Do-Nothing
	# Do-Nothing is added to responses so the okayjack JavaScript can prevent swapping for those responses

	def test_do_nothing(self):
		response = test_requests.post_general(self, {'HX-Do-Nothing': ''})
		self.assertEqual(response.status_code, 204)
		self.assertEqual(response.headers.get('HX-Do-Nothing'), 'true')

	def test_success_do_nothing(self):
		response = test_requests.post_success(self, {'HX-Success-Do-Nothing': ''})
		self.assertEqual(response.status_code, 204)
		self.assertEqual(response.headers.get('HX-Do-Nothing'), 'true')

	def test_error_do_nothing(self):
		response = test_requests.post_error(self, {'HX-Error-Do-Nothing': ''})
		self.assertEqual(response.status_code, 422)
		self.assertEqual(response.headers.get('HX-Do-Nothing'), 'true')


	### Fire-After-Receive

	def test_fire_after_receive(self):
		response = test_requests.post_general(self, {'HX-Fire-After-Receive': 'testevent'})
		self.assertEqual(response.status_code, 200)
		self.assertEqual(response.headers.get('HX-Trigger'), 'testevent')

	def test_success_fire_after_receive(self):
		response = test_requests.post_success(self, {'HX-Success-Fire-After-Receive': 'testevent'})
		self.assertEqual(response.status_code, 200)
		self.assertEqual(response.headers.get('HX-Trigger'), 'testevent')
	
	def test_error_fire_after_receive(self):
		response = test_requests.post_error(self, {'HX-Error-Fire-After-Receive': 'testevent'})
		self.assertEqual(response.status_code, 422)
		self.assertEqual(response.headers.get('HX-Trigger'), 'testevent')

	def test_error_fire_after_receive_precendence(self):
		# In this test, the HX-Error event should take precedence over the general one
		response = test_requests.post_error(self, {'HX-Fire-After-Receive': 'general-event'})
		response = test_requests.post_error(self, {'HX-Error-Fire-After-Receive': 'error-event'})
		self.assertEqual(response.status_code, 422)
		self.assertEqual(response.headers.get('HX-Trigger'), 'error-event')

	def test_fire(self):
		# 'fire' is a shorthand for hx-fire-after-receive (or success/error variants), we're testing that the shorthand works here
		response = test_requests.post_general(self, {'HX-Fire': 'testevent'})
		self.assertEqual(response.status_code, 200)
		self.assertEqual(response.headers.get('HX-Trigger'), 'testevent')


	### Fire-After-Settle

	def test_fire_after_settle(self):
		response = test_requests.post_general(self, {'HX-Fire-After-Settle': 'testevent'})
		self.assertEqual(response.status_code, 200)
		self.assertEqual(response.headers.get('HX-Trigger-After-Settle'), 'testevent')
		self.assertEqual(response.headers.get('HX-Trigger'), None)

	def test_success_fire_after_settle(self):
		response = test_requests.post_success(self, {'HX-Success-Fire-After-Settle': 'testevent'})
		self.assertEqual(response.status_code, 200)
		self.assertEqual(response.headers.get('HX-Trigger-After-Settle'), 'testevent')
		self.assertEqual(response.headers.get('HX-Trigger'), None)

	def test_error_fire_after_settle(self):
		response = test_requests.post_error(self, {'HX-Error-Fire-After-Settle': 'testevent'})
		self.assertEqual(response.status_code, 422)
		self.assertEqual(response.headers.get('HX-Trigger-After-Settle'), 'testevent')
		self.assertEqual(response.headers.get('HX-Trigger'), None)


	### Fire-After-Swap

	def test_fire_after_swap(self):
		response = test_requests.post_general(self, {'HX-Fire-After-Swap': 'testevent'})
		self.assertEqual(response.status_code, 200)
		self.assertEqual(response.headers.get('HX-Trigger-After-Swap'), 'testevent')
		self.assertEqual(response.headers.get('HX-Trigger'), None)

	def test_success_fire_after_swap(self):
		response = test_requests.post_success(self, {'HX-Success-Fire-After-Swap': 'testevent'})
		self.assertEqual(response.status_code, 200)
		self.assertEqual(response.headers.get('HX-Trigger-After-Swap'), 'testevent')
		self.assertEqual(response.headers.get('HX-Trigger'), None)

	def test_error_fire_after_swap(self):
		response = test_requests.post_error(self, {'HX-Error-Fire-After-Swap': 'testevent'})
		self.assertEqual(response.status_code, 422)
		self.assertEqual(response.headers.get('HX-Trigger-After-Swap'), 'testevent')
		self.assertEqual(response.headers.get('HX-Trigger'), None)


	### Fire via view
	# In these tests, we're simulating the user defining the fire/trigger behaviour in the view, rather than in the markup via headers
			
	def test_view_hx_fire(self):
		response = test_requests.post_general_formless(self, None, view='hx_fire_view') # No event passed, it is being set in the view
		self.assertEqual(response.status_code, 200)
		self.assertEqual(response.headers.get('HX-Trigger'), 'testevent')

	def test_view_hx_fire_after_swap(self):
		response = test_requests.post_general_formless(self, None, view='hx_fire_after_swap_view') # No event passed, it is being set in the view
		self.assertEqual(response.status_code, 200)
		self.assertEqual(response.headers.get('HX-Trigger-After-Swap'), 'testevent')


	### Location

	def test_location(self):
		response = test_requests.post_general(self, {'HX-Location': '{"path":"/test2", "target":"#testdiv"}'})
		self.assertEqual(response.status_code, 200)
		self.assertEqual(response.headers.get('HX-Location'), '{"path":"/test2", "target":"#testdiv"}')

	def test_success_location(self):
		response = test_requests.post_success(self, {'HX-Success-Location': '{"path":"/test2", "target":"#testdiv"}'})
		self.assertEqual(response.status_code, 200)
		self.assertEqual(response.headers.get('HX-Location'), '{"path":"/test2", "target":"#testdiv"}')

	def test_error_location(self):
		response = test_requests.post_error(self, {'HX-Error-Location': '{"path":"/test2", "target":"#testdiv"}'})
		self.assertEqual(response.status_code, 422)
		self.assertEqual(response.headers.get('HX-Location'), '{"path":"/test2", "target":"#testdiv"}')


	### Push-Url

	# No general tests for these as htmx handles those attributes directly

	def test_success_push_url(self):
		response = test_requests.post_success(self, {'HX-Success-Push-Url': '/yo'})
		self.assertEqual(response.status_code, 200)
		self.assertEqual(response.headers.get('HX-Push-Url'), '/yo')

	def test_success_push_url_true(self):
		response = test_requests.post_success(self, {'HX-Success-Push-Url': 'true'})
		self.assertEqual(response.status_code, 200)
		self.assertEqual(response.headers.get('HX-Push-Url'), reverse('state_form_view'))

	def test_error_push_url(self):
		response = test_requests.post_error(self, {'HX-Error-Push-Url': '/yo'})
		self.assertEqual(response.status_code, 422)
		self.assertEqual(response.headers.get('HX-Push-Url'), '/yo')

	def test_error_push_url_true(self):
		response = test_requests.post_error(self, {'HX-Error-Push-Url': 'true'})
		self.assertEqual(response.status_code, 422)
		self.assertEqual(response.headers.get('HX-Push-Url'), reverse('state_form_view'))


	### Redirect

	def test_redirect(self):
		response = test_requests.post_general(self, {'HX-Redirect': '/test2'})
		self.assertEqual(response.status_code, 200)
		self.assertEqual(response.headers.get('HX-Redirect'), '/test2')

	def test_success_redirect(self):
		response = test_requests.post_success(self, {'HX-Success-Redirect': '/test2'})
		self.assertEqual(response.status_code, 200)
		self.assertEqual(response.headers.get('HX-Redirect'), '/test2')

	def test_error_redirect(self):
		response = test_requests.post_error(self, {'HX-Error-Redirect': '/test2'})
		self.assertEqual(response.status_code, 422)
		self.assertEqual(response.headers.get('HX-Redirect'), '/test2')


	### Refresh

	def test_refresh(self):
		response = test_requests.post_general(self, {'HX-Refresh': 'true'})
		self.assertEqual(response.status_code, 200)
		self.assertEqual(response.headers.get('HX-Refresh'), 'true')

	def test_success_refresh(self):
		response = test_requests.post_success(self, {'HX-Success-Refresh': 'true'})
		self.assertEqual(response.status_code, 200)
		self.assertEqual(response.headers.get('HX-Refresh'), 'true')

	def test_error_refresh(self):
		response = test_requests.post_error(self, {'HX-Error-Refresh': 'true'})
		self.assertEqual(response.status_code, 422)
		self.assertEqual(response.headers.get('HX-Refresh'), 'true')

	# These last 2 test that the user can do hx-refresh attributes without a value
	def test_refresh_empty_string(self):
		response = test_requests.post_general(self, {'HX-Refresh': ''})
		self.assertEqual(response.status_code, 200)
		self.assertEqual(response.headers.get('HX-Refresh'), 'true')

	def test_success_refresh_empty_string(self):
		response = test_requests.post_success(self, {'HX-Success-Refresh': ''})
		self.assertEqual(response.status_code, 200)
		self.assertEqual(response.headers.get('HX-Refresh'), 'true')


	### Replace-Url

	# No general tests as htmx handles hx-replace-url directly

	def test_success_replace_url(self):
		response = test_requests.post_success(self, {'HX-Success-Replace-Url': '/test2'})
		self.assertEqual(response.status_code, 200)
		self.assertEqual(response.headers.get('HX-Replace-Url'), '/test2')

	def test_error_replace_url(self):
		response = test_requests.post_error(self, {'HX-Error-Replace-Url': '/test2'})
		self.assertEqual(response.status_code, 422)
		self.assertEqual(response.headers.get('HX-Replace-Url'), '/test2')


	### Swap

	# No general tests as htmx handles hx-swap directly

	def test_success_swap(self):
		response = test_requests.post_success(self, {'HX-Success-Swap': 'delete'})
		self.assertEqual(response.status_code, 200)
		self.assertEqual(response.headers.get('HX-Reswap'), 'delete')

	def test_error_swap(self):
		response = test_requests.post_error(self, {'HX-Error-Swap': 'afterend'})
		self.assertEqual(response.status_code, 422)
		self.assertEqual(response.headers.get('HX-Reswap'), 'afterend')


	### Target

	# No general tests as htmx handles hx-target directly

	def test_success_target(self):
		response = test_requests.post_success(self, {'HX-Success-Target': '#main'})
		self.assertEqual(response.status_code, 200)
		self.assertEqual(response.headers.get('HX-Retarget'), '#main')

	def test_error_target(self):
		response = test_requests.post_error(self, {'HX-Error-Target': '#errors'})
		self.assertEqual(response.status_code, 422)
		self.assertEqual(response.headers.get('HX-Retarget'), '#errors')


	### Block

	def test_block(self):
		response = test_requests.post_general(self, {'HX-Block': 'tests/index.html#main_area'})
		expected_html = '<div id="main">I am the main section 😎</div>'
		self.assertEqual(response.status_code, 200)
		self.assertEqual(response.content.decode(), expected_html)

	def test_success_block(self):
		response = test_requests.post_success(self, {'HX-Success-Block': 'tests/index.html#main_area'})
		expected_html = '<div id="main">I am the main section 😎</div>'
		self.assertEqual(response.status_code, 200)
		self.assertEqual(response.content.decode(), expected_html)

	def test_error_block(self):
		response = test_requests.post_error(self, {'HX-Error-Block': 'tests/index.html#errors_block'})
		expected_html = '<div id="errors"></div>'
		self.assertEqual(response.status_code, 422)
		self.assertEqual(response.content.decode(), expected_html)


	### hx-patch tests
	# We don't test much for these because post, patch, and put are treated the same way - okayjack is about hx attributes being turned into headers

	def test_success_patch_do_nothing(self):
		response = test_requests.patch_success(self, {'HX-Success-Do-Nothing': ''})
		self.assertEqual(response.status_code, 204)

	def test_patch_fire_after_receive(self):
		response = test_requests.patch_general(self, {'HX-Fire-After-Receive': 'testevent'})
		self.assertEqual(response.status_code, 200)
		self.assertEqual(response.headers.get('HX-Trigger'), 'testevent')

	def test_error_patch_swap(self):
		response = test_requests.patch_error(self, {'HX-Error-Swap': 'afterend'})
		self.assertEqual(response.status_code, 422)
		self.assertEqual(response.headers.get('HX-Reswap'), 'afterend')

	def test_error_patch_block(self):
		response = test_requests.patch_error(self, {'HX-Error-Block': 'tests/index.html#errors_block'})
		expected_html = '<div id="errors"></div>'
		self.assertEqual(response.status_code, 422)
		self.assertEqual(response.content.decode(), expected_html)


	### hx-delete tests

	def test_delete_success_block(self):
		response = test_requests.success_delete_view(self, {'HX-Success-Block': 'tests/index.html#main_area'})
		expected_html = '<div id="main">I am the main section 😎</div>'
		self.assertEqual(response.status_code, 200)
		self.assertEqual(response.content.decode(), expected_html)

	def test_error_block(self):
		response = test_requests.error_delete_view(self, {'HX-Error-Block': 'tests/index.html#errors_block'})
		expected_html = '<div id="errors"></div>'
		self.assertEqual(response.status_code, 422)
		self.assertEqual(response.content.decode(), expected_html)


	### Combo tests
	# 
	# These ones test what should happen when some attributes take precedence over others

	def test_combo1(self):
		response = test_requests.post_success(
			self, 
			{ 'HX-Block': 'tests/index.html#foo',
			'HX-Success-Block': 'tests/index.html#main_area', }
		)
		html_main = '<div id="main">I am the main section 😎</div>'
		html_foo = '<div id="foo">Yo!</div>'
		self.assertEqual(response.status_code, 200)
		self.assertEqual(response.content.decode(), html_main)

	def test_combo2(self):
		response = test_requests.post_success(
			self, 
			{ 'HX-Block': 'tests/index.html#foo',
			'HX-Success-Block': 'tests/index.html#main_area',
			'HX-Success-Refresh': 'true',}
		)
		self.assertEqual(response.status_code, 200)
		self.assertEqual(response.content.decode(), '') # No content because success refresh should take precedence
		self.assertEqual(response.headers.get('HX-Refresh'), 'true')

	def test_combo3(self):
		response = test_requests.post_general(
			self, 
			{ 'HX-Block': 'tests/index.html#foo',
			'HX-Success-Block': 'tests/index.html#main_area',
			'HX-Success-Refresh': 'true', }
		)
		html_foo = '<div id="foo">Yo!</div>'
		self.assertEqual(response.status_code, 200)
		self.assertEqual(response.content.decode(), html_foo)
		self.assertEqual(response.headers.get('HX-Refresh'), None)

	def test_combo4(self):
		response = test_requests.post_error(
			self, 
			{ 'HX-Block': 'tests/index.html#foo',
			'HX-Success-Block': 'tests/index.html#main_area',
			'HX-Success-Refresh': 'true', }
		)
		html_foo = '<div id="foo">Yo!</div>'
		self.assertEqual(response.status_code, 422)
		self.assertEqual(response.content.decode(), html_foo)
		self.assertEqual(response.headers.get('HX-Refresh'), None)

	def test_combo4(self):
		response = test_requests.post_error(
			self, 
			{ 'HX-Block': 'tests/index.html#foo',
			'HX-Error-Block': 'tests/index.html#main_area',
			'HX-Error-Refresh': 'true',
			'HX-Do-Nothing': 'true', }
		)
		self.assertEqual(response.status_code, 422)
		self.assertEqual(response.content.decode(), '')
		self.assertEqual(response.headers.get('HX-Refresh'), None)
		self.assertEqual(response.headers.get('HX-Do-Nothing'), 'true') # HX-Do-Nothing should have precedence over HX-Refresh


	### Attribute override tests
	# 
	# These test the View overriding what was received in the request. 
	# The view does this using keyword arguments.

	def test_block_kwarg(self):
		'''In this test, the request is for this block:

			'<div id="main">I am the main section 😎</div>'

		But the view sets the block to:

			'<div id="foo">Yo!</div>'
		'''
		response = test_requests.post_success(
			self, 
			{'HX-Block': 'tests/index.html#main_area'},
			view='success_block_override_view'
		)
		expected_html = '<div id="foo">Yo!</div>'
		self.assertEqual(response.status_code, 200)
		self.assertEqual(response.content.decode(), expected_html)

	def test_swap_kwarg(self):
		'''Same test as above (test_block_kwarg) except this also has 'swap' and target kwargs
		'''
		response = test_requests.post_success(
			self, 
			{ 'HX-Block': 'tests/index.html#main_area',
			'HX-Swap': 'innerHTML',
			'HX-Target': '#lonely-div' },
			view='hx_swap_override_view'
		)
		expected_html = '<div id="foo">Yo!</div>'
		self.assertEqual(response.status_code, 200)
		self.assertEqual(response.content.decode(), expected_html)
		self.assertEqual(response.headers.get('HX-Retarget'), '#foo')
		self.assertEqual(response.headers.get('HX-Reswap'), 'outerHTML')

	def test_success_swap_kwarg(self):
		'''Same test as above (test_block_kwarg) except this also has 'swap' and target kwargs
		'''
		response = test_requests.post_success(
			self, 
			{ 'HX-Block': 'tests/index.html#main_area',
			'HX-Swap': 'innerHTML',
			'HX-Target': '#lonely-div' },
			view='hx_success_swap_override_view'
		)
		expected_html = '<div id="foo">Yo!</div>'
		self.assertEqual(response.status_code, 200)
		self.assertEqual(response.content.decode(), expected_html)
		self.assertEqual(response.headers.get('HX-Retarget'), '#foo')
		self.assertEqual(response.headers.get('HX-Reswap'), 'outerHTML')
