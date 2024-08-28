/***
 * htmx extension that looks for extra hx attributes when a request is made and adds them to the request headers.
 * 
 * The intention is this is used with the Django Okayjack middleware to set appropriate response headers to tell htmx what to do in the case of a success or error response. E.g. if hx-success-target is set on the request, the Okayjack middleware will add hx.success['target] to the request object.
 * 
 * It supports all headers listed here https://htmx.org/reference/#response_headers
 * 
 * In the HTML markup, instead of (or in addition to) things like hx-target="..." you can now do hx-success-target="..." or hx-error-target="...".
 * 
 * It also supports a hx-block attribute, which is for use with a HxResponse Django class and django-render-block.
 * And it supports hx-trigger-after, which htmx doesn't have in request attributes (but supports as a response header)
 */
(function(){

	const htmxAttrsNames = [
		'Location',
		'Push-Url',
		'Redirect',
		'Refresh',
		'Replace-Url',
		'Swap',
		'Target',
	]
	const customAttrsNames = [
		'Block',
		'Trigger-After-Receive',
		'Trigger-After-Settle',
		'Trigger-After-Swap',
	]

	htmx.defineExtension('okayjack', {
		onEvent: function (name, evt) {
			if (name === "htmx:configRequest") {
				function appendHxAttribute(attr) {
					var attrLower = attr.toLowerCase()
					var blockEl = htmx.closest(evt.detail.elt, "[" + attrLower + "]") // Find the nearest element with the custom attribute
					if (blockEl) {
						evt.detail.headers[attr] = blockEl.getAttribute(attrLower)
					}
				}
				// Add any success/error attributes - htmx + custom
				for (let attrName of htmxAttrsNames.concat(customAttrsNames)) {
					appendHxAttribute('HX-Success-'+attrName)
					appendHxAttribute('HX-Error-'+attrName)
				}
				// htmx will automatically do whatever its normal attributes specify, but we need to implement our custom attribute by using response headers so we have to send those to the server as well
				for (let attrName of customAttrsNames) {
					appendHxAttribute('HX-'+attrName)
				}
			}
		}
	})

	/***
	 * Swaps in the body of 4xx HTTP status code error pages - except for 422, which okayjack uses to say there was a generic client error
	 */
	document.addEventListener("htmx:beforeOnLoad", function (event) {
		const xhr = event.detail.xhr
		if (xhr.status == 422) {
			// Process 422 status code responses the same way as 200 responses
			evt.detail.shouldSwap = true;
			evt.detail.isError = false;

		} else if ((xhr.status >= 400) && (xhr.status < 500)) {
			event.stopPropagation() // Tell htmx not to process these requests
			document.children[0].innerHTML = xhr.response // Swap in body of response instead
		}
	})

})()