.. :changelog:

Changelog
#########

2.0 (19 December 2024)
======================

Breaking change
---------------

* The ``hx-trigger-after-*`` (and the success and error variants) have been renamed to ``hx-fire-after-*``. Version 1's API avoided introducing a new term ("fire") so it could match the htmx API https://htmx.org/headers/hx-trigger/ but that made the markup a bit confusing for newcomers - so we're going to use ``fire`` now.

Improvements
------------

* Added a 'do-nothing' attribute. i.e. hx-do-nothing, hx-success-do-nothing, hx-error-do-nothing. This can be useful for being explicit about behaviour. e.g. hx-error-block="main_form" hx-error-target="index.html#mainform" hx-success-do-nothing.
* Added tests, refactored code, fixed bugs

1.0 (28 August 2024)
====================

* First PyPI release
