# Okayjack (Django+htmx)

Okayjack (+`django-render-blocks`) extends Django and htmx a smidge so they are even more pleasant to use! 🥳

1. Extends htmx by moving all htmx logic to the request markup by default
	a. Which template or DTL block to use for a response
	a. How to handle a successful (valid) form submission vs an errorenous (invalid) ones 
	a. Triggering an action after a response is received
1. Extends Django's REST verbs support (adds a body to PATCH etc)

Codewise, Okayjack is:
1. Some Django middleware
1. A few HttpResponse classes
1. A htmx JavaScript extension.

![Farside comic](https://github.com/benopotamus/okayjack-htmx/assets/3161149/f293e078-989a-4539-adc6-cc43d54c8308)


## Overview
### htmx extension
Normal htmx requests - with a bit of Django form error display - look something like this

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


## Installation
Install things in the usual way.

1. `pip install django-render-blocks`

1. Add `okayjack` app to Django project

```
INSTALLED_APPS = [
    ...
    'render_block',
    'okayjack',
]
```

```
MIDDLEWARE = [
    ...
	'okayjack.middleware.OkayjackMiddleware',
]
```

3. Import the `okayjack.http` in your `views.py` to use the `HttpResponse-like` classes

4. Load htmx extension <https://htmx.org/attributes/hx-ext/> in template


# API

## htmx extension

Supports all htmx response headers https://htmx.org/reference/#response_headers. 

You can use a combination of:
* Regular `hx-*` attributes. E.g. `hx-target="..."`
* Regular `hx-success-*` attributes - used when Django returned a `HxSuccessResponse`. E.g. `hx-success-target="..."`
* Regular `hx-error-*` attributes - used when Django returned a `HxErrorResponse`. E.g. `hx-error-target="..."`

htmx will use the values of `hx-*` unless there is a `hx-success-*` or `hx-error-*` value (for a success or error response respectively).

The `*` in `hx-success-*` and `hx-error-*` attributes can be any of the following.

* location
* push-url
* redirect
* refresh
* replace-url
* swap
* target
* trigger-after-receive
* trigger-after-settle
* trigger-after-swap
* block

`trigger-after-receive` isn't a normal htmx attribute. It sets the `HX-Trigger` response header. It had to be renamed so it doesn't conflict with `hx-trigger` for triggering the request itself 🤷

`bock` is the path to a template and optional template block to use when generating the HTML response. E.g.

```hx-block="base/home.html:welcome_block"``` or ```hx-success-block="base/home.html:new_item"```

Blocks are regular Django template blocks. E.g.

```{% block welcome_block %}<p>some html here</p>{% endblock }```


## HttpResponse classes (main)

The main response classes you will use are

### HxResponse(request[, context, block=None, swap=None, trigger-after-receive=None, trigger_after_settle=None, trigger_after_swap=None])

Creates a TemplateResponse-like object using django-render-block and htmx header functions. Its main purpose is to make it easy to specify - on the server side - what htmx should do with a response.

Automatically gets the block name from `HX-Block` header, or it can be specified as a kwarg. The format of block should be `path/to/template.html:block_name`

```HxResponse(request, { 'form': form })```

Supports optional kwargs

```HxResponse(request, { 'form': form, trigger-after-receive='do-this-when-response-is-received'})```

### HxSuccessResponse(request[, context, block=None, swap=None, trigger-after-receive=None, trigger_after_settle=None, trigger_after_swap=None])

Creating a 'success' `HxResponse`. The response will use any `hx-success-*` attributes specified in the request markup. 

### HxErrorResponse(request[, context, block=None, swap=None, trigger-after-receive=None, trigger_after_settle=None, trigger_after_swap=None])

Creates an 'error' HxResponse. The response will use any `hx-error-*` attributes specified in the request markup.


## HttpResponse classes (extra)

Some extra response classes for when you don't intend to swap some new HTML into the page.

### HxDoNothing

A `HttpResponse` that tells htmx to do nothing

```HxDoNothing()```

### HxRedirect

A `HttpResponse` that tells htmx to do a client side redirect to the provided URL

```HxRedirect(reverse('home'))```

### HxRefresh

A `HttpResponse` that tells htmx to refresh the page

```HxRefresh()```

### HxTrigger(trigger_after_receive=None, trigger_after_swap=None, trigger_after_settle=None)

A `HttpResponse` that tells htmx to trigger an event - and do nothing else. 
https://htmx.org/headers/hx-trigger/

trigger: the name of the event to trigger. Can also be JSON string, which allows for triggering multiple events and/or passing data for the event

```HxTrigger('close-modal')```

### BlockResponse(block)

Creates a `TemplateResponse-like` object using django-render-block to render just a block in a template
The format of block is `template_path/template_name:block_name`. 

```BlockResponse('base/home.html:welcome_block')```