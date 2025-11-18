Django Okayjack (Django+htmx)
#############################

Okayjack adds a few extra ``hx-*`` attributes which let you create conditional response rules (i.e. for success (2xx) and error (4xx) responses) in the template instead of the View. This results in much simpler Views.

.. code-block:: html

	<form hx-patch="/contacts"
		hx-success-block="page.html#toast"
		hx-success-target="#toast-container"
		hx-error-block="page.html#form"
		hx-error-target="#contact-form">

.. code-block:: python

	def contacts(request, question_id):
		form = ContactForm(request.PATCH)
		if form.is_valid():
			form.save()
			return HxSuccessResponse(request)
		return HxErrorResponse(request, {'form': form})

The ``hx-success-*`` attributes are used when the response is ``HxSuccessResponse``, and ``hx-error-*`` attributes for ``HxErrorResponse``.

The extra attributes don't change htmx, all the regular htmx attributes work as normal and you can mix them as you wish. The extra attributes, combined with the Django Hx classes, just set htmx response headers which htmx processes as it normally would.

Okayjack also adds support for using *parts* of a template (DTL ``{% block %}``) in a response, rather than creating separate template files for each response. 

And it adds PUT and PATCH support to Django as well because they're nice to use 😁.

Table of contents
=================

* `Requirements <#requirements>`_
* `Installation <#installation>`_
* `htmx attributes <#htmx-attributes>`_
* `Django API <#django-api>`_
* `Extended example <#extended-example>`_


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


htmx attributes
===============

Okayjack supports all htmx response headers https://htmx.org/reference/#response_headers.

You can use any combination of: 

* ``hx-*`` attributes``
* ``hx-success-*``
* ``hx-error-*``

htmx will use the values of ``hx-*`` unless there is a ``hx-success-*`` or ``hx-error-*`` value (for a success or error response respectively).

The ``*`` in ``hx-success-*`` and ``hx-error-*`` attributes can be any of the following.

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
-  fire
-  block

``refresh``
	This attribute supports two types of refresh.

	1. ``hx-refresh="true"`` will do the normal refresh that is achieved by setting the ``HX-Refresh`` response header to ``true`` - see https://htmx.org/reference/#response_headers. 
	2. ``hx-refresh`` (without an attribute value) will call the view that handles the current url and returns a response that contains the html from that view (assumes a GET request to the view). When the response is received by htmx, the ``body`` element of the page is replaced with the ``body`` element from the response content. 
	
	This second refresh style acheives the same result as a normal refresh except it does not require the additional GET request that the normal method uses, and the content is swapped into the page which results in less/no page loading flicker.
	
	If the attribute value is a path, that will be used to generate the html instead of the current page's url.

	e.g. ``hx-refresh="{% url 'a_different_view' arg1 etc %}"``

``fire-after-*`` 
	Use these attributes to specify events you want to fire when the response is returned. The event can be fired after receiving, swapping, or settling. The names are based on the response headers - see https://htmx.org/headers/hx-trigger/. 

	Note that ``hx-trigger`` is used for specifying which event "triggers" htmx to send a request to the server (i.e. the event that was fired that made htmx do something), whereas these attributes are for specifying which events should be fired when a response is returned.

``fire`` 
	Shorthand for ``fire-after-receive``

``block``
	This is the path to a template and optional template block. Used to generate the HTML response. 
	
	``hx-block="base/home.html#welcome_block"``

	Blocks are regular Django template blocks.

	``{% block welcome_block %}<p>I'm inside a block!</p>{% endblock }``

``do-nothing``
	Returns a HttpResponse with a 204 (No Content) status code.


Django API
==========

Main classes
------------

``HxSuccessResponse``

	Creates a ‘success’ ``HxResponse``. The response will use ``hx-success-*`` and ``hx-*`` attributes specified in the template.
	
	``HxSuccessResponse(request[, context, block=None, swap=None, target=None, fire-after-receive=None, fire_after_settle=None, fire_after_swap=None])``

``HxErrorResponse``

	Creates an ‘error’ HxResponse. The response will use ``hx-error-*`` and ``hx-*`` attributes specified in the template.
	
	``HxErrorResponse(request[, context, block=None, swap=None, target=None, fire-after-receive=None, fire_after_settle=None, fire_after_swap=None])``


``HxResponse``

	Creates a response that uses ``hx-*`` attributes in the template.
	
	At a minimum, it will automatically get the template/block for the response from either the ``block`` kwarg or the ``hx-block`` attribute used in the htmx request. 

	``HxResponse(request[, context, block=None, swap=None, target=None, fire-after-receive=None, fire_after_settle=None, fire_after_swap=None])``
	
	``HxResponse(request, { 'form': form })``

	``HxResponse(request, { 'form': form, fire-after-receive='fire-this-event-when-response-is-received'})``


Additional handy classes
------------------------

These are response classes for common htmx actions besides swapping new HTML into the page.

