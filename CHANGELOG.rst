.. :changelog:

Changelog
#########

5.0.1  (25 Jul 2026)
====================

Breaking changes
----------------

* ``django-render-block`` optional dependency renamed to ``[block]`` (no "s") to match the package name. Install using ``pip install django-htmx-okayjack[block]``


5.0 (25 Jul 2026)
=================

Breaking changes
----------------

* ``django-render-block`` now installs as an optional dependency

Bug fixes
---------

* Various


4.0.2 (28 May 2026)
===================

Bug fixes
---------

* ``hx-*-refresh`` now correctly handles ``"true"`` value. This does the same thing as setting ``HX-Refresh=true`` response header https://htmx.org/reference/#response_headers. 


4.0.1 (25 May 2026)
===================

Doco
----

* Updated readme to include notes on ``HxAlert`` and ``hx-*-alert`` (oops!)

Bug fixes
---------

* refresh now correctly handles querystring parameters


4.0 (25 May 2026)
=================

Breaking changes
----------------

* Attributes no longer cascade. htmx 4 attributes don't cascade/inherit by default. Let me know if you need cascading and I'll add the same cascading modifiers (e.g. `:inherit`) as htmx 4.

New
---

* ``hx-partial`` support 🥳. Works the same as ``hx-block``. The intention is ``hx-partial`` eventually supercedes ``hx-block`` but, as partials are only in Django 6.0, we'll have two options for the forseeable future. And besides, who wants to rename a bunch of blocks to partial.
* ``HxAlert`` and ``HxErrorAlert`` classes and ``hx-*-alert`` attributes. A HxAlert will display a JavaScript alert when the response has been processed. They all take a single argument which is the alert text.
* A ``refresh`` variable is now automatically added to the request context (accessed in view or template as ``request.hx_refresh``). This is useful for conditional rendering. E.g. ``{% if request.hx_refresh }<script>...</script>{% endif %}``

Bug fixes
---------

* ``hx-refresh=true`` will actutually do a normal refresh now. It was errornously using the new body swap style before.


3.0 (18 Nov 2025)
=================

Breaking change
---------------

* *Minor* breaking change really. ``hx-refresh`` and ``HxRefresh`` now support a "body swap" refresh. The normal refresh style is to set a ``HX-Refresh`` response header which causes htmx to issue a new GET request to the url the client is on, which causes the url to be reloaded and thus the page refreshed. The "body swap" way is includes a page refresh worth of html in the first response and swaps the body element from that html into the DOM, thus removing the need for the second GET request. ``hx-refresh=true`` will do a normal refresh, ``hx-refresh`` or ``hx-refresh="{% url 'somepath' arg1 etc %}"`` will do a body swap style refresh.


2.1 (23 Sep 2025)
=================

Improvements
------------

* ``hx-error-do-nothing`` now has a response status code of 422 (was 204). This will make it nicer to query in request analytics tools such as `django-silent-mammoth-whistle <https://pypi.org/project/django-silent-mammoth-whistle/>`_.
* Added a ``status`` kwarg to ``HxResponse`` so custom statuses can be set when using the class directly.
* Refactored ``http.py`` and removed ``HxStateResponse``

Bug fixes
---------

* Fixed a bug where ``hx-refresh`` (and success and error variants) were not correctly superseding other hx attributes. The intended behaviour is an ``hx-refresh`` or ``hx-do-nothing`` will do a refresh or nothing and all other attributes will be ignored.


2.0.2 (31 Jan 2025)
===================

Improvements
------------

* Added ``hx-fire-*`` attribute as a shorthand for ``hx-fire-after-receive``. This can be used in the html markup. Also added success and error variants for this shorthand.
* Added ``fire`` kwarg to the various Hx response classes as a shorthand for ``fire_after_receive``

Bug fixes
---------

* HxResponse context was being passed to HttpResponse (which doesn't support context)
* Updated tests to include context parameter


2.0 (19 Dec 2024)
=================

Breaking change
---------------

* The ``hx-trigger-after-*`` (and the success and error variants) have been renamed to ``hx-fire-after-*``. Version 1's API avoided introducing a new term ("fire") so it could match the htmx API https://htmx.org/headers/hx-trigger/ but that made the markup a bit confusing for newcomers - so we're going to use ``fire`` now.

Improvements
------------

* Added a 'do-nothing' attribute. i.e. hx-do-nothing, hx-success-do-nothing, hx-error-do-nothing. This can be useful for being explicit about behaviour. e.g. hx-error-block="main_form" hx-error-target="index.html#mainform" hx-success-do-nothing.
* Added tests, refactored code, fixed bugs

1.0 (28 Aug 2024)
=================

* First PyPI release
