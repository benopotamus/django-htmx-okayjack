from okayjack.http import *
from .forms import *

### hx-success|error-* views
def state_form_view(request):
	'''Returns appropriate hx-success/hx-error response'''
	form = TestForm(request.POST or request.PATCH or request.PUT)
	if form.is_valid():
		return HxSuccessResponse(request, form)
	return HxErrorResponse(request, form)

### hx-* views
def general_form_view(request):
	'''Returns a HxResponse response. For testing hx-* attributes.'''
	form = TestForm(request.POST or request.PATCH or request.PUT)
	if form.is_valid():
		return HxResponse(request, form)
	raise Exception('Invalid form in general_form_view')

def general_formless_view(request):
	'''Returns a HxResponse response without validating a form so we can just check the headers.'''
	return HxResponse(request) # No context for formless view

### Delete views
# These _could_ have contexts but that is tested enough by state_form_view
def general_delete_view(request):
	'''Returns a HxResponse to a DELETE request'''
	return HxResponse(request) 

def success_delete_view(request):
	'''Returns a HxSuccessResponse to a DELETE request'''
	return HxSuccessResponse(request)

def error_delete_view(request):
	'''Returns a HxErrorResponse to a DELETE request'''
	return HxErrorResponse(request)

### HxFire
def hx_fire_view(request):
	return HxFire('testevent')

def hx_fire_after_swap_view(request):
	return HxFire(fire_after_swap='testevent')