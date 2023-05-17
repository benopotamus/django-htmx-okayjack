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
 */
const attrsNames = [
	'Location',
	'Push-Url',
	'Redirect',
	'Refresh',
	'Replace-Url',
	'Swap',
	'Target',
	'Trigger',
	'Trigger-After-Settle',
	'Trigger-After-Swap',
	'Block'
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
			appendHxAttribute('HX-Block')
			for (let attrName of attrsNames) {
				appendHxAttribute('HX-Success-'+attrName)
				appendHxAttribute('HX-Error-'+attrName)
			}
		}
	}
})
