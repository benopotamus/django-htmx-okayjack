# Okayjack Django and HTMX extension

Okayjack is some Django middleware, some Django response classes, and an HTMX extension, to make HTMX forms even easier. It also uses `django-render-blocks`.

![image](https://github.com/benopotamus/okayjack-htmx/assets/3161149/f293e078-989a-4539-adc6-cc43d54c8308)


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
Install things in the usual way.

1. `pip install django-render-blocks`

1. Load HTMX extension <https://htmx.org/attributes/hx-ext/>

1. Add the Django middleware <https://docs.djangoproject.com/en/4.2/topics/http/middleware/#activating-middleware>

1. import the `http` file to use the response classes

# API

## HTMX extension

Supports all HTMX response headers https://htmx.org/reference/#response_headers

You can use a combination of:
* Regular `hx-*` attributes. E.g. `hx-target="..."`
* Regular `hx-success-*` attributes - used when Django returned a `HxSuccessResponse`. E.g. `hx-success-target="..."`
* Regular `hx-error-*` attributes - used when Django returned a `HxErrorResponse`. E.g. `hx-error-target="..."`

HTMX will use the values of `hx-*` unless there is a `hx-success-*` or `hx-error-*` value (for a success or error response respectively).

The `*` in `hx-success-*` and `hx-error-*` attributes can be any of the following. Note: these are the regular HTMX attribute names, there's no custom ones.

* location
* push-url
* redirect
* refresh
* replace-url
* swap
* target
* trigger
* trigger-after-settle
* trigger-after-swap

### hx-block

Okay, there is **one** custom attribute `hx-block` - including `hx-success-block` and `hx-error-block` variants.

The block is the path to a template, and optionally a block within that template, to use when generating the HTML response. E.g.

```hx-success-block="base/home.html:welcome_block"```

Blocks are regular Django template blocks. E.g.

```{% block welcome_block %}<p>some html here</p>{% endblock }```

 * It also supports a hx-block attribute, which is for use with a HxResponse Django class and django-render-block.

## HttpResponse classes

### HxDoNothing

A HttpResponse that tells htmx to do nothing

```HxDoNothing()```

### HxRedirect

A HttpResponse that tells htmx to do a client side redirect to the provided URL

```HxRedirect(reverse('home'))```

### HxRefresh

A HttpResponse that tells htmx to refresh the page

```HxRefresh()```

### HxTrigger(trigger)

A HttpResponse that tells htmx to trigger an event - and do nothing else. 
https://htmx.org/headers/hx-trigger/

trigger: the name of the event to trigger. Can also be JSON string, which allows for triggering multiple events and/or passing data for the event

```HxTrigger('close-modal')```

### BlockResponse(block)

Creates a TemplateResponse like object using django-render-block to render just a block in a template
The format of block is "template_path/template_name:block_name"

```BlockResponse('base/home.html:welcome_block')```

### HxResponse(request[, context, block=None, swap=None, trigger=None, trigger_after_settle=None, trigger_after_swap=None)

Creates a TemplateResponse-like object using django-render-block and HTMX header functions. Its main purpose is to make it easy to specify - on the server side - what HTMX should do with a response.

Automatically gets the block name from HX-Block header, or it can be specified as a kwarg. The format of block should be "path/to/template.html:block_name"

```HxResponse(request, { 'form': form, trigger='do-this-when-response-is-received'})```

### HxSuccessResponse(request)

A convenience class for creating a 'sucess' HxResponse. The response will include any hx-success-* attributes specified in the request markup.

```HxSuccessResponse(request, { 'form': form, trigger='do-this-when-response-is-received'})```

### HxErrorResponse(request)

A convenience class for creating an 'error' HxResponse. The response will include any hx-error-* attributes specified in the request markup.

```HxErrorResponse(request, { 'form': form, trigger='do-this-when-response-is-received'})```