``HxDoNothing``

	A ``HttpResponse`` that tells htmx to do nothing

	``HxDoNothing()``

``HxRedirect``

	A ``HttpResponse`` that tells htmx to do a client side redirect to the
	provided URL

	``HxRedirect(reverse('home'))``

``HxRefresh``

	A ``HttpResponse`` that tells htmx to refresh the page. 

	``HxRefresh()``

	If a path is provided, instead of the usual refresh operation, the response will include the html of the path along with headers to tell htmx to replace the ``body`` element in the page with the ``body`` element in the response content. The net result is a page refresh without the second network request and without the usual page refresh screen flicker (as the content is being swapped in rather than being reloaded via a GET request).

	In the following example, Django's reverse (from ``django.urls``) is used to create the path.

	``HxRefresh(request, reverse('add_client', args=[client.id]))``

``HxFire(fire=None, fire_after_receive=None, fire_after_swap=None, fire_after_settle=None)``

	A ``HttpResponse`` that tells htmx to fire (aka trigger) an event - and do nothing else. https://htmx.org/headers/hx-trigger/
	The arg value is the name of the event to fire. If the event name is supplied as a positional argument, ``fire_after_received`` is used. 
	
	``HxFire('close-dialog-box')``

	The value can also be a JSON string, which allows for firing multiple events and/or passing data for the event. 

``BlockResponse(block)``

	Creates a ``TemplateResponse-like`` object using django-render-block to
	render a block in a template. It's a light wrapper around django-render-block.
	
	The format of block is ``template_path/template_name#block_name``.

	``BlockResponse('base/home.html#welcome_block')``


Extended example
================

Let's say you have a basic contact form.

.. code-block:: html

	<form method="post" action="/contact">
		{{ form.as_div }}
		<button type='submit'>
	</form>

To receive data on the server you have a basic View. It validates the Form, and returns a success or error page.

.. code-block:: Python

	def contact(request):
		form = ContactForm(request.POST or None)
		if form.is_valid():
			form.save()
			return render(request, "contact_success.html", {'form': form})
		return render(request, "contact_error.html", {'form': form})

With htmx, you can return partials instead of full pages, and swap them into the page. So you might decide to add an extra section to swap a success message into - no page refresh required 🥳. The partial needs to be a separate file so it can be used as a template in the View.

.. code-block:: html

	{% include 'app/partials/success-message.html' %}
	<form hx-post="/contact" hx-target="#success-message">
		{{ form.as_div }}
		<button type='submit'>
	</form>

The View will need a little update to reference the partial.

.. code-block:: Python

	def contact(request):
		form = ContactForm(request.POST or None)
		if form.is_valid():
			form.save()
			return render(request, "app/partials/contact_success.html", {'form': form})
		return = render(request, "contact_error.html", {'form': form})

This will work well for a successful form submission, but if there's an error, it will refresh the page. It would be nicer to swap out the form with one that displays the errors instead - no page refresh. We do this of course in the View using Response headers https://htmx.org/reference/#response_headers.

.. code-block:: Python

	def contact(request):
		form = ContactForm(request.POST or None)
		if form.is_valid():
			form.save()
			return render(request, "app/partials/contact_success.html", {'form': form})

		response = render(request, "app/partials/contact_error.html", {'form': form})
		response['HX-Retarget'] = 'form'
		return response

And that's it for vanilla htmx. We now have a page which submits a form, and uses htmx to swap in the results depending upon whether it is valid or invalid. 

One downside is that to understand the UI behaviour and see what html will be generated, we now need to read three templates (2 partials + the main page) plus the View. It's not terrible but can get tedious.

With Okayjack, we move most/all of the UI behaviour to the template so it can be read all in one place.

.. code-block:: html

	{% block success_message %}
		<div id='success-message' class='alert success tick'></div>
	{% endblock %}
	<form 
		hx-post="/contact" 
		hx-success-target="#success-message"
		hx-success-block="contacts.html#success_message"
		hx-error-target="form"
		hx-error-block="contacts.html#contact_form">
			{% block contact_form %}
				{{ form.as_div }}
			{% endblock %}
			<button type='submit'>
	</form>

Because of the above, we can now simplify the view. 

.. code-block:: Python

	def contact(request):
		form = ContactForm(request.POST or None)
		if form.is_valid():
			form.save()
			return HxSuccessResponse(request)
		return HxErrorResponse(request, {'form': form})

The changes in the above example using Okayjack are:

1. We reference ``{% blocks %}`` to get our partials rather than seperate files, which keeps the html in one place.
2. We specify different ``target`` and ``block`` attributes for use with successful/valid or error/invalid requests.
3. We have the one ``hx-post`` attribute still. There's no need to specify it twice when it's the same for both.
4. Valid forms return ``HxSuccessResponse``, invalid returns ``HxErrorResponse``. Our View no longer needs to do Retargets, etc, and it doesn't need to specify which partials/blocks to use, so it becomes simple enough that it can usually be ignored when reading templates.
