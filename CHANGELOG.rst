.. :changelog:

Changelog
#########

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
