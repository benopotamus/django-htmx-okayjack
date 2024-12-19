from django import forms

class TestForm(forms.Form):
	'''Basic form field. All our form tests just have this one field as we're testing headers rather than form fields.'''
	testfield = forms.CharField()