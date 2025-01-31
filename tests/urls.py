from inspect import getmembers, isfunction
from django.urls import path
from tests import views

def create_path(view_name):
	view_func = getattr(views, view_name)
	return path(view_name, view_func, name=view_name)


# Get the view names from the views file
view_names = [member[0] for member in getmembers(views, isfunction)]

# Create paths based on the view names
urlpatterns = [create_path(view_name) for view_name in view_names]
