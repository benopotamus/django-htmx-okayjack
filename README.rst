Django Okayjack (Django+htmx)
#############################

Tell htmx what to do with success (200) and error (4xx) responses for a request by using new ``hx-*`` attributes.

.. code-block:: html
	hx-success-target="#toast-container"
	hx-success-trigger="open-toast-container"
	hx-error-target="#contact-form"

It also adds support for using *parts* of a template in a response, rather than creating separate template responses for each response type. And it adds PUT and PATCH to Django.


Requirements
============

`django-render-block <https://github.com/clokep/django-render-block/blob/main/README.rst>`_

Installation
============

1. ``pip install django-htmx-okayjack``

2. Add to ``settings.py``::

		INSTALLED_APPS = [
			...,
			'render_block',
			'okayjack',
			...,
		]


		MIDDLEWARE = [
			...,
			'okayjack.middleware.OkayjackMiddleware',
			...,
		]

3. Import ``okayjack.http`` in your ``views.py`` to use the ``HttpResponse``-like classes::
		
		from okayjack.http import HxSuccessResponse, HxErrorResponse

4. Load the htmx extension in the template in the usual way - see https://htmx.org/attributes/hx-ext/.::

		<head>
			<script defer src="{% static 'okayjack/js/htmx.ext.okayjack.js' %}"></script>
		</head>

		<body hx-ext="okayjack>


Examples
========

This example shows the new htmx-like attributes being used to specify which DTL block to use for a "success" response, and which to use for an "error" response (e.g. form failed validaiton).

The DTL blocks can be in any file - even in the same file as the originating htmx, as is the case in this example.

You can also just reference a template file without the block part (the part after the colon).

.. code-block:: html

	{% block title_form %}
	<form 
		hx-post="/store"
		hx-success-target="h1"
		hx-success-swap="outerHTML"
		hx-success-block="this-example-file.html:title_success"
		hx-error-block="this-example-file.html:title_form">
	
			<input id="title" name="title" type="text" {% if form.title.errors % class="error"{% endif %}>
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


Given the above HTML, in the corresponding Django ``views.py`` we now only have to do the following to handle both success and error variations.

.. code-block:: python

   def title(request, question_id):
       form = TitleForm(request.POST)
       if form.is_valid():
           form.save()
           return HxSuccessResponse(request, {'form': form})
       return HxErrorResponse(request, {'form': form})

As you can see, all of the UI logic about which template to use for success and error responses has been moved to the template, leaving the ``views.py`` to just specify whether the response should be treated as a success or error.

API
===

htmx extension
--------------

Okayjack supports all htmx response headers https://htmx.org/reference/#response_headers.

You can use any combination of: 

* ``hx-*`` attributes. E.g. ``hx-target="..."``
* ``hx-success-*`` attributes. E.g. ``hx-success-target="..."``. Used when Django returns a ``HxSuccessResponse``.
* ``hx-error-*`` attributes. E.g. ``hx-error-target="..."``. Used when Django returns a ``HxErrorResponse``.

htmx will use the values of ``hx-*`` unless there is a ``hx-success-*``
or ``hx-error-*`` value (for a success or error response respectively).

The ``*`` in ``hx-success-*`` and ``hx-error-*`` attributes can be any
of the following.

-  location
-  push-url
-  redirect
-  refresh
-  replace-url
-  swap
-  target
-  trigger-after-receive
-  trigger-after-settle
-  trigger-after-swap
-  block

``trigger-after-receive`` 
	This isn’t a normal htmx attribute. It sets the ``HX-Trigger`` response header. It was renamed so it doesn’t conflict with ``hx-trigger`` for triggering the request itself 🤷

``block``
	This is the path to a template and optional template block. Used to generate the HTML response. 
	
	``hx-block="base/home.html:welcome_block"``

	Blocks are regular Django template blocks.

	``{% block welcome_block %}<p>some html here</p>{% endblock }``

HttpResponse classes (main)
---------------------------

``HxSuccessResponse``

	Creates a ‘success’ ``HxResponse``. The response will use any ``hx-success-*`` attributes specified in the template.
	
	``HxSuccessResponse(request[, context, block=None, swap=None, trigger-after-receive=None, trigger_after_settle=None, trigger_after_swap=None])``

``HxErrorResponse``

	Creates an ‘error’ HxResponse. The response will use any ``hx-error-*``
	attributes specified in the request markup.
	
	``HxErrorResponse(request[, context, block=None, swap=None, trigger-after-receive=None, trigger_after_settle=None, trigger_after_swap=None])``


``HxResponse``

	This is the base Okayjack response class. It gives you Okayjack's features (using kwargs) but lets you specify which ones to use. 
	
	At a minimum, it will automatically get the template/block for the response from either the ``block`` kwarg or the ``HX-Block`` request header. 

	``HxResponse(request[, context, block=None, swap=None, trigger-after-receive=None, trigger_after_settle=None, trigger_after_swap=None])``
	
	``HxResponse(request, { 'form': form })``

	``HxResponse(request, { 'form': form, trigger-after-receive='do-this-when-response-is-received'})``


HttpResponse classes (extra)
----------------------------

These are response classes for common htmx actions besides swapping new HTML into the page.

``HxDoNothing``

	A ``HttpResponse`` that tells htmx to do nothing

	``HxDoNothing()``

``HxRedirect``

	A ``HttpResponse`` that tells htmx to do a client side redirect to the
	provided URL

	``HxRedirect(reverse('home'))``

``HxRefresh``

	A ``HttpResponse`` that tells htmx to refresh the page

	``HxRefresh()``

``HxTrigger(trigger_after_receive=None, trigger_after_swap=None, trigger_after_settle=None)``

	A ``HttpResponse`` that tells htmx to trigger an event - and do nothing
	else. https://htmx.org/headers/hx-trigger/

	The arg value is the name of the event to trigger. The value can also be a JSON string, which allows for triggering multiple events and/or passing data for the
	event

	``HxTrigger('close-modal')``

``BlockResponse(block)``

	Creates a ``TemplateResponse-like`` object using django-render-block to
	render a block in a template. It's a light wrapper around django-render-block.
	
	The format of block is ``template_path/template_name:block_name``.

	``BlockResponse('base/home.html:welcome_block')``