/***
 * This is an htmx extension that looks for extra hx attributes on elements when a request is made and adds them to the request headers. The intention is this is used with the Django Okayjack middleware (https://pypi.org/project/django-htmx-okayjack/) to set appropriate response headers to tell htmx what to do in the case of a success or error response.
 */
(function(){

	// htmx already processes these attributes. We still need to process the hx-success and hx-error variants though
	const clientProcessedAttrs = [
		'Push-Url',
		'Replace-Url',
		'Swap',
		'Target',
	]
	// htmx doesn't process these normally. These are new okayjack ones, or those which htmx will only process when they are received in a header from the server
	const headerAttrs = [
		'Block',
		'Do-Nothing',
		'Fire-After-Receive',
		'Fire-After-Settle',
		'Fire-After-Swap',
		'Fire', // Shorthand for Fire-After-Receive
		'Location',
		'Redirect',
		'Refresh',
	]

	htmx.defineExtension('okayjack', {
		onEvent: function (name, evt) {
			if (name === 'htmx:configRequest') {
				function appendHxAttribute(attr) {
					var attrLower = attr.toLowerCase()
					var blockEl = htmx.closest(evt.detail.elt, "[" + attrLower + "]") // Find the nearest element with the custom attribute
					if (blockEl) {
						evt.detail.headers[attr] = blockEl.getAttribute(attrLower)
					}
				}

				// Make general headers for the attributes that htmx doesn't normally process (unless they come in as a response header)
				for (let attrName of headerAttrs) {
					appendHxAttribute('HX-'+attrName)
				}

				// Make success and error headers for all attributes
				// success and error attributes are all okayjack ones so they need response headers for htmx to process them
				for (let attrName of headerAttrs.concat(clientProcessedAttrs)) {
					appendHxAttribute('HX-Success-'+attrName)
					appendHxAttribute('HX-Error-'+attrName)
				}

			}
		}
	})

	/***
	 * Swaps in the body of 4xx HTTP status code error pages - except for 422, which we use to denote a generic client error
	 */
	document.addEventListener("htmx:beforeOnLoad", function (e) {
		const xhr = e.detail.xhr
		if (xhr.status == 422) {
			// Process 422 status code responses the same way as 200 responses
			e.detail.shouldSwap = true;
			e.detail.isError = false;

		} else if ((xhr.status >= 400) && (xhr.status < 500)) {
			e.stopPropagation() // Tell htmx not to process these requests
			document.children[0].innerHTML = xhr.response // Swap in body of response instead
		}
	})

})()