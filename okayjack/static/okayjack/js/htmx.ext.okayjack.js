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
		'Partial',
		'Do-Nothing',
		'Fire-After-Receive',
		'Fire-After-Settle',
		'Fire-After-Swap',
		'Fire', // Shorthand for Fire-After-Receive
		'Location',
		'Redirect',
		'Refresh',
		'Alert',
	]

	htmx.defineExtension('okayjack', {
		onEvent: function (name, evt) {
			if (name === 'htmx:configRequest') {
				function appendHxAttribute(attr) {
					const srcElement = evt.srcElement
					if (srcElement.hasAttribute(attr)) {
						let value = srcElement.getAttribute(attr)
						let attrLower = attr.toLowerCase()

						// If a Refresh attribute doesn't specify what path to use to generate the html, use the current path
						if (attrLower.includes('refresh')  &&  ((value == '') || (value.toLowerCase() == 'true')) ) {
							value = window.location.pathname + window.location.search

						// base64 encode alert text so it can be sent in a http header
						} else if (attrLower.includes('alert')) {
							const bytes = new TextEncoder().encode(value.replace(/\\n/g, '\n')) // Convert text to UTF-8 bytes (Uint8Array)
							const binaryString = String.fromCharCode(...bytes) // Convert bytes to binary string
							value = btoa(binaryString) // Encodes binary string to Base64
						}
						evt.detail.headers[attr] = value
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
	 * 
	 * Responses can also have a HX-Do-Nothing header, which htmx supports natively by using a 204 response code.
	 * We want to support having 4xx response codes that also don't swap, so this listener has some extra code for that.
	 */
	document.addEventListener("htmx:beforeOnLoad", function (e) {
		const xhr = e.detail.xhr
		const doNothing = xhr.getResponseHeader("HX-Do-Nothing")
		const reswap = xhr.getResponseHeader("HX-Reswap")

		if (doNothing) {
			e.detail.shouldSwap = false
		}

		if (xhr.status == 422) {
			// Process 422 status code responses the same way as 200 responses...
			e.detail.isError = false

			// ...except if the user specifically chose a noswap option (e.g. HxAlert is a noswap option)
			if (!doNothing || (reswap != 'none')) {
				e.detail.shouldSwap = true
			}

		} else if ((xhr.status >= 400) && (xhr.status < 500)) {
			e.stopPropagation() // Tell htmx not to process these requests
			document.children[0].innerHTML = xhr.response // Swap in body of response instead
		}


	})

	/***
	 * Display alerts 
	 * 
	 * We do this after the response is processed (settled) so, to a user, the UI has been updated and the alert is displayed on top.
	 * 
	 * The alert text in the header is encoded on the server so it can be included in http headers (which don't support things like new line characters).
	 */
	document.addEventListener("htmx:afterSettle", function (e) {
		const xhr = e.detail.xhr
		const encodedText = xhr.getResponseHeader("HX-Alert")
		if (encodedText) {
			console.log('encodedText', encodedText)
			const bytes = Uint8Array.from(atob(encodedText), c => c.charCodeAt(0)) // TODO replace this with fromBase64 in the future
			const decodedText = new TextDecoder().decode(bytes)
			alert(decodedText)
		}
	})

})()