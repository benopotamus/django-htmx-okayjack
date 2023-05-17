# Okayjack Django and HTMX extension

Okayjack is some Django middleware, some Django response classes, and an HTMX extension, to make HTMX forms even easier. It also uses `django-render-blocks`.

## Overview
### HTMX extension
Normal HTMX requests - with a bit of Django form error display - look something like this

```html
	<form hx-post="/store">

		<input id="title" name="title" type="text" {% if form.title.errors %}class="error"{% endif %}>
		{% if form.title.errors %}
			<div class='error'>{{ form.title.errors }}</div>
		{% endif %}
		<button type="submit">Submit</button>

	</form>
```

With Okayjack, you can do this.
```html
{% block title_form %}
	<form 
		hx-post="/store"
		hx-success-target="h1"
		hx-success-swap="outerHTML"
		hx-success-block="this-example-file.html:title_success"
		hx-error-block="this-example-file.html:title_form">

			<input id="title" name="title" type="text" {% if form.title.errors %}class="error"{% endif %}>
			{% if form.title.errors %}
				<div class='error'>{{ form.title.errors }}</div>
			{% endif %}
			<button type="submit">Submit</button>

	</form>
{% endblock %}

<template>
	{% block title_success %}
		<h1>{{ title }}</h1>
	{% endblock %}
</template>
```

### Django middleware and response classes
Given the above HTML, in the corresponding Django view we now only have to do the following to handle both success and error variations.
```python
def title(request, question_id):
	form = TitleForm(request.POST)
	if form.is_valid():
		form.save()
		return HxSuccessResponse(request, {'form': form)
	return HxErrorResponse(request, {'form': form})
```

This is nice because it keeps all the view declaration stuff in the HTML file.

## Installation
Install things in the normal way.

1. `pip install django-render-blocks`

1. Load HTMX extension <https://htmx.org/attributes/hx-ext/>

1. Add the Django middleware <https://docs.djangoproject.com/en/4.2/topics/http/middleware/#activating-middleware>

1. import the `http` file to use the response classes
