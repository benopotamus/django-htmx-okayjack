from okayjack.http import *
from .forms import *
	
def state_form_view(request):
	'''Returns appropriate hx-success/hx-error response'''
	form = TestForm(request.POST or request.PATCH or request.PUT)
	if form.is_valid():
		return HxSuccessResponse(request)
	return HxErrorResponse(request)

def general_form_view(request):
	'''Just returns a success response so we can check the headers. It doesn't bother with form validation.'''
	return HxResponse(request)
	
def general_delete_view(request):
	'''Returns a HxResponse to a DELETE request'''
	return HxResponse(request)

def success_delete_view(request):
	'''Returns a HxSuccessResponse to a DELETE request'''
	return HxSuccessResponse(request)

def error_delete_view(request):
	'''Returns a HxErrorResponse to a DELETE request'''
	return HxErrorResponse(request)
