from django.urls import path
from tests import views

view_names = [
	'state_form_view',
	'general_form_view',
	'general_delete_view',
	'success_delete_view',
	'error_delete_view',
]

def create_path(view_name):
	view_func = getattr(views, view_name)
	return path(view_name, view_func, name=view_name)

urlpatterns = [create_path(view_name) for view_name in view_names]
