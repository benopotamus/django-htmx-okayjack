Django Okayjack (Django+htmx)
#############################

``hx-*`` attributes for specifying different behaviours and templates for a request's success (2xx) and error (4xx) responses. 

.. code-block:: html

	hx-success-target="#toast-container"
	hx-success-fire="open-toast-container"
	hx-error-target="#contact-form"

Also adds support for using *parts* (DTL blocks) of a template in a response, rather than creating separate template files for each response type. And it adds PUT and PATCH support to Django as well because they're fun to use 😁.


Requirements
============

`django-render-block <https://github.com/clokep/django-render-block/blob/main/README.rst>`_

Installation
============

1. ``pip install django-htmx-okayjack``

2. Add to ``settings.py``::

		INSTALLED_APPS = [
			...,
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

This example shows the new htmx-like attributes being used to specify which DTL block to use for a "success" response, and which to use for an "error" response (e.g. form failed validation).

The DTL blocks can be in any file - even in the same file as the originating htmx, as is the case in this example.

You can also just reference a template file without the block part (the part after the ``#``).

.. code-block:: html

	{% block title_form %}
	<form 
		hx-post="/store"
		hx-success-block="this-example-file.html#title_success"
		hx-success-target="h1"
		hx-success-swap="outerHTML"
		hx-error-block="this-example-file.html#title_form"
		hx-error-target="this">
	
			<input id="title" name="title" type="text" {% if form.title.errors % class="error"{% endif %}>
			{% if form.title.errors %}
				<div class='error'>{{ form.title.errors }}</div>
			{% endif %}
			<button type="submit">Submit</button>
	
	</form>
	{% endblock %}
	
	<template>
	{% block title_success %}
		<h1>{{ store.title }}</h1>
	{% endblock %}
	</template>


Given the above HTML, in the corresponding Django ``views.py`` we now only have to do the following to handle both success and error variations.

.. code-block:: python

   def title(request, question_id):
       form = TitleForm(request.POST)
       if form.is_valid():
           form.save()
           return HxSuccessResponse(request, {'store': store})
       return HxErrorResponse(request, {'form': form})

As you can see, all of the UI logic about which template, target, etc to use for success and error responses has been moved to the template, leaving the ``views.py`` to just specify whether the response should be treated as a success or error.

API
===

htmx extension
--------------

Okayjack supports all htmx response headers https://htmx.org/reference/#response_headers.

You can use any combination of: 

* ``hx-*`` attributes``
* ``hx-success-*``
* ``hx-error-*``

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
-  fire-after-receive
-  fire-after-settle
-  fire-after-swap
-  block

``fire-after-*`` 
	Use these attributes to specify events you want to fire when the response is returned. The event can be fired either: after receiving, after swapping, or after settling. The names are based on the response headers - see https://htmx.org/headers/hx-trigger/. 

	Note that ``hx-trigger`` is used for specifying which event "triggers" htmx to send a request to the server (i.e. the event that was fired that made htmx do something), whereas these attributes are for specifying which events should be fired when a response is returned.

``block``
	This is the path to a template and optional template block. Used to generate the HTML response. 
	
	``hx-block="base/home.html#welcome_block"``

	Blocks are regular Django template blocks.

	``{% block welcome_block %}<p>I'm inside a block!</p>{% endblock }``

	Blocks can also be empty (e.g. hx-block=""). This is useful for deleting objects from the DOM. hx-target the object with the block set to "".

``do-nothing``
	Returns a HttpResponse with a 204 (No Content) status code.

HttpResponse classes (main)
---------------------------

``HxSuccessResponse``

	Creates a ‘success’ ``HxResponse``. The response will use ``hx-success-*`` and ``hx-*`` attributes specified in the template.
	
	``HxSuccessResponse(request[, context, block=None, swap=None, fire-after-receive=None, fire_after_settle=None, fire_after_swap=None])``

``HxErrorResponse``

	Creates an ‘error’ HxResponse. The response will use ``hx-error-*`` and ``hx-*`` attributes specified in the template.
	
	``HxErrorResponse(request[, context, block=None, swap=None, fire-after-receive=None, fire_after_settle=None, fire_after_swap=None])``


``HxResponse``

	Creates a response that uses ``hx-*`` attributes in the template.
	
	At a minimum, it will automatically get the template/block for the response from either the ``block`` kwarg or the ``hx-block`` attribute used in the htmx request. 

	``HxResponse(request[, context, block=None, swap=None, fire-after-receive=None, fire_after_settle=None, fire_after_swap=None])``
	
	``HxResponse(request, { 'form': form })``

	``HxResponse(request, { 'form': form, fire-after-receive='fire-this-event-when-response-is-received'})``


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

``HxFire(fire_after_receive=None, fire_after_swap=None, fire_after_settle=None)``

	A ``HttpResponse`` that tells htmx to fire (aka trigger) an event - and do nothing
	else. https://htmx.org/headers/hx-trigger/

	The arg value is the name of the event to fire. The value can also be a JSON string, which allows for firing multiple events and/or passing data for the event

	``HxFire('close-modal')``

``BlockResponse(block)``

	Creates a ``TemplateResponse-like`` object using django-render-block to
	render a block in a template. It's a light wrapper around django-render-block.
	
	The format of block is ``template_path/template_name#block_name``.

	``BlockResponse('base/home.html#welcome_block')``
