/***
 * HTMX extension that looks for extra hx attributes when a request is made and adds them to the request headers.
 * 
 * The intention is this is used with the Django Okayjack middleware to set appropriate response headers to tell HTMX what to do in the case of a success or error response. E.g. if hx-success-target is set on the request, the Okayjack middleware will add hx.success['target] to the request object.
 * 
 * It supports all headers here https://htmx.org/reference/#response_headers
 * 
 * In the HTML markup, instead of (or in addition to) things like hx-target="..." you can now do hx-success-target="..." or hx-error-target="...".
 * 
 * It also supports a hx-block attribute, which is for use with a HxResponse Django class and django-render-block.
 * And it supports hx-trigger-after, which htmx doesn't have in request attributes (but supports as response headers)
 * 
 * 30 June 2023
 */
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
			// htmx will automatically do whatever its normally attributes specify, but we need to implement our custom attribute by using response headers so we have to send those to the server as well
			for (let attrName of customAttrsNames) {
				appendHxAttribute('HX-'+attrName)
			}
			console.log(evt.detail.headers)
		}
	}
})
