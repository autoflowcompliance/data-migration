import { Di as e, Ji as t, La as n, Oi as r, Pn as i, Qi as a, Yi as o, dr as s, ea as c, yi as ee } from "./index-Dl4ETd_L-D2oMd1k2.js";
import { n as te, t as ne } from "./index-DINISCAW-DhRXH5fW.js";
import { t as l } from "./index-Df-1Z3LJ-BbKzDPIK.js";
//#region ../react/build/index-B7jxgHEF.js
var re = {}.hasOwnProperty;
function ie(e, t) {
	let n = t || {};
	function r(t, ...n) {
		let i = r.invalid, a = r.handlers;
		if (t && re.call(t, e)) {
			let n = String(t[e]);
			i = re.call(a, n) ? a[n] : r.unknown;
		}
		if (i) return i.call(this, t, ...n);
	}
	return r.handlers = n.handlers || {}, r.invalid = n.invalid, r.unknown = n.unknown, r;
}
function ae(e) {
	let t = String(e), n = [];
	return {
		toOffset: i,
		toPoint: r
	};
	function r(e) {
		if (typeof e == "number" && e > -1 && e <= t.length) {
			let r = 0;
			for (;;) {
				let i = n[r];
				if (i === void 0) {
					let e = oe(t, n[r - 1]);
					i = e === -1 ? t.length + 1 : e + 1, n[r] = i;
				}
				if (i > e) return {
					line: r + 1,
					column: e - (r > 0 ? n[r - 1] : 0) + 1,
					offset: e
				};
				r++;
			}
		}
	}
	function i(e) {
		if (e && typeof e.line == "number" && typeof e.column == "number" && !Number.isNaN(e.line) && !Number.isNaN(e.column)) {
			for (; n.length < e.line;) {
				let e = n[n.length - 1], r = oe(t, e), i = r === -1 ? t.length + 1 : r + 1;
				if (e === i) break;
				n.push(i);
			}
			let r = (e.line > 1 ? n[e.line - 2] : 0) + e.column - 1;
			if (r < n[e.line - 1]) return r;
		}
	}
}
function oe(e, t) {
	let n = e.indexOf("\r", t), r = e.indexOf("\n", t);
	return r === -1 ? n : n === -1 || n + 1 === r ? r : n < r ? n : r;
}
var se = {}.hasOwnProperty, ce = Object.prototype;
function le(e, t) {
	let n = t || {};
	return ue({
		file: n.file || void 0,
		location: !1,
		schema: n.space === "svg" ? c : s,
		verbose: n.verbose || !1
	}, e);
}
function ue(e, t) {
	let n;
	switch (t.nodeName) {
		case "#comment": {
			let r = t;
			return n = {
				type: "comment",
				value: r.data
			}, pe(e, r, n), n;
		}
		case "#document":
		case "#document-fragment": {
			let r = t, i = "mode" in r ? r.mode === "quirks" || r.mode === "limited-quirks" : !1;
			if (n = {
				type: "root",
				children: de(e, t.childNodes),
				data: { quirksMode: i }
			}, e.file && e.location) {
				let t = String(e.file), r = ae(t), i = r.toPoint(0), a = r.toPoint(t.length);
				n.position = {
					start: i,
					end: a
				};
			}
			return n;
		}
		case "#documentType": {
			let r = t;
			return n = { type: "doctype" }, pe(e, r, n), n;
		}
		case "#text": {
			let r = t;
			return n = {
				type: "text",
				value: r.value
			}, pe(e, r, n), n;
		}
		default: return n = fe(e, t), n;
	}
}
function de(e, t) {
	let n = -1, r = [];
	for (; ++n < t.length;) {
		let i = ue(e, t[n]);
		r.push(i);
	}
	return r;
}
function fe(e, t) {
	let n = e.schema;
	e.schema = t.namespaceURI === l.svg ? c : s;
	let r = -1, i = {};
	for (; ++r < t.attrs.length;) {
		let e = t.attrs[r], n = (e.prefix ? e.prefix + ":" : "") + e.name;
		se.call(ce, n) || (i[n] = e.value);
	}
	let a = (e.schema.space === "svg" ? te : ne)(t.tagName, i, de(e, t.childNodes));
	if (pe(e, t, a), a.tagName === "template") {
		let n = t, r = n.sourceCodeLocation, i = r && r.startTag && u(r.startTag), o = r && r.endTag && u(r.endTag), s = ue(e, n.content);
		i && o && e.file && (s.position = {
			start: i.end,
			end: o.start
		}), a.content = s;
	}
	return e.schema = n, a;
}
function pe(e, t, n) {
	if ("sourceCodeLocation" in t && t.sourceCodeLocation && e.file) {
		let r = me(e, n, t.sourceCodeLocation);
		r && (e.location = !0, n.position = r);
	}
}
function me(e, t, n) {
	let r = u(n);
	if (t.type === "element") {
		let a = t.children[t.children.length - 1];
		if (r && !n.endTag && a && a.position && a.position.end && (r.end = Object.assign({}, a.position.end)), e.verbose) {
			let r = {}, a;
			if (n.attrs) for (a in n.attrs) se.call(n.attrs, a) && (r[i(e.schema, a).property] = u(n.attrs[a]));
			ee(n.startTag);
			let o = u(n.startTag), s = n.endTag ? u(n.endTag) : void 0, c = { opening: o };
			s && (c.closing = s), c.properties = r, t.data = { position: c };
		}
	}
	return r;
}
function u(e) {
	let t = he({
		line: e.startLine,
		column: e.startCol,
		offset: e.startOffset
	}), n = he({
		line: e.endLine,
		column: e.endCol,
		offset: e.endOffset
	});
	return t || n ? {
		start: t,
		end: n
	} : void 0;
}
function he(e) {
	return e.line && e.column ? e : void 0;
}
var d = class {
	constructor(e, t, n) {
		this.property = e, this.normal = t, n && (this.space = n);
	}
};
d.prototype.property = {}, d.prototype.normal = {}, d.prototype.space = null;
function ge(e, t) {
	let n = {}, r = {}, i = -1;
	for (; ++i < e.length;) Object.assign(n, e[i].property), Object.assign(r, e[i].normal);
	return new d(n, r, t);
}
function _e(e) {
	return e.toLowerCase();
}
var f = class {
	constructor(e, t) {
		this.property = e, this.attribute = t;
	}
};
f.prototype.space = null, f.prototype.boolean = !1, f.prototype.booleanish = !1, f.prototype.overloadedBoolean = !1, f.prototype.number = !1, f.prototype.commaSeparated = !1, f.prototype.spaceSeparated = !1, f.prototype.commaOrSpaceSeparated = !1, f.prototype.mustUseProperty = !1, f.prototype.defined = !1;
var ve = 0, p = y(), m = y(), ye = y(), h = y(), g = y(), _ = y(), v = y();
function y() {
	return 2 ** ++ve;
}
var be = /* @__PURE__ */ Object.freeze(/* @__PURE__ */ Object.defineProperty({
	__proto__: null,
	boolean: p,
	booleanish: m,
	commaOrSpaceSeparated: v,
	commaSeparated: _,
	number: h,
	overloadedBoolean: ye,
	spaceSeparated: g
}, Symbol.toStringTag, { value: "Module" })), xe = Object.keys(be), Se = class extends f {
	constructor(e, t, n, r) {
		let i = -1;
		if (super(e, t), Ce(this, "space", r), typeof n == "number") for (; ++i < xe.length;) {
			let e = xe[i];
			Ce(this, xe[i], (n & be[e]) === be[e]);
		}
	}
};
Se.prototype.defined = !0;
function Ce(e, t, n) {
	n && (e[t] = n);
}
var we = {}.hasOwnProperty;
function b(e) {
	let t = {}, n = {}, r;
	for (r in e.properties) if (we.call(e.properties, r)) {
		let i = e.properties[r], a = new Se(r, e.transform(e.attributes || {}, r), i, e.space);
		e.mustUseProperty && e.mustUseProperty.includes(r) && (a.mustUseProperty = !0), t[r] = a, n[_e(r)] = r, n[_e(a.attribute)] = r;
	}
	return new d(t, n, e.space);
}
var Te = b({
	space: "xlink",
	transform(e, t) {
		return "xlink:" + t.slice(5).toLowerCase();
	},
	properties: {
		xLinkActuate: null,
		xLinkArcRole: null,
		xLinkHref: null,
		xLinkRole: null,
		xLinkShow: null,
		xLinkTitle: null,
		xLinkType: null
	}
}), Ee = b({
	space: "xml",
	transform(e, t) {
		return "xml:" + t.slice(3).toLowerCase();
	},
	properties: {
		xmlLang: null,
		xmlBase: null,
		xmlSpace: null
	}
});
function De(e, t) {
	return t in e ? e[t] : t;
}
function Oe(e, t) {
	return De(e, t.toLowerCase());
}
var ke = b({
	space: "xmlns",
	attributes: { xmlnsxlink: "xmlns:xlink" },
	transform: Oe,
	properties: {
		xmlns: null,
		xmlnsXLink: null
	}
}), Ae = b({
	transform(e, t) {
		return t === "role" ? t : "aria-" + t.slice(4).toLowerCase();
	},
	properties: {
		ariaActiveDescendant: null,
		ariaAtomic: m,
		ariaAutoComplete: null,
		ariaBusy: m,
		ariaChecked: m,
		ariaColCount: h,
		ariaColIndex: h,
		ariaColSpan: h,
		ariaControls: g,
		ariaCurrent: null,
		ariaDescribedBy: g,
		ariaDetails: null,
		ariaDisabled: m,
		ariaDropEffect: g,
		ariaErrorMessage: null,
		ariaExpanded: m,
		ariaFlowTo: g,
		ariaGrabbed: m,
		ariaHasPopup: null,
		ariaHidden: m,
		ariaInvalid: null,
		ariaKeyShortcuts: null,
		ariaLabel: null,
		ariaLabelledBy: g,
		ariaLevel: h,
		ariaLive: null,
		ariaModal: m,
		ariaMultiLine: m,
		ariaMultiSelectable: m,
		ariaOrientation: null,
		ariaOwns: g,
		ariaPlaceholder: null,
		ariaPosInSet: h,
		ariaPressed: m,
		ariaReadOnly: m,
		ariaRelevant: null,
		ariaRequired: m,
		ariaRoleDescription: g,
		ariaRowCount: h,
		ariaRowIndex: h,
		ariaRowSpan: h,
		ariaSelected: m,
		ariaSetSize: h,
		ariaSort: null,
		ariaValueMax: h,
		ariaValueMin: h,
		ariaValueNow: h,
		ariaValueText: null,
		role: null
	}
}), je = b({
	space: "html",
	attributes: {
		acceptcharset: "accept-charset",
		classname: "class",
		htmlfor: "for",
		httpequiv: "http-equiv"
	},
	transform: Oe,
	mustUseProperty: [
		"checked",
		"multiple",
		"muted",
		"selected"
	],
	properties: {
		abbr: null,
		accept: _,
		acceptCharset: g,
		accessKey: g,
		action: null,
		allow: null,
		allowFullScreen: p,
		allowPaymentRequest: p,
		allowUserMedia: p,
		alt: null,
		as: null,
		async: p,
		autoCapitalize: null,
		autoComplete: g,
		autoFocus: p,
		autoPlay: p,
		blocking: g,
		capture: null,
		charSet: null,
		checked: p,
		cite: null,
		className: g,
		cols: h,
		colSpan: null,
		content: null,
		contentEditable: m,
		controls: p,
		controlsList: g,
		coords: h | _,
		crossOrigin: null,
		data: null,
		dateTime: null,
		decoding: null,
		default: p,
		defer: p,
		dir: null,
		dirName: null,
		disabled: p,
		download: ye,
		draggable: m,
		encType: null,
		enterKeyHint: null,
		fetchPriority: null,
		form: null,
		formAction: null,
		formEncType: null,
		formMethod: null,
		formNoValidate: p,
		formTarget: null,
		headers: g,
		height: h,
		hidden: p,
		high: h,
		href: null,
		hrefLang: null,
		htmlFor: g,
		httpEquiv: g,
		id: null,
		imageSizes: null,
		imageSrcSet: null,
		inert: p,
		inputMode: null,
		integrity: null,
		is: null,
		isMap: p,
		itemId: null,
		itemProp: g,
		itemRef: g,
		itemScope: p,
		itemType: g,
		kind: null,
		label: null,
		lang: null,
		language: null,
		list: null,
		loading: null,
		loop: p,
		low: h,
		manifest: null,
		max: null,
		maxLength: h,
		media: null,
		method: null,
		min: null,
		minLength: h,
		multiple: p,
		muted: p,
		name: null,
		nonce: null,
		noModule: p,
		noValidate: p,
		onAbort: null,
		onAfterPrint: null,
		onAuxClick: null,
		onBeforeMatch: null,
		onBeforePrint: null,
		onBeforeToggle: null,
		onBeforeUnload: null,
		onBlur: null,
		onCancel: null,
		onCanPlay: null,
		onCanPlayThrough: null,
		onChange: null,
		onClick: null,
		onClose: null,
		onContextLost: null,
		onContextMenu: null,
		onContextRestored: null,
		onCopy: null,
		onCueChange: null,
		onCut: null,
		onDblClick: null,
		onDrag: null,
		onDragEnd: null,
		onDragEnter: null,
		onDragExit: null,
		onDragLeave: null,
		onDragOver: null,
		onDragStart: null,
		onDrop: null,
		onDurationChange: null,
		onEmptied: null,
		onEnded: null,
		onError: null,
		onFocus: null,
		onFormData: null,
		onHashChange: null,
		onInput: null,
		onInvalid: null,
		onKeyDown: null,
		onKeyPress: null,
		onKeyUp: null,
		onLanguageChange: null,
		onLoad: null,
		onLoadedData: null,
		onLoadedMetadata: null,
		onLoadEnd: null,
		onLoadStart: null,
		onMessage: null,
		onMessageError: null,
		onMouseDown: null,
		onMouseEnter: null,
		onMouseLeave: null,
		onMouseMove: null,
		onMouseOut: null,
		onMouseOver: null,
		onMouseUp: null,
		onOffline: null,
		onOnline: null,
		onPageHide: null,
		onPageShow: null,
		onPaste: null,
		onPause: null,
		onPlay: null,
		onPlaying: null,
		onPopState: null,
		onProgress: null,
		onRateChange: null,
		onRejectionHandled: null,
		onReset: null,
		onResize: null,
		onScroll: null,
		onScrollEnd: null,
		onSecurityPolicyViolation: null,
		onSeeked: null,
		onSeeking: null,
		onSelect: null,
		onSlotChange: null,
		onStalled: null,
		onStorage: null,
		onSubmit: null,
		onSuspend: null,
		onTimeUpdate: null,
		onToggle: null,
		onUnhandledRejection: null,
		onUnload: null,
		onVolumeChange: null,
		onWaiting: null,
		onWheel: null,
		open: p,
		optimum: h,
		pattern: null,
		ping: g,
		placeholder: null,
		playsInline: p,
		popover: null,
		popoverTarget: null,
		popoverTargetAction: null,
		poster: null,
		preload: null,
		readOnly: p,
		referrerPolicy: null,
		rel: g,
		required: p,
		reversed: p,
		rows: h,
		rowSpan: h,
		sandbox: g,
		scope: null,
		scoped: p,
		seamless: p,
		selected: p,
		shadowRootClonable: p,
		shadowRootDelegatesFocus: p,
		shadowRootMode: null,
		shape: null,
		size: h,
		sizes: null,
		slot: null,
		span: h,
		spellCheck: m,
		src: null,
		srcDoc: null,
		srcLang: null,
		srcSet: null,
		start: h,
		step: null,
		style: null,
		tabIndex: h,
		target: null,
		title: null,
		translate: null,
		type: null,
		typeMustMatch: p,
		useMap: null,
		value: m,
		width: h,
		wrap: null,
		writingSuggestions: null,
		align: null,
		aLink: null,
		archive: g,
		axis: null,
		background: null,
		bgColor: null,
		border: h,
		borderColor: null,
		bottomMargin: h,
		cellPadding: null,
		cellSpacing: null,
		char: null,
		charOff: null,
		classId: null,
		clear: null,
		code: null,
		codeBase: null,
		codeType: null,
		color: null,
		compact: p,
		declare: p,
		event: null,
		face: null,
		frame: null,
		frameBorder: null,
		hSpace: h,
		leftMargin: h,
		link: null,
		longDesc: null,
		lowSrc: null,
		marginHeight: h,
		marginWidth: h,
		noResize: p,
		noHref: p,
		noShade: p,
		noWrap: p,
		object: null,
		profile: null,
		prompt: null,
		rev: null,
		rightMargin: h,
		rules: null,
		scheme: null,
		scrolling: m,
		standby: null,
		summary: null,
		text: null,
		topMargin: h,
		valueType: null,
		version: null,
		vAlign: null,
		vLink: null,
		vSpace: h,
		allowTransparency: null,
		autoCorrect: null,
		autoSave: null,
		disablePictureInPicture: p,
		disableRemotePlayback: p,
		prefix: null,
		property: null,
		results: h,
		security: null,
		unselectable: null
	}
}), Me = b({
	space: "svg",
	attributes: {
		accentHeight: "accent-height",
		alignmentBaseline: "alignment-baseline",
		arabicForm: "arabic-form",
		baselineShift: "baseline-shift",
		capHeight: "cap-height",
		className: "class",
		clipPath: "clip-path",
		clipRule: "clip-rule",
		colorInterpolation: "color-interpolation",
		colorInterpolationFilters: "color-interpolation-filters",
		colorProfile: "color-profile",
		colorRendering: "color-rendering",
		crossOrigin: "crossorigin",
		dataType: "datatype",
		dominantBaseline: "dominant-baseline",
		enableBackground: "enable-background",
		fillOpacity: "fill-opacity",
		fillRule: "fill-rule",
		floodColor: "flood-color",
		floodOpacity: "flood-opacity",
		fontFamily: "font-family",
		fontSize: "font-size",
		fontSizeAdjust: "font-size-adjust",
		fontStretch: "font-stretch",
		fontStyle: "font-style",
		fontVariant: "font-variant",
		fontWeight: "font-weight",
		glyphName: "glyph-name",
		glyphOrientationHorizontal: "glyph-orientation-horizontal",
		glyphOrientationVertical: "glyph-orientation-vertical",
		hrefLang: "hreflang",
		horizAdvX: "horiz-adv-x",
		horizOriginX: "horiz-origin-x",
		horizOriginY: "horiz-origin-y",
		imageRendering: "image-rendering",
		letterSpacing: "letter-spacing",
		lightingColor: "lighting-color",
		markerEnd: "marker-end",
		markerMid: "marker-mid",
		markerStart: "marker-start",
		navDown: "nav-down",
		navDownLeft: "nav-down-left",
		navDownRight: "nav-down-right",
		navLeft: "nav-left",
		navNext: "nav-next",
		navPrev: "nav-prev",
		navRight: "nav-right",
		navUp: "nav-up",
		navUpLeft: "nav-up-left",
		navUpRight: "nav-up-right",
		onAbort: "onabort",
		onActivate: "onactivate",
		onAfterPrint: "onafterprint",
		onBeforePrint: "onbeforeprint",
		onBegin: "onbegin",
		onCancel: "oncancel",
		onCanPlay: "oncanplay",
		onCanPlayThrough: "oncanplaythrough",
		onChange: "onchange",
		onClick: "onclick",
		onClose: "onclose",
		onCopy: "oncopy",
		onCueChange: "oncuechange",
		onCut: "oncut",
		onDblClick: "ondblclick",
		onDrag: "ondrag",
		onDragEnd: "ondragend",
		onDragEnter: "ondragenter",
		onDragExit: "ondragexit",
		onDragLeave: "ondragleave",
		onDragOver: "ondragover",
		onDragStart: "ondragstart",
		onDrop: "ondrop",
		onDurationChange: "ondurationchange",
		onEmptied: "onemptied",
		onEnd: "onend",
		onEnded: "onended",
		onError: "onerror",
		onFocus: "onfocus",
		onFocusIn: "onfocusin",
		onFocusOut: "onfocusout",
		onHashChange: "onhashchange",
		onInput: "oninput",
		onInvalid: "oninvalid",
		onKeyDown: "onkeydown",
		onKeyPress: "onkeypress",
		onKeyUp: "onkeyup",
		onLoad: "onload",
		onLoadedData: "onloadeddata",
		onLoadedMetadata: "onloadedmetadata",
		onLoadStart: "onloadstart",
		onMessage: "onmessage",
		onMouseDown: "onmousedown",
		onMouseEnter: "onmouseenter",
		onMouseLeave: "onmouseleave",
		onMouseMove: "onmousemove",
		onMouseOut: "onmouseout",
		onMouseOver: "onmouseover",
		onMouseUp: "onmouseup",
		onMouseWheel: "onmousewheel",
		onOffline: "onoffline",
		onOnline: "ononline",
		onPageHide: "onpagehide",
		onPageShow: "onpageshow",
		onPaste: "onpaste",
		onPause: "onpause",
		onPlay: "onplay",
		onPlaying: "onplaying",
		onPopState: "onpopstate",
		onProgress: "onprogress",
		onRateChange: "onratechange",
		onRepeat: "onrepeat",
		onReset: "onreset",
		onResize: "onresize",
		onScroll: "onscroll",
		onSeeked: "onseeked",
		onSeeking: "onseeking",
		onSelect: "onselect",
		onShow: "onshow",
		onStalled: "onstalled",
		onStorage: "onstorage",
		onSubmit: "onsubmit",
		onSuspend: "onsuspend",
		onTimeUpdate: "ontimeupdate",
		onToggle: "ontoggle",
		onUnload: "onunload",
		onVolumeChange: "onvolumechange",
		onWaiting: "onwaiting",
		onZoom: "onzoom",
		overlinePosition: "overline-position",
		overlineThickness: "overline-thickness",
		paintOrder: "paint-order",
		panose1: "panose-1",
		pointerEvents: "pointer-events",
		referrerPolicy: "referrerpolicy",
		renderingIntent: "rendering-intent",
		shapeRendering: "shape-rendering",
		stopColor: "stop-color",
		stopOpacity: "stop-opacity",
		strikethroughPosition: "strikethrough-position",
		strikethroughThickness: "strikethrough-thickness",
		strokeDashArray: "stroke-dasharray",
		strokeDashOffset: "stroke-dashoffset",
		strokeLineCap: "stroke-linecap",
		strokeLineJoin: "stroke-linejoin",
		strokeMiterLimit: "stroke-miterlimit",
		strokeOpacity: "stroke-opacity",
		strokeWidth: "stroke-width",
		tabIndex: "tabindex",
		textAnchor: "text-anchor",
		textDecoration: "text-decoration",
		textRendering: "text-rendering",
		transformOrigin: "transform-origin",
		typeOf: "typeof",
		underlinePosition: "underline-position",
		underlineThickness: "underline-thickness",
		unicodeBidi: "unicode-bidi",
		unicodeRange: "unicode-range",
		unitsPerEm: "units-per-em",
		vAlphabetic: "v-alphabetic",
		vHanging: "v-hanging",
		vIdeographic: "v-ideographic",
		vMathematical: "v-mathematical",
		vectorEffect: "vector-effect",
		vertAdvY: "vert-adv-y",
		vertOriginX: "vert-origin-x",
		vertOriginY: "vert-origin-y",
		wordSpacing: "word-spacing",
		writingMode: "writing-mode",
		xHeight: "x-height",
		playbackOrder: "playbackorder",
		timelineBegin: "timelinebegin"
	},
	transform: De,
	properties: {
		about: v,
		accentHeight: h,
		accumulate: null,
		additive: null,
		alignmentBaseline: null,
		alphabetic: h,
		amplitude: h,
		arabicForm: null,
		ascent: h,
		attributeName: null,
		attributeType: null,
		azimuth: h,
		bandwidth: null,
		baselineShift: null,
		baseFrequency: null,
		baseProfile: null,
		bbox: null,
		begin: null,
		bias: h,
		by: null,
		calcMode: null,
		capHeight: h,
		className: g,
		clip: null,
		clipPath: null,
		clipPathUnits: null,
		clipRule: null,
		color: null,
		colorInterpolation: null,
		colorInterpolationFilters: null,
		colorProfile: null,
		colorRendering: null,
		content: null,
		contentScriptType: null,
		contentStyleType: null,
		crossOrigin: null,
		cursor: null,
		cx: null,
		cy: null,
		d: null,
		dataType: null,
		defaultAction: null,
		descent: h,
		diffuseConstant: h,
		direction: null,
		display: null,
		dur: null,
		divisor: h,
		dominantBaseline: null,
		download: p,
		dx: null,
		dy: null,
		edgeMode: null,
		editable: null,
		elevation: h,
		enableBackground: null,
		end: null,
		event: null,
		exponent: h,
		externalResourcesRequired: null,
		fill: null,
		fillOpacity: h,
		fillRule: null,
		filter: null,
		filterRes: null,
		filterUnits: null,
		floodColor: null,
		floodOpacity: null,
		focusable: null,
		focusHighlight: null,
		fontFamily: null,
		fontSize: null,
		fontSizeAdjust: null,
		fontStretch: null,
		fontStyle: null,
		fontVariant: null,
		fontWeight: null,
		format: null,
		fr: null,
		from: null,
		fx: null,
		fy: null,
		g1: _,
		g2: _,
		glyphName: _,
		glyphOrientationHorizontal: null,
		glyphOrientationVertical: null,
		glyphRef: null,
		gradientTransform: null,
		gradientUnits: null,
		handler: null,
		hanging: h,
		hatchContentUnits: null,
		hatchUnits: null,
		height: null,
		href: null,
		hrefLang: null,
		horizAdvX: h,
		horizOriginX: h,
		horizOriginY: h,
		id: null,
		ideographic: h,
		imageRendering: null,
		initialVisibility: null,
		in: null,
		in2: null,
		intercept: h,
		k: h,
		k1: h,
		k2: h,
		k3: h,
		k4: h,
		kernelMatrix: v,
		kernelUnitLength: null,
		keyPoints: null,
		keySplines: null,
		keyTimes: null,
		kerning: null,
		lang: null,
		lengthAdjust: null,
		letterSpacing: null,
		lightingColor: null,
		limitingConeAngle: h,
		local: null,
		markerEnd: null,
		markerMid: null,
		markerStart: null,
		markerHeight: null,
		markerUnits: null,
		markerWidth: null,
		mask: null,
		maskContentUnits: null,
		maskUnits: null,
		mathematical: null,
		max: null,
		media: null,
		mediaCharacterEncoding: null,
		mediaContentEncodings: null,
		mediaSize: h,
		mediaTime: null,
		method: null,
		min: null,
		mode: null,
		name: null,
		navDown: null,
		navDownLeft: null,
		navDownRight: null,
		navLeft: null,
		navNext: null,
		navPrev: null,
		navRight: null,
		navUp: null,
		navUpLeft: null,
		navUpRight: null,
		numOctaves: null,
		observer: null,
		offset: null,
		onAbort: null,
		onActivate: null,
		onAfterPrint: null,
		onBeforePrint: null,
		onBegin: null,
		onCancel: null,
		onCanPlay: null,
		onCanPlayThrough: null,
		onChange: null,
		onClick: null,
		onClose: null,
		onCopy: null,
		onCueChange: null,
		onCut: null,
		onDblClick: null,
		onDrag: null,
		onDragEnd: null,
		onDragEnter: null,
		onDragExit: null,
		onDragLeave: null,
		onDragOver: null,
		onDragStart: null,
		onDrop: null,
		onDurationChange: null,
		onEmptied: null,
		onEnd: null,
		onEnded: null,
		onError: null,
		onFocus: null,
		onFocusIn: null,
		onFocusOut: null,
		onHashChange: null,
		onInput: null,
		onInvalid: null,
		onKeyDown: null,
		onKeyPress: null,
		onKeyUp: null,
		onLoad: null,
		onLoadedData: null,
		onLoadedMetadata: null,
		onLoadStart: null,
		onMessage: null,
		onMouseDown: null,
		onMouseEnter: null,
		onMouseLeave: null,
		onMouseMove: null,
		onMouseOut: null,
		onMouseOver: null,
		onMouseUp: null,
		onMouseWheel: null,
		onOffline: null,
		onOnline: null,
		onPageHide: null,
		onPageShow: null,
		onPaste: null,
		onPause: null,
		onPlay: null,
		onPlaying: null,
		onPopState: null,
		onProgress: null,
		onRateChange: null,
		onRepeat: null,
		onReset: null,
		onResize: null,
		onScroll: null,
		onSeeked: null,
		onSeeking: null,
		onSelect: null,
		onShow: null,
		onStalled: null,
		onStorage: null,
		onSubmit: null,
		onSuspend: null,
		onTimeUpdate: null,
		onToggle: null,
		onUnload: null,
		onVolumeChange: null,
		onWaiting: null,
		onZoom: null,
		opacity: null,
		operator: null,
		order: null,
		orient: null,
		orientation: null,
		origin: null,
		overflow: null,
		overlay: null,
		overlinePosition: h,
		overlineThickness: h,
		paintOrder: null,
		panose1: null,
		path: null,
		pathLength: h,
		patternContentUnits: null,
		patternTransform: null,
		patternUnits: null,
		phase: null,
		ping: g,
		pitch: null,
		playbackOrder: null,
		pointerEvents: null,
		points: null,
		pointsAtX: h,
		pointsAtY: h,
		pointsAtZ: h,
		preserveAlpha: null,
		preserveAspectRatio: null,
		primitiveUnits: null,
		propagate: null,
		property: v,
		r: null,
		radius: null,
		referrerPolicy: null,
		refX: null,
		refY: null,
		rel: v,
		rev: v,
		renderingIntent: null,
		repeatCount: null,
		repeatDur: null,
		requiredExtensions: v,
		requiredFeatures: v,
		requiredFonts: v,
		requiredFormats: v,
		resource: null,
		restart: null,
		result: null,
		rotate: null,
		rx: null,
		ry: null,
		scale: null,
		seed: null,
		shapeRendering: null,
		side: null,
		slope: null,
		snapshotTime: null,
		specularConstant: h,
		specularExponent: h,
		spreadMethod: null,
		spacing: null,
		startOffset: null,
		stdDeviation: null,
		stemh: null,
		stemv: null,
		stitchTiles: null,
		stopColor: null,
		stopOpacity: null,
		strikethroughPosition: h,
		strikethroughThickness: h,
		string: null,
		stroke: null,
		strokeDashArray: v,
		strokeDashOffset: null,
		strokeLineCap: null,
		strokeLineJoin: null,
		strokeMiterLimit: h,
		strokeOpacity: h,
		strokeWidth: null,
		style: null,
		surfaceScale: h,
		syncBehavior: null,
		syncBehaviorDefault: null,
		syncMaster: null,
		syncTolerance: null,
		syncToleranceDefault: null,
		systemLanguage: v,
		tabIndex: h,
		tableValues: null,
		target: null,
		targetX: h,
		targetY: h,
		textAnchor: null,
		textDecoration: null,
		textRendering: null,
		textLength: null,
		timelineBegin: null,
		title: null,
		transformBehavior: null,
		type: null,
		typeOf: v,
		to: null,
		transform: null,
		transformOrigin: null,
		u1: null,
		u2: null,
		underlinePosition: h,
		underlineThickness: h,
		unicode: null,
		unicodeBidi: null,
		unicodeRange: null,
		unitsPerEm: h,
		values: null,
		vAlphabetic: h,
		vMathematical: h,
		vectorEffect: null,
		vHanging: h,
		vIdeographic: h,
		version: null,
		vertAdvY: h,
		vertOriginX: h,
		vertOriginY: h,
		viewBox: null,
		viewTarget: null,
		visibility: null,
		width: null,
		widths: null,
		wordSpacing: null,
		writingMode: null,
		x: null,
		x1: null,
		x2: null,
		xChannelSelector: null,
		xHeight: h,
		y: null,
		y1: null,
		y2: null,
		yChannelSelector: null,
		z: null,
		zoomAndPan: null
	}
}), Ne = /^data[-\w.:]+$/i, Pe = /-[a-z]/g, Fe = /[A-Z]/g;
function Ie(e, t) {
	let n = _e(t), r = t, i = f;
	if (n in e.normal) return e.property[e.normal[n]];
	if (n.length > 4 && n.slice(0, 4) === "data" && Ne.test(t)) {
		if (t.charAt(4) === "-") {
			let e = t.slice(5).replace(Pe, Re);
			r = "data" + e.charAt(0).toUpperCase() + e.slice(1);
		} else {
			let e = t.slice(4);
			if (!Pe.test(e)) {
				let n = e.replace(Fe, Le);
				n.charAt(0) !== "-" && (n = "-" + n), t = "data" + n;
			}
		}
		i = Se;
	}
	return new i(r, t);
}
function Le(e) {
	return "-" + e.toLowerCase();
}
function Re(e) {
	return e.charAt(1).toUpperCase();
}
var ze = ge([
	Ee,
	Te,
	ke,
	Ae,
	je
], "html"), Be = ge([
	Ee,
	Te,
	ke,
	Ae,
	Me
], "svg"), Ve = {}, He = {}.hasOwnProperty, Ue = ie("type", { handlers: {
	root: Ge,
	element: Xe,
	text: Je,
	comment: Ye,
	doctype: qe
} });
function We(e, t) {
	let n = (t || Ve).space;
	return Ue(e, n === "svg" ? Be : ze);
}
function Ge(e, t) {
	let n = {
		nodeName: "#document",
		mode: (e.data || {}).quirksMode ? "quirks" : "no-quirks",
		childNodes: []
	};
	return n.childNodes = Qe(e.children, n, t), x(e, n), n;
}
function Ke(e, t) {
	let n = {
		nodeName: "#document-fragment",
		childNodes: []
	};
	return n.childNodes = Qe(e.children, n, t), x(e, n), n;
}
function qe(e) {
	let t = {
		nodeName: "#documentType",
		name: "html",
		publicId: "",
		systemId: "",
		parentNode: null
	};
	return x(e, t), t;
}
function Je(e) {
	let t = {
		nodeName: "#text",
		value: e.value,
		parentNode: null
	};
	return x(e, t), t;
}
function Ye(e) {
	let t = {
		nodeName: "#comment",
		data: e.value,
		parentNode: null
	};
	return x(e, t), t;
}
function Xe(e, t) {
	let n = t, r = n;
	e.type === "element" && e.tagName.toLowerCase() === "svg" && n.space === "html" && (r = Be);
	let i = [], a;
	if (e.properties) {
		for (a in e.properties) if (a !== "children" && He.call(e.properties, a)) {
			let t = Ze(r, a, e.properties[a]);
			t && i.push(t);
		}
	}
	let o = r.space, s = {
		nodeName: e.tagName,
		tagName: e.tagName,
		attrs: i,
		namespaceURI: l[o],
		childNodes: [],
		parentNode: null
	};
	return s.childNodes = Qe(e.children, s, r), x(e, s), e.tagName === "template" && e.content && (s.content = Ke(e.content, r)), s;
}
function Ze(e, n, r) {
	let i = Ie(e, n);
	if (r === !1 || r == null || typeof r == "number" && Number.isNaN(r) || !r && i.boolean) return;
	Array.isArray(r) && (r = i.commaSeparated ? o(r) : t(r));
	let a = {
		name: i.attribute,
		value: r === !0 ? "" : String(r)
	};
	if (i.space && i.space !== "html" && i.space !== "svg") {
		let e = a.name.indexOf(":");
		e < 0 ? a.prefix = "" : (a.name = a.name.slice(e + 1), a.prefix = i.attribute.slice(0, e)), a.namespace = l[i.space];
	}
	return a;
}
function Qe(e, t, n) {
	let r = -1, i = [];
	if (e) for (; ++r < e.length;) {
		let a = Ue(e[r], n);
		a.parentNode = t, i.push(a);
	}
	return i;
}
function x(e, t) {
	let n = e.position;
	n && n.start && n.end && (ee(typeof n.start.offset == "number"), ee(typeof n.end.offset == "number"), t.sourceCodeLocation = {
		startLine: n.start.line,
		startCol: n.start.column,
		startOffset: n.start.offset,
		endLine: n.end.line,
		endCol: n.end.column,
		endOffset: n.end.offset
	});
}
var $e = [
	"area",
	"base",
	"basefont",
	"bgsound",
	"br",
	"col",
	"command",
	"embed",
	"frame",
	"hr",
	"image",
	"img",
	"input",
	"keygen",
	"link",
	"meta",
	"param",
	"source",
	"track",
	"wbr"
], et = /* @__PURE__ */ new Set([
	65534,
	65535,
	131070,
	131071,
	196606,
	196607,
	262142,
	262143,
	327678,
	327679,
	393214,
	393215,
	458750,
	458751,
	524286,
	524287,
	589822,
	589823,
	655358,
	655359,
	720894,
	720895,
	786430,
	786431,
	851966,
	851967,
	917502,
	917503,
	983038,
	983039,
	1048574,
	1048575,
	1114110,
	1114111
]), S = "�", C;
(function(e) {
	e[e.EOF = -1] = "EOF", e[e.NULL = 0] = "NULL", e[e.TABULATION = 9] = "TABULATION", e[e.CARRIAGE_RETURN = 13] = "CARRIAGE_RETURN", e[e.LINE_FEED = 10] = "LINE_FEED", e[e.FORM_FEED = 12] = "FORM_FEED", e[e.SPACE = 32] = "SPACE", e[e.EXCLAMATION_MARK = 33] = "EXCLAMATION_MARK", e[e.QUOTATION_MARK = 34] = "QUOTATION_MARK", e[e.AMPERSAND = 38] = "AMPERSAND", e[e.APOSTROPHE = 39] = "APOSTROPHE", e[e.HYPHEN_MINUS = 45] = "HYPHEN_MINUS", e[e.SOLIDUS = 47] = "SOLIDUS", e[e.DIGIT_0 = 48] = "DIGIT_0", e[e.DIGIT_9 = 57] = "DIGIT_9", e[e.SEMICOLON = 59] = "SEMICOLON", e[e.LESS_THAN_SIGN = 60] = "LESS_THAN_SIGN", e[e.EQUALS_SIGN = 61] = "EQUALS_SIGN", e[e.GREATER_THAN_SIGN = 62] = "GREATER_THAN_SIGN", e[e.QUESTION_MARK = 63] = "QUESTION_MARK", e[e.LATIN_CAPITAL_A = 65] = "LATIN_CAPITAL_A", e[e.LATIN_CAPITAL_Z = 90] = "LATIN_CAPITAL_Z", e[e.RIGHT_SQUARE_BRACKET = 93] = "RIGHT_SQUARE_BRACKET", e[e.GRAVE_ACCENT = 96] = "GRAVE_ACCENT", e[e.LATIN_SMALL_A = 97] = "LATIN_SMALL_A", e[e.LATIN_SMALL_Z = 122] = "LATIN_SMALL_Z";
})(C ||= {});
var w = {
	DASH_DASH: "--",
	CDATA_START: "[CDATA[",
	DOCTYPE: "doctype",
	SCRIPT: "script",
	PUBLIC: "public",
	SYSTEM: "system"
};
function tt(e) {
	return e >= 55296 && e <= 57343;
}
function nt(e) {
	return e >= 56320 && e <= 57343;
}
function rt(e, t) {
	return (e - 55296) * 1024 + 9216 + t;
}
function it(e) {
	return e !== 32 && e !== 10 && e !== 13 && e !== 9 && e !== 12 && e >= 1 && e <= 31 || e >= 127 && e <= 159;
}
function at(e) {
	return e >= 64976 && e <= 65007 || et.has(e);
}
var T;
(function(e) {
	e.controlCharacterInInputStream = "control-character-in-input-stream", e.noncharacterInInputStream = "noncharacter-in-input-stream", e.surrogateInInputStream = "surrogate-in-input-stream", e.nonVoidHtmlElementStartTagWithTrailingSolidus = "non-void-html-element-start-tag-with-trailing-solidus", e.endTagWithAttributes = "end-tag-with-attributes", e.endTagWithTrailingSolidus = "end-tag-with-trailing-solidus", e.unexpectedSolidusInTag = "unexpected-solidus-in-tag", e.unexpectedNullCharacter = "unexpected-null-character", e.unexpectedQuestionMarkInsteadOfTagName = "unexpected-question-mark-instead-of-tag-name", e.invalidFirstCharacterOfTagName = "invalid-first-character-of-tag-name", e.unexpectedEqualsSignBeforeAttributeName = "unexpected-equals-sign-before-attribute-name", e.missingEndTagName = "missing-end-tag-name", e.unexpectedCharacterInAttributeName = "unexpected-character-in-attribute-name", e.unknownNamedCharacterReference = "unknown-named-character-reference", e.missingSemicolonAfterCharacterReference = "missing-semicolon-after-character-reference", e.unexpectedCharacterAfterDoctypeSystemIdentifier = "unexpected-character-after-doctype-system-identifier", e.unexpectedCharacterInUnquotedAttributeValue = "unexpected-character-in-unquoted-attribute-value", e.eofBeforeTagName = "eof-before-tag-name", e.eofInTag = "eof-in-tag", e.missingAttributeValue = "missing-attribute-value", e.missingWhitespaceBetweenAttributes = "missing-whitespace-between-attributes", e.missingWhitespaceAfterDoctypePublicKeyword = "missing-whitespace-after-doctype-public-keyword", e.missingWhitespaceBetweenDoctypePublicAndSystemIdentifiers = "missing-whitespace-between-doctype-public-and-system-identifiers", e.missingWhitespaceAfterDoctypeSystemKeyword = "missing-whitespace-after-doctype-system-keyword", e.missingQuoteBeforeDoctypePublicIdentifier = "missing-quote-before-doctype-public-identifier", e.missingQuoteBeforeDoctypeSystemIdentifier = "missing-quote-before-doctype-system-identifier", e.missingDoctypePublicIdentifier = "missing-doctype-public-identifier", e.missingDoctypeSystemIdentifier = "missing-doctype-system-identifier", e.abruptDoctypePublicIdentifier = "abrupt-doctype-public-identifier", e.abruptDoctypeSystemIdentifier = "abrupt-doctype-system-identifier", e.cdataInHtmlContent = "cdata-in-html-content", e.incorrectlyOpenedComment = "incorrectly-opened-comment", e.eofInScriptHtmlCommentLikeText = "eof-in-script-html-comment-like-text", e.eofInDoctype = "eof-in-doctype", e.nestedComment = "nested-comment", e.abruptClosingOfEmptyComment = "abrupt-closing-of-empty-comment", e.eofInComment = "eof-in-comment", e.incorrectlyClosedComment = "incorrectly-closed-comment", e.eofInCdata = "eof-in-cdata", e.absenceOfDigitsInNumericCharacterReference = "absence-of-digits-in-numeric-character-reference", e.nullCharacterReference = "null-character-reference", e.surrogateCharacterReference = "surrogate-character-reference", e.characterReferenceOutsideUnicodeRange = "character-reference-outside-unicode-range", e.controlCharacterReference = "control-character-reference", e.noncharacterCharacterReference = "noncharacter-character-reference", e.missingWhitespaceBeforeDoctypeName = "missing-whitespace-before-doctype-name", e.missingDoctypeName = "missing-doctype-name", e.invalidCharacterSequenceAfterDoctypeName = "invalid-character-sequence-after-doctype-name", e.duplicateAttribute = "duplicate-attribute", e.nonConformingDoctype = "non-conforming-doctype", e.missingDoctype = "missing-doctype", e.misplacedDoctype = "misplaced-doctype", e.endTagWithoutMatchingOpenElement = "end-tag-without-matching-open-element", e.closingOfElementWithOpenChildElements = "closing-of-element-with-open-child-elements", e.disallowedContentInNoscriptInHead = "disallowed-content-in-noscript-in-head", e.openElementsLeftAfterEof = "open-elements-left-after-eof", e.abandonedHeadElementChild = "abandoned-head-element-child", e.misplacedStartTagForHeadElement = "misplaced-start-tag-for-head-element", e.nestedNoscriptInHead = "nested-noscript-in-head", e.eofInElementThatCanContainOnlyText = "eof-in-element-that-can-contain-only-text";
})(T ||= {});
var ot = 65536, st = class {
	constructor(e) {
		this.handler = e, this.html = "", this.pos = -1, this.lastGapPos = -2, this.gapStack = [], this.skipNextNewLine = !1, this.lastChunkWritten = !1, this.endOfChunkHit = !1, this.bufferWaterline = ot, this.isEol = !1, this.lineStartPos = 0, this.droppedBufferSize = 0, this.line = 1, this.lastErrOffset = -1;
	}
	get col() {
		return this.pos - this.lineStartPos + +(this.lastGapPos !== this.pos);
	}
	get offset() {
		return this.droppedBufferSize + this.pos;
	}
	getError(e, t) {
		let { line: n, col: r, offset: i } = this, a = r + t, o = i + t;
		return {
			code: e,
			startLine: n,
			endLine: n,
			startCol: a,
			endCol: a,
			startOffset: o,
			endOffset: o
		};
	}
	_err(e) {
		this.handler.onParseError && this.lastErrOffset !== this.offset && (this.lastErrOffset = this.offset, this.handler.onParseError(this.getError(e, 0)));
	}
	_addGap() {
		this.gapStack.push(this.lastGapPos), this.lastGapPos = this.pos;
	}
	_processSurrogate(e) {
		if (this.pos !== this.html.length - 1) {
			let t = this.html.charCodeAt(this.pos + 1);
			if (nt(t)) return this.pos++, this._addGap(), rt(e, t);
		} else if (!this.lastChunkWritten) return this.endOfChunkHit = !0, C.EOF;
		return this._err(T.surrogateInInputStream), e;
	}
	willDropParsedChunk() {
		return this.pos > this.bufferWaterline;
	}
	dropParsedChunk() {
		this.willDropParsedChunk() && (this.html = this.html.substring(this.pos), this.lineStartPos -= this.pos, this.droppedBufferSize += this.pos, this.pos = 0, this.lastGapPos = -2, this.gapStack.length = 0);
	}
	write(e, t) {
		this.html.length > 0 ? this.html += e : this.html = e, this.endOfChunkHit = !1, this.lastChunkWritten = t;
	}
	insertHtmlAtCurrentPos(e) {
		this.html = this.html.substring(0, this.pos + 1) + e + this.html.substring(this.pos + 1), this.endOfChunkHit = !1;
	}
	startsWith(e, t) {
		if (this.pos + e.length > this.html.length) return this.endOfChunkHit = !this.lastChunkWritten, !1;
		if (t) return this.html.startsWith(e, this.pos);
		for (let t = 0; t < e.length; t++) if ((this.html.charCodeAt(this.pos + t) | 32) !== e.charCodeAt(t)) return !1;
		return !0;
	}
	peek(e) {
		let t = this.pos + e;
		if (t >= this.html.length) return this.endOfChunkHit = !this.lastChunkWritten, C.EOF;
		let n = this.html.charCodeAt(t);
		return n === C.CARRIAGE_RETURN ? C.LINE_FEED : n;
	}
	advance() {
		if (this.pos++, this.isEol && (this.isEol = !1, this.line++, this.lineStartPos = this.pos), this.pos >= this.html.length) return this.endOfChunkHit = !this.lastChunkWritten, C.EOF;
		let e = this.html.charCodeAt(this.pos);
		return e === C.CARRIAGE_RETURN ? (this.isEol = !0, this.skipNextNewLine = !0, C.LINE_FEED) : e === C.LINE_FEED && (this.isEol = !0, this.skipNextNewLine) ? (this.line--, this.skipNextNewLine = !1, this._addGap(), this.advance()) : (this.skipNextNewLine = !1, tt(e) && (e = this._processSurrogate(e)), this.handler.onParseError === null || e > 31 && e < 127 || e === C.LINE_FEED || e === C.CARRIAGE_RETURN || e > 159 && e < 64976 || this._checkForProblematicCharacters(e), e);
	}
	_checkForProblematicCharacters(e) {
		it(e) ? this._err(T.controlCharacterInInputStream) : at(e) && this._err(T.noncharacterInInputStream);
	}
	retreat(e) {
		for (this.pos -= e; this.pos < this.lastGapPos;) this.lastGapPos = this.gapStack.pop(), this.pos--;
		this.isEol = !1;
	}
}, E;
(function(e) {
	e[e.CHARACTER = 0] = "CHARACTER", e[e.NULL_CHARACTER = 1] = "NULL_CHARACTER", e[e.WHITESPACE_CHARACTER = 2] = "WHITESPACE_CHARACTER", e[e.START_TAG = 3] = "START_TAG", e[e.END_TAG = 4] = "END_TAG", e[e.COMMENT = 5] = "COMMENT", e[e.DOCTYPE = 6] = "DOCTYPE", e[e.EOF = 7] = "EOF", e[e.HIBERNATION = 8] = "HIBERNATION";
})(E ||= {});
function ct(e, t) {
	for (let n = e.attrs.length - 1; n >= 0; n--) if (e.attrs[n].name === t) return e.attrs[n].value;
	return null;
}
var lt = /* @__PURE__ */ new Uint16Array(/* @__PURE__ */ "ᵁ<Õıʊҝջאٵ۞ޢߖࠏ੊ઑඡ๭༉༦჊ረዡᐕᒝᓃᓟᔥ\0\0\0\0\0\0ᕫᛍᦍᰒᷝ὾⁠↰⊍⏀⏻⑂⠤⤒ⴈ⹈⿎〖㊺㘹㞬㣾㨨㩱㫠㬮ࠀEMabcfglmnoprstu\\bfms¦³¹ÈÏlig耻Æ䃆P耻&䀦cute耻Á䃁reve;䄂Āiyx}rc耻Â䃂;䐐r;쀀𝔄rave耻À䃀pha;䎑acr;䄀d;橓Āgp¡on;䄄f;쀀𝔸plyFunction;恡ing耻Å䃅Ācs¾Ãr;쀀𝒜ign;扔ilde耻Ã䃃ml耻Ä䃄ЀaceforsuåûþėĜĢħĪĀcrêòkslash;或Ŷöø;櫧ed;挆y;䐑ƀcrtąċĔause;戵noullis;愬a;䎒r;쀀𝔅pf;쀀𝔹eve;䋘còēmpeq;扎܀HOacdefhilorsuōőŖƀƞƢƵƷƺǜȕɳɸɾcy;䐧PY耻©䂩ƀcpyŝŢźute;䄆Ā;iŧŨ拒talDifferentialD;慅leys;愭ȀaeioƉƎƔƘron;䄌dil耻Ç䃇rc;䄈nint;戰ot;䄊ĀdnƧƭilla;䂸terDot;䂷òſi;䎧rcleȀDMPTǇǋǑǖot;抙inus;抖lus;投imes;抗oĀcsǢǸkwiseContourIntegral;戲eCurlyĀDQȃȏoubleQuote;思uote;怙ȀlnpuȞȨɇɕonĀ;eȥȦ户;橴ƀgitȯȶȺruent;扡nt;戯ourIntegral;戮ĀfrɌɎ;愂oduct;成nterClockwiseContourIntegral;戳oss;樯cr;쀀𝒞pĀ;Cʄʅ拓ap;才րDJSZacefiosʠʬʰʴʸˋ˗ˡ˦̳ҍĀ;oŹʥtrahd;椑cy;䐂cy;䐅cy;䐏ƀgrsʿ˄ˇger;怡r;憡hv;櫤Āayː˕ron;䄎;䐔lĀ;t˝˞戇a;䎔r;쀀𝔇Āaf˫̧Ācm˰̢riticalȀADGT̖̜̀̆cute;䂴oŴ̋̍;䋙bleAcute;䋝rave;䁠ilde;䋜ond;拄ferentialD;慆Ѱ̽\0\0\0͔͂\0Ѕf;쀀𝔻ƀ;DE͈͉͍䂨ot;惜qual;扐blèCDLRUVͣͲ΂ϏϢϸontourIntegraìȹoɴ͹\0\0ͻ»͉nArrow;懓Āeo·ΤftƀARTΐΖΡrrow;懐ightArrow;懔eåˊngĀLRΫτeftĀARγιrrow;柸ightArrow;柺ightArrow;柹ightĀATϘϞrrow;懒ee;抨pɁϩ\0\0ϯrrow;懑ownArrow;懕erticalBar;戥ǹABLRTaВЪаўѿͼrrowƀ;BUНОТ憓ar;椓pArrow;懵reve;䌑eft˒к\0ц\0ѐightVector;楐eeVector;楞ectorĀ;Bљњ憽ar;楖ightǔѧ\0ѱeeVector;楟ectorĀ;BѺѻ懁ar;楗eeĀ;A҆҇护rrow;憧ĀctҒҗr;쀀𝒟rok;䄐ࠀNTacdfglmopqstuxҽӀӄӋӞӢӧӮӵԡԯԶՒ՝ՠեG;䅊H耻Ð䃐cute耻É䃉ƀaiyӒӗӜron;䄚rc耻Ê䃊;䐭ot;䄖r;쀀𝔈rave耻È䃈ement;戈ĀapӺӾcr;䄒tyɓԆ\0\0ԒmallSquare;旻erySmallSquare;斫ĀgpԦԪon;䄘f;쀀𝔼silon;䎕uĀaiԼՉlĀ;TՂՃ橵ilde;扂librium;懌Āci՗՚r;愰m;橳a;䎗ml耻Ë䃋Āipժկsts;戃onentialE;慇ʀcfiosօֈ֍ֲ׌y;䐤r;쀀𝔉lledɓ֗\0\0֣mallSquare;旼erySmallSquare;斪Ͱֺ\0ֿ\0\0ׄf;쀀𝔽All;戀riertrf;愱cò׋؀JTabcdfgorstר׬ׯ׺؀ؒؖ؛؝أ٬ٲcy;䐃耻>䀾mmaĀ;d׷׸䎓;䏜reve;䄞ƀeiy؇،ؐdil;䄢rc;䄜;䐓ot;䄠r;쀀𝔊;拙pf;쀀𝔾eater̀EFGLSTصلَٖٛ٦qualĀ;Lؾؿ扥ess;招ullEqual;执reater;檢ess;扷lantEqual;橾ilde;扳cr;쀀𝒢;扫ЀAacfiosuڅڋږڛڞڪھۊRDcy;䐪Āctڐڔek;䋇;䁞irc;䄤r;愌lbertSpace;愋ǰگ\0ڲf;愍izontalLine;攀Āctۃۅòکrok;䄦mpńېۘownHumðįqual;扏܀EJOacdfgmnostuۺ۾܃܇܎ܚܞܡܨ݄ݸދޏޕcy;䐕lig;䄲cy;䐁cute耻Í䃍Āiyܓܘrc耻Î䃎;䐘ot;䄰r;愑rave耻Ì䃌ƀ;apܠܯܿĀcgܴܷr;䄪inaryI;慈lieóϝǴ݉\0ݢĀ;eݍݎ戬Āgrݓݘral;戫section;拂isibleĀCTݬݲomma;恣imes;恢ƀgptݿރވon;䄮f;쀀𝕀a;䎙cr;愐ilde;䄨ǫޚ\0ޞcy;䐆l耻Ï䃏ʀcfosuެ޷޼߂ߐĀiyޱ޵rc;䄴;䐙r;쀀𝔍pf;쀀𝕁ǣ߇\0ߌr;쀀𝒥rcy;䐈kcy;䐄΀HJacfosߤߨ߽߬߱ࠂࠈcy;䐥cy;䐌ppa;䎚Āey߶߻dil;䄶;䐚r;쀀𝔎pf;쀀𝕂cr;쀀𝒦րJTaceflmostࠥࠩࠬࡐࡣ঳সে্਷ੇcy;䐉耻<䀼ʀcmnpr࠷࠼ࡁࡄࡍute;䄹bda;䎛g;柪lacetrf;愒r;憞ƀaeyࡗ࡜ࡡron;䄽dil;䄻;䐛Āfsࡨ॰tԀACDFRTUVarࡾࢩࢱࣦ࣠ࣼयज़ΐ४Ānrࢃ࢏gleBracket;柨rowƀ;BR࢙࢚࢞憐ar;懤ightArrow;懆eiling;挈oǵࢷ\0ࣃbleBracket;柦nǔࣈ\0࣒eeVector;楡ectorĀ;Bࣛࣜ懃ar;楙loor;挊ightĀAV࣯ࣵrrow;憔ector;楎Āerँगeƀ;AVउऊऐ抣rrow;憤ector;楚iangleƀ;BEतथऩ抲ar;槏qual;抴pƀDTVषूौownVector;楑eeVector;楠ectorĀ;Bॖॗ憿ar;楘ectorĀ;B॥०憼ar;楒ightáΜs̀EFGLSTॾঋকঝঢভqualGreater;拚ullEqual;扦reater;扶ess;檡lantEqual;橽ilde;扲r;쀀𝔏Ā;eঽা拘ftarrow;懚idot;䄿ƀnpw৔ਖਛgȀLRlr৞৷ਂਐeftĀAR০৬rrow;柵ightArrow;柷ightArrow;柶eftĀarγਊightáοightáϊf;쀀𝕃erĀLRਢਬeftArrow;憙ightArrow;憘ƀchtਾੀੂòࡌ;憰rok;䅁;扪Ѐacefiosuਗ਼੝੠੷੼અઋ઎p;椅y;䐜Ādl੥੯iumSpace;恟lintrf;愳r;쀀𝔐nusPlus;戓pf;쀀𝕄cò੶;䎜ҀJacefostuણધભીଔଙඑ඗ඞcy;䐊cute;䅃ƀaey઴હાron;䅇dil;䅅;䐝ƀgswે૰଎ativeƀMTV૓૟૨ediumSpace;怋hiĀcn૦૘ë૙eryThiî૙tedĀGL૸ଆreaterGreateòٳessLesóੈLine;䀊r;쀀𝔑ȀBnptଢନଷ଺reak;恠BreakingSpace;䂠f;愕ڀ;CDEGHLNPRSTV୕ୖ୪୼஡௫ఄ౞಄ದ೘ൡඅ櫬Āou୛୤ngruent;扢pCap;扭oubleVerticalBar;戦ƀlqxஃஊ஛ement;戉ualĀ;Tஒஓ扠ilde;쀀≂̸ists;戄reater΀;EFGLSTஶஷ஽௉௓௘௥扯qual;扱ullEqual;쀀≧̸reater;쀀≫̸ess;批lantEqual;쀀⩾̸ilde;扵umpń௲௽ownHump;쀀≎̸qual;쀀≏̸eĀfsఊధtTriangleƀ;BEచఛడ拪ar;쀀⧏̸qual;括s̀;EGLSTవశ఼ౄోౘ扮qual;扰reater;扸ess;쀀≪̸lantEqual;쀀⩽̸ilde;扴estedĀGL౨౹reaterGreater;쀀⪢̸essLess;쀀⪡̸recedesƀ;ESಒಓಛ技qual;쀀⪯̸lantEqual;拠ĀeiಫಹverseElement;戌ghtTriangleƀ;BEೋೌ೒拫ar;쀀⧐̸qual;拭ĀquೝഌuareSuĀbp೨೹setĀ;E೰ೳ쀀⊏̸qual;拢ersetĀ;Eഃആ쀀⊐̸qual;拣ƀbcpഓതൎsetĀ;Eഛഞ쀀⊂⃒qual;抈ceedsȀ;ESTലള഻െ抁qual;쀀⪰̸lantEqual;拡ilde;쀀≿̸ersetĀ;E൘൛쀀⊃⃒qual;抉ildeȀ;EFT൮൯൵ൿ扁qual;扄ullEqual;扇ilde;扉erticalBar;戤cr;쀀𝒩ilde耻Ñ䃑;䎝܀Eacdfgmoprstuvලෂ෉෕ෛ෠෧෼ขภยา฿ไlig;䅒cute耻Ó䃓Āiy෎ීrc耻Ô䃔;䐞blac;䅐r;쀀𝔒rave耻Ò䃒ƀaei෮ෲ෶cr;䅌ga;䎩cron;䎟pf;쀀𝕆enCurlyĀDQฎบoubleQuote;怜uote;怘;橔Āclวฬr;쀀𝒪ash耻Ø䃘iŬื฼de耻Õ䃕es;樷ml耻Ö䃖erĀBP๋๠Āar๐๓r;怾acĀek๚๜;揞et;掴arenthesis;揜Ҁacfhilors๿ງຊຏຒດຝະ໼rtialD;戂y;䐟r;쀀𝔓i;䎦;䎠usMinus;䂱Āipຢອncareplanåڝf;愙Ȁ;eio຺ູ໠໤檻cedesȀ;EST່້໏໚扺qual;檯lantEqual;扼ilde;找me;怳Ādp໩໮uct;戏ortionĀ;aȥ໹l;戝Āci༁༆r;쀀𝒫;䎨ȀUfos༑༖༛༟OT耻\"䀢r;쀀𝔔pf;愚cr;쀀𝒬؀BEacefhiorsu༾གྷཇའཱིྦྷྪྭ႖ႩႴႾarr;椐G耻®䂮ƀcnrཎནབute;䅔g;柫rĀ;tཛྷཝ憠l;椖ƀaeyཧཬཱron;䅘dil;䅖;䐠Ā;vླྀཹ愜erseĀEUྂྙĀlq྇ྎement;戋uilibrium;懋pEquilibrium;楯r»ཹo;䎡ghtЀACDFTUVa࿁࿫࿳ဢဨၛႇϘĀnr࿆࿒gleBracket;柩rowƀ;BL࿜࿝࿡憒ar;懥eftArrow;懄eiling;按oǵ࿹\0စbleBracket;柧nǔည\0နeeVector;楝ectorĀ;Bဝသ懂ar;楕loor;挋Āerိ၃eƀ;AVဵံြ抢rrow;憦ector;楛iangleƀ;BEၐၑၕ抳ar;槐qual;抵pƀDTVၣၮၸownVector;楏eeVector;楜ectorĀ;Bႂႃ憾ar;楔ectorĀ;B႑႒懀ar;楓Āpuႛ႞f;愝ndImplies;楰ightarrow;懛ĀchႹႼr;愛;憱leDelayed;槴ڀHOacfhimoqstuფჱჷჽᄙᄞᅑᅖᅡᅧᆵᆻᆿĀCcჩხHcy;䐩y;䐨FTcy;䐬cute;䅚ʀ;aeiyᄈᄉᄎᄓᄗ檼ron;䅠dil;䅞rc;䅜;䐡r;쀀𝔖ortȀDLRUᄪᄴᄾᅉownArrow»ОeftArrow»࢚ightArrow»࿝pArrow;憑gma;䎣allCircle;战pf;쀀𝕊ɲᅭ\0\0ᅰt;戚areȀ;ISUᅻᅼᆉᆯ斡ntersection;抓uĀbpᆏᆞsetĀ;Eᆗᆘ抏qual;抑ersetĀ;Eᆨᆩ抐qual;抒nion;抔cr;쀀𝒮ar;拆ȀbcmpᇈᇛሉላĀ;sᇍᇎ拐etĀ;Eᇍᇕqual;抆ĀchᇠህeedsȀ;ESTᇭᇮᇴᇿ扻qual;檰lantEqual;扽ilde;承Tháྌ;我ƀ;esሒሓሣ拑rsetĀ;Eሜም抃qual;抇et»ሓրHRSacfhiorsሾቄ቉ቕ቞ቱቶኟዂወዑORN耻Þ䃞ADE;愢ĀHc቎ቒcy;䐋y;䐦Ābuቚቜ;䀉;䎤ƀaeyብቪቯron;䅤dil;䅢;䐢r;쀀𝔗Āeiቻ኉ǲኀ\0ኇefore;戴a;䎘Ācn኎ኘkSpace;쀀  Space;怉ldeȀ;EFTካኬኲኼ戼qual;扃ullEqual;扅ilde;扈pf;쀀𝕋ipleDot;惛Āctዖዛr;쀀𝒯rok;䅦ૡዷጎጚጦ\0ጬጱ\0\0\0\0\0ጸጽ፷ᎅ\0᏿ᐄᐊᐐĀcrዻጁute耻Ú䃚rĀ;oጇገ憟cir;楉rǣጓ\0጖y;䐎ve;䅬Āiyጞጣrc耻Û䃛;䐣blac;䅰r;쀀𝔘rave耻Ù䃙acr;䅪Ādiፁ፩erĀBPፈ፝Āarፍፐr;䁟acĀekፗፙ;揟et;掵arenthesis;揝onĀ;P፰፱拃lus;抎Āgp፻፿on;䅲f;쀀𝕌ЀADETadps᎕ᎮᎸᏄϨᏒᏗᏳrrowƀ;BDᅐᎠᎤar;椒ownArrow;懅ownArrow;憕quilibrium;楮eeĀ;AᏋᏌ报rrow;憥ownáϳerĀLRᏞᏨeftArrow;憖ightArrow;憗iĀ;lᏹᏺ䏒on;䎥ing;䅮cr;쀀𝒰ilde;䅨ml耻Ü䃜ҀDbcdefosvᐧᐬᐰᐳᐾᒅᒊᒐᒖash;披ar;櫫y;䐒ashĀ;lᐻᐼ抩;櫦Āerᑃᑅ;拁ƀbtyᑌᑐᑺar;怖Ā;iᑏᑕcalȀBLSTᑡᑥᑪᑴar;戣ine;䁼eparator;杘ilde;所ThinSpace;怊r;쀀𝔙pf;쀀𝕍cr;쀀𝒱dash;抪ʀcefosᒧᒬᒱᒶᒼirc;䅴dge;拀r;쀀𝔚pf;쀀𝕎cr;쀀𝒲Ȁfiosᓋᓐᓒᓘr;쀀𝔛;䎞pf;쀀𝕏cr;쀀𝒳ҀAIUacfosuᓱᓵᓹᓽᔄᔏᔔᔚᔠcy;䐯cy;䐇cy;䐮cute耻Ý䃝Āiyᔉᔍrc;䅶;䐫r;쀀𝔜pf;쀀𝕐cr;쀀𝒴ml;䅸ЀHacdefosᔵᔹᔿᕋᕏᕝᕠᕤcy;䐖cute;䅹Āayᕄᕉron;䅽;䐗ot;䅻ǲᕔ\0ᕛoWidtè૙a;䎖r;愨pf;愤cr;쀀𝒵௡ᖃᖊᖐ\0ᖰᖶᖿ\0\0\0\0ᗆᗛᗫᙟ᙭\0ᚕ᚛ᚲᚹ\0ᚾcute耻á䃡reve;䄃̀;Ediuyᖜᖝᖡᖣᖨᖭ戾;쀀∾̳;房rc耻â䃢te肻´̆;䐰lig耻æ䃦Ā;r²ᖺ;쀀𝔞rave耻à䃠ĀepᗊᗖĀfpᗏᗔsym;愵èᗓha;䎱ĀapᗟcĀclᗤᗧr;䄁g;樿ɤᗰ\0\0ᘊʀ;adsvᗺᗻᗿᘁᘇ戧nd;橕;橜lope;橘;橚΀;elmrszᘘᘙᘛᘞᘿᙏᙙ戠;榤e»ᘙsdĀ;aᘥᘦ戡ѡᘰᘲᘴᘶᘸᘺᘼᘾ;榨;榩;榪;榫;榬;榭;榮;榯tĀ;vᙅᙆ戟bĀ;dᙌᙍ抾;榝Āptᙔᙗh;戢»¹arr;捼Āgpᙣᙧon;䄅f;쀀𝕒΀;Eaeiop዁ᙻᙽᚂᚄᚇᚊ;橰cir;橯;扊d;手s;䀧roxĀ;e዁ᚒñᚃing耻å䃥ƀctyᚡᚦᚨr;쀀𝒶;䀪mpĀ;e዁ᚯñʈilde耻ã䃣ml耻ä䃤Āciᛂᛈoninôɲnt;樑ࠀNabcdefiklnoprsu᛭ᛱᜰ᜼ᝃᝈ᝸᝽០៦ᠹᡐᜍ᤽᥈ᥰot;櫭Ācrᛶ᜞kȀcepsᜀᜅᜍᜓong;扌psilon;䏶rime;怵imĀ;e᜚᜛戽q;拍Ŷᜢᜦee;抽edĀ;gᜬᜭ挅e»ᜭrkĀ;t፜᜷brk;掶Āoyᜁᝁ;䐱quo;怞ʀcmprtᝓ᝛ᝡᝤᝨausĀ;eĊĉptyv;榰séᜌnoõēƀahwᝯ᝱ᝳ;䎲;愶een;扬r;쀀𝔟g΀costuvwឍឝឳេ៕៛៞ƀaiuបពរðݠrc;旯p»፱ƀdptឤឨឭot;樀lus;樁imes;樂ɱឹ\0\0ើcup;樆ar;昅riangleĀdu៍្own;施p;斳plus;樄eåᑄåᒭarow;植ƀako៭ᠦᠵĀcn៲ᠣkƀlst៺֫᠂ozenge;槫riangleȀ;dlr᠒᠓᠘᠝斴own;斾eft;旂ight;斸k;搣Ʊᠫ\0ᠳƲᠯ\0ᠱ;斒;斑4;斓ck;斈ĀeoᠾᡍĀ;qᡃᡆ쀀=⃥uiv;쀀≡⃥t;挐Ȁptwxᡙᡞᡧᡬf;쀀𝕓Ā;tᏋᡣom»Ꮜtie;拈؀DHUVbdhmptuvᢅᢖᢪᢻᣗᣛᣬ᣿ᤅᤊᤐᤡȀLRlrᢎᢐᢒᢔ;敗;敔;敖;敓ʀ;DUduᢡᢢᢤᢦᢨ敐;敦;敩;敤;敧ȀLRlrᢳᢵᢷᢹ;敝;敚;敜;教΀;HLRhlrᣊᣋᣍᣏᣑᣓᣕ救;敬;散;敠;敫;敢;敟ox;槉ȀLRlrᣤᣦᣨᣪ;敕;敒;攐;攌ʀ;DUduڽ᣷᣹᣻᣽;敥;敨;攬;攴inus;抟lus;択imes;抠ȀLRlrᤙᤛᤝ᤟;敛;敘;攘;攔΀;HLRhlrᤰᤱᤳᤵᤷ᤻᤹攂;敪;敡;敞;攼;攤;攜Āevģ᥂bar耻¦䂦Ȁceioᥑᥖᥚᥠr;쀀𝒷mi;恏mĀ;e᜚᜜lƀ;bhᥨᥩᥫ䁜;槅sub;柈Ŭᥴ᥾lĀ;e᥹᥺怢t»᥺pƀ;Eeįᦅᦇ;檮Ā;qۜۛೡᦧ\0᧨ᨑᨕᨲ\0ᨷᩐ\0\0᪴\0\0᫁\0\0ᬡᬮ᭍᭒\0᯽\0ᰌƀcpr᦭ᦲ᧝ute;䄇̀;abcdsᦿᧀᧄ᧊᧕᧙戩nd;橄rcup;橉Āau᧏᧒p;橋p;橇ot;橀;쀀∩︀Āeo᧢᧥t;恁îړȀaeiu᧰᧻ᨁᨅǰ᧵\0᧸s;橍on;䄍dil耻ç䃧rc;䄉psĀ;sᨌᨍ橌m;橐ot;䄋ƀdmnᨛᨠᨦil肻¸ƭptyv;榲t脀¢;eᨭᨮ䂢räƲr;쀀𝔠ƀceiᨽᩀᩍy;䑇ckĀ;mᩇᩈ朓ark»ᩈ;䏇r΀;Ecefms᩟᩠ᩢᩫ᪤᪪᪮旋;槃ƀ;elᩩᩪᩭ䋆q;扗eɡᩴ\0\0᪈rrowĀlr᩼᪁eft;憺ight;憻ʀRSacd᪒᪔᪖᪚᪟»ཇ;擈st;抛irc;抚ash;抝nint;樐id;櫯cir;槂ubsĀ;u᪻᪼晣it»᪼ˬ᫇᫔᫺\0ᬊonĀ;eᫍᫎ䀺Ā;qÇÆɭ᫙\0\0᫢aĀ;t᫞᫟䀬;䁀ƀ;fl᫨᫩᫫戁îᅠeĀmx᫱᫶ent»᫩eóɍǧ᫾\0ᬇĀ;dኻᬂot;橭nôɆƀfryᬐᬔᬗ;쀀𝕔oäɔ脀©;sŕᬝr;愗Āaoᬥᬩrr;憵ss;朗Ācuᬲᬷr;쀀𝒸Ābpᬼ᭄Ā;eᭁᭂ櫏;櫑Ā;eᭉᭊ櫐;櫒dot;拯΀delprvw᭠᭬᭷ᮂᮬᯔ᯹arrĀlr᭨᭪;椸;椵ɰ᭲\0\0᭵r;拞c;拟arrĀ;p᭿ᮀ憶;椽̀;bcdosᮏᮐᮖᮡᮥᮨ截rcap;橈Āauᮛᮞp;橆p;橊ot;抍r;橅;쀀∪︀Ȁalrv᮵ᮿᯞᯣrrĀ;mᮼᮽ憷;椼yƀevwᯇᯔᯘqɰᯎ\0\0ᯒreã᭳uã᭵ee;拎edge;拏en耻¤䂤earrowĀlrᯮ᯳eft»ᮀight»ᮽeäᯝĀciᰁᰇoninôǷnt;戱lcty;挭ঀAHabcdefhijlorstuwz᰸᰻᰿ᱝᱩᱵᲊᲞᲬᲷ᳻᳿ᴍᵻᶑᶫᶻ᷆᷍rò΁ar;楥Ȁglrs᱈ᱍ᱒᱔ger;怠eth;愸òᄳhĀ;vᱚᱛ怐»ऊūᱡᱧarow;椏aã̕Āayᱮᱳron;䄏;䐴ƀ;ao̲ᱼᲄĀgrʿᲁr;懊tseq;橷ƀglmᲑᲔᲘ耻°䂰ta;䎴ptyv;榱ĀirᲣᲨsht;楿;쀀𝔡arĀlrᲳᲵ»ࣜ»သʀaegsv᳂͸᳖᳜᳠mƀ;oș᳊᳔ndĀ;ș᳑uit;晦amma;䏝in;拲ƀ;io᳧᳨᳸䃷de脀÷;o᳧ᳰntimes;拇nø᳷cy;䑒cɯᴆ\0\0ᴊrn;挞op;挍ʀlptuwᴘᴝᴢᵉᵕlar;䀤f;쀀𝕕ʀ;emps̋ᴭᴷᴽᵂqĀ;d͒ᴳot;扑inus;戸lus;戔quare;抡blebarwedgåúnƀadhᄮᵝᵧownarrowóᲃarpoonĀlrᵲᵶefôᲴighôᲶŢᵿᶅkaro÷གɯᶊ\0\0ᶎrn;挟op;挌ƀcotᶘᶣᶦĀryᶝᶡ;쀀𝒹;䑕l;槶rok;䄑Ādrᶰᶴot;拱iĀ;fᶺ᠖斿Āah᷀᷃ròЩaòྦangle;榦Āci᷒ᷕy;䑟grarr;柿ऀDacdefglmnopqrstuxḁḉḙḸոḼṉṡṾấắẽỡἪἷὄ὎὚ĀDoḆᴴoôᲉĀcsḎḔute耻é䃩ter;橮ȀaioyḢḧḱḶron;䄛rĀ;cḭḮ扖耻ê䃪lon;払;䑍ot;䄗ĀDrṁṅot;扒;쀀𝔢ƀ;rsṐṑṗ檚ave耻è䃨Ā;dṜṝ檖ot;檘Ȁ;ilsṪṫṲṴ檙nters;揧;愓Ā;dṹṺ檕ot;檗ƀapsẅẉẗcr;䄓tyƀ;svẒẓẕ戅et»ẓpĀ1;ẝẤĳạả;怄;怅怃ĀgsẪẬ;䅋p;怂ĀgpẴẸon;䄙f;쀀𝕖ƀalsỄỎỒrĀ;sỊị拕l;槣us;橱iƀ;lvỚớở䎵on»ớ;䏵ȀcsuvỪỳἋἣĀioữḱrc»Ḯɩỹ\0\0ỻíՈantĀglἂἆtr»ṝess»Ṻƀaeiἒ἖Ἒls;䀽st;扟vĀ;DȵἠD;橸parsl;槥ĀDaἯἳot;打rr;楱ƀcdiἾὁỸr;愯oô͒ĀahὉὋ;䎷耻ð䃰Āmrὓὗl耻ë䃫o;悬ƀcipὡὤὧl;䀡sôծĀeoὬὴctatioîՙnentialåչৡᾒ\0ᾞ\0ᾡᾧ\0\0ῆῌ\0ΐ\0ῦῪ \0 ⁚llingdotseñṄy;䑄male;晀ƀilrᾭᾳ῁lig;耀ﬃɩᾹ\0\0᾽g;耀ﬀig;耀ﬄ;쀀𝔣lig;耀ﬁlig;쀀fjƀaltῙ῜ῡt;晭ig;耀ﬂns;斱of;䆒ǰ΅\0ῳf;쀀𝕗ĀakֿῷĀ;vῼ´拔;櫙artint;樍Āao‌⁕Ācs‑⁒α‚‰‸⁅⁈\0⁐β•‥‧‪‬\0‮耻½䂽;慓耻¼䂼;慕;慙;慛Ƴ‴\0‶;慔;慖ʴ‾⁁\0\0⁃耻¾䂾;慗;慜5;慘ƶ⁌\0⁎;慚;慝8;慞l;恄wn;挢cr;쀀𝒻ࢀEabcdefgijlnorstv₂₉₟₥₰₴⃰⃵⃺⃿℃ℒℸ̗ℾ⅒↞Ā;lٍ₇;檌ƀcmpₐₕ₝ute;䇵maĀ;dₜ᳚䎳;檆reve;䄟Āiy₪₮rc;䄝;䐳ot;䄡Ȁ;lqsؾق₽⃉ƀ;qsؾٌ⃄lanô٥Ȁ;cdl٥⃒⃥⃕c;檩otĀ;o⃜⃝檀Ā;l⃢⃣檂;檄Ā;e⃪⃭쀀⋛︀s;檔r;쀀𝔤Ā;gٳ؛mel;愷cy;䑓Ȁ;Eajٚℌℎℐ;檒;檥;檤ȀEaesℛℝ℩ℴ;扩pĀ;p℣ℤ檊rox»ℤĀ;q℮ℯ檈Ā;q℮ℛim;拧pf;쀀𝕘Āci⅃ⅆr;愊mƀ;el٫ⅎ⅐;檎;檐茀>;cdlqr׮ⅠⅪⅮⅳⅹĀciⅥⅧ;檧r;橺ot;拗Par;榕uest;橼ʀadelsↄⅪ←ٖ↛ǰ↉\0↎proø₞r;楸qĀlqؿ↖lesó₈ií٫Āen↣↭rtneqq;쀀≩︀Å↪ԀAabcefkosy⇄⇇⇱⇵⇺∘∝∯≨≽ròΠȀilmr⇐⇔⇗⇛rsðᒄf»․ilôکĀdr⇠⇤cy;䑊ƀ;cwࣴ⇫⇯ir;楈;憭ar;意irc;䄥ƀalr∁∎∓rtsĀ;u∉∊晥it»∊lip;怦con;抹r;쀀𝔥sĀew∣∩arow;椥arow;椦ʀamopr∺∾≃≞≣rr;懿tht;戻kĀlr≉≓eftarrow;憩ightarrow;憪f;쀀𝕙bar;怕ƀclt≯≴≸r;쀀𝒽asè⇴rok;䄧Ābp⊂⊇ull;恃hen»ᱛૡ⊣\0⊪\0⊸⋅⋎\0⋕⋳\0\0⋸⌢⍧⍢⍿\0⎆⎪⎴cute耻í䃭ƀ;iyݱ⊰⊵rc耻î䃮;䐸Ācx⊼⊿y;䐵cl耻¡䂡ĀfrΟ⋉;쀀𝔦rave耻ì䃬Ȁ;inoܾ⋝⋩⋮Āin⋢⋦nt;樌t;戭fin;槜ta;愩lig;䄳ƀaop⋾⌚⌝ƀcgt⌅⌈⌗r;䄫ƀelpܟ⌏⌓inåގarôܠh;䄱f;抷ed;䆵ʀ;cfotӴ⌬⌱⌽⍁are;愅inĀ;t⌸⌹戞ie;槝doô⌙ʀ;celpݗ⍌⍐⍛⍡al;抺Āgr⍕⍙eróᕣã⍍arhk;樗rod;樼Ȁcgpt⍯⍲⍶⍻y;䑑on;䄯f;쀀𝕚a;䎹uest耻¿䂿Āci⎊⎏r;쀀𝒾nʀ;EdsvӴ⎛⎝⎡ӳ;拹ot;拵Ā;v⎦⎧拴;拳Ā;iݷ⎮lde;䄩ǫ⎸\0⎼cy;䑖l耻ï䃯̀cfmosu⏌⏗⏜⏡⏧⏵Āiy⏑⏕rc;䄵;䐹r;쀀𝔧ath;䈷pf;쀀𝕛ǣ⏬\0⏱r;쀀𝒿rcy;䑘kcy;䑔Ѐacfghjos␋␖␢␧␭␱␵␻ppaĀ;v␓␔䎺;䏰Āey␛␠dil;䄷;䐺r;쀀𝔨reen;䄸cy;䑅cy;䑜pf;쀀𝕜cr;쀀𝓀஀ABEHabcdefghjlmnoprstuv⑰⒁⒆⒍⒑┎┽╚▀♎♞♥♹♽⚚⚲⛘❝❨➋⟀⠁⠒ƀart⑷⑺⑼rò৆òΕail;椛arr;椎Ā;gঔ⒋;檋ar;楢ॣ⒥\0⒪\0⒱\0\0\0\0\0⒵Ⓔ\0ⓆⓈⓍ\0⓹ute;䄺mptyv;榴raîࡌbda;䎻gƀ;dlࢎⓁⓃ;榑åࢎ;檅uo耻«䂫rЀ;bfhlpst࢙ⓞⓦⓩ⓫⓮⓱⓵Ā;f࢝ⓣs;椟s;椝ë≒p;憫l;椹im;楳l;憢ƀ;ae⓿─┄檫il;椙Ā;s┉┊檭;쀀⪭︀ƀabr┕┙┝rr;椌rk;杲Āak┢┬cĀek┨┪;䁻;䁛Āes┱┳;榋lĀdu┹┻;榏;榍Ȁaeuy╆╋╖╘ron;䄾Ādi═╔il;䄼ìࢰâ┩;䐻Ȁcqrs╣╦╭╽a;椶uoĀ;rนᝆĀdu╲╷har;楧shar;楋h;憲ʀ;fgqs▋▌উ◳◿扤tʀahlrt▘▤▷◂◨rrowĀ;t࢙□aé⓶arpoonĀdu▯▴own»њp»०eftarrows;懇ightƀahs◍◖◞rrowĀ;sࣴࢧarpoonó྘quigarro÷⇰hreetimes;拋ƀ;qs▋ও◺lanôবʀ;cdgsব☊☍☝☨c;檨otĀ;o☔☕橿Ā;r☚☛檁;檃Ā;e☢☥쀀⋚︀s;檓ʀadegs☳☹☽♉♋pproøⓆot;拖qĀgq♃♅ôউgtò⒌ôছiíলƀilr♕࣡♚sht;楼;쀀𝔩Ā;Eজ♣;檑š♩♶rĀdu▲♮Ā;l॥♳;楪lk;斄cy;䑙ʀ;achtੈ⚈⚋⚑⚖rò◁orneòᴈard;楫ri;旺Āio⚟⚤dot;䅀ustĀ;a⚬⚭掰che»⚭ȀEaes⚻⚽⛉⛔;扨pĀ;p⛃⛄檉rox»⛄Ā;q⛎⛏檇Ā;q⛎⚻im;拦Ѐabnoptwz⛩⛴⛷✚✯❁❇❐Ānr⛮⛱g;柬r;懽rëࣁgƀlmr⛿✍✔eftĀar০✇ightá৲apsto;柼ightá৽parrowĀlr✥✩efô⓭ight;憬ƀafl✶✹✽r;榅;쀀𝕝us;樭imes;樴š❋❏st;戗áፎƀ;ef❗❘᠀旊nge»❘arĀ;l❤❥䀨t;榓ʀachmt❳❶❼➅➇ròࢨorneòᶌarĀ;d྘➃;業;怎ri;抿̀achiqt➘➝ੀ➢➮➻quo;怹r;쀀𝓁mƀ;egল➪➬;檍;檏Ābu┪➳oĀ;rฟ➹;怚rok;䅂萀<;cdhilqrࠫ⟒☹⟜⟠⟥⟪⟰Āci⟗⟙;檦r;橹reå◲mes;拉arr;楶uest;橻ĀPi⟵⟹ar;榖ƀ;ef⠀भ᠛旃rĀdu⠇⠍shar;楊har;楦Āen⠗⠡rtneqq;쀀≨︀Å⠞܀Dacdefhilnopsu⡀⡅⢂⢎⢓⢠⢥⢨⣚⣢⣤ઃ⣳⤂Dot;戺Ȁclpr⡎⡒⡣⡽r耻¯䂯Āet⡗⡙;時Ā;e⡞⡟朠se»⡟Ā;sျ⡨toȀ;dluျ⡳⡷⡻owîҌefôएðᏑker;斮Āoy⢇⢌mma;権;䐼ash;怔asuredangle»ᘦr;쀀𝔪o;愧ƀcdn⢯⢴⣉ro耻µ䂵Ȁ;acdᑤ⢽⣀⣄sôᚧir;櫰ot肻·Ƶusƀ;bd⣒ᤃ⣓戒Ā;uᴼ⣘;横ţ⣞⣡p;櫛ò−ðઁĀdp⣩⣮els;抧f;쀀𝕞Āct⣸⣽r;쀀𝓂pos»ᖝƀ;lm⤉⤊⤍䎼timap;抸ఀGLRVabcdefghijlmoprstuvw⥂⥓⥾⦉⦘⧚⧩⨕⨚⩘⩝⪃⪕⪤⪨⬄⬇⭄⭿⮮ⰴⱧⱼ⳩Āgt⥇⥋;쀀⋙̸Ā;v⥐௏쀀≫⃒ƀelt⥚⥲⥶ftĀar⥡⥧rrow;懍ightarrow;懎;쀀⋘̸Ā;v⥻ే쀀≪⃒ightarrow;懏ĀDd⦎⦓ash;抯ash;抮ʀbcnpt⦣⦧⦬⦱⧌la»˞ute;䅄g;쀀∠⃒ʀ;Eiop඄⦼⧀⧅⧈;쀀⩰̸d;쀀≋̸s;䅉roø඄urĀ;a⧓⧔普lĀ;s⧓ସǳ⧟\0⧣p肻\xA0ଷmpĀ;e௹ఀʀaeouy⧴⧾⨃⨐⨓ǰ⧹\0⧻;橃on;䅈dil;䅆ngĀ;dൾ⨊ot;쀀⩭̸p;橂;䐽ash;怓΀;Aadqsxஒ⨩⨭⨻⩁⩅⩐rr;懗rĀhr⨳⨶k;椤Ā;oᏲᏰot;쀀≐̸uiöୣĀei⩊⩎ar;椨í஘istĀ;s஠டr;쀀𝔫ȀEest௅⩦⩹⩼ƀ;qs஼⩭௡ƀ;qs஼௅⩴lanô௢ií௪Ā;rஶ⪁»ஷƀAap⪊⪍⪑rò⥱rr;憮ar;櫲ƀ;svྍ⪜ྌĀ;d⪡⪢拼;拺cy;䑚΀AEadest⪷⪺⪾⫂⫅⫶⫹rò⥦;쀀≦̸rr;憚r;急Ȁ;fqs఻⫎⫣⫯tĀar⫔⫙rro÷⫁ightarro÷⪐ƀ;qs఻⪺⫪lanôౕĀ;sౕ⫴»శiíౝĀ;rవ⫾iĀ;eచథiäඐĀpt⬌⬑f;쀀𝕟膀¬;in⬙⬚⬶䂬nȀ;Edvஉ⬤⬨⬮;쀀⋹̸ot;쀀⋵̸ǡஉ⬳⬵;拷;拶iĀ;vಸ⬼ǡಸ⭁⭃;拾;拽ƀaor⭋⭣⭩rȀ;ast୻⭕⭚⭟lleì୻l;쀀⫽⃥;쀀∂̸lint;樔ƀ;ceಒ⭰⭳uåಥĀ;cಘ⭸Ā;eಒ⭽ñಘȀAait⮈⮋⮝⮧rò⦈rrƀ;cw⮔⮕⮙憛;쀀⤳̸;쀀↝̸ghtarrow»⮕riĀ;eೋೖ΀chimpqu⮽⯍⯙⬄୸⯤⯯Ȁ;cerല⯆ഷ⯉uå൅;쀀𝓃ortɭ⬅\0\0⯖ará⭖mĀ;e൮⯟Ā;q൴൳suĀbp⯫⯭å೸åഋƀbcp⯶ⰑⰙȀ;Ees⯿ⰀഢⰄ抄;쀀⫅̸etĀ;eഛⰋqĀ;qണⰀcĀ;eലⰗñസȀ;EesⰢⰣൟⰧ抅;쀀⫆̸etĀ;e൘ⰮqĀ;qൠⰣȀgilrⰽⰿⱅⱇìௗlde耻ñ䃱çృiangleĀlrⱒⱜeftĀ;eచⱚñదightĀ;eೋⱥñ೗Ā;mⱬⱭ䎽ƀ;esⱴⱵⱹ䀣ro;愖p;怇ҀDHadgilrsⲏⲔⲙⲞⲣⲰⲶⳓⳣash;抭arr;椄p;쀀≍⃒ash;抬ĀetⲨⲬ;쀀≥⃒;쀀>⃒nfin;槞ƀAetⲽⳁⳅrr;椂;쀀≤⃒Ā;rⳊⳍ쀀<⃒ie;쀀⊴⃒ĀAtⳘⳜrr;椃rie;쀀⊵⃒im;쀀∼⃒ƀAan⳰⳴ⴂrr;懖rĀhr⳺⳽k;椣Ā;oᏧᏥear;椧ቓ᪕\0\0\0\0\0\0\0\0\0\0\0\0\0ⴭ\0ⴸⵈⵠⵥ⵲ⶄᬇ\0\0ⶍⶫ\0ⷈⷎ\0ⷜ⸙⸫⸾⹃Ācsⴱ᪗ute耻ó䃳ĀiyⴼⵅrĀ;c᪞ⵂ耻ô䃴;䐾ʀabios᪠ⵒⵗǈⵚlac;䅑v;樸old;榼lig;䅓Ācr⵩⵭ir;榿;쀀𝔬ͯ⵹\0\0⵼\0ⶂn;䋛ave耻ò䃲;槁Ābmⶈ෴ar;榵Ȁacitⶕ⶘ⶥⶨrò᪀Āir⶝ⶠr;榾oss;榻nå๒;槀ƀaeiⶱⶵⶹcr;䅍ga;䏉ƀcdnⷀⷅǍron;䎿;榶pf;쀀𝕠ƀaelⷔ⷗ǒr;榷rp;榹΀;adiosvⷪⷫⷮ⸈⸍⸐⸖戨rò᪆Ȁ;efmⷷⷸ⸂⸅橝rĀ;oⷾⷿ愴f»ⷿ耻ª䂪耻º䂺gof;抶r;橖lope;橗;橛ƀclo⸟⸡⸧ò⸁ash耻ø䃸l;折iŬⸯ⸴de耻õ䃵esĀ;aǛ⸺s;樶ml耻ö䃶bar;挽ૡ⹞\0⹽\0⺀⺝\0⺢⺹\0\0⻋ຜ\0⼓\0\0⼫⾼\0⿈rȀ;astЃ⹧⹲຅脀¶;l⹭⹮䂶leìЃɩ⹸\0\0⹻m;櫳;櫽y;䐿rʀcimpt⺋⺏⺓ᡥ⺗nt;䀥od;䀮il;怰enk;怱r;쀀𝔭ƀimo⺨⺰⺴Ā;v⺭⺮䏆;䏕maô੶ne;明ƀ;tv⺿⻀⻈䏀chfork»´;䏖Āau⻏⻟nĀck⻕⻝kĀ;h⇴⻛;愎ö⇴sҀ;abcdemst⻳⻴ᤈ⻹⻽⼄⼆⼊⼎䀫cir;樣ir;樢Āouᵀ⼂;樥;橲n肻±ຝim;樦wo;樧ƀipu⼙⼠⼥ntint;樕f;쀀𝕡nd耻£䂣Ԁ;Eaceinosu່⼿⽁⽄⽇⾁⾉⾒⽾⾶;檳p;檷uå໙Ā;c໎⽌̀;acens່⽙⽟⽦⽨⽾pproø⽃urlyeñ໙ñ໎ƀaes⽯⽶⽺pprox;檹qq;檵im;拨iíໟmeĀ;s⾈ຮ怲ƀEas⽸⾐⽺ð⽵ƀdfp໬⾙⾯ƀals⾠⾥⾪lar;挮ine;挒urf;挓Ā;t໻⾴ï໻rel;抰Āci⿀⿅r;쀀𝓅;䏈ncsp;怈̀fiopsu⿚⋢⿟⿥⿫⿱r;쀀𝔮pf;쀀𝕢rime;恗cr;쀀𝓆ƀaeo⿸〉〓tĀei⿾々rnionóڰnt;樖stĀ;e【】䀿ñἙô༔઀ABHabcdefhilmnoprstux぀けさすムㄎㄫㅇㅢㅲㆎ㈆㈕㈤㈩㉘㉮㉲㊐㊰㊷ƀartぇおがròႳòϝail;検aròᱥar;楤΀cdenqrtとふへみわゔヌĀeuねぱ;쀀∽̱te;䅕iãᅮmptyv;榳gȀ;del࿑らるろ;榒;榥å࿑uo耻»䂻rր;abcfhlpstw࿜ガクシスゼゾダッデナp;極Ā;f࿠ゴs;椠;椳s;椞ë≝ð✮l;楅im;楴l;憣;憝Āaiパフil;椚oĀ;nホボ戶aló༞ƀabrョリヮrò៥rk;杳ĀakンヽcĀekヹ・;䁽;䁝Āes㄂㄄;榌lĀduㄊㄌ;榎;榐Ȁaeuyㄗㄜㄧㄩron;䅙Ādiㄡㄥil;䅗ì࿲âヺ;䑀Ȁclqsㄴㄷㄽㅄa;椷dhar;楩uoĀ;rȎȍh;憳ƀacgㅎㅟངlȀ;ipsླྀㅘㅛႜnåႻarôྩt;断ƀilrㅩဣㅮsht;楽;쀀𝔯ĀaoㅷㆆrĀduㅽㅿ»ѻĀ;l႑ㆄ;楬Ā;vㆋㆌ䏁;䏱ƀgns㆕ㇹㇼht̀ahlrstㆤㆰ㇂㇘㇤㇮rrowĀ;t࿜ㆭaéトarpoonĀduㆻㆿowîㅾp»႒eftĀah㇊㇐rrowó࿪arpoonóՑightarrows;應quigarro÷ニhreetimes;拌g;䋚ingdotseñἲƀahm㈍㈐㈓rò࿪aòՑ;怏oustĀ;a㈞㈟掱che»㈟mid;櫮Ȁabpt㈲㈽㉀㉒Ānr㈷㈺g;柭r;懾rëဃƀafl㉇㉊㉎r;榆;쀀𝕣us;樮imes;樵Āap㉝㉧rĀ;g㉣㉤䀩t;榔olint;樒arò㇣Ȁachq㉻㊀Ⴜ㊅quo;怺r;쀀𝓇Ābu・㊊oĀ;rȔȓƀhir㊗㊛㊠reåㇸmes;拊iȀ;efl㊪ၙᠡ㊫方tri;槎luhar;楨;愞ൡ㋕㋛㋟㌬㌸㍱\0㍺㎤\0\0㏬㏰\0㐨㑈㑚㒭㒱㓊㓱\0㘖\0\0㘳cute;䅛quï➺Ԁ;Eaceinpsyᇭ㋳㋵㋿㌂㌋㌏㌟㌦㌩;檴ǰ㋺\0㋼;檸on;䅡uåᇾĀ;dᇳ㌇il;䅟rc;䅝ƀEas㌖㌘㌛;檶p;檺im;择olint;樓iíሄ;䑁otƀ;be㌴ᵇ㌵担;橦΀Aacmstx㍆㍊㍗㍛㍞㍣㍭rr;懘rĀhr㍐㍒ë∨Ā;oਸ਼਴t耻§䂧i;䀻war;椩mĀin㍩ðnuóñt;朶rĀ;o㍶⁕쀀𝔰Ȁacoy㎂㎆㎑㎠rp;景Āhy㎋㎏cy;䑉;䑈rtɭ㎙\0\0㎜iäᑤaraì⹯耻­䂭Āgm㎨㎴maƀ;fv㎱㎲㎲䏃;䏂Ѐ;deglnprካ㏅㏉㏎㏖㏞㏡㏦ot;橪Ā;q኱ኰĀ;E㏓㏔檞;檠Ā;E㏛㏜檝;檟e;扆lus;樤arr;楲aròᄽȀaeit㏸㐈㐏㐗Āls㏽㐄lsetmé㍪hp;樳parsl;槤Ādlᑣ㐔e;挣Ā;e㐜㐝檪Ā;s㐢㐣檬;쀀⪬︀ƀflp㐮㐳㑂tcy;䑌Ā;b㐸㐹䀯Ā;a㐾㐿槄r;挿f;쀀𝕤aĀdr㑍ЂesĀ;u㑔㑕晠it»㑕ƀcsu㑠㑹㒟Āau㑥㑯pĀ;sᆈ㑫;쀀⊓︀pĀ;sᆴ㑵;쀀⊔︀uĀbp㑿㒏ƀ;esᆗᆜ㒆etĀ;eᆗ㒍ñᆝƀ;esᆨᆭ㒖etĀ;eᆨ㒝ñᆮƀ;afᅻ㒦ְrť㒫ֱ»ᅼaròᅈȀcemt㒹㒾㓂㓅r;쀀𝓈tmîñiì㐕aræᆾĀar㓎㓕rĀ;f㓔ឿ昆Āan㓚㓭ightĀep㓣㓪psiloîỠhé⺯s»⡒ʀbcmnp㓻㕞ሉ㖋㖎Ҁ;Edemnprs㔎㔏㔑㔕㔞㔣㔬㔱㔶抂;櫅ot;檽Ā;dᇚ㔚ot;櫃ult;櫁ĀEe㔨㔪;櫋;把lus;檿arr;楹ƀeiu㔽㕒㕕tƀ;en㔎㕅㕋qĀ;qᇚ㔏eqĀ;q㔫㔨m;櫇Ābp㕚㕜;櫕;櫓c̀;acensᇭ㕬㕲㕹㕻㌦pproø㋺urlyeñᇾñᇳƀaes㖂㖈㌛pproø㌚qñ㌗g;晪ڀ123;Edehlmnps㖩㖬㖯ሜ㖲㖴㗀㗉㗕㗚㗟㗨㗭耻¹䂹耻²䂲耻³䂳;櫆Āos㖹㖼t;檾ub;櫘Ā;dሢ㗅ot;櫄sĀou㗏㗒l;柉b;櫗arr;楻ult;櫂ĀEe㗤㗦;櫌;抋lus;櫀ƀeiu㗴㘉㘌tƀ;enሜ㗼㘂qĀ;qሢ㖲eqĀ;q㗧㗤m;櫈Ābp㘑㘓;櫔;櫖ƀAan㘜㘠㘭rr;懙rĀhr㘦㘨ë∮Ā;oਫ਩war;椪lig耻ß䃟௡㙑㙝㙠ዎ㙳㙹\0㙾㛂\0\0\0\0\0㛛㜃\0㜉㝬\0\0\0㞇ɲ㙖\0\0㙛get;挖;䏄rë๟ƀaey㙦㙫㙰ron;䅥dil;䅣;䑂lrec;挕r;쀀𝔱Ȁeiko㚆㚝㚵㚼ǲ㚋\0㚑eĀ4fኄኁaƀ;sv㚘㚙㚛䎸ym;䏑Ācn㚢㚲kĀas㚨㚮pproø዁im»ኬsðኞĀas㚺㚮ð዁rn耻þ䃾Ǭ̟㛆⋧es膀×;bd㛏㛐㛘䃗Ā;aᤏ㛕r;樱;樰ƀeps㛡㛣㜀á⩍Ȁ;bcf҆㛬㛰㛴ot;挶ir;櫱Ā;o㛹㛼쀀𝕥rk;櫚á㍢rime;怴ƀaip㜏㜒㝤dåቈ΀adempst㜡㝍㝀㝑㝗㝜㝟ngleʀ;dlqr㜰㜱㜶㝀㝂斵own»ᶻeftĀ;e⠀㜾ñम;扜ightĀ;e㊪㝋ñၚot;旬inus;樺lus;樹b;槍ime;樻ezium;揢ƀcht㝲㝽㞁Āry㝷㝻;쀀𝓉;䑆cy;䑛rok;䅧Āio㞋㞎xô᝷headĀlr㞗㞠eftarro÷ࡏightarrow»ཝऀAHabcdfghlmoprstuw㟐㟓㟗㟤㟰㟼㠎㠜㠣㠴㡑㡝㡫㢩㣌㣒㣪㣶ròϭar;楣Ācr㟜㟢ute耻ú䃺òᅐrǣ㟪\0㟭y;䑞ve;䅭Āiy㟵㟺rc耻û䃻;䑃ƀabh㠃㠆㠋ròᎭlac;䅱aòᏃĀir㠓㠘sht;楾;쀀𝔲rave耻ù䃹š㠧㠱rĀlr㠬㠮»ॗ»ႃlk;斀Āct㠹㡍ɯ㠿\0\0㡊rnĀ;e㡅㡆挜r»㡆op;挏ri;旸Āal㡖㡚cr;䅫肻¨͉Āgp㡢㡦on;䅳f;쀀𝕦̀adhlsuᅋ㡸㡽፲㢑㢠ownáᎳarpoonĀlr㢈㢌efô㠭ighô㠯iƀ;hl㢙㢚㢜䏅»ᏺon»㢚parrows;懈ƀcit㢰㣄㣈ɯ㢶\0\0㣁rnĀ;e㢼㢽挝r»㢽op;挎ng;䅯ri;旹cr;쀀𝓊ƀdir㣙㣝㣢ot;拰lde;䅩iĀ;f㜰㣨»᠓Āam㣯㣲rò㢨l耻ü䃼angle;榧ހABDacdeflnoprsz㤜㤟㤩㤭㦵㦸㦽㧟㧤㧨㧳㧹㧽㨁㨠ròϷarĀ;v㤦㤧櫨;櫩asèϡĀnr㤲㤷grt;榜΀eknprst㓣㥆㥋㥒㥝㥤㦖appá␕othinçẖƀhir㓫⻈㥙opô⾵Ā;hᎷ㥢ïㆍĀiu㥩㥭gmá㎳Ābp㥲㦄setneqĀ;q㥽㦀쀀⊊︀;쀀⫋︀setneqĀ;q㦏㦒쀀⊋︀;쀀⫌︀Āhr㦛㦟etá㚜iangleĀlr㦪㦯eft»थight»ၑy;䐲ash»ံƀelr㧄㧒㧗ƀ;beⷪ㧋㧏ar;抻q;扚lip;拮Ābt㧜ᑨaòᑩr;쀀𝔳tré㦮suĀbp㧯㧱»ജ»൙pf;쀀𝕧roð໻tré㦴Ācu㨆㨋r;쀀𝓋Ābp㨐㨘nĀEe㦀㨖»㥾nĀEe㦒㨞»㦐igzag;榚΀cefoprs㨶㨻㩖㩛㩔㩡㩪irc;䅵Ādi㩀㩑Ābg㩅㩉ar;機eĀ;qᗺ㩏;扙erp;愘r;쀀𝔴pf;쀀𝕨Ā;eᑹ㩦atèᑹcr;쀀𝓌ૣណ㪇\0㪋\0㪐㪛\0\0㪝㪨㪫㪯\0\0㫃㫎\0㫘ៜ៟tré៑r;쀀𝔵ĀAa㪔㪗ròσrò৶;䎾ĀAa㪡㪤ròθrò৫að✓is;拻ƀdptឤ㪵㪾Āfl㪺ឩ;쀀𝕩imåឲĀAa㫇㫊ròώròਁĀcq㫒ីr;쀀𝓍Āpt៖㫜ré។Ѐacefiosu㫰㫽㬈㬌㬑㬕㬛㬡cĀuy㫶㫻te耻ý䃽;䑏Āiy㬂㬆rc;䅷;䑋n耻¥䂥r;쀀𝔶cy;䑗pf;쀀𝕪cr;쀀𝓎Ācm㬦㬩y;䑎l耻ÿ䃿Ԁacdefhiosw㭂㭈㭔㭘㭤㭩㭭㭴㭺㮀cute;䅺Āay㭍㭒ron;䅾;䐷ot;䅼Āet㭝㭡træᕟa;䎶r;쀀𝔷cy;䐶grarr;懝pf;쀀𝕫cr;쀀𝓏Ājn㮅㮇;怍j;怌".split("").map((e) => e.charCodeAt(0))), ut = /* @__PURE__ */ new Map([
	[0, 65533],
	[128, 8364],
	[130, 8218],
	[131, 402],
	[132, 8222],
	[133, 8230],
	[134, 8224],
	[135, 8225],
	[136, 710],
	[137, 8240],
	[138, 352],
	[139, 8249],
	[140, 338],
	[142, 381],
	[145, 8216],
	[146, 8217],
	[147, 8220],
	[148, 8221],
	[149, 8226],
	[150, 8211],
	[151, 8212],
	[152, 732],
	[153, 8482],
	[154, 353],
	[155, 8250],
	[156, 339],
	[158, 382],
	[159, 376]
]);
function dt(e) {
	return e >= 55296 && e <= 57343 || e > 1114111 ? 65533 : ut.get(e) ?? e;
}
var D;
(function(e) {
	e[e.NUM = 35] = "NUM", e[e.SEMI = 59] = "SEMI", e[e.EQUALS = 61] = "EQUALS", e[e.ZERO = 48] = "ZERO", e[e.NINE = 57] = "NINE", e[e.LOWER_A = 97] = "LOWER_A", e[e.LOWER_F = 102] = "LOWER_F", e[e.LOWER_X = 120] = "LOWER_X", e[e.LOWER_Z = 122] = "LOWER_Z", e[e.UPPER_A = 65] = "UPPER_A", e[e.UPPER_F = 70] = "UPPER_F", e[e.UPPER_Z = 90] = "UPPER_Z";
})(D ||= {});
var ft = 32, O;
(function(e) {
	e[e.VALUE_LENGTH = 49152] = "VALUE_LENGTH", e[e.BRANCH_LENGTH = 16256] = "BRANCH_LENGTH", e[e.JUMP_TABLE = 127] = "JUMP_TABLE";
})(O ||= {});
function pt(e) {
	return e >= D.ZERO && e <= D.NINE;
}
function mt(e) {
	return e >= D.UPPER_A && e <= D.UPPER_F || e >= D.LOWER_A && e <= D.LOWER_F;
}
function ht(e) {
	return e >= D.UPPER_A && e <= D.UPPER_Z || e >= D.LOWER_A && e <= D.LOWER_Z || pt(e);
}
function gt(e) {
	return e === D.EQUALS || ht(e);
}
var k;
(function(e) {
	e[e.EntityStart = 0] = "EntityStart", e[e.NumericStart = 1] = "NumericStart", e[e.NumericDecimal = 2] = "NumericDecimal", e[e.NumericHex = 3] = "NumericHex", e[e.NamedEntity = 4] = "NamedEntity";
})(k ||= {});
var A;
(function(e) {
	e[e.Legacy = 0] = "Legacy", e[e.Strict = 1] = "Strict", e[e.Attribute = 2] = "Attribute";
})(A ||= {});
var _t = class {
	constructor(e, t, n) {
		this.decodeTree = e, this.emitCodePoint = t, this.errors = n, this.state = k.EntityStart, this.consumed = 1, this.result = 0, this.treeIndex = 0, this.excess = 1, this.decodeMode = A.Strict;
	}
	startEntity(e) {
		this.decodeMode = e, this.state = k.EntityStart, this.result = 0, this.treeIndex = 0, this.excess = 1, this.consumed = 1;
	}
	write(e, t) {
		switch (this.state) {
			case k.EntityStart: return e.charCodeAt(t) === D.NUM ? (this.state = k.NumericStart, this.consumed += 1, this.stateNumericStart(e, t + 1)) : (this.state = k.NamedEntity, this.stateNamedEntity(e, t));
			case k.NumericStart: return this.stateNumericStart(e, t);
			case k.NumericDecimal: return this.stateNumericDecimal(e, t);
			case k.NumericHex: return this.stateNumericHex(e, t);
			case k.NamedEntity: return this.stateNamedEntity(e, t);
		}
	}
	stateNumericStart(e, t) {
		return t >= e.length ? -1 : (e.charCodeAt(t) | ft) === D.LOWER_X ? (this.state = k.NumericHex, this.consumed += 1, this.stateNumericHex(e, t + 1)) : (this.state = k.NumericDecimal, this.stateNumericDecimal(e, t));
	}
	addToNumericResult(e, t, n, r) {
		if (t !== n) {
			let i = n - t;
			this.result = this.result * r ** +i + Number.parseInt(e.substr(t, i), r), this.consumed += i;
		}
	}
	stateNumericHex(e, t) {
		let n = t;
		for (; t < e.length;) {
			let r = e.charCodeAt(t);
			if (pt(r) || mt(r)) t += 1;
			else return this.addToNumericResult(e, n, t, 16), this.emitNumericEntity(r, 3);
		}
		return this.addToNumericResult(e, n, t, 16), -1;
	}
	stateNumericDecimal(e, t) {
		let n = t;
		for (; t < e.length;) {
			let r = e.charCodeAt(t);
			if (pt(r)) t += 1;
			else return this.addToNumericResult(e, n, t, 10), this.emitNumericEntity(r, 2);
		}
		return this.addToNumericResult(e, n, t, 10), -1;
	}
	emitNumericEntity(e, t) {
		var n;
		if (this.consumed <= t) return (n = this.errors) == null || n.absenceOfDigitsInNumericCharacterReference(this.consumed), 0;
		if (e === D.SEMI) this.consumed += 1;
		else if (this.decodeMode === A.Strict) return 0;
		return this.emitCodePoint(dt(this.result), this.consumed), this.errors && (e !== D.SEMI && this.errors.missingSemicolonAfterCharacterReference(), this.errors.validateNumericCharacterReference(this.result)), this.consumed;
	}
	stateNamedEntity(e, t) {
		let { decodeTree: n } = this, r = n[this.treeIndex], i = (r & O.VALUE_LENGTH) >> 14;
		for (; t < e.length; t++, this.excess++) {
			let a = e.charCodeAt(t);
			if (this.treeIndex = vt(n, r, this.treeIndex + Math.max(1, i), a), this.treeIndex < 0) return this.result === 0 || this.decodeMode === A.Attribute && (i === 0 || gt(a)) ? 0 : this.emitNotTerminatedNamedEntity();
			if (r = n[this.treeIndex], i = (r & O.VALUE_LENGTH) >> 14, i !== 0) {
				if (a === D.SEMI) return this.emitNamedEntityData(this.treeIndex, i, this.consumed + this.excess);
				this.decodeMode !== A.Strict && (this.result = this.treeIndex, this.consumed += this.excess, this.excess = 0);
			}
		}
		return -1;
	}
	emitNotTerminatedNamedEntity() {
		var e;
		let { result: t, decodeTree: n } = this, r = (n[t] & O.VALUE_LENGTH) >> 14;
		return this.emitNamedEntityData(t, r, this.consumed), (e = this.errors) == null || e.missingSemicolonAfterCharacterReference(), this.consumed;
	}
	emitNamedEntityData(e, t, n) {
		let { decodeTree: r } = this;
		return this.emitCodePoint(t === 1 ? r[e] & ~O.VALUE_LENGTH : r[e + 1], n), t === 3 && this.emitCodePoint(r[e + 2], n), n;
	}
	end() {
		var e;
		switch (this.state) {
			case k.NamedEntity: return this.result !== 0 && (this.decodeMode !== A.Attribute || this.result === this.treeIndex) ? this.emitNotTerminatedNamedEntity() : 0;
			case k.NumericDecimal: return this.emitNumericEntity(0, 2);
			case k.NumericHex: return this.emitNumericEntity(0, 3);
			case k.NumericStart: return (e = this.errors) == null || e.absenceOfDigitsInNumericCharacterReference(this.consumed), 0;
			case k.EntityStart: return 0;
		}
	}
};
function vt(e, t, n, r) {
	let i = (t & O.BRANCH_LENGTH) >> 7, a = t & O.JUMP_TABLE;
	if (i === 0) return a !== 0 && r === a ? n : -1;
	if (a) {
		let t = r - a;
		return t < 0 || t >= i ? -1 : e[n + t] - 1;
	}
	let o = n, s = o + i - 1;
	for (; o <= s;) {
		let t = o + s >>> 1, n = e[t];
		if (n < r) o = t + 1;
		else if (n > r) s = t - 1;
		else return e[t + i];
	}
	return -1;
}
var j;
(function(e) {
	e.HTML = "http://www.w3.org/1999/xhtml", e.MATHML = "http://www.w3.org/1998/Math/MathML", e.SVG = "http://www.w3.org/2000/svg", e.XLINK = "http://www.w3.org/1999/xlink", e.XML = "http://www.w3.org/XML/1998/namespace", e.XMLNS = "http://www.w3.org/2000/xmlns/";
})(j ||= {});
var M;
(function(e) {
	e.TYPE = "type", e.ACTION = "action", e.ENCODING = "encoding", e.PROMPT = "prompt", e.NAME = "name", e.COLOR = "color", e.FACE = "face", e.SIZE = "size";
})(M ||= {});
var N;
(function(e) {
	e.NO_QUIRKS = "no-quirks", e.QUIRKS = "quirks", e.LIMITED_QUIRKS = "limited-quirks";
})(N ||= {});
var P;
(function(e) {
	e.A = "a", e.ADDRESS = "address", e.ANNOTATION_XML = "annotation-xml", e.APPLET = "applet", e.AREA = "area", e.ARTICLE = "article", e.ASIDE = "aside", e.B = "b", e.BASE = "base", e.BASEFONT = "basefont", e.BGSOUND = "bgsound", e.BIG = "big", e.BLOCKQUOTE = "blockquote", e.BODY = "body", e.BR = "br", e.BUTTON = "button", e.CAPTION = "caption", e.CENTER = "center", e.CODE = "code", e.COL = "col", e.COLGROUP = "colgroup", e.DD = "dd", e.DESC = "desc", e.DETAILS = "details", e.DIALOG = "dialog", e.DIR = "dir", e.DIV = "div", e.DL = "dl", e.DT = "dt", e.EM = "em", e.EMBED = "embed", e.FIELDSET = "fieldset", e.FIGCAPTION = "figcaption", e.FIGURE = "figure", e.FONT = "font", e.FOOTER = "footer", e.FOREIGN_OBJECT = "foreignObject", e.FORM = "form", e.FRAME = "frame", e.FRAMESET = "frameset", e.H1 = "h1", e.H2 = "h2", e.H3 = "h3", e.H4 = "h4", e.H5 = "h5", e.H6 = "h6", e.HEAD = "head", e.HEADER = "header", e.HGROUP = "hgroup", e.HR = "hr", e.HTML = "html", e.I = "i", e.IMG = "img", e.IMAGE = "image", e.INPUT = "input", e.IFRAME = "iframe", e.KEYGEN = "keygen", e.LABEL = "label", e.LI = "li", e.LINK = "link", e.LISTING = "listing", e.MAIN = "main", e.MALIGNMARK = "malignmark", e.MARQUEE = "marquee", e.MATH = "math", e.MENU = "menu", e.META = "meta", e.MGLYPH = "mglyph", e.MI = "mi", e.MO = "mo", e.MN = "mn", e.MS = "ms", e.MTEXT = "mtext", e.NAV = "nav", e.NOBR = "nobr", e.NOFRAMES = "noframes", e.NOEMBED = "noembed", e.NOSCRIPT = "noscript", e.OBJECT = "object", e.OL = "ol", e.OPTGROUP = "optgroup", e.OPTION = "option", e.P = "p", e.PARAM = "param", e.PLAINTEXT = "plaintext", e.PRE = "pre", e.RB = "rb", e.RP = "rp", e.RT = "rt", e.RTC = "rtc", e.RUBY = "ruby", e.S = "s", e.SCRIPT = "script", e.SEARCH = "search", e.SECTION = "section", e.SELECT = "select", e.SOURCE = "source", e.SMALL = "small", e.SPAN = "span", e.STRIKE = "strike", e.STRONG = "strong", e.STYLE = "style", e.SUB = "sub", e.SUMMARY = "summary", e.SUP = "sup", e.TABLE = "table", e.TBODY = "tbody", e.TEMPLATE = "template", e.TEXTAREA = "textarea", e.TFOOT = "tfoot", e.TD = "td", e.TH = "th", e.THEAD = "thead", e.TITLE = "title", e.TR = "tr", e.TRACK = "track", e.TT = "tt", e.U = "u", e.UL = "ul", e.SVG = "svg", e.VAR = "var", e.WBR = "wbr", e.XMP = "xmp";
})(P ||= {});
var F;
(function(e) {
	e[e.UNKNOWN = 0] = "UNKNOWN", e[e.A = 1] = "A", e[e.ADDRESS = 2] = "ADDRESS", e[e.ANNOTATION_XML = 3] = "ANNOTATION_XML", e[e.APPLET = 4] = "APPLET", e[e.AREA = 5] = "AREA", e[e.ARTICLE = 6] = "ARTICLE", e[e.ASIDE = 7] = "ASIDE", e[e.B = 8] = "B", e[e.BASE = 9] = "BASE", e[e.BASEFONT = 10] = "BASEFONT", e[e.BGSOUND = 11] = "BGSOUND", e[e.BIG = 12] = "BIG", e[e.BLOCKQUOTE = 13] = "BLOCKQUOTE", e[e.BODY = 14] = "BODY", e[e.BR = 15] = "BR", e[e.BUTTON = 16] = "BUTTON", e[e.CAPTION = 17] = "CAPTION", e[e.CENTER = 18] = "CENTER", e[e.CODE = 19] = "CODE", e[e.COL = 20] = "COL", e[e.COLGROUP = 21] = "COLGROUP", e[e.DD = 22] = "DD", e[e.DESC = 23] = "DESC", e[e.DETAILS = 24] = "DETAILS", e[e.DIALOG = 25] = "DIALOG", e[e.DIR = 26] = "DIR", e[e.DIV = 27] = "DIV", e[e.DL = 28] = "DL", e[e.DT = 29] = "DT", e[e.EM = 30] = "EM", e[e.EMBED = 31] = "EMBED", e[e.FIELDSET = 32] = "FIELDSET", e[e.FIGCAPTION = 33] = "FIGCAPTION", e[e.FIGURE = 34] = "FIGURE", e[e.FONT = 35] = "FONT", e[e.FOOTER = 36] = "FOOTER", e[e.FOREIGN_OBJECT = 37] = "FOREIGN_OBJECT", e[e.FORM = 38] = "FORM", e[e.FRAME = 39] = "FRAME", e[e.FRAMESET = 40] = "FRAMESET", e[e.H1 = 41] = "H1", e[e.H2 = 42] = "H2", e[e.H3 = 43] = "H3", e[e.H4 = 44] = "H4", e[e.H5 = 45] = "H5", e[e.H6 = 46] = "H6", e[e.HEAD = 47] = "HEAD", e[e.HEADER = 48] = "HEADER", e[e.HGROUP = 49] = "HGROUP", e[e.HR = 50] = "HR", e[e.HTML = 51] = "HTML", e[e.I = 52] = "I", e[e.IMG = 53] = "IMG", e[e.IMAGE = 54] = "IMAGE", e[e.INPUT = 55] = "INPUT", e[e.IFRAME = 56] = "IFRAME", e[e.KEYGEN = 57] = "KEYGEN", e[e.LABEL = 58] = "LABEL", e[e.LI = 59] = "LI", e[e.LINK = 60] = "LINK", e[e.LISTING = 61] = "LISTING", e[e.MAIN = 62] = "MAIN", e[e.MALIGNMARK = 63] = "MALIGNMARK", e[e.MARQUEE = 64] = "MARQUEE", e[e.MATH = 65] = "MATH", e[e.MENU = 66] = "MENU", e[e.META = 67] = "META", e[e.MGLYPH = 68] = "MGLYPH", e[e.MI = 69] = "MI", e[e.MO = 70] = "MO", e[e.MN = 71] = "MN", e[e.MS = 72] = "MS", e[e.MTEXT = 73] = "MTEXT", e[e.NAV = 74] = "NAV", e[e.NOBR = 75] = "NOBR", e[e.NOFRAMES = 76] = "NOFRAMES", e[e.NOEMBED = 77] = "NOEMBED", e[e.NOSCRIPT = 78] = "NOSCRIPT", e[e.OBJECT = 79] = "OBJECT", e[e.OL = 80] = "OL", e[e.OPTGROUP = 81] = "OPTGROUP", e[e.OPTION = 82] = "OPTION", e[e.P = 83] = "P", e[e.PARAM = 84] = "PARAM", e[e.PLAINTEXT = 85] = "PLAINTEXT", e[e.PRE = 86] = "PRE", e[e.RB = 87] = "RB", e[e.RP = 88] = "RP", e[e.RT = 89] = "RT", e[e.RTC = 90] = "RTC", e[e.RUBY = 91] = "RUBY", e[e.S = 92] = "S", e[e.SCRIPT = 93] = "SCRIPT", e[e.SEARCH = 94] = "SEARCH", e[e.SECTION = 95] = "SECTION", e[e.SELECT = 96] = "SELECT", e[e.SOURCE = 97] = "SOURCE", e[e.SMALL = 98] = "SMALL", e[e.SPAN = 99] = "SPAN", e[e.STRIKE = 100] = "STRIKE", e[e.STRONG = 101] = "STRONG", e[e.STYLE = 102] = "STYLE", e[e.SUB = 103] = "SUB", e[e.SUMMARY = 104] = "SUMMARY", e[e.SUP = 105] = "SUP", e[e.TABLE = 106] = "TABLE", e[e.TBODY = 107] = "TBODY", e[e.TEMPLATE = 108] = "TEMPLATE", e[e.TEXTAREA = 109] = "TEXTAREA", e[e.TFOOT = 110] = "TFOOT", e[e.TD = 111] = "TD", e[e.TH = 112] = "TH", e[e.THEAD = 113] = "THEAD", e[e.TITLE = 114] = "TITLE", e[e.TR = 115] = "TR", e[e.TRACK = 116] = "TRACK", e[e.TT = 117] = "TT", e[e.U = 118] = "U", e[e.UL = 119] = "UL", e[e.SVG = 120] = "SVG", e[e.VAR = 121] = "VAR", e[e.WBR = 122] = "WBR", e[e.XMP = 123] = "XMP";
})(F ||= {});
var yt = /* @__PURE__ */ new Map([
	[P.A, F.A],
	[P.ADDRESS, F.ADDRESS],
	[P.ANNOTATION_XML, F.ANNOTATION_XML],
	[P.APPLET, F.APPLET],
	[P.AREA, F.AREA],
	[P.ARTICLE, F.ARTICLE],
	[P.ASIDE, F.ASIDE],
	[P.B, F.B],
	[P.BASE, F.BASE],
	[P.BASEFONT, F.BASEFONT],
	[P.BGSOUND, F.BGSOUND],
	[P.BIG, F.BIG],
	[P.BLOCKQUOTE, F.BLOCKQUOTE],
	[P.BODY, F.BODY],
	[P.BR, F.BR],
	[P.BUTTON, F.BUTTON],
	[P.CAPTION, F.CAPTION],
	[P.CENTER, F.CENTER],
	[P.CODE, F.CODE],
	[P.COL, F.COL],
	[P.COLGROUP, F.COLGROUP],
	[P.DD, F.DD],
	[P.DESC, F.DESC],
	[P.DETAILS, F.DETAILS],
	[P.DIALOG, F.DIALOG],
	[P.DIR, F.DIR],
	[P.DIV, F.DIV],
	[P.DL, F.DL],
	[P.DT, F.DT],
	[P.EM, F.EM],
	[P.EMBED, F.EMBED],
	[P.FIELDSET, F.FIELDSET],
	[P.FIGCAPTION, F.FIGCAPTION],
	[P.FIGURE, F.FIGURE],
	[P.FONT, F.FONT],
	[P.FOOTER, F.FOOTER],
	[P.FOREIGN_OBJECT, F.FOREIGN_OBJECT],
	[P.FORM, F.FORM],
	[P.FRAME, F.FRAME],
	[P.FRAMESET, F.FRAMESET],
	[P.H1, F.H1],
	[P.H2, F.H2],
	[P.H3, F.H3],
	[P.H4, F.H4],
	[P.H5, F.H5],
	[P.H6, F.H6],
	[P.HEAD, F.HEAD],
	[P.HEADER, F.HEADER],
	[P.HGROUP, F.HGROUP],
	[P.HR, F.HR],
	[P.HTML, F.HTML],
	[P.I, F.I],
	[P.IMG, F.IMG],
	[P.IMAGE, F.IMAGE],
	[P.INPUT, F.INPUT],
	[P.IFRAME, F.IFRAME],
	[P.KEYGEN, F.KEYGEN],
	[P.LABEL, F.LABEL],
	[P.LI, F.LI],
	[P.LINK, F.LINK],
	[P.LISTING, F.LISTING],
	[P.MAIN, F.MAIN],
	[P.MALIGNMARK, F.MALIGNMARK],
	[P.MARQUEE, F.MARQUEE],
	[P.MATH, F.MATH],
	[P.MENU, F.MENU],
	[P.META, F.META],
	[P.MGLYPH, F.MGLYPH],
	[P.MI, F.MI],
	[P.MO, F.MO],
	[P.MN, F.MN],
	[P.MS, F.MS],
	[P.MTEXT, F.MTEXT],
	[P.NAV, F.NAV],
	[P.NOBR, F.NOBR],
	[P.NOFRAMES, F.NOFRAMES],
	[P.NOEMBED, F.NOEMBED],
	[P.NOSCRIPT, F.NOSCRIPT],
	[P.OBJECT, F.OBJECT],
	[P.OL, F.OL],
	[P.OPTGROUP, F.OPTGROUP],
	[P.OPTION, F.OPTION],
	[P.P, F.P],
	[P.PARAM, F.PARAM],
	[P.PLAINTEXT, F.PLAINTEXT],
	[P.PRE, F.PRE],
	[P.RB, F.RB],
	[P.RP, F.RP],
	[P.RT, F.RT],
	[P.RTC, F.RTC],
	[P.RUBY, F.RUBY],
	[P.S, F.S],
	[P.SCRIPT, F.SCRIPT],
	[P.SEARCH, F.SEARCH],
	[P.SECTION, F.SECTION],
	[P.SELECT, F.SELECT],
	[P.SOURCE, F.SOURCE],
	[P.SMALL, F.SMALL],
	[P.SPAN, F.SPAN],
	[P.STRIKE, F.STRIKE],
	[P.STRONG, F.STRONG],
	[P.STYLE, F.STYLE],
	[P.SUB, F.SUB],
	[P.SUMMARY, F.SUMMARY],
	[P.SUP, F.SUP],
	[P.TABLE, F.TABLE],
	[P.TBODY, F.TBODY],
	[P.TEMPLATE, F.TEMPLATE],
	[P.TEXTAREA, F.TEXTAREA],
	[P.TFOOT, F.TFOOT],
	[P.TD, F.TD],
	[P.TH, F.TH],
	[P.THEAD, F.THEAD],
	[P.TITLE, F.TITLE],
	[P.TR, F.TR],
	[P.TRACK, F.TRACK],
	[P.TT, F.TT],
	[P.U, F.U],
	[P.UL, F.UL],
	[P.SVG, F.SVG],
	[P.VAR, F.VAR],
	[P.WBR, F.WBR],
	[P.XMP, F.XMP]
]);
function I(e) {
	return yt.get(e) ?? F.UNKNOWN;
}
var L = F, bt = {
	[j.HTML]: /* @__PURE__ */ new Set([
		L.ADDRESS,
		L.APPLET,
		L.AREA,
		L.ARTICLE,
		L.ASIDE,
		L.BASE,
		L.BASEFONT,
		L.BGSOUND,
		L.BLOCKQUOTE,
		L.BODY,
		L.BR,
		L.BUTTON,
		L.CAPTION,
		L.CENTER,
		L.COL,
		L.COLGROUP,
		L.DD,
		L.DETAILS,
		L.DIR,
		L.DIV,
		L.DL,
		L.DT,
		L.EMBED,
		L.FIELDSET,
		L.FIGCAPTION,
		L.FIGURE,
		L.FOOTER,
		L.FORM,
		L.FRAME,
		L.FRAMESET,
		L.H1,
		L.H2,
		L.H3,
		L.H4,
		L.H5,
		L.H6,
		L.HEAD,
		L.HEADER,
		L.HGROUP,
		L.HR,
		L.HTML,
		L.IFRAME,
		L.IMG,
		L.INPUT,
		L.LI,
		L.LINK,
		L.LISTING,
		L.MAIN,
		L.MARQUEE,
		L.MENU,
		L.META,
		L.NAV,
		L.NOEMBED,
		L.NOFRAMES,
		L.NOSCRIPT,
		L.OBJECT,
		L.OL,
		L.P,
		L.PARAM,
		L.PLAINTEXT,
		L.PRE,
		L.SCRIPT,
		L.SECTION,
		L.SELECT,
		L.SOURCE,
		L.STYLE,
		L.SUMMARY,
		L.TABLE,
		L.TBODY,
		L.TD,
		L.TEMPLATE,
		L.TEXTAREA,
		L.TFOOT,
		L.TH,
		L.THEAD,
		L.TITLE,
		L.TR,
		L.TRACK,
		L.UL,
		L.WBR,
		L.XMP
	]),
	[j.MATHML]: /* @__PURE__ */ new Set([
		L.MI,
		L.MO,
		L.MN,
		L.MS,
		L.MTEXT,
		L.ANNOTATION_XML
	]),
	[j.SVG]: /* @__PURE__ */ new Set([
		L.TITLE,
		L.FOREIGN_OBJECT,
		L.DESC
	]),
	[j.XLINK]: /* @__PURE__ */ new Set(),
	[j.XML]: /* @__PURE__ */ new Set(),
	[j.XMLNS]: /* @__PURE__ */ new Set()
}, xt = /* @__PURE__ */ new Set([
	L.H1,
	L.H2,
	L.H3,
	L.H4,
	L.H5,
	L.H6
]);
P.STYLE, P.SCRIPT, P.XMP, P.IFRAME, P.NOEMBED, P.NOFRAMES, P.PLAINTEXT;
var R;
(function(e) {
	e[e.DATA = 0] = "DATA", e[e.RCDATA = 1] = "RCDATA", e[e.RAWTEXT = 2] = "RAWTEXT", e[e.SCRIPT_DATA = 3] = "SCRIPT_DATA", e[e.PLAINTEXT = 4] = "PLAINTEXT", e[e.TAG_OPEN = 5] = "TAG_OPEN", e[e.END_TAG_OPEN = 6] = "END_TAG_OPEN", e[e.TAG_NAME = 7] = "TAG_NAME", e[e.RCDATA_LESS_THAN_SIGN = 8] = "RCDATA_LESS_THAN_SIGN", e[e.RCDATA_END_TAG_OPEN = 9] = "RCDATA_END_TAG_OPEN", e[e.RCDATA_END_TAG_NAME = 10] = "RCDATA_END_TAG_NAME", e[e.RAWTEXT_LESS_THAN_SIGN = 11] = "RAWTEXT_LESS_THAN_SIGN", e[e.RAWTEXT_END_TAG_OPEN = 12] = "RAWTEXT_END_TAG_OPEN", e[e.RAWTEXT_END_TAG_NAME = 13] = "RAWTEXT_END_TAG_NAME", e[e.SCRIPT_DATA_LESS_THAN_SIGN = 14] = "SCRIPT_DATA_LESS_THAN_SIGN", e[e.SCRIPT_DATA_END_TAG_OPEN = 15] = "SCRIPT_DATA_END_TAG_OPEN", e[e.SCRIPT_DATA_END_TAG_NAME = 16] = "SCRIPT_DATA_END_TAG_NAME", e[e.SCRIPT_DATA_ESCAPE_START = 17] = "SCRIPT_DATA_ESCAPE_START", e[e.SCRIPT_DATA_ESCAPE_START_DASH = 18] = "SCRIPT_DATA_ESCAPE_START_DASH", e[e.SCRIPT_DATA_ESCAPED = 19] = "SCRIPT_DATA_ESCAPED", e[e.SCRIPT_DATA_ESCAPED_DASH = 20] = "SCRIPT_DATA_ESCAPED_DASH", e[e.SCRIPT_DATA_ESCAPED_DASH_DASH = 21] = "SCRIPT_DATA_ESCAPED_DASH_DASH", e[e.SCRIPT_DATA_ESCAPED_LESS_THAN_SIGN = 22] = "SCRIPT_DATA_ESCAPED_LESS_THAN_SIGN", e[e.SCRIPT_DATA_ESCAPED_END_TAG_OPEN = 23] = "SCRIPT_DATA_ESCAPED_END_TAG_OPEN", e[e.SCRIPT_DATA_ESCAPED_END_TAG_NAME = 24] = "SCRIPT_DATA_ESCAPED_END_TAG_NAME", e[e.SCRIPT_DATA_DOUBLE_ESCAPE_START = 25] = "SCRIPT_DATA_DOUBLE_ESCAPE_START", e[e.SCRIPT_DATA_DOUBLE_ESCAPED = 26] = "SCRIPT_DATA_DOUBLE_ESCAPED", e[e.SCRIPT_DATA_DOUBLE_ESCAPED_DASH = 27] = "SCRIPT_DATA_DOUBLE_ESCAPED_DASH", e[e.SCRIPT_DATA_DOUBLE_ESCAPED_DASH_DASH = 28] = "SCRIPT_DATA_DOUBLE_ESCAPED_DASH_DASH", e[e.SCRIPT_DATA_DOUBLE_ESCAPED_LESS_THAN_SIGN = 29] = "SCRIPT_DATA_DOUBLE_ESCAPED_LESS_THAN_SIGN", e[e.SCRIPT_DATA_DOUBLE_ESCAPE_END = 30] = "SCRIPT_DATA_DOUBLE_ESCAPE_END", e[e.BEFORE_ATTRIBUTE_NAME = 31] = "BEFORE_ATTRIBUTE_NAME", e[e.ATTRIBUTE_NAME = 32] = "ATTRIBUTE_NAME", e[e.AFTER_ATTRIBUTE_NAME = 33] = "AFTER_ATTRIBUTE_NAME", e[e.BEFORE_ATTRIBUTE_VALUE = 34] = "BEFORE_ATTRIBUTE_VALUE", e[e.ATTRIBUTE_VALUE_DOUBLE_QUOTED = 35] = "ATTRIBUTE_VALUE_DOUBLE_QUOTED", e[e.ATTRIBUTE_VALUE_SINGLE_QUOTED = 36] = "ATTRIBUTE_VALUE_SINGLE_QUOTED", e[e.ATTRIBUTE_VALUE_UNQUOTED = 37] = "ATTRIBUTE_VALUE_UNQUOTED", e[e.AFTER_ATTRIBUTE_VALUE_QUOTED = 38] = "AFTER_ATTRIBUTE_VALUE_QUOTED", e[e.SELF_CLOSING_START_TAG = 39] = "SELF_CLOSING_START_TAG", e[e.BOGUS_COMMENT = 40] = "BOGUS_COMMENT", e[e.MARKUP_DECLARATION_OPEN = 41] = "MARKUP_DECLARATION_OPEN", e[e.COMMENT_START = 42] = "COMMENT_START", e[e.COMMENT_START_DASH = 43] = "COMMENT_START_DASH", e[e.COMMENT = 44] = "COMMENT", e[e.COMMENT_LESS_THAN_SIGN = 45] = "COMMENT_LESS_THAN_SIGN", e[e.COMMENT_LESS_THAN_SIGN_BANG = 46] = "COMMENT_LESS_THAN_SIGN_BANG", e[e.COMMENT_LESS_THAN_SIGN_BANG_DASH = 47] = "COMMENT_LESS_THAN_SIGN_BANG_DASH", e[e.COMMENT_LESS_THAN_SIGN_BANG_DASH_DASH = 48] = "COMMENT_LESS_THAN_SIGN_BANG_DASH_DASH", e[e.COMMENT_END_DASH = 49] = "COMMENT_END_DASH", e[e.COMMENT_END = 50] = "COMMENT_END", e[e.COMMENT_END_BANG = 51] = "COMMENT_END_BANG", e[e.DOCTYPE = 52] = "DOCTYPE", e[e.BEFORE_DOCTYPE_NAME = 53] = "BEFORE_DOCTYPE_NAME", e[e.DOCTYPE_NAME = 54] = "DOCTYPE_NAME", e[e.AFTER_DOCTYPE_NAME = 55] = "AFTER_DOCTYPE_NAME", e[e.AFTER_DOCTYPE_PUBLIC_KEYWORD = 56] = "AFTER_DOCTYPE_PUBLIC_KEYWORD", e[e.BEFORE_DOCTYPE_PUBLIC_IDENTIFIER = 57] = "BEFORE_DOCTYPE_PUBLIC_IDENTIFIER", e[e.DOCTYPE_PUBLIC_IDENTIFIER_DOUBLE_QUOTED = 58] = "DOCTYPE_PUBLIC_IDENTIFIER_DOUBLE_QUOTED", e[e.DOCTYPE_PUBLIC_IDENTIFIER_SINGLE_QUOTED = 59] = "DOCTYPE_PUBLIC_IDENTIFIER_SINGLE_QUOTED", e[e.AFTER_DOCTYPE_PUBLIC_IDENTIFIER = 60] = "AFTER_DOCTYPE_PUBLIC_IDENTIFIER", e[e.BETWEEN_DOCTYPE_PUBLIC_AND_SYSTEM_IDENTIFIERS = 61] = "BETWEEN_DOCTYPE_PUBLIC_AND_SYSTEM_IDENTIFIERS", e[e.AFTER_DOCTYPE_SYSTEM_KEYWORD = 62] = "AFTER_DOCTYPE_SYSTEM_KEYWORD", e[e.BEFORE_DOCTYPE_SYSTEM_IDENTIFIER = 63] = "BEFORE_DOCTYPE_SYSTEM_IDENTIFIER", e[e.DOCTYPE_SYSTEM_IDENTIFIER_DOUBLE_QUOTED = 64] = "DOCTYPE_SYSTEM_IDENTIFIER_DOUBLE_QUOTED", e[e.DOCTYPE_SYSTEM_IDENTIFIER_SINGLE_QUOTED = 65] = "DOCTYPE_SYSTEM_IDENTIFIER_SINGLE_QUOTED", e[e.AFTER_DOCTYPE_SYSTEM_IDENTIFIER = 66] = "AFTER_DOCTYPE_SYSTEM_IDENTIFIER", e[e.BOGUS_DOCTYPE = 67] = "BOGUS_DOCTYPE", e[e.CDATA_SECTION = 68] = "CDATA_SECTION", e[e.CDATA_SECTION_BRACKET = 69] = "CDATA_SECTION_BRACKET", e[e.CDATA_SECTION_END = 70] = "CDATA_SECTION_END", e[e.CHARACTER_REFERENCE = 71] = "CHARACTER_REFERENCE", e[e.AMBIGUOUS_AMPERSAND = 72] = "AMBIGUOUS_AMPERSAND";
})(R ||= {});
var z = {
	DATA: R.DATA,
	RCDATA: R.RCDATA,
	RAWTEXT: R.RAWTEXT,
	SCRIPT_DATA: R.SCRIPT_DATA,
	PLAINTEXT: R.PLAINTEXT,
	CDATA_SECTION: R.CDATA_SECTION
};
function St(e) {
	return e >= C.DIGIT_0 && e <= C.DIGIT_9;
}
function B(e) {
	return e >= C.LATIN_CAPITAL_A && e <= C.LATIN_CAPITAL_Z;
}
function Ct(e) {
	return e >= C.LATIN_SMALL_A && e <= C.LATIN_SMALL_Z;
}
function V(e) {
	return Ct(e) || B(e);
}
function wt(e) {
	return V(e) || St(e);
}
function Tt(e) {
	return e + 32;
}
function Et(e) {
	return e === C.SPACE || e === C.LINE_FEED || e === C.TABULATION || e === C.FORM_FEED;
}
function Dt(e) {
	return Et(e) || e === C.SOLIDUS || e === C.GREATER_THAN_SIGN;
}
function Ot(e) {
	return e === C.NULL ? T.nullCharacterReference : e > 1114111 ? T.characterReferenceOutsideUnicodeRange : tt(e) ? T.surrogateCharacterReference : at(e) ? T.noncharacterCharacterReference : it(e) || e === C.CARRIAGE_RETURN ? T.controlCharacterReference : null;
}
var kt = class {
	constructor(e, t) {
		this.options = e, this.handler = t, this.paused = !1, this.inLoop = !1, this.inForeignNode = !1, this.lastStartTagName = "", this.active = !1, this.state = R.DATA, this.returnState = R.DATA, this.entityStartPos = 0, this.consumedAfterSnapshot = -1, this.currentCharacterToken = null, this.currentToken = null, this.currentAttr = {
			name: "",
			value: ""
		}, this.preprocessor = new st(t), this.currentLocation = this.getCurrentLocation(-1), this.entityDecoder = new _t(lt, (e, t) => {
			this.preprocessor.pos = this.entityStartPos + t - 1, this._flushCodePointConsumedAsCharacterReference(e);
		}, t.onParseError ? {
			missingSemicolonAfterCharacterReference: () => {
				this._err(T.missingSemicolonAfterCharacterReference, 1);
			},
			absenceOfDigitsInNumericCharacterReference: (e) => {
				this._err(T.absenceOfDigitsInNumericCharacterReference, this.entityStartPos - this.preprocessor.pos + e);
			},
			validateNumericCharacterReference: (e) => {
				let t = Ot(e);
				t && this._err(t, 1);
			}
		} : void 0);
	}
	_err(e, t = 0) {
		var n, r;
		(r = (n = this.handler).onParseError) == null || r.call(n, this.preprocessor.getError(e, t));
	}
	getCurrentLocation(e) {
		return this.options.sourceCodeLocationInfo ? {
			startLine: this.preprocessor.line,
			startCol: this.preprocessor.col - e,
			startOffset: this.preprocessor.offset - e,
			endLine: -1,
			endCol: -1,
			endOffset: -1
		} : null;
	}
	_runParsingLoop() {
		if (!this.inLoop) {
			for (this.inLoop = !0; this.active && !this.paused;) {
				this.consumedAfterSnapshot = 0;
				let e = this._consume();
				this._ensureHibernation() || this._callState(e);
			}
			this.inLoop = !1;
		}
	}
	pause() {
		this.paused = !0;
	}
	resume(e) {
		if (!this.paused) throw Error("Parser was already resumed");
		this.paused = !1, !this.inLoop && (this._runParsingLoop(), this.paused || e?.());
	}
	write(e, t, n) {
		this.active = !0, this.preprocessor.write(e, t), this._runParsingLoop(), this.paused || n?.();
	}
	insertHtmlAtCurrentPos(e) {
		this.active = !0, this.preprocessor.insertHtmlAtCurrentPos(e), this._runParsingLoop();
	}
	_ensureHibernation() {
		return this.preprocessor.endOfChunkHit ? (this.preprocessor.retreat(this.consumedAfterSnapshot), this.consumedAfterSnapshot = 0, this.active = !1, !0) : !1;
	}
	_consume() {
		return this.consumedAfterSnapshot++, this.preprocessor.advance();
	}
	_advanceBy(e) {
		this.consumedAfterSnapshot += e;
		for (let t = 0; t < e; t++) this.preprocessor.advance();
	}
	_consumeSequenceIfMatch(e, t) {
		return this.preprocessor.startsWith(e, t) ? (this._advanceBy(e.length - 1), !0) : !1;
	}
	_createStartTagToken() {
		this.currentToken = {
			type: E.START_TAG,
			tagName: "",
			tagID: F.UNKNOWN,
			selfClosing: !1,
			ackSelfClosing: !1,
			attrs: [],
			location: this.getCurrentLocation(1)
		};
	}
	_createEndTagToken() {
		this.currentToken = {
			type: E.END_TAG,
			tagName: "",
			tagID: F.UNKNOWN,
			selfClosing: !1,
			ackSelfClosing: !1,
			attrs: [],
			location: this.getCurrentLocation(2)
		};
	}
	_createCommentToken(e) {
		this.currentToken = {
			type: E.COMMENT,
			data: "",
			location: this.getCurrentLocation(e)
		};
	}
	_createDoctypeToken(e) {
		this.currentToken = {
			type: E.DOCTYPE,
			name: e,
			forceQuirks: !1,
			publicId: null,
			systemId: null,
			location: this.currentLocation
		};
	}
	_createCharacterToken(e, t) {
		this.currentCharacterToken = {
			type: e,
			chars: t,
			location: this.currentLocation
		};
	}
	_createAttr(e) {
		this.currentAttr = {
			name: e,
			value: ""
		}, this.currentLocation = this.getCurrentLocation(0);
	}
	_leaveAttrName() {
		var e;
		let t = this.currentToken;
		if (ct(t, this.currentAttr.name) === null) {
			if (t.attrs.push(this.currentAttr), t.location && this.currentLocation) {
				let n = (e = t.location).attrs ?? (e.attrs = /* @__PURE__ */ Object.create(null));
				n[this.currentAttr.name] = this.currentLocation, this._leaveAttrValue();
			}
		} else this._err(T.duplicateAttribute);
	}
	_leaveAttrValue() {
		this.currentLocation && (this.currentLocation.endLine = this.preprocessor.line, this.currentLocation.endCol = this.preprocessor.col, this.currentLocation.endOffset = this.preprocessor.offset);
	}
	prepareToken(e) {
		this._emitCurrentCharacterToken(e.location), this.currentToken = null, e.location && (e.location.endLine = this.preprocessor.line, e.location.endCol = this.preprocessor.col + 1, e.location.endOffset = this.preprocessor.offset + 1), this.currentLocation = this.getCurrentLocation(-1);
	}
	emitCurrentTagToken() {
		let e = this.currentToken;
		this.prepareToken(e), e.tagID = I(e.tagName), e.type === E.START_TAG ? (this.lastStartTagName = e.tagName, this.handler.onStartTag(e)) : (e.attrs.length > 0 && this._err(T.endTagWithAttributes), e.selfClosing && this._err(T.endTagWithTrailingSolidus), this.handler.onEndTag(e)), this.preprocessor.dropParsedChunk();
	}
	emitCurrentComment(e) {
		this.prepareToken(e), this.handler.onComment(e), this.preprocessor.dropParsedChunk();
	}
	emitCurrentDoctype(e) {
		this.prepareToken(e), this.handler.onDoctype(e), this.preprocessor.dropParsedChunk();
	}
	_emitCurrentCharacterToken(e) {
		if (this.currentCharacterToken) {
			switch (e && this.currentCharacterToken.location && (this.currentCharacterToken.location.endLine = e.startLine, this.currentCharacterToken.location.endCol = e.startCol, this.currentCharacterToken.location.endOffset = e.startOffset), this.currentCharacterToken.type) {
				case E.CHARACTER:
					this.handler.onCharacter(this.currentCharacterToken);
					break;
				case E.NULL_CHARACTER:
					this.handler.onNullCharacter(this.currentCharacterToken);
					break;
				case E.WHITESPACE_CHARACTER:
					this.handler.onWhitespaceCharacter(this.currentCharacterToken);
					break;
			}
			this.currentCharacterToken = null;
		}
	}
	_emitEOFToken() {
		let e = this.getCurrentLocation(0);
		e && (e.endLine = e.startLine, e.endCol = e.startCol, e.endOffset = e.startOffset), this._emitCurrentCharacterToken(e), this.handler.onEof({
			type: E.EOF,
			location: e
		}), this.active = !1;
	}
	_appendCharToCurrentCharacterToken(e, t) {
		if (this.currentCharacterToken) if (this.currentCharacterToken.type === e) {
			this.currentCharacterToken.chars += t;
			return;
		} else this.currentLocation = this.getCurrentLocation(0), this._emitCurrentCharacterToken(this.currentLocation), this.preprocessor.dropParsedChunk();
		this._createCharacterToken(e, t);
	}
	_emitCodePoint(e) {
		let t = Et(e) ? E.WHITESPACE_CHARACTER : e === C.NULL ? E.NULL_CHARACTER : E.CHARACTER;
		this._appendCharToCurrentCharacterToken(t, String.fromCodePoint(e));
	}
	_emitChars(e) {
		this._appendCharToCurrentCharacterToken(E.CHARACTER, e);
	}
	_startCharacterReference() {
		this.returnState = this.state, this.state = R.CHARACTER_REFERENCE, this.entityStartPos = this.preprocessor.pos, this.entityDecoder.startEntity(this._isCharacterReferenceInAttribute() ? A.Attribute : A.Legacy);
	}
	_isCharacterReferenceInAttribute() {
		return this.returnState === R.ATTRIBUTE_VALUE_DOUBLE_QUOTED || this.returnState === R.ATTRIBUTE_VALUE_SINGLE_QUOTED || this.returnState === R.ATTRIBUTE_VALUE_UNQUOTED;
	}
	_flushCodePointConsumedAsCharacterReference(e) {
		this._isCharacterReferenceInAttribute() ? this.currentAttr.value += String.fromCodePoint(e) : this._emitCodePoint(e);
	}
	_callState(e) {
		switch (this.state) {
			case R.DATA:
				this._stateData(e);
				break;
			case R.RCDATA:
				this._stateRcdata(e);
				break;
			case R.RAWTEXT:
				this._stateRawtext(e);
				break;
			case R.SCRIPT_DATA:
				this._stateScriptData(e);
				break;
			case R.PLAINTEXT:
				this._statePlaintext(e);
				break;
			case R.TAG_OPEN:
				this._stateTagOpen(e);
				break;
			case R.END_TAG_OPEN:
				this._stateEndTagOpen(e);
				break;
			case R.TAG_NAME:
				this._stateTagName(e);
				break;
			case R.RCDATA_LESS_THAN_SIGN:
				this._stateRcdataLessThanSign(e);
				break;
			case R.RCDATA_END_TAG_OPEN:
				this._stateRcdataEndTagOpen(e);
				break;
			case R.RCDATA_END_TAG_NAME:
				this._stateRcdataEndTagName(e);
				break;
			case R.RAWTEXT_LESS_THAN_SIGN:
				this._stateRawtextLessThanSign(e);
				break;
			case R.RAWTEXT_END_TAG_OPEN:
				this._stateRawtextEndTagOpen(e);
				break;
			case R.RAWTEXT_END_TAG_NAME:
				this._stateRawtextEndTagName(e);
				break;
			case R.SCRIPT_DATA_LESS_THAN_SIGN:
				this._stateScriptDataLessThanSign(e);
				break;
			case R.SCRIPT_DATA_END_TAG_OPEN:
				this._stateScriptDataEndTagOpen(e);
				break;
			case R.SCRIPT_DATA_END_TAG_NAME:
				this._stateScriptDataEndTagName(e);
				break;
			case R.SCRIPT_DATA_ESCAPE_START:
				this._stateScriptDataEscapeStart(e);
				break;
			case R.SCRIPT_DATA_ESCAPE_START_DASH:
				this._stateScriptDataEscapeStartDash(e);
				break;
			case R.SCRIPT_DATA_ESCAPED:
				this._stateScriptDataEscaped(e);
				break;
			case R.SCRIPT_DATA_ESCAPED_DASH:
				this._stateScriptDataEscapedDash(e);
				break;
			case R.SCRIPT_DATA_ESCAPED_DASH_DASH:
				this._stateScriptDataEscapedDashDash(e);
				break;
			case R.SCRIPT_DATA_ESCAPED_LESS_THAN_SIGN:
				this._stateScriptDataEscapedLessThanSign(e);
				break;
			case R.SCRIPT_DATA_ESCAPED_END_TAG_OPEN:
				this._stateScriptDataEscapedEndTagOpen(e);
				break;
			case R.SCRIPT_DATA_ESCAPED_END_TAG_NAME:
				this._stateScriptDataEscapedEndTagName(e);
				break;
			case R.SCRIPT_DATA_DOUBLE_ESCAPE_START:
				this._stateScriptDataDoubleEscapeStart(e);
				break;
			case R.SCRIPT_DATA_DOUBLE_ESCAPED:
				this._stateScriptDataDoubleEscaped(e);
				break;
			case R.SCRIPT_DATA_DOUBLE_ESCAPED_DASH:
				this._stateScriptDataDoubleEscapedDash(e);
				break;
			case R.SCRIPT_DATA_DOUBLE_ESCAPED_DASH_DASH:
				this._stateScriptDataDoubleEscapedDashDash(e);
				break;
			case R.SCRIPT_DATA_DOUBLE_ESCAPED_LESS_THAN_SIGN:
				this._stateScriptDataDoubleEscapedLessThanSign(e);
				break;
			case R.SCRIPT_DATA_DOUBLE_ESCAPE_END:
				this._stateScriptDataDoubleEscapeEnd(e);
				break;
			case R.BEFORE_ATTRIBUTE_NAME:
				this._stateBeforeAttributeName(e);
				break;
			case R.ATTRIBUTE_NAME:
				this._stateAttributeName(e);
				break;
			case R.AFTER_ATTRIBUTE_NAME:
				this._stateAfterAttributeName(e);
				break;
			case R.BEFORE_ATTRIBUTE_VALUE:
				this._stateBeforeAttributeValue(e);
				break;
			case R.ATTRIBUTE_VALUE_DOUBLE_QUOTED:
				this._stateAttributeValueDoubleQuoted(e);
				break;
			case R.ATTRIBUTE_VALUE_SINGLE_QUOTED:
				this._stateAttributeValueSingleQuoted(e);
				break;
			case R.ATTRIBUTE_VALUE_UNQUOTED:
				this._stateAttributeValueUnquoted(e);
				break;
			case R.AFTER_ATTRIBUTE_VALUE_QUOTED:
				this._stateAfterAttributeValueQuoted(e);
				break;
			case R.SELF_CLOSING_START_TAG:
				this._stateSelfClosingStartTag(e);
				break;
			case R.BOGUS_COMMENT:
				this._stateBogusComment(e);
				break;
			case R.MARKUP_DECLARATION_OPEN:
				this._stateMarkupDeclarationOpen(e);
				break;
			case R.COMMENT_START:
				this._stateCommentStart(e);
				break;
			case R.COMMENT_START_DASH:
				this._stateCommentStartDash(e);
				break;
			case R.COMMENT:
				this._stateComment(e);
				break;
			case R.COMMENT_LESS_THAN_SIGN:
				this._stateCommentLessThanSign(e);
				break;
			case R.COMMENT_LESS_THAN_SIGN_BANG:
				this._stateCommentLessThanSignBang(e);
				break;
			case R.COMMENT_LESS_THAN_SIGN_BANG_DASH:
				this._stateCommentLessThanSignBangDash(e);
				break;
			case R.COMMENT_LESS_THAN_SIGN_BANG_DASH_DASH:
				this._stateCommentLessThanSignBangDashDash(e);
				break;
			case R.COMMENT_END_DASH:
				this._stateCommentEndDash(e);
				break;
			case R.COMMENT_END:
				this._stateCommentEnd(e);
				break;
			case R.COMMENT_END_BANG:
				this._stateCommentEndBang(e);
				break;
			case R.DOCTYPE:
				this._stateDoctype(e);
				break;
			case R.BEFORE_DOCTYPE_NAME:
				this._stateBeforeDoctypeName(e);
				break;
			case R.DOCTYPE_NAME:
				this._stateDoctypeName(e);
				break;
			case R.AFTER_DOCTYPE_NAME:
				this._stateAfterDoctypeName(e);
				break;
			case R.AFTER_DOCTYPE_PUBLIC_KEYWORD:
				this._stateAfterDoctypePublicKeyword(e);
				break;
			case R.BEFORE_DOCTYPE_PUBLIC_IDENTIFIER:
				this._stateBeforeDoctypePublicIdentifier(e);
				break;
			case R.DOCTYPE_PUBLIC_IDENTIFIER_DOUBLE_QUOTED:
				this._stateDoctypePublicIdentifierDoubleQuoted(e);
				break;
			case R.DOCTYPE_PUBLIC_IDENTIFIER_SINGLE_QUOTED:
				this._stateDoctypePublicIdentifierSingleQuoted(e);
				break;
			case R.AFTER_DOCTYPE_PUBLIC_IDENTIFIER:
				this._stateAfterDoctypePublicIdentifier(e);
				break;
			case R.BETWEEN_DOCTYPE_PUBLIC_AND_SYSTEM_IDENTIFIERS:
				this._stateBetweenDoctypePublicAndSystemIdentifiers(e);
				break;
			case R.AFTER_DOCTYPE_SYSTEM_KEYWORD:
				this._stateAfterDoctypeSystemKeyword(e);
				break;
			case R.BEFORE_DOCTYPE_SYSTEM_IDENTIFIER:
				this._stateBeforeDoctypeSystemIdentifier(e);
				break;
			case R.DOCTYPE_SYSTEM_IDENTIFIER_DOUBLE_QUOTED:
				this._stateDoctypeSystemIdentifierDoubleQuoted(e);
				break;
			case R.DOCTYPE_SYSTEM_IDENTIFIER_SINGLE_QUOTED:
				this._stateDoctypeSystemIdentifierSingleQuoted(e);
				break;
			case R.AFTER_DOCTYPE_SYSTEM_IDENTIFIER:
				this._stateAfterDoctypeSystemIdentifier(e);
				break;
			case R.BOGUS_DOCTYPE:
				this._stateBogusDoctype(e);
				break;
			case R.CDATA_SECTION:
				this._stateCdataSection(e);
				break;
			case R.CDATA_SECTION_BRACKET:
				this._stateCdataSectionBracket(e);
				break;
			case R.CDATA_SECTION_END:
				this._stateCdataSectionEnd(e);
				break;
			case R.CHARACTER_REFERENCE:
				this._stateCharacterReference();
				break;
			case R.AMBIGUOUS_AMPERSAND:
				this._stateAmbiguousAmpersand(e);
				break;
			default: throw Error("Unknown state");
		}
	}
	_stateData(e) {
		switch (e) {
			case C.LESS_THAN_SIGN:
				this.state = R.TAG_OPEN;
				break;
			case C.AMPERSAND:
				this._startCharacterReference();
				break;
			case C.NULL:
				this._err(T.unexpectedNullCharacter), this._emitCodePoint(e);
				break;
			case C.EOF:
				this._emitEOFToken();
				break;
			default: this._emitCodePoint(e);
		}
	}
	_stateRcdata(e) {
		switch (e) {
			case C.AMPERSAND:
				this._startCharacterReference();
				break;
			case C.LESS_THAN_SIGN:
				this.state = R.RCDATA_LESS_THAN_SIGN;
				break;
			case C.NULL:
				this._err(T.unexpectedNullCharacter), this._emitChars(S);
				break;
			case C.EOF:
				this._emitEOFToken();
				break;
			default: this._emitCodePoint(e);
		}
	}
	_stateRawtext(e) {
		switch (e) {
			case C.LESS_THAN_SIGN:
				this.state = R.RAWTEXT_LESS_THAN_SIGN;
				break;
			case C.NULL:
				this._err(T.unexpectedNullCharacter), this._emitChars(S);
				break;
			case C.EOF:
				this._emitEOFToken();
				break;
			default: this._emitCodePoint(e);
		}
	}
	_stateScriptData(e) {
		switch (e) {
			case C.LESS_THAN_SIGN:
				this.state = R.SCRIPT_DATA_LESS_THAN_SIGN;
				break;
			case C.NULL:
				this._err(T.unexpectedNullCharacter), this._emitChars(S);
				break;
			case C.EOF:
				this._emitEOFToken();
				break;
			default: this._emitCodePoint(e);
		}
	}
	_statePlaintext(e) {
		switch (e) {
			case C.NULL:
				this._err(T.unexpectedNullCharacter), this._emitChars(S);
				break;
			case C.EOF:
				this._emitEOFToken();
				break;
			default: this._emitCodePoint(e);
		}
	}
	_stateTagOpen(e) {
		if (V(e)) this._createStartTagToken(), this.state = R.TAG_NAME, this._stateTagName(e);
		else switch (e) {
			case C.EXCLAMATION_MARK:
				this.state = R.MARKUP_DECLARATION_OPEN;
				break;
			case C.SOLIDUS:
				this.state = R.END_TAG_OPEN;
				break;
			case C.QUESTION_MARK:
				this._err(T.unexpectedQuestionMarkInsteadOfTagName), this._createCommentToken(1), this.state = R.BOGUS_COMMENT, this._stateBogusComment(e);
				break;
			case C.EOF:
				this._err(T.eofBeforeTagName), this._emitChars("<"), this._emitEOFToken();
				break;
			default: this._err(T.invalidFirstCharacterOfTagName), this._emitChars("<"), this.state = R.DATA, this._stateData(e);
		}
	}
	_stateEndTagOpen(e) {
		if (V(e)) this._createEndTagToken(), this.state = R.TAG_NAME, this._stateTagName(e);
		else switch (e) {
			case C.GREATER_THAN_SIGN:
				this._err(T.missingEndTagName), this.state = R.DATA;
				break;
			case C.EOF:
				this._err(T.eofBeforeTagName), this._emitChars("</"), this._emitEOFToken();
				break;
			default: this._err(T.invalidFirstCharacterOfTagName), this._createCommentToken(2), this.state = R.BOGUS_COMMENT, this._stateBogusComment(e);
		}
	}
	_stateTagName(e) {
		let t = this.currentToken;
		switch (e) {
			case C.SPACE:
			case C.LINE_FEED:
			case C.TABULATION:
			case C.FORM_FEED:
				this.state = R.BEFORE_ATTRIBUTE_NAME;
				break;
			case C.SOLIDUS:
				this.state = R.SELF_CLOSING_START_TAG;
				break;
			case C.GREATER_THAN_SIGN:
				this.state = R.DATA, this.emitCurrentTagToken();
				break;
			case C.NULL:
				this._err(T.unexpectedNullCharacter), t.tagName += S;
				break;
			case C.EOF:
				this._err(T.eofInTag), this._emitEOFToken();
				break;
			default: t.tagName += String.fromCodePoint(B(e) ? Tt(e) : e);
		}
	}
	_stateRcdataLessThanSign(e) {
		e === C.SOLIDUS ? this.state = R.RCDATA_END_TAG_OPEN : (this._emitChars("<"), this.state = R.RCDATA, this._stateRcdata(e));
	}
	_stateRcdataEndTagOpen(e) {
		V(e) ? (this.state = R.RCDATA_END_TAG_NAME, this._stateRcdataEndTagName(e)) : (this._emitChars("</"), this.state = R.RCDATA, this._stateRcdata(e));
	}
	handleSpecialEndTag(e) {
		if (!this.preprocessor.startsWith(this.lastStartTagName, !1)) return !this._ensureHibernation();
		this._createEndTagToken();
		let t = this.currentToken;
		switch (t.tagName = this.lastStartTagName, this.preprocessor.peek(this.lastStartTagName.length)) {
			case C.SPACE:
			case C.LINE_FEED:
			case C.TABULATION:
			case C.FORM_FEED: return this._advanceBy(this.lastStartTagName.length), this.state = R.BEFORE_ATTRIBUTE_NAME, !1;
			case C.SOLIDUS: return this._advanceBy(this.lastStartTagName.length), this.state = R.SELF_CLOSING_START_TAG, !1;
			case C.GREATER_THAN_SIGN: return this._advanceBy(this.lastStartTagName.length), this.emitCurrentTagToken(), this.state = R.DATA, !1;
			default: return !this._ensureHibernation();
		}
	}
	_stateRcdataEndTagName(e) {
		this.handleSpecialEndTag(e) && (this._emitChars("</"), this.state = R.RCDATA, this._stateRcdata(e));
	}
	_stateRawtextLessThanSign(e) {
		e === C.SOLIDUS ? this.state = R.RAWTEXT_END_TAG_OPEN : (this._emitChars("<"), this.state = R.RAWTEXT, this._stateRawtext(e));
	}
	_stateRawtextEndTagOpen(e) {
		V(e) ? (this.state = R.RAWTEXT_END_TAG_NAME, this._stateRawtextEndTagName(e)) : (this._emitChars("</"), this.state = R.RAWTEXT, this._stateRawtext(e));
	}
	_stateRawtextEndTagName(e) {
		this.handleSpecialEndTag(e) && (this._emitChars("</"), this.state = R.RAWTEXT, this._stateRawtext(e));
	}
	_stateScriptDataLessThanSign(e) {
		switch (e) {
			case C.SOLIDUS:
				this.state = R.SCRIPT_DATA_END_TAG_OPEN;
				break;
			case C.EXCLAMATION_MARK:
				this.state = R.SCRIPT_DATA_ESCAPE_START, this._emitChars("<!");
				break;
			default: this._emitChars("<"), this.state = R.SCRIPT_DATA, this._stateScriptData(e);
		}
	}
	_stateScriptDataEndTagOpen(e) {
		V(e) ? (this.state = R.SCRIPT_DATA_END_TAG_NAME, this._stateScriptDataEndTagName(e)) : (this._emitChars("</"), this.state = R.SCRIPT_DATA, this._stateScriptData(e));
	}
	_stateScriptDataEndTagName(e) {
		this.handleSpecialEndTag(e) && (this._emitChars("</"), this.state = R.SCRIPT_DATA, this._stateScriptData(e));
	}
	_stateScriptDataEscapeStart(e) {
		e === C.HYPHEN_MINUS ? (this.state = R.SCRIPT_DATA_ESCAPE_START_DASH, this._emitChars("-")) : (this.state = R.SCRIPT_DATA, this._stateScriptData(e));
	}
	_stateScriptDataEscapeStartDash(e) {
		e === C.HYPHEN_MINUS ? (this.state = R.SCRIPT_DATA_ESCAPED_DASH_DASH, this._emitChars("-")) : (this.state = R.SCRIPT_DATA, this._stateScriptData(e));
	}
	_stateScriptDataEscaped(e) {
		switch (e) {
			case C.HYPHEN_MINUS:
				this.state = R.SCRIPT_DATA_ESCAPED_DASH, this._emitChars("-");
				break;
			case C.LESS_THAN_SIGN:
				this.state = R.SCRIPT_DATA_ESCAPED_LESS_THAN_SIGN;
				break;
			case C.NULL:
				this._err(T.unexpectedNullCharacter), this._emitChars(S);
				break;
			case C.EOF:
				this._err(T.eofInScriptHtmlCommentLikeText), this._emitEOFToken();
				break;
			default: this._emitCodePoint(e);
		}
	}
	_stateScriptDataEscapedDash(e) {
		switch (e) {
			case C.HYPHEN_MINUS:
				this.state = R.SCRIPT_DATA_ESCAPED_DASH_DASH, this._emitChars("-");
				break;
			case C.LESS_THAN_SIGN:
				this.state = R.SCRIPT_DATA_ESCAPED_LESS_THAN_SIGN;
				break;
			case C.NULL:
				this._err(T.unexpectedNullCharacter), this.state = R.SCRIPT_DATA_ESCAPED, this._emitChars(S);
				break;
			case C.EOF:
				this._err(T.eofInScriptHtmlCommentLikeText), this._emitEOFToken();
				break;
			default: this.state = R.SCRIPT_DATA_ESCAPED, this._emitCodePoint(e);
		}
	}
	_stateScriptDataEscapedDashDash(e) {
		switch (e) {
			case C.HYPHEN_MINUS:
				this._emitChars("-");
				break;
			case C.LESS_THAN_SIGN:
				this.state = R.SCRIPT_DATA_ESCAPED_LESS_THAN_SIGN;
				break;
			case C.GREATER_THAN_SIGN:
				this.state = R.SCRIPT_DATA, this._emitChars(">");
				break;
			case C.NULL:
				this._err(T.unexpectedNullCharacter), this.state = R.SCRIPT_DATA_ESCAPED, this._emitChars(S);
				break;
			case C.EOF:
				this._err(T.eofInScriptHtmlCommentLikeText), this._emitEOFToken();
				break;
			default: this.state = R.SCRIPT_DATA_ESCAPED, this._emitCodePoint(e);
		}
	}
	_stateScriptDataEscapedLessThanSign(e) {
		e === C.SOLIDUS ? this.state = R.SCRIPT_DATA_ESCAPED_END_TAG_OPEN : V(e) ? (this._emitChars("<"), this.state = R.SCRIPT_DATA_DOUBLE_ESCAPE_START, this._stateScriptDataDoubleEscapeStart(e)) : (this._emitChars("<"), this.state = R.SCRIPT_DATA_ESCAPED, this._stateScriptDataEscaped(e));
	}
	_stateScriptDataEscapedEndTagOpen(e) {
		V(e) ? (this.state = R.SCRIPT_DATA_ESCAPED_END_TAG_NAME, this._stateScriptDataEscapedEndTagName(e)) : (this._emitChars("</"), this.state = R.SCRIPT_DATA_ESCAPED, this._stateScriptDataEscaped(e));
	}
	_stateScriptDataEscapedEndTagName(e) {
		this.handleSpecialEndTag(e) && (this._emitChars("</"), this.state = R.SCRIPT_DATA_ESCAPED, this._stateScriptDataEscaped(e));
	}
	_stateScriptDataDoubleEscapeStart(e) {
		if (this.preprocessor.startsWith(w.SCRIPT, !1) && Dt(this.preprocessor.peek(w.SCRIPT.length))) {
			this._emitCodePoint(e);
			for (let e = 0; e < w.SCRIPT.length; e++) this._emitCodePoint(this._consume());
			this.state = R.SCRIPT_DATA_DOUBLE_ESCAPED;
		} else this._ensureHibernation() || (this.state = R.SCRIPT_DATA_ESCAPED, this._stateScriptDataEscaped(e));
	}
	_stateScriptDataDoubleEscaped(e) {
		switch (e) {
			case C.HYPHEN_MINUS:
				this.state = R.SCRIPT_DATA_DOUBLE_ESCAPED_DASH, this._emitChars("-");
				break;
			case C.LESS_THAN_SIGN:
				this.state = R.SCRIPT_DATA_DOUBLE_ESCAPED_LESS_THAN_SIGN, this._emitChars("<");
				break;
			case C.NULL:
				this._err(T.unexpectedNullCharacter), this._emitChars(S);
				break;
			case C.EOF:
				this._err(T.eofInScriptHtmlCommentLikeText), this._emitEOFToken();
				break;
			default: this._emitCodePoint(e);
		}
	}
	_stateScriptDataDoubleEscapedDash(e) {
		switch (e) {
			case C.HYPHEN_MINUS:
				this.state = R.SCRIPT_DATA_DOUBLE_ESCAPED_DASH_DASH, this._emitChars("-");
				break;
			case C.LESS_THAN_SIGN:
				this.state = R.SCRIPT_DATA_DOUBLE_ESCAPED_LESS_THAN_SIGN, this._emitChars("<");
				break;
			case C.NULL:
				this._err(T.unexpectedNullCharacter), this.state = R.SCRIPT_DATA_DOUBLE_ESCAPED, this._emitChars(S);
				break;
			case C.EOF:
				this._err(T.eofInScriptHtmlCommentLikeText), this._emitEOFToken();
				break;
			default: this.state = R.SCRIPT_DATA_DOUBLE_ESCAPED, this._emitCodePoint(e);
		}
	}
	_stateScriptDataDoubleEscapedDashDash(e) {
		switch (e) {
			case C.HYPHEN_MINUS:
				this._emitChars("-");
				break;
			case C.LESS_THAN_SIGN:
				this.state = R.SCRIPT_DATA_DOUBLE_ESCAPED_LESS_THAN_SIGN, this._emitChars("<");
				break;
			case C.GREATER_THAN_SIGN:
				this.state = R.SCRIPT_DATA, this._emitChars(">");
				break;
			case C.NULL:
				this._err(T.unexpectedNullCharacter), this.state = R.SCRIPT_DATA_DOUBLE_ESCAPED, this._emitChars(S);
				break;
			case C.EOF:
				this._err(T.eofInScriptHtmlCommentLikeText), this._emitEOFToken();
				break;
			default: this.state = R.SCRIPT_DATA_DOUBLE_ESCAPED, this._emitCodePoint(e);
		}
	}
	_stateScriptDataDoubleEscapedLessThanSign(e) {
		e === C.SOLIDUS ? (this.state = R.SCRIPT_DATA_DOUBLE_ESCAPE_END, this._emitChars("/")) : (this.state = R.SCRIPT_DATA_DOUBLE_ESCAPED, this._stateScriptDataDoubleEscaped(e));
	}
	_stateScriptDataDoubleEscapeEnd(e) {
		if (this.preprocessor.startsWith(w.SCRIPT, !1) && Dt(this.preprocessor.peek(w.SCRIPT.length))) {
			this._emitCodePoint(e);
			for (let e = 0; e < w.SCRIPT.length; e++) this._emitCodePoint(this._consume());
			this.state = R.SCRIPT_DATA_ESCAPED;
		} else this._ensureHibernation() || (this.state = R.SCRIPT_DATA_DOUBLE_ESCAPED, this._stateScriptDataDoubleEscaped(e));
	}
	_stateBeforeAttributeName(e) {
		switch (e) {
			case C.SPACE:
			case C.LINE_FEED:
			case C.TABULATION:
			case C.FORM_FEED: break;
			case C.SOLIDUS:
			case C.GREATER_THAN_SIGN:
			case C.EOF:
				this.state = R.AFTER_ATTRIBUTE_NAME, this._stateAfterAttributeName(e);
				break;
			case C.EQUALS_SIGN:
				this._err(T.unexpectedEqualsSignBeforeAttributeName), this._createAttr("="), this.state = R.ATTRIBUTE_NAME;
				break;
			default: this._createAttr(""), this.state = R.ATTRIBUTE_NAME, this._stateAttributeName(e);
		}
	}
	_stateAttributeName(e) {
		switch (e) {
			case C.SPACE:
			case C.LINE_FEED:
			case C.TABULATION:
			case C.FORM_FEED:
			case C.SOLIDUS:
			case C.GREATER_THAN_SIGN:
			case C.EOF:
				this._leaveAttrName(), this.state = R.AFTER_ATTRIBUTE_NAME, this._stateAfterAttributeName(e);
				break;
			case C.EQUALS_SIGN:
				this._leaveAttrName(), this.state = R.BEFORE_ATTRIBUTE_VALUE;
				break;
			case C.QUOTATION_MARK:
			case C.APOSTROPHE:
			case C.LESS_THAN_SIGN:
				this._err(T.unexpectedCharacterInAttributeName), this.currentAttr.name += String.fromCodePoint(e);
				break;
			case C.NULL:
				this._err(T.unexpectedNullCharacter), this.currentAttr.name += S;
				break;
			default: this.currentAttr.name += String.fromCodePoint(B(e) ? Tt(e) : e);
		}
	}
	_stateAfterAttributeName(e) {
		switch (e) {
			case C.SPACE:
			case C.LINE_FEED:
			case C.TABULATION:
			case C.FORM_FEED: break;
			case C.SOLIDUS:
				this.state = R.SELF_CLOSING_START_TAG;
				break;
			case C.EQUALS_SIGN:
				this.state = R.BEFORE_ATTRIBUTE_VALUE;
				break;
			case C.GREATER_THAN_SIGN:
				this.state = R.DATA, this.emitCurrentTagToken();
				break;
			case C.EOF:
				this._err(T.eofInTag), this._emitEOFToken();
				break;
			default: this._createAttr(""), this.state = R.ATTRIBUTE_NAME, this._stateAttributeName(e);
		}
	}
	_stateBeforeAttributeValue(e) {
		switch (e) {
			case C.SPACE:
			case C.LINE_FEED:
			case C.TABULATION:
			case C.FORM_FEED: break;
			case C.QUOTATION_MARK:
				this.state = R.ATTRIBUTE_VALUE_DOUBLE_QUOTED;
				break;
			case C.APOSTROPHE:
				this.state = R.ATTRIBUTE_VALUE_SINGLE_QUOTED;
				break;
			case C.GREATER_THAN_SIGN:
				this._err(T.missingAttributeValue), this.state = R.DATA, this.emitCurrentTagToken();
				break;
			default: this.state = R.ATTRIBUTE_VALUE_UNQUOTED, this._stateAttributeValueUnquoted(e);
		}
	}
	_stateAttributeValueDoubleQuoted(e) {
		switch (e) {
			case C.QUOTATION_MARK:
				this.state = R.AFTER_ATTRIBUTE_VALUE_QUOTED;
				break;
			case C.AMPERSAND:
				this._startCharacterReference();
				break;
			case C.NULL:
				this._err(T.unexpectedNullCharacter), this.currentAttr.value += S;
				break;
			case C.EOF:
				this._err(T.eofInTag), this._emitEOFToken();
				break;
			default: this.currentAttr.value += String.fromCodePoint(e);
		}
	}
	_stateAttributeValueSingleQuoted(e) {
		switch (e) {
			case C.APOSTROPHE:
				this.state = R.AFTER_ATTRIBUTE_VALUE_QUOTED;
				break;
			case C.AMPERSAND:
				this._startCharacterReference();
				break;
			case C.NULL:
				this._err(T.unexpectedNullCharacter), this.currentAttr.value += S;
				break;
			case C.EOF:
				this._err(T.eofInTag), this._emitEOFToken();
				break;
			default: this.currentAttr.value += String.fromCodePoint(e);
		}
	}
	_stateAttributeValueUnquoted(e) {
		switch (e) {
			case C.SPACE:
			case C.LINE_FEED:
			case C.TABULATION:
			case C.FORM_FEED:
				this._leaveAttrValue(), this.state = R.BEFORE_ATTRIBUTE_NAME;
				break;
			case C.AMPERSAND:
				this._startCharacterReference();
				break;
			case C.GREATER_THAN_SIGN:
				this._leaveAttrValue(), this.state = R.DATA, this.emitCurrentTagToken();
				break;
			case C.NULL:
				this._err(T.unexpectedNullCharacter), this.currentAttr.value += S;
				break;
			case C.QUOTATION_MARK:
			case C.APOSTROPHE:
			case C.LESS_THAN_SIGN:
			case C.EQUALS_SIGN:
			case C.GRAVE_ACCENT:
				this._err(T.unexpectedCharacterInUnquotedAttributeValue), this.currentAttr.value += String.fromCodePoint(e);
				break;
			case C.EOF:
				this._err(T.eofInTag), this._emitEOFToken();
				break;
			default: this.currentAttr.value += String.fromCodePoint(e);
		}
	}
	_stateAfterAttributeValueQuoted(e) {
		switch (e) {
			case C.SPACE:
			case C.LINE_FEED:
			case C.TABULATION:
			case C.FORM_FEED:
				this._leaveAttrValue(), this.state = R.BEFORE_ATTRIBUTE_NAME;
				break;
			case C.SOLIDUS:
				this._leaveAttrValue(), this.state = R.SELF_CLOSING_START_TAG;
				break;
			case C.GREATER_THAN_SIGN:
				this._leaveAttrValue(), this.state = R.DATA, this.emitCurrentTagToken();
				break;
			case C.EOF:
				this._err(T.eofInTag), this._emitEOFToken();
				break;
			default: this._err(T.missingWhitespaceBetweenAttributes), this.state = R.BEFORE_ATTRIBUTE_NAME, this._stateBeforeAttributeName(e);
		}
	}
	_stateSelfClosingStartTag(e) {
		switch (e) {
			case C.GREATER_THAN_SIGN: {
				let e = this.currentToken;
				e.selfClosing = !0, this.state = R.DATA, this.emitCurrentTagToken();
				break;
			}
			case C.EOF:
				this._err(T.eofInTag), this._emitEOFToken();
				break;
			default: this._err(T.unexpectedSolidusInTag), this.state = R.BEFORE_ATTRIBUTE_NAME, this._stateBeforeAttributeName(e);
		}
	}
	_stateBogusComment(e) {
		let t = this.currentToken;
		switch (e) {
			case C.GREATER_THAN_SIGN:
				this.state = R.DATA, this.emitCurrentComment(t);
				break;
			case C.EOF:
				this.emitCurrentComment(t), this._emitEOFToken();
				break;
			case C.NULL:
				this._err(T.unexpectedNullCharacter), t.data += S;
				break;
			default: t.data += String.fromCodePoint(e);
		}
	}
	_stateMarkupDeclarationOpen(e) {
		this._consumeSequenceIfMatch(w.DASH_DASH, !0) ? (this._createCommentToken(w.DASH_DASH.length + 1), this.state = R.COMMENT_START) : this._consumeSequenceIfMatch(w.DOCTYPE, !1) ? (this.currentLocation = this.getCurrentLocation(w.DOCTYPE.length + 1), this.state = R.DOCTYPE) : this._consumeSequenceIfMatch(w.CDATA_START, !0) ? this.inForeignNode ? this.state = R.CDATA_SECTION : (this._err(T.cdataInHtmlContent), this._createCommentToken(w.CDATA_START.length + 1), this.currentToken.data = "[CDATA[", this.state = R.BOGUS_COMMENT) : this._ensureHibernation() || (this._err(T.incorrectlyOpenedComment), this._createCommentToken(2), this.state = R.BOGUS_COMMENT, this._stateBogusComment(e));
	}
	_stateCommentStart(e) {
		switch (e) {
			case C.HYPHEN_MINUS:
				this.state = R.COMMENT_START_DASH;
				break;
			case C.GREATER_THAN_SIGN: {
				this._err(T.abruptClosingOfEmptyComment), this.state = R.DATA;
				let e = this.currentToken;
				this.emitCurrentComment(e);
				break;
			}
			default: this.state = R.COMMENT, this._stateComment(e);
		}
	}
	_stateCommentStartDash(e) {
		let t = this.currentToken;
		switch (e) {
			case C.HYPHEN_MINUS:
				this.state = R.COMMENT_END;
				break;
			case C.GREATER_THAN_SIGN:
				this._err(T.abruptClosingOfEmptyComment), this.state = R.DATA, this.emitCurrentComment(t);
				break;
			case C.EOF:
				this._err(T.eofInComment), this.emitCurrentComment(t), this._emitEOFToken();
				break;
			default: t.data += "-", this.state = R.COMMENT, this._stateComment(e);
		}
	}
	_stateComment(e) {
		let t = this.currentToken;
		switch (e) {
			case C.HYPHEN_MINUS:
				this.state = R.COMMENT_END_DASH;
				break;
			case C.LESS_THAN_SIGN:
				t.data += "<", this.state = R.COMMENT_LESS_THAN_SIGN;
				break;
			case C.NULL:
				this._err(T.unexpectedNullCharacter), t.data += S;
				break;
			case C.EOF:
				this._err(T.eofInComment), this.emitCurrentComment(t), this._emitEOFToken();
				break;
			default: t.data += String.fromCodePoint(e);
		}
	}
	_stateCommentLessThanSign(e) {
		let t = this.currentToken;
		switch (e) {
			case C.EXCLAMATION_MARK:
				t.data += "!", this.state = R.COMMENT_LESS_THAN_SIGN_BANG;
				break;
			case C.LESS_THAN_SIGN:
				t.data += "<";
				break;
			default: this.state = R.COMMENT, this._stateComment(e);
		}
	}
	_stateCommentLessThanSignBang(e) {
		e === C.HYPHEN_MINUS ? this.state = R.COMMENT_LESS_THAN_SIGN_BANG_DASH : (this.state = R.COMMENT, this._stateComment(e));
	}
	_stateCommentLessThanSignBangDash(e) {
		e === C.HYPHEN_MINUS ? this.state = R.COMMENT_LESS_THAN_SIGN_BANG_DASH_DASH : (this.state = R.COMMENT_END_DASH, this._stateCommentEndDash(e));
	}
	_stateCommentLessThanSignBangDashDash(e) {
		e !== C.GREATER_THAN_SIGN && e !== C.EOF && this._err(T.nestedComment), this.state = R.COMMENT_END, this._stateCommentEnd(e);
	}
	_stateCommentEndDash(e) {
		let t = this.currentToken;
		switch (e) {
			case C.HYPHEN_MINUS:
				this.state = R.COMMENT_END;
				break;
			case C.EOF:
				this._err(T.eofInComment), this.emitCurrentComment(t), this._emitEOFToken();
				break;
			default: t.data += "-", this.state = R.COMMENT, this._stateComment(e);
		}
	}
	_stateCommentEnd(e) {
		let t = this.currentToken;
		switch (e) {
			case C.GREATER_THAN_SIGN:
				this.state = R.DATA, this.emitCurrentComment(t);
				break;
			case C.EXCLAMATION_MARK:
				this.state = R.COMMENT_END_BANG;
				break;
			case C.HYPHEN_MINUS:
				t.data += "-";
				break;
			case C.EOF:
				this._err(T.eofInComment), this.emitCurrentComment(t), this._emitEOFToken();
				break;
			default: t.data += "--", this.state = R.COMMENT, this._stateComment(e);
		}
	}
	_stateCommentEndBang(e) {
		let t = this.currentToken;
		switch (e) {
			case C.HYPHEN_MINUS:
				t.data += "--!", this.state = R.COMMENT_END_DASH;
				break;
			case C.GREATER_THAN_SIGN:
				this._err(T.incorrectlyClosedComment), this.state = R.DATA, this.emitCurrentComment(t);
				break;
			case C.EOF:
				this._err(T.eofInComment), this.emitCurrentComment(t), this._emitEOFToken();
				break;
			default: t.data += "--!", this.state = R.COMMENT, this._stateComment(e);
		}
	}
	_stateDoctype(e) {
		switch (e) {
			case C.SPACE:
			case C.LINE_FEED:
			case C.TABULATION:
			case C.FORM_FEED:
				this.state = R.BEFORE_DOCTYPE_NAME;
				break;
			case C.GREATER_THAN_SIGN:
				this.state = R.BEFORE_DOCTYPE_NAME, this._stateBeforeDoctypeName(e);
				break;
			case C.EOF: {
				this._err(T.eofInDoctype), this._createDoctypeToken(null);
				let e = this.currentToken;
				e.forceQuirks = !0, this.emitCurrentDoctype(e), this._emitEOFToken();
				break;
			}
			default: this._err(T.missingWhitespaceBeforeDoctypeName), this.state = R.BEFORE_DOCTYPE_NAME, this._stateBeforeDoctypeName(e);
		}
	}
	_stateBeforeDoctypeName(e) {
		if (B(e)) this._createDoctypeToken(String.fromCharCode(Tt(e))), this.state = R.DOCTYPE_NAME;
		else switch (e) {
			case C.SPACE:
			case C.LINE_FEED:
			case C.TABULATION:
			case C.FORM_FEED: break;
			case C.NULL:
				this._err(T.unexpectedNullCharacter), this._createDoctypeToken(S), this.state = R.DOCTYPE_NAME;
				break;
			case C.GREATER_THAN_SIGN: {
				this._err(T.missingDoctypeName), this._createDoctypeToken(null);
				let e = this.currentToken;
				e.forceQuirks = !0, this.emitCurrentDoctype(e), this.state = R.DATA;
				break;
			}
			case C.EOF: {
				this._err(T.eofInDoctype), this._createDoctypeToken(null);
				let e = this.currentToken;
				e.forceQuirks = !0, this.emitCurrentDoctype(e), this._emitEOFToken();
				break;
			}
			default: this._createDoctypeToken(String.fromCodePoint(e)), this.state = R.DOCTYPE_NAME;
		}
	}
	_stateDoctypeName(e) {
		let t = this.currentToken;
		switch (e) {
			case C.SPACE:
			case C.LINE_FEED:
			case C.TABULATION:
			case C.FORM_FEED:
				this.state = R.AFTER_DOCTYPE_NAME;
				break;
			case C.GREATER_THAN_SIGN:
				this.state = R.DATA, this.emitCurrentDoctype(t);
				break;
			case C.NULL:
				this._err(T.unexpectedNullCharacter), t.name += S;
				break;
			case C.EOF:
				this._err(T.eofInDoctype), t.forceQuirks = !0, this.emitCurrentDoctype(t), this._emitEOFToken();
				break;
			default: t.name += String.fromCodePoint(B(e) ? Tt(e) : e);
		}
	}
	_stateAfterDoctypeName(e) {
		let t = this.currentToken;
		switch (e) {
			case C.SPACE:
			case C.LINE_FEED:
			case C.TABULATION:
			case C.FORM_FEED: break;
			case C.GREATER_THAN_SIGN:
				this.state = R.DATA, this.emitCurrentDoctype(t);
				break;
			case C.EOF:
				this._err(T.eofInDoctype), t.forceQuirks = !0, this.emitCurrentDoctype(t), this._emitEOFToken();
				break;
			default: this._consumeSequenceIfMatch(w.PUBLIC, !1) ? this.state = R.AFTER_DOCTYPE_PUBLIC_KEYWORD : this._consumeSequenceIfMatch(w.SYSTEM, !1) ? this.state = R.AFTER_DOCTYPE_SYSTEM_KEYWORD : this._ensureHibernation() || (this._err(T.invalidCharacterSequenceAfterDoctypeName), t.forceQuirks = !0, this.state = R.BOGUS_DOCTYPE, this._stateBogusDoctype(e));
		}
	}
	_stateAfterDoctypePublicKeyword(e) {
		let t = this.currentToken;
		switch (e) {
			case C.SPACE:
			case C.LINE_FEED:
			case C.TABULATION:
			case C.FORM_FEED:
				this.state = R.BEFORE_DOCTYPE_PUBLIC_IDENTIFIER;
				break;
			case C.QUOTATION_MARK:
				this._err(T.missingWhitespaceAfterDoctypePublicKeyword), t.publicId = "", this.state = R.DOCTYPE_PUBLIC_IDENTIFIER_DOUBLE_QUOTED;
				break;
			case C.APOSTROPHE:
				this._err(T.missingWhitespaceAfterDoctypePublicKeyword), t.publicId = "", this.state = R.DOCTYPE_PUBLIC_IDENTIFIER_SINGLE_QUOTED;
				break;
			case C.GREATER_THAN_SIGN:
				this._err(T.missingDoctypePublicIdentifier), t.forceQuirks = !0, this.state = R.DATA, this.emitCurrentDoctype(t);
				break;
			case C.EOF:
				this._err(T.eofInDoctype), t.forceQuirks = !0, this.emitCurrentDoctype(t), this._emitEOFToken();
				break;
			default: this._err(T.missingQuoteBeforeDoctypePublicIdentifier), t.forceQuirks = !0, this.state = R.BOGUS_DOCTYPE, this._stateBogusDoctype(e);
		}
	}
	_stateBeforeDoctypePublicIdentifier(e) {
		let t = this.currentToken;
		switch (e) {
			case C.SPACE:
			case C.LINE_FEED:
			case C.TABULATION:
			case C.FORM_FEED: break;
			case C.QUOTATION_MARK:
				t.publicId = "", this.state = R.DOCTYPE_PUBLIC_IDENTIFIER_DOUBLE_QUOTED;
				break;
			case C.APOSTROPHE:
				t.publicId = "", this.state = R.DOCTYPE_PUBLIC_IDENTIFIER_SINGLE_QUOTED;
				break;
			case C.GREATER_THAN_SIGN:
				this._err(T.missingDoctypePublicIdentifier), t.forceQuirks = !0, this.state = R.DATA, this.emitCurrentDoctype(t);
				break;
			case C.EOF:
				this._err(T.eofInDoctype), t.forceQuirks = !0, this.emitCurrentDoctype(t), this._emitEOFToken();
				break;
			default: this._err(T.missingQuoteBeforeDoctypePublicIdentifier), t.forceQuirks = !0, this.state = R.BOGUS_DOCTYPE, this._stateBogusDoctype(e);
		}
	}
	_stateDoctypePublicIdentifierDoubleQuoted(e) {
		let t = this.currentToken;
		switch (e) {
			case C.QUOTATION_MARK:
				this.state = R.AFTER_DOCTYPE_PUBLIC_IDENTIFIER;
				break;
			case C.NULL:
				this._err(T.unexpectedNullCharacter), t.publicId += S;
				break;
			case C.GREATER_THAN_SIGN:
				this._err(T.abruptDoctypePublicIdentifier), t.forceQuirks = !0, this.emitCurrentDoctype(t), this.state = R.DATA;
				break;
			case C.EOF:
				this._err(T.eofInDoctype), t.forceQuirks = !0, this.emitCurrentDoctype(t), this._emitEOFToken();
				break;
			default: t.publicId += String.fromCodePoint(e);
		}
	}
	_stateDoctypePublicIdentifierSingleQuoted(e) {
		let t = this.currentToken;
		switch (e) {
			case C.APOSTROPHE:
				this.state = R.AFTER_DOCTYPE_PUBLIC_IDENTIFIER;
				break;
			case C.NULL:
				this._err(T.unexpectedNullCharacter), t.publicId += S;
				break;
			case C.GREATER_THAN_SIGN:
				this._err(T.abruptDoctypePublicIdentifier), t.forceQuirks = !0, this.emitCurrentDoctype(t), this.state = R.DATA;
				break;
			case C.EOF:
				this._err(T.eofInDoctype), t.forceQuirks = !0, this.emitCurrentDoctype(t), this._emitEOFToken();
				break;
			default: t.publicId += String.fromCodePoint(e);
		}
	}
	_stateAfterDoctypePublicIdentifier(e) {
		let t = this.currentToken;
		switch (e) {
			case C.SPACE:
			case C.LINE_FEED:
			case C.TABULATION:
			case C.FORM_FEED:
				this.state = R.BETWEEN_DOCTYPE_PUBLIC_AND_SYSTEM_IDENTIFIERS;
				break;
			case C.GREATER_THAN_SIGN:
				this.state = R.DATA, this.emitCurrentDoctype(t);
				break;
			case C.QUOTATION_MARK:
				this._err(T.missingWhitespaceBetweenDoctypePublicAndSystemIdentifiers), t.systemId = "", this.state = R.DOCTYPE_SYSTEM_IDENTIFIER_DOUBLE_QUOTED;
				break;
			case C.APOSTROPHE:
				this._err(T.missingWhitespaceBetweenDoctypePublicAndSystemIdentifiers), t.systemId = "", this.state = R.DOCTYPE_SYSTEM_IDENTIFIER_SINGLE_QUOTED;
				break;
			case C.EOF:
				this._err(T.eofInDoctype), t.forceQuirks = !0, this.emitCurrentDoctype(t), this._emitEOFToken();
				break;
			default: this._err(T.missingQuoteBeforeDoctypeSystemIdentifier), t.forceQuirks = !0, this.state = R.BOGUS_DOCTYPE, this._stateBogusDoctype(e);
		}
	}
	_stateBetweenDoctypePublicAndSystemIdentifiers(e) {
		let t = this.currentToken;
		switch (e) {
			case C.SPACE:
			case C.LINE_FEED:
			case C.TABULATION:
			case C.FORM_FEED: break;
			case C.GREATER_THAN_SIGN:
				this.emitCurrentDoctype(t), this.state = R.DATA;
				break;
			case C.QUOTATION_MARK:
				t.systemId = "", this.state = R.DOCTYPE_SYSTEM_IDENTIFIER_DOUBLE_QUOTED;
				break;
			case C.APOSTROPHE:
				t.systemId = "", this.state = R.DOCTYPE_SYSTEM_IDENTIFIER_SINGLE_QUOTED;
				break;
			case C.EOF:
				this._err(T.eofInDoctype), t.forceQuirks = !0, this.emitCurrentDoctype(t), this._emitEOFToken();
				break;
			default: this._err(T.missingQuoteBeforeDoctypeSystemIdentifier), t.forceQuirks = !0, this.state = R.BOGUS_DOCTYPE, this._stateBogusDoctype(e);
		}
	}
	_stateAfterDoctypeSystemKeyword(e) {
		let t = this.currentToken;
		switch (e) {
			case C.SPACE:
			case C.LINE_FEED:
			case C.TABULATION:
			case C.FORM_FEED:
				this.state = R.BEFORE_DOCTYPE_SYSTEM_IDENTIFIER;
				break;
			case C.QUOTATION_MARK:
				this._err(T.missingWhitespaceAfterDoctypeSystemKeyword), t.systemId = "", this.state = R.DOCTYPE_SYSTEM_IDENTIFIER_DOUBLE_QUOTED;
				break;
			case C.APOSTROPHE:
				this._err(T.missingWhitespaceAfterDoctypeSystemKeyword), t.systemId = "", this.state = R.DOCTYPE_SYSTEM_IDENTIFIER_SINGLE_QUOTED;
				break;
			case C.GREATER_THAN_SIGN:
				this._err(T.missingDoctypeSystemIdentifier), t.forceQuirks = !0, this.state = R.DATA, this.emitCurrentDoctype(t);
				break;
			case C.EOF:
				this._err(T.eofInDoctype), t.forceQuirks = !0, this.emitCurrentDoctype(t), this._emitEOFToken();
				break;
			default: this._err(T.missingQuoteBeforeDoctypeSystemIdentifier), t.forceQuirks = !0, this.state = R.BOGUS_DOCTYPE, this._stateBogusDoctype(e);
		}
	}
	_stateBeforeDoctypeSystemIdentifier(e) {
		let t = this.currentToken;
		switch (e) {
			case C.SPACE:
			case C.LINE_FEED:
			case C.TABULATION:
			case C.FORM_FEED: break;
			case C.QUOTATION_MARK:
				t.systemId = "", this.state = R.DOCTYPE_SYSTEM_IDENTIFIER_DOUBLE_QUOTED;
				break;
			case C.APOSTROPHE:
				t.systemId = "", this.state = R.DOCTYPE_SYSTEM_IDENTIFIER_SINGLE_QUOTED;
				break;
			case C.GREATER_THAN_SIGN:
				this._err(T.missingDoctypeSystemIdentifier), t.forceQuirks = !0, this.state = R.DATA, this.emitCurrentDoctype(t);
				break;
			case C.EOF:
				this._err(T.eofInDoctype), t.forceQuirks = !0, this.emitCurrentDoctype(t), this._emitEOFToken();
				break;
			default: this._err(T.missingQuoteBeforeDoctypeSystemIdentifier), t.forceQuirks = !0, this.state = R.BOGUS_DOCTYPE, this._stateBogusDoctype(e);
		}
	}
	_stateDoctypeSystemIdentifierDoubleQuoted(e) {
		let t = this.currentToken;
		switch (e) {
			case C.QUOTATION_MARK:
				this.state = R.AFTER_DOCTYPE_SYSTEM_IDENTIFIER;
				break;
			case C.NULL:
				this._err(T.unexpectedNullCharacter), t.systemId += S;
				break;
			case C.GREATER_THAN_SIGN:
				this._err(T.abruptDoctypeSystemIdentifier), t.forceQuirks = !0, this.emitCurrentDoctype(t), this.state = R.DATA;
				break;
			case C.EOF:
				this._err(T.eofInDoctype), t.forceQuirks = !0, this.emitCurrentDoctype(t), this._emitEOFToken();
				break;
			default: t.systemId += String.fromCodePoint(e);
		}
	}
	_stateDoctypeSystemIdentifierSingleQuoted(e) {
		let t = this.currentToken;
		switch (e) {
			case C.APOSTROPHE:
				this.state = R.AFTER_DOCTYPE_SYSTEM_IDENTIFIER;
				break;
			case C.NULL:
				this._err(T.unexpectedNullCharacter), t.systemId += S;
				break;
			case C.GREATER_THAN_SIGN:
				this._err(T.abruptDoctypeSystemIdentifier), t.forceQuirks = !0, this.emitCurrentDoctype(t), this.state = R.DATA;
				break;
			case C.EOF:
				this._err(T.eofInDoctype), t.forceQuirks = !0, this.emitCurrentDoctype(t), this._emitEOFToken();
				break;
			default: t.systemId += String.fromCodePoint(e);
		}
	}
	_stateAfterDoctypeSystemIdentifier(e) {
		let t = this.currentToken;
		switch (e) {
			case C.SPACE:
			case C.LINE_FEED:
			case C.TABULATION:
			case C.FORM_FEED: break;
			case C.GREATER_THAN_SIGN:
				this.emitCurrentDoctype(t), this.state = R.DATA;
				break;
			case C.EOF:
				this._err(T.eofInDoctype), t.forceQuirks = !0, this.emitCurrentDoctype(t), this._emitEOFToken();
				break;
			default: this._err(T.unexpectedCharacterAfterDoctypeSystemIdentifier), this.state = R.BOGUS_DOCTYPE, this._stateBogusDoctype(e);
		}
	}
	_stateBogusDoctype(e) {
		let t = this.currentToken;
		switch (e) {
			case C.GREATER_THAN_SIGN:
				this.emitCurrentDoctype(t), this.state = R.DATA;
				break;
			case C.NULL:
				this._err(T.unexpectedNullCharacter);
				break;
			case C.EOF:
				this.emitCurrentDoctype(t), this._emitEOFToken();
				break;
		}
	}
	_stateCdataSection(e) {
		switch (e) {
			case C.RIGHT_SQUARE_BRACKET:
				this.state = R.CDATA_SECTION_BRACKET;
				break;
			case C.EOF:
				this._err(T.eofInCdata), this._emitEOFToken();
				break;
			default: this._emitCodePoint(e);
		}
	}
	_stateCdataSectionBracket(e) {
		e === C.RIGHT_SQUARE_BRACKET ? this.state = R.CDATA_SECTION_END : (this._emitChars("]"), this.state = R.CDATA_SECTION, this._stateCdataSection(e));
	}
	_stateCdataSectionEnd(e) {
		switch (e) {
			case C.GREATER_THAN_SIGN:
				this.state = R.DATA;
				break;
			case C.RIGHT_SQUARE_BRACKET:
				this._emitChars("]");
				break;
			default: this._emitChars("]]"), this.state = R.CDATA_SECTION, this._stateCdataSection(e);
		}
	}
	_stateCharacterReference() {
		let e = this.entityDecoder.write(this.preprocessor.html, this.preprocessor.pos);
		if (e < 0) if (this.preprocessor.lastChunkWritten) e = this.entityDecoder.end();
		else {
			this.active = !1, this.preprocessor.pos = this.preprocessor.html.length - 1, this.consumedAfterSnapshot = 0, this.preprocessor.endOfChunkHit = !0;
			return;
		}
		e === 0 ? (this.preprocessor.pos = this.entityStartPos, this._flushCodePointConsumedAsCharacterReference(C.AMPERSAND), this.state = !this._isCharacterReferenceInAttribute() && wt(this.preprocessor.peek(1)) ? R.AMBIGUOUS_AMPERSAND : this.returnState) : this.state = this.returnState;
	}
	_stateAmbiguousAmpersand(e) {
		wt(e) ? this._flushCodePointConsumedAsCharacterReference(e) : (e === C.SEMICOLON && this._err(T.unknownNamedCharacterReference), this.state = this.returnState, this._callState(e));
	}
}, At = /* @__PURE__ */ new Set([
	F.DD,
	F.DT,
	F.LI,
	F.OPTGROUP,
	F.OPTION,
	F.P,
	F.RB,
	F.RP,
	F.RT,
	F.RTC
]), jt = /* @__PURE__ */ new Set([
	...At,
	F.CAPTION,
	F.COLGROUP,
	F.TBODY,
	F.TD,
	F.TFOOT,
	F.TH,
	F.THEAD,
	F.TR
]), Mt = /* @__PURE__ */ new Set([
	F.APPLET,
	F.CAPTION,
	F.HTML,
	F.MARQUEE,
	F.OBJECT,
	F.TABLE,
	F.TD,
	F.TEMPLATE,
	F.TH
]), Nt = /* @__PURE__ */ new Set([
	...Mt,
	F.OL,
	F.UL
]), Pt = /* @__PURE__ */ new Set([...Mt, F.BUTTON]), Ft = /* @__PURE__ */ new Set([
	F.ANNOTATION_XML,
	F.MI,
	F.MN,
	F.MO,
	F.MS,
	F.MTEXT
]), It = /* @__PURE__ */ new Set([
	F.DESC,
	F.FOREIGN_OBJECT,
	F.TITLE
]), Lt = /* @__PURE__ */ new Set([
	F.TR,
	F.TEMPLATE,
	F.HTML
]), Rt = /* @__PURE__ */ new Set([
	F.TBODY,
	F.TFOOT,
	F.THEAD,
	F.TEMPLATE,
	F.HTML
]), zt = /* @__PURE__ */ new Set([
	F.TABLE,
	F.TEMPLATE,
	F.HTML
]), Bt = /* @__PURE__ */ new Set([F.TD, F.TH]), Vt = class {
	get currentTmplContentOrNode() {
		return this._isInTemplate() ? this.treeAdapter.getTemplateContent(this.current) : this.current;
	}
	constructor(e, t, n) {
		this.treeAdapter = t, this.handler = n, this.items = [], this.tagIDs = [], this.stackTop = -1, this.tmplCount = 0, this.currentTagId = F.UNKNOWN, this.current = e;
	}
	_indexOf(e) {
		return this.items.lastIndexOf(e, this.stackTop);
	}
	_isInTemplate() {
		return this.currentTagId === F.TEMPLATE && this.treeAdapter.getNamespaceURI(this.current) === j.HTML;
	}
	_updateCurrentElement() {
		this.current = this.items[this.stackTop], this.currentTagId = this.tagIDs[this.stackTop];
	}
	push(e, t) {
		this.stackTop++, this.items[this.stackTop] = e, this.current = e, this.tagIDs[this.stackTop] = t, this.currentTagId = t, this._isInTemplate() && this.tmplCount++, this.handler.onItemPush(e, t, !0);
	}
	pop() {
		let e = this.current;
		this.tmplCount > 0 && this._isInTemplate() && this.tmplCount--, this.stackTop--, this._updateCurrentElement(), this.handler.onItemPop(e, !0);
	}
	replace(e, t) {
		let n = this._indexOf(e);
		this.items[n] = t, n === this.stackTop && (this.current = t);
	}
	insertAfter(e, t, n) {
		let r = this._indexOf(e) + 1;
		this.items.splice(r, 0, t), this.tagIDs.splice(r, 0, n), this.stackTop++, r === this.stackTop && this._updateCurrentElement(), this.current && this.currentTagId !== void 0 && this.handler.onItemPush(this.current, this.currentTagId, r === this.stackTop);
	}
	popUntilTagNamePopped(e) {
		let t = this.stackTop + 1;
		do
			t = this.tagIDs.lastIndexOf(e, t - 1);
		while (t > 0 && this.treeAdapter.getNamespaceURI(this.items[t]) !== j.HTML);
		this.shortenToLength(Math.max(t, 0));
	}
	shortenToLength(e) {
		for (; this.stackTop >= e;) {
			let t = this.current;
			this.tmplCount > 0 && this._isInTemplate() && --this.tmplCount, this.stackTop--, this._updateCurrentElement(), this.handler.onItemPop(t, this.stackTop < e);
		}
	}
	popUntilElementPopped(e) {
		let t = this._indexOf(e);
		this.shortenToLength(Math.max(t, 0));
	}
	popUntilPopped(e, t) {
		let n = this._indexOfTagNames(e, t);
		this.shortenToLength(Math.max(n, 0));
	}
	popUntilNumberedHeaderPopped() {
		this.popUntilPopped(xt, j.HTML);
	}
	popUntilTableCellPopped() {
		this.popUntilPopped(Bt, j.HTML);
	}
	popAllUpToHtmlElement() {
		this.tmplCount = 0, this.shortenToLength(1);
	}
	_indexOfTagNames(e, t) {
		for (let n = this.stackTop; n >= 0; n--) if (e.has(this.tagIDs[n]) && this.treeAdapter.getNamespaceURI(this.items[n]) === t) return n;
		return -1;
	}
	clearBackTo(e, t) {
		let n = this._indexOfTagNames(e, t);
		this.shortenToLength(n + 1);
	}
	clearBackToTableContext() {
		this.clearBackTo(zt, j.HTML);
	}
	clearBackToTableBodyContext() {
		this.clearBackTo(Rt, j.HTML);
	}
	clearBackToTableRowContext() {
		this.clearBackTo(Lt, j.HTML);
	}
	remove(e) {
		let t = this._indexOf(e);
		t >= 0 && (t === this.stackTop ? this.pop() : (this.items.splice(t, 1), this.tagIDs.splice(t, 1), this.stackTop--, this._updateCurrentElement(), this.handler.onItemPop(e, !1)));
	}
	tryPeekProperlyNestedBodyElement() {
		return this.stackTop >= 1 && this.tagIDs[1] === F.BODY ? this.items[1] : null;
	}
	contains(e) {
		return this._indexOf(e) > -1;
	}
	getCommonAncestor(e) {
		let t = this._indexOf(e) - 1;
		return t >= 0 ? this.items[t] : null;
	}
	isRootHtmlElementCurrent() {
		return this.stackTop === 0 && this.tagIDs[0] === F.HTML;
	}
	hasInDynamicScope(e, t) {
		for (let n = this.stackTop; n >= 0; n--) {
			let r = this.tagIDs[n];
			switch (this.treeAdapter.getNamespaceURI(this.items[n])) {
				case j.HTML:
					if (r === e) return !0;
					if (t.has(r)) return !1;
					break;
				case j.SVG:
					if (It.has(r)) return !1;
					break;
				case j.MATHML:
					if (Ft.has(r)) return !1;
					break;
			}
		}
		return !0;
	}
	hasInScope(e) {
		return this.hasInDynamicScope(e, Mt);
	}
	hasInListItemScope(e) {
		return this.hasInDynamicScope(e, Nt);
	}
	hasInButtonScope(e) {
		return this.hasInDynamicScope(e, Pt);
	}
	hasNumberedHeaderInScope() {
		for (let e = this.stackTop; e >= 0; e--) {
			let t = this.tagIDs[e];
			switch (this.treeAdapter.getNamespaceURI(this.items[e])) {
				case j.HTML:
					if (xt.has(t)) return !0;
					if (Mt.has(t)) return !1;
					break;
				case j.SVG:
					if (It.has(t)) return !1;
					break;
				case j.MATHML:
					if (Ft.has(t)) return !1;
					break;
			}
		}
		return !0;
	}
	hasInTableScope(e) {
		for (let t = this.stackTop; t >= 0; t--) if (this.treeAdapter.getNamespaceURI(this.items[t]) === j.HTML) switch (this.tagIDs[t]) {
			case e: return !0;
			case F.TABLE:
			case F.HTML: return !1;
		}
		return !0;
	}
	hasTableBodyContextInTableScope() {
		for (let e = this.stackTop; e >= 0; e--) if (this.treeAdapter.getNamespaceURI(this.items[e]) === j.HTML) switch (this.tagIDs[e]) {
			case F.TBODY:
			case F.THEAD:
			case F.TFOOT: return !0;
			case F.TABLE:
			case F.HTML: return !1;
		}
		return !0;
	}
	hasInSelectScope(e) {
		for (let t = this.stackTop; t >= 0; t--) if (this.treeAdapter.getNamespaceURI(this.items[t]) === j.HTML) switch (this.tagIDs[t]) {
			case e: return !0;
			case F.OPTION:
			case F.OPTGROUP: break;
			default: return !1;
		}
		return !0;
	}
	generateImpliedEndTags() {
		for (; this.currentTagId !== void 0 && At.has(this.currentTagId);) this.pop();
	}
	generateImpliedEndTagsThoroughly() {
		for (; this.currentTagId !== void 0 && jt.has(this.currentTagId);) this.pop();
	}
	generateImpliedEndTagsWithExclusion(e) {
		for (; this.currentTagId !== void 0 && this.currentTagId !== e && jt.has(this.currentTagId);) this.pop();
	}
}, Ht = 3, H;
(function(e) {
	e[e.Marker = 0] = "Marker", e[e.Element = 1] = "Element";
})(H ||= {});
var Ut = { type: H.Marker }, Wt = class {
	constructor(e) {
		this.treeAdapter = e, this.entries = [], this.bookmark = null;
	}
	_getNoahArkConditionCandidates(e, t) {
		let n = [], r = t.length, i = this.treeAdapter.getTagName(e), a = this.treeAdapter.getNamespaceURI(e);
		for (let e = 0; e < this.entries.length; e++) {
			let t = this.entries[e];
			if (t.type === H.Marker) break;
			let { element: o } = t;
			if (this.treeAdapter.getTagName(o) === i && this.treeAdapter.getNamespaceURI(o) === a) {
				let t = this.treeAdapter.getAttrList(o);
				t.length === r && n.push({
					idx: e,
					attrs: t
				});
			}
		}
		return n;
	}
	_ensureNoahArkCondition(e) {
		if (this.entries.length < Ht) return;
		let t = this.treeAdapter.getAttrList(e), n = this._getNoahArkConditionCandidates(e, t);
		if (n.length < Ht) return;
		let r = new Map(t.map((e) => [e.name, e.value])), i = 0;
		for (let e = 0; e < n.length; e++) {
			let t = n[e];
			t.attrs.every((e) => r.get(e.name) === e.value) && (i += 1, i >= Ht && this.entries.splice(t.idx, 1));
		}
	}
	insertMarker() {
		this.entries.unshift(Ut);
	}
	pushElement(e, t) {
		this._ensureNoahArkCondition(e), this.entries.unshift({
			type: H.Element,
			element: e,
			token: t
		});
	}
	insertElementAfterBookmark(e, t) {
		let n = this.entries.indexOf(this.bookmark);
		this.entries.splice(n, 0, {
			type: H.Element,
			element: e,
			token: t
		});
	}
	removeEntry(e) {
		let t = this.entries.indexOf(e);
		t !== -1 && this.entries.splice(t, 1);
	}
	clearToLastMarker() {
		let e = this.entries.indexOf(Ut);
		e === -1 ? this.entries.length = 0 : this.entries.splice(0, e + 1);
	}
	getElementEntryInScopeWithTagName(e) {
		let t = this.entries.find((t) => t.type === H.Marker || this.treeAdapter.getTagName(t.element) === e);
		return t && t.type === H.Element ? t : null;
	}
	getElementEntry(e) {
		return this.entries.find((t) => t.type === H.Element && t.element === e);
	}
}, U = {
	createDocument() {
		return {
			nodeName: "#document",
			mode: N.NO_QUIRKS,
			childNodes: []
		};
	},
	createDocumentFragment() {
		return {
			nodeName: "#document-fragment",
			childNodes: []
		};
	},
	createElement(e, t, n) {
		return {
			nodeName: e,
			tagName: e,
			attrs: n,
			namespaceURI: t,
			childNodes: [],
			parentNode: null
		};
	},
	createCommentNode(e) {
		return {
			nodeName: "#comment",
			data: e,
			parentNode: null
		};
	},
	createTextNode(e) {
		return {
			nodeName: "#text",
			value: e,
			parentNode: null
		};
	},
	appendChild(e, t) {
		e.childNodes.push(t), t.parentNode = e;
	},
	insertBefore(e, t, n) {
		let r = e.childNodes.indexOf(n);
		e.childNodes.splice(r, 0, t), t.parentNode = e;
	},
	setTemplateContent(e, t) {
		e.content = t;
	},
	getTemplateContent(e) {
		return e.content;
	},
	setDocumentType(e, t, n, r) {
		let i = e.childNodes.find((e) => e.nodeName === "#documentType");
		if (i) i.name = t, i.publicId = n, i.systemId = r;
		else {
			let i = {
				nodeName: "#documentType",
				name: t,
				publicId: n,
				systemId: r,
				parentNode: null
			};
			U.appendChild(e, i);
		}
	},
	setDocumentMode(e, t) {
		e.mode = t;
	},
	getDocumentMode(e) {
		return e.mode;
	},
	detachNode(e) {
		if (e.parentNode) {
			let t = e.parentNode.childNodes.indexOf(e);
			e.parentNode.childNodes.splice(t, 1), e.parentNode = null;
		}
	},
	insertText(e, t) {
		if (e.childNodes.length > 0) {
			let n = e.childNodes[e.childNodes.length - 1];
			if (U.isTextNode(n)) {
				n.value += t;
				return;
			}
		}
		U.appendChild(e, U.createTextNode(t));
	},
	insertTextBefore(e, t, n) {
		let r = e.childNodes[e.childNodes.indexOf(n) - 1];
		r && U.isTextNode(r) ? r.value += t : U.insertBefore(e, U.createTextNode(t), n);
	},
	adoptAttributes(e, t) {
		let n = new Set(e.attrs.map((e) => e.name));
		for (let r = 0; r < t.length; r++) n.has(t[r].name) || e.attrs.push(t[r]);
	},
	getFirstChild(e) {
		return e.childNodes[0];
	},
	getChildNodes(e) {
		return e.childNodes;
	},
	getParentNode(e) {
		return e.parentNode;
	},
	getAttrList(e) {
		return e.attrs;
	},
	getTagName(e) {
		return e.tagName;
	},
	getNamespaceURI(e) {
		return e.namespaceURI;
	},
	getTextNodeContent(e) {
		return e.value;
	},
	getCommentNodeContent(e) {
		return e.data;
	},
	getDocumentTypeNodeName(e) {
		return e.name;
	},
	getDocumentTypeNodePublicId(e) {
		return e.publicId;
	},
	getDocumentTypeNodeSystemId(e) {
		return e.systemId;
	},
	isTextNode(e) {
		return e.nodeName === "#text";
	},
	isCommentNode(e) {
		return e.nodeName === "#comment";
	},
	isDocumentTypeNode(e) {
		return e.nodeName === "#documentType";
	},
	isElementNode(e) {
		return Object.prototype.hasOwnProperty.call(e, "tagName");
	},
	setNodeSourceCodeLocation(e, t) {
		e.sourceCodeLocation = t;
	},
	getNodeSourceCodeLocation(e) {
		return e.sourceCodeLocation;
	},
	updateNodeSourceCodeLocation(e, t) {
		e.sourceCodeLocation = {
			...e.sourceCodeLocation,
			...t
		};
	}
}, Gt = "html", Kt = "about:legacy-compat", qt = "http://www.ibm.com/data/dtd/v11/ibmxhtml1-transitional.dtd", Jt = /* @__PURE__ */ "+//silmaril//dtd html pro v0r11 19970101//,-//as//dtd html 3.0 aswedit + extensions//,-//advasoft ltd//dtd html 3.0 aswedit + extensions//,-//ietf//dtd html 2.0 level 1//,-//ietf//dtd html 2.0 level 2//,-//ietf//dtd html 2.0 strict level 1//,-//ietf//dtd html 2.0 strict level 2//,-//ietf//dtd html 2.0 strict//,-//ietf//dtd html 2.0//,-//ietf//dtd html 2.1e//,-//ietf//dtd html 3.0//,-//ietf//dtd html 3.2 final//,-//ietf//dtd html 3.2//,-//ietf//dtd html 3//,-//ietf//dtd html level 0//,-//ietf//dtd html level 1//,-//ietf//dtd html level 2//,-//ietf//dtd html level 3//,-//ietf//dtd html strict level 0//,-//ietf//dtd html strict level 1//,-//ietf//dtd html strict level 2//,-//ietf//dtd html strict level 3//,-//ietf//dtd html strict//,-//ietf//dtd html//,-//metrius//dtd metrius presentational//,-//microsoft//dtd internet explorer 2.0 html strict//,-//microsoft//dtd internet explorer 2.0 html//,-//microsoft//dtd internet explorer 2.0 tables//,-//microsoft//dtd internet explorer 3.0 html strict//,-//microsoft//dtd internet explorer 3.0 html//,-//microsoft//dtd internet explorer 3.0 tables//,-//netscape comm. corp.//dtd html//,-//netscape comm. corp.//dtd strict html//,-//o'reilly and associates//dtd html 2.0//,-//o'reilly and associates//dtd html extended 1.0//,-//o'reilly and associates//dtd html extended relaxed 1.0//,-//sq//dtd html 2.0 hotmetal + extensions//,-//softquad software//dtd hotmetal pro 6.0::19990601::extensions to html 4.0//,-//softquad//dtd hotmetal pro 4.0::19971010::extensions to html 4.0//,-//spyglass//dtd html 2.0 extended//,-//sun microsystems corp.//dtd hotjava html//,-//sun microsystems corp.//dtd hotjava strict html//,-//w3c//dtd html 3 1995-03-24//,-//w3c//dtd html 3.2 draft//,-//w3c//dtd html 3.2 final//,-//w3c//dtd html 3.2//,-//w3c//dtd html 3.2s draft//,-//w3c//dtd html 4.0 frameset//,-//w3c//dtd html 4.0 transitional//,-//w3c//dtd html experimental 19960712//,-//w3c//dtd html experimental 970421//,-//w3c//dtd w3 html//,-//w3o//dtd w3 html 3.0//,-//webtechs//dtd mozilla html 2.0//,-//webtechs//dtd mozilla html//".split(","), Yt = [
	...Jt,
	"-//w3c//dtd html 4.01 frameset//",
	"-//w3c//dtd html 4.01 transitional//"
], Xt = /* @__PURE__ */ new Set([
	"-//w3o//dtd w3 html strict 3.0//en//",
	"-/w3c/dtd html 4.0 transitional/en",
	"html"
]), Zt = ["-//w3c//dtd xhtml 1.0 frameset//", "-//w3c//dtd xhtml 1.0 transitional//"], Qt = [
	...Zt,
	"-//w3c//dtd html 4.01 frameset//",
	"-//w3c//dtd html 4.01 transitional//"
];
function $t(e, t) {
	return t.some((t) => e.startsWith(t));
}
function en(e) {
	return e.name === Gt && e.publicId === null && (e.systemId === null || e.systemId === Kt);
}
function tn(e) {
	if (e.name !== Gt) return N.QUIRKS;
	let { systemId: t } = e;
	if (t && t.toLowerCase() === qt) return N.QUIRKS;
	let { publicId: n } = e;
	if (n !== null) {
		if (n = n.toLowerCase(), Xt.has(n)) return N.QUIRKS;
		let e = t === null ? Yt : Jt;
		if ($t(n, e)) return N.QUIRKS;
		if (e = t === null ? Zt : Qt, $t(n, e)) return N.LIMITED_QUIRKS;
	}
	return N.NO_QUIRKS;
}
var nn = {
	TEXT_HTML: "text/html",
	APPLICATION_XML: "application/xhtml+xml"
}, rn = "definitionurl", an = "definitionURL", on = new Map((/* @__PURE__ */ "attributeName.attributeType.baseFrequency.baseProfile.calcMode.clipPathUnits.diffuseConstant.edgeMode.filterUnits.glyphRef.gradientTransform.gradientUnits.kernelMatrix.kernelUnitLength.keyPoints.keySplines.keyTimes.lengthAdjust.limitingConeAngle.markerHeight.markerUnits.markerWidth.maskContentUnits.maskUnits.numOctaves.pathLength.patternContentUnits.patternTransform.patternUnits.pointsAtX.pointsAtY.pointsAtZ.preserveAlpha.preserveAspectRatio.primitiveUnits.refX.refY.repeatCount.repeatDur.requiredExtensions.requiredFeatures.specularConstant.specularExponent.spreadMethod.startOffset.stdDeviation.stitchTiles.surfaceScale.systemLanguage.tableValues.targetX.targetY.textLength.viewBox.viewTarget.xChannelSelector.yChannelSelector.zoomAndPan".split(".")).map((e) => [e.toLowerCase(), e])), sn = /* @__PURE__ */ new Map([
	["xlink:actuate", {
		prefix: "xlink",
		name: "actuate",
		namespace: j.XLINK
	}],
	["xlink:arcrole", {
		prefix: "xlink",
		name: "arcrole",
		namespace: j.XLINK
	}],
	["xlink:href", {
		prefix: "xlink",
		name: "href",
		namespace: j.XLINK
	}],
	["xlink:role", {
		prefix: "xlink",
		name: "role",
		namespace: j.XLINK
	}],
	["xlink:show", {
		prefix: "xlink",
		name: "show",
		namespace: j.XLINK
	}],
	["xlink:title", {
		prefix: "xlink",
		name: "title",
		namespace: j.XLINK
	}],
	["xlink:type", {
		prefix: "xlink",
		name: "type",
		namespace: j.XLINK
	}],
	["xml:lang", {
		prefix: "xml",
		name: "lang",
		namespace: j.XML
	}],
	["xml:space", {
		prefix: "xml",
		name: "space",
		namespace: j.XML
	}],
	["xmlns", {
		prefix: "",
		name: "xmlns",
		namespace: j.XMLNS
	}],
	["xmlns:xlink", {
		prefix: "xmlns",
		name: "xlink",
		namespace: j.XMLNS
	}]
]), cn = new Map((/* @__PURE__ */ "altGlyph.altGlyphDef.altGlyphItem.animateColor.animateMotion.animateTransform.clipPath.feBlend.feColorMatrix.feComponentTransfer.feComposite.feConvolveMatrix.feDiffuseLighting.feDisplacementMap.feDistantLight.feFlood.feFuncA.feFuncB.feFuncG.feFuncR.feGaussianBlur.feImage.feMerge.feMergeNode.feMorphology.feOffset.fePointLight.feSpecularLighting.feSpotLight.feTile.feTurbulence.foreignObject.glyphRef.linearGradient.radialGradient.textPath".split(".")).map((e) => [e.toLowerCase(), e])), ln = /* @__PURE__ */ new Set([
	F.B,
	F.BIG,
	F.BLOCKQUOTE,
	F.BODY,
	F.BR,
	F.CENTER,
	F.CODE,
	F.DD,
	F.DIV,
	F.DL,
	F.DT,
	F.EM,
	F.EMBED,
	F.H1,
	F.H2,
	F.H3,
	F.H4,
	F.H5,
	F.H6,
	F.HEAD,
	F.HR,
	F.I,
	F.IMG,
	F.LI,
	F.LISTING,
	F.MENU,
	F.META,
	F.NOBR,
	F.OL,
	F.P,
	F.PRE,
	F.RUBY,
	F.S,
	F.SMALL,
	F.SPAN,
	F.STRONG,
	F.STRIKE,
	F.SUB,
	F.SUP,
	F.TABLE,
	F.TT,
	F.U,
	F.UL,
	F.VAR
]);
function un(e) {
	let t = e.tagID;
	return t === F.FONT && e.attrs.some(({ name: e }) => e === M.COLOR || e === M.SIZE || e === M.FACE) || ln.has(t);
}
function dn(e) {
	for (let t = 0; t < e.attrs.length; t++) if (e.attrs[t].name === rn) {
		e.attrs[t].name = an;
		break;
	}
}
function fn(e) {
	for (let t = 0; t < e.attrs.length; t++) {
		let n = on.get(e.attrs[t].name);
		n != null && (e.attrs[t].name = n);
	}
}
function pn(e) {
	for (let t = 0; t < e.attrs.length; t++) {
		let n = sn.get(e.attrs[t].name);
		n && (e.attrs[t].prefix = n.prefix, e.attrs[t].name = n.name, e.attrs[t].namespace = n.namespace);
	}
}
function mn(e) {
	let t = cn.get(e.tagName);
	t != null && (e.tagName = t, e.tagID = I(e.tagName));
}
function hn(e, t) {
	return t === j.MATHML && (e === F.MI || e === F.MO || e === F.MN || e === F.MS || e === F.MTEXT);
}
function gn(e, t, n) {
	if (t === j.MATHML && e === F.ANNOTATION_XML) {
		for (let e = 0; e < n.length; e++) if (n[e].name === M.ENCODING) {
			let t = n[e].value.toLowerCase();
			return t === nn.TEXT_HTML || t === nn.APPLICATION_XML;
		}
	}
	return t === j.SVG && (e === F.FOREIGN_OBJECT || e === F.DESC || e === F.TITLE);
}
function _n(e, t, n, r) {
	return (!r || r === j.HTML) && gn(e, t, n) || (!r || r === j.MATHML) && hn(e, t);
}
var vn = "hidden", yn = 8, bn = 3, W;
(function(e) {
	e[e.INITIAL = 0] = "INITIAL", e[e.BEFORE_HTML = 1] = "BEFORE_HTML", e[e.BEFORE_HEAD = 2] = "BEFORE_HEAD", e[e.IN_HEAD = 3] = "IN_HEAD", e[e.IN_HEAD_NO_SCRIPT = 4] = "IN_HEAD_NO_SCRIPT", e[e.AFTER_HEAD = 5] = "AFTER_HEAD", e[e.IN_BODY = 6] = "IN_BODY", e[e.TEXT = 7] = "TEXT", e[e.IN_TABLE = 8] = "IN_TABLE", e[e.IN_TABLE_TEXT = 9] = "IN_TABLE_TEXT", e[e.IN_CAPTION = 10] = "IN_CAPTION", e[e.IN_COLUMN_GROUP = 11] = "IN_COLUMN_GROUP", e[e.IN_TABLE_BODY = 12] = "IN_TABLE_BODY", e[e.IN_ROW = 13] = "IN_ROW", e[e.IN_CELL = 14] = "IN_CELL", e[e.IN_SELECT = 15] = "IN_SELECT", e[e.IN_SELECT_IN_TABLE = 16] = "IN_SELECT_IN_TABLE", e[e.IN_TEMPLATE = 17] = "IN_TEMPLATE", e[e.AFTER_BODY = 18] = "AFTER_BODY", e[e.IN_FRAMESET = 19] = "IN_FRAMESET", e[e.AFTER_FRAMESET = 20] = "AFTER_FRAMESET", e[e.AFTER_AFTER_BODY = 21] = "AFTER_AFTER_BODY", e[e.AFTER_AFTER_FRAMESET = 22] = "AFTER_AFTER_FRAMESET";
})(W ||= {});
var xn = {
	startLine: -1,
	startCol: -1,
	startOffset: -1,
	endLine: -1,
	endCol: -1,
	endOffset: -1
}, Sn = /* @__PURE__ */ new Set([
	F.TABLE,
	F.TBODY,
	F.TFOOT,
	F.THEAD,
	F.TR
]), Cn = {
	scriptingEnabled: !0,
	sourceCodeLocationInfo: !1,
	treeAdapter: U,
	onParseError: null
}, wn = class {
	constructor(e, t, n = null, r = null) {
		this.fragmentContext = n, this.scriptHandler = r, this.currentToken = null, this.stopped = !1, this.insertionMode = W.INITIAL, this.originalInsertionMode = W.INITIAL, this.headElement = null, this.formElement = null, this.currentNotInHTML = !1, this.tmplInsertionModeStack = [], this.pendingCharacterTokens = [], this.hasNonWhitespacePendingCharacterToken = !1, this.framesetOk = !0, this.skipNextNewLine = !1, this.fosterParentingEnabled = !1, this.options = {
			...Cn,
			...e
		}, this.treeAdapter = this.options.treeAdapter, this.onParseError = this.options.onParseError, this.onParseError && (this.options.sourceCodeLocationInfo = !0), this.document = t ?? this.treeAdapter.createDocument(), this.tokenizer = new kt(this.options, this), this.activeFormattingElements = new Wt(this.treeAdapter), this.fragmentContextID = n ? I(this.treeAdapter.getTagName(n)) : F.UNKNOWN, this._setContextModes(n ?? this.document, this.fragmentContextID), this.openElements = new Vt(this.document, this.treeAdapter, this);
	}
	static parse(e, t) {
		let n = new this(t);
		return n.tokenizer.write(e, !0), n.document;
	}
	static getFragmentParser(e, t) {
		let n = {
			...Cn,
			...t
		};
		e ??= n.treeAdapter.createElement(P.TEMPLATE, j.HTML, []);
		let r = n.treeAdapter.createElement("documentmock", j.HTML, []), i = new this(n, r, e);
		return i.fragmentContextID === F.TEMPLATE && i.tmplInsertionModeStack.unshift(W.IN_TEMPLATE), i._initTokenizerForFragmentParsing(), i._insertFakeRootElement(), i._resetInsertionMode(), i._findFormInFragmentContext(), i;
	}
	getFragment() {
		let e = this.treeAdapter.getFirstChild(this.document), t = this.treeAdapter.createDocumentFragment();
		return this._adoptNodes(e, t), t;
	}
	_err(e, t, n) {
		if (!this.onParseError) return;
		let r = e.location ?? xn, i = {
			code: t,
			startLine: r.startLine,
			startCol: r.startCol,
			startOffset: r.startOffset,
			endLine: n ? r.startLine : r.endLine,
			endCol: n ? r.startCol : r.endCol,
			endOffset: n ? r.startOffset : r.endOffset
		};
		this.onParseError(i);
	}
	onItemPush(e, t, n) {
		var r, i;
		(i = (r = this.treeAdapter).onItemPush) == null || i.call(r, e), n && this.openElements.stackTop > 0 && this._setContextModes(e, t);
	}
	onItemPop(e, t) {
		var n, r;
		if (this.options.sourceCodeLocationInfo && this._setEndLocation(e, this.currentToken), (r = (n = this.treeAdapter).onItemPop) == null || r.call(n, e, this.openElements.current), t) {
			let e, t;
			this.openElements.stackTop === 0 && this.fragmentContext ? (e = this.fragmentContext, t = this.fragmentContextID) : {current: e, currentTagId: t} = this.openElements, this._setContextModes(e, t);
		}
	}
	_setContextModes(e, t) {
		let n = e === this.document || e && this.treeAdapter.getNamespaceURI(e) === j.HTML;
		this.currentNotInHTML = !n, this.tokenizer.inForeignNode = !n && e !== void 0 && t !== void 0 && !this._isIntegrationPoint(t, e);
	}
	_switchToTextParsing(e, t) {
		this._insertElement(e, j.HTML), this.tokenizer.state = t, this.originalInsertionMode = this.insertionMode, this.insertionMode = W.TEXT;
	}
	switchToPlaintextParsing() {
		this.insertionMode = W.TEXT, this.originalInsertionMode = W.IN_BODY, this.tokenizer.state = z.PLAINTEXT;
	}
	_getAdjustedCurrentElement() {
		return this.openElements.stackTop === 0 && this.fragmentContext ? this.fragmentContext : this.openElements.current;
	}
	_findFormInFragmentContext() {
		let e = this.fragmentContext;
		for (; e;) {
			if (this.treeAdapter.getTagName(e) === P.FORM) {
				this.formElement = e;
				break;
			}
			e = this.treeAdapter.getParentNode(e);
		}
	}
	_initTokenizerForFragmentParsing() {
		if (!(!this.fragmentContext || this.treeAdapter.getNamespaceURI(this.fragmentContext) !== j.HTML)) switch (this.fragmentContextID) {
			case F.TITLE:
			case F.TEXTAREA:
				this.tokenizer.state = z.RCDATA;
				break;
			case F.STYLE:
			case F.XMP:
			case F.IFRAME:
			case F.NOEMBED:
			case F.NOFRAMES:
			case F.NOSCRIPT:
				this.tokenizer.state = z.RAWTEXT;
				break;
			case F.SCRIPT:
				this.tokenizer.state = z.SCRIPT_DATA;
				break;
			case F.PLAINTEXT:
				this.tokenizer.state = z.PLAINTEXT;
				break;
		}
	}
	_setDocumentType(e) {
		let t = e.name || "", n = e.publicId || "", r = e.systemId || "";
		if (this.treeAdapter.setDocumentType(this.document, t, n, r), e.location) {
			let t = this.treeAdapter.getChildNodes(this.document).find((e) => this.treeAdapter.isDocumentTypeNode(e));
			t && this.treeAdapter.setNodeSourceCodeLocation(t, e.location);
		}
	}
	_attachElementToTree(e, t) {
		if (this.options.sourceCodeLocationInfo) {
			let n = t && {
				...t,
				startTag: t
			};
			this.treeAdapter.setNodeSourceCodeLocation(e, n);
		}
		if (this._shouldFosterParentOnInsertion()) this._fosterParentElement(e);
		else {
			let t = this.openElements.currentTmplContentOrNode;
			this.treeAdapter.appendChild(t ?? this.document, e);
		}
	}
	_appendElement(e, t) {
		let n = this.treeAdapter.createElement(e.tagName, t, e.attrs);
		this._attachElementToTree(n, e.location);
	}
	_insertElement(e, t) {
		let n = this.treeAdapter.createElement(e.tagName, t, e.attrs);
		this._attachElementToTree(n, e.location), this.openElements.push(n, e.tagID);
	}
	_insertFakeElement(e, t) {
		let n = this.treeAdapter.createElement(e, j.HTML, []);
		this._attachElementToTree(n, null), this.openElements.push(n, t);
	}
	_insertTemplate(e) {
		let t = this.treeAdapter.createElement(e.tagName, j.HTML, e.attrs), n = this.treeAdapter.createDocumentFragment();
		this.treeAdapter.setTemplateContent(t, n), this._attachElementToTree(t, e.location), this.openElements.push(t, e.tagID), this.options.sourceCodeLocationInfo && this.treeAdapter.setNodeSourceCodeLocation(n, null);
	}
	_insertFakeRootElement() {
		let e = this.treeAdapter.createElement(P.HTML, j.HTML, []);
		this.options.sourceCodeLocationInfo && this.treeAdapter.setNodeSourceCodeLocation(e, null), this.treeAdapter.appendChild(this.openElements.current, e), this.openElements.push(e, F.HTML);
	}
	_appendCommentNode(e, t) {
		let n = this.treeAdapter.createCommentNode(e.data);
		this.treeAdapter.appendChild(t, n), this.options.sourceCodeLocationInfo && this.treeAdapter.setNodeSourceCodeLocation(n, e.location);
	}
	_insertCharacters(e) {
		let t, n;
		if (this._shouldFosterParentOnInsertion() ? ({parent: t, beforeElement: n} = this._findFosterParentingLocation(), n ? this.treeAdapter.insertTextBefore(t, e.chars, n) : this.treeAdapter.insertText(t, e.chars)) : (t = this.openElements.currentTmplContentOrNode, this.treeAdapter.insertText(t, e.chars)), !e.location) return;
		let r = this.treeAdapter.getChildNodes(t), i = r[(n ? r.lastIndexOf(n) : r.length) - 1];
		if (this.treeAdapter.getNodeSourceCodeLocation(i)) {
			let { endLine: t, endCol: n, endOffset: r } = e.location;
			this.treeAdapter.updateNodeSourceCodeLocation(i, {
				endLine: t,
				endCol: n,
				endOffset: r
			});
		} else this.options.sourceCodeLocationInfo && this.treeAdapter.setNodeSourceCodeLocation(i, e.location);
	}
	_adoptNodes(e, t) {
		for (let n = this.treeAdapter.getFirstChild(e); n; n = this.treeAdapter.getFirstChild(e)) this.treeAdapter.detachNode(n), this.treeAdapter.appendChild(t, n);
	}
	_setEndLocation(e, t) {
		if (this.treeAdapter.getNodeSourceCodeLocation(e) && t.location) {
			let n = t.location, r = this.treeAdapter.getTagName(e), i = t.type === E.END_TAG && r === t.tagName ? {
				endTag: { ...n },
				endLine: n.endLine,
				endCol: n.endCol,
				endOffset: n.endOffset
			} : {
				endLine: n.startLine,
				endCol: n.startCol,
				endOffset: n.startOffset
			};
			this.treeAdapter.updateNodeSourceCodeLocation(e, i);
		}
	}
	shouldProcessStartTagTokenInForeignContent(e) {
		if (!this.currentNotInHTML) return !1;
		let t, n;
		return this.openElements.stackTop === 0 && this.fragmentContext ? (t = this.fragmentContext, n = this.fragmentContextID) : {current: t, currentTagId: n} = this.openElements, e.tagID === F.SVG && this.treeAdapter.getTagName(t) === P.ANNOTATION_XML && this.treeAdapter.getNamespaceURI(t) === j.MATHML ? !1 : this.tokenizer.inForeignNode || (e.tagID === F.MGLYPH || e.tagID === F.MALIGNMARK) && n !== void 0 && !this._isIntegrationPoint(n, t, j.HTML);
	}
	_processToken(e) {
		switch (e.type) {
			case E.CHARACTER:
				this.onCharacter(e);
				break;
			case E.NULL_CHARACTER:
				this.onNullCharacter(e);
				break;
			case E.COMMENT:
				this.onComment(e);
				break;
			case E.DOCTYPE:
				this.onDoctype(e);
				break;
			case E.START_TAG:
				this._processStartTag(e);
				break;
			case E.END_TAG:
				this.onEndTag(e);
				break;
			case E.EOF:
				this.onEof(e);
				break;
			case E.WHITESPACE_CHARACTER:
				this.onWhitespaceCharacter(e);
				break;
		}
	}
	_isIntegrationPoint(e, t, n) {
		return _n(e, this.treeAdapter.getNamespaceURI(t), this.treeAdapter.getAttrList(t), n);
	}
	_reconstructActiveFormattingElements() {
		let e = this.activeFormattingElements.entries.length;
		if (e) {
			let t = this.activeFormattingElements.entries.findIndex((e) => e.type === H.Marker || this.openElements.contains(e.element)), n = t === -1 ? e - 1 : t - 1;
			for (let e = n; e >= 0; e--) {
				let t = this.activeFormattingElements.entries[e];
				this._insertElement(t.token, this.treeAdapter.getNamespaceURI(t.element)), t.element = this.openElements.current;
			}
		}
	}
	_closeTableCell() {
		this.openElements.generateImpliedEndTags(), this.openElements.popUntilTableCellPopped(), this.activeFormattingElements.clearToLastMarker(), this.insertionMode = W.IN_ROW;
	}
	_closePElement() {
		this.openElements.generateImpliedEndTagsWithExclusion(F.P), this.openElements.popUntilTagNamePopped(F.P);
	}
	_resetInsertionMode() {
		for (let e = this.openElements.stackTop; e >= 0; e--) switch (e === 0 && this.fragmentContext ? this.fragmentContextID : this.openElements.tagIDs[e]) {
			case F.TR:
				this.insertionMode = W.IN_ROW;
				return;
			case F.TBODY:
			case F.THEAD:
			case F.TFOOT:
				this.insertionMode = W.IN_TABLE_BODY;
				return;
			case F.CAPTION:
				this.insertionMode = W.IN_CAPTION;
				return;
			case F.COLGROUP:
				this.insertionMode = W.IN_COLUMN_GROUP;
				return;
			case F.TABLE:
				this.insertionMode = W.IN_TABLE;
				return;
			case F.BODY:
				this.insertionMode = W.IN_BODY;
				return;
			case F.FRAMESET:
				this.insertionMode = W.IN_FRAMESET;
				return;
			case F.SELECT:
				this._resetInsertionModeForSelect(e);
				return;
			case F.TEMPLATE:
				this.insertionMode = this.tmplInsertionModeStack[0];
				return;
			case F.HTML:
				this.insertionMode = this.headElement ? W.AFTER_HEAD : W.BEFORE_HEAD;
				return;
			case F.TD:
			case F.TH:
				if (e > 0) {
					this.insertionMode = W.IN_CELL;
					return;
				}
				break;
			case F.HEAD:
				if (e > 0) {
					this.insertionMode = W.IN_HEAD;
					return;
				}
				break;
		}
		this.insertionMode = W.IN_BODY;
	}
	_resetInsertionModeForSelect(e) {
		if (e > 0) for (let t = e - 1; t > 0; t--) {
			let e = this.openElements.tagIDs[t];
			if (e === F.TEMPLATE) break;
			if (e === F.TABLE) {
				this.insertionMode = W.IN_SELECT_IN_TABLE;
				return;
			}
		}
		this.insertionMode = W.IN_SELECT;
	}
	_isElementCausesFosterParenting(e) {
		return Sn.has(e);
	}
	_shouldFosterParentOnInsertion() {
		return this.fosterParentingEnabled && this.openElements.currentTagId !== void 0 && this._isElementCausesFosterParenting(this.openElements.currentTagId);
	}
	_findFosterParentingLocation() {
		for (let e = this.openElements.stackTop; e >= 0; e--) {
			let t = this.openElements.items[e];
			switch (this.openElements.tagIDs[e]) {
				case F.TEMPLATE:
					if (this.treeAdapter.getNamespaceURI(t) === j.HTML) return {
						parent: this.treeAdapter.getTemplateContent(t),
						beforeElement: null
					};
					break;
				case F.TABLE: {
					let n = this.treeAdapter.getParentNode(t);
					return n ? {
						parent: n,
						beforeElement: t
					} : {
						parent: this.openElements.items[e - 1],
						beforeElement: null
					};
				}
			}
		}
		return {
			parent: this.openElements.items[0],
			beforeElement: null
		};
	}
	_fosterParentElement(e) {
		let t = this._findFosterParentingLocation();
		t.beforeElement ? this.treeAdapter.insertBefore(t.parent, e, t.beforeElement) : this.treeAdapter.appendChild(t.parent, e);
	}
	_isSpecialElement(e, t) {
		return bt[this.treeAdapter.getNamespaceURI(e)].has(t);
	}
	onCharacter(e) {
		if (this.skipNextNewLine = !1, this.tokenizer.inForeignNode) {
			Pi(this, e);
			return;
		}
		switch (this.insertionMode) {
			case W.INITIAL:
				G(this, e);
				break;
			case W.BEFORE_HTML:
				K(this, e);
				break;
			case W.BEFORE_HEAD:
				q(this, e);
				break;
			case W.IN_HEAD:
				X(this, e);
				break;
			case W.IN_HEAD_NO_SCRIPT:
				Wn(this, e);
				break;
			case W.AFTER_HEAD:
				qn(this, e);
				break;
			case W.IN_BODY:
			case W.IN_CAPTION:
			case W.IN_CELL:
			case W.IN_TEMPLATE:
				Xn(this, e);
				break;
			case W.TEXT:
			case W.IN_SELECT:
			case W.IN_SELECT_IN_TABLE:
				this._insertCharacters(e);
				break;
			case W.IN_TABLE:
			case W.IN_TABLE_BODY:
			case W.IN_ROW:
				Wr(this, e);
				break;
			case W.IN_TABLE_TEXT:
				ni(this, e);
				break;
			case W.IN_COLUMN_GROUP:
				li(this, e);
				break;
			case W.AFTER_BODY:
				Ti(this, e);
				break;
			case W.AFTER_AFTER_BODY:
				ji(this, e);
				break;
		}
	}
	onNullCharacter(e) {
		if (this.skipNextNewLine = !1, this.tokenizer.inForeignNode) {
			Ni(this, e);
			return;
		}
		switch (this.insertionMode) {
			case W.INITIAL:
				G(this, e);
				break;
			case W.BEFORE_HTML:
				K(this, e);
				break;
			case W.BEFORE_HEAD:
				q(this, e);
				break;
			case W.IN_HEAD:
				X(this, e);
				break;
			case W.IN_HEAD_NO_SCRIPT:
				Wn(this, e);
				break;
			case W.AFTER_HEAD:
				qn(this, e);
				break;
			case W.TEXT:
				this._insertCharacters(e);
				break;
			case W.IN_TABLE:
			case W.IN_TABLE_BODY:
			case W.IN_ROW:
				Wr(this, e);
				break;
			case W.IN_COLUMN_GROUP:
				li(this, e);
				break;
			case W.AFTER_BODY:
				Ti(this, e);
				break;
			case W.AFTER_AFTER_BODY:
				ji(this, e);
				break;
		}
	}
	onComment(e) {
		if (this.skipNextNewLine = !1, this.currentNotInHTML) {
			Mn(this, e);
			return;
		}
		switch (this.insertionMode) {
			case W.INITIAL:
			case W.BEFORE_HTML:
			case W.BEFORE_HEAD:
			case W.IN_HEAD:
			case W.IN_HEAD_NO_SCRIPT:
			case W.AFTER_HEAD:
			case W.IN_BODY:
			case W.IN_TABLE:
			case W.IN_CAPTION:
			case W.IN_COLUMN_GROUP:
			case W.IN_TABLE_BODY:
			case W.IN_ROW:
			case W.IN_CELL:
			case W.IN_SELECT:
			case W.IN_SELECT_IN_TABLE:
			case W.IN_TEMPLATE:
			case W.IN_FRAMESET:
			case W.AFTER_FRAMESET:
				Mn(this, e);
				break;
			case W.IN_TABLE_TEXT:
				ri(this, e);
				break;
			case W.AFTER_BODY:
				Nn(this, e);
				break;
			case W.AFTER_AFTER_BODY:
			case W.AFTER_AFTER_FRAMESET:
				Pn(this, e);
				break;
		}
	}
	onDoctype(e) {
		switch (this.skipNextNewLine = !1, this.insertionMode) {
			case W.INITIAL:
				In(this, e);
				break;
			case W.BEFORE_HEAD:
			case W.IN_HEAD:
			case W.IN_HEAD_NO_SCRIPT:
			case W.AFTER_HEAD:
				this._err(e, T.misplacedDoctype);
				break;
			case W.IN_TABLE_TEXT:
				ri(this, e);
				break;
		}
	}
	onStartTag(e) {
		this.skipNextNewLine = !1, this.currentToken = e, this._processStartTag(e), e.selfClosing && !e.ackSelfClosing && this._err(e, T.nonVoidHtmlElementStartTagWithTrailingSolidus);
	}
	_processStartTag(e) {
		this.shouldProcessStartTagTokenInForeignContent(e) ? Ii(this, e) : this._startTagOutsideForeignContent(e);
	}
	_startTagOutsideForeignContent(e) {
		switch (this.insertionMode) {
			case W.INITIAL:
				G(this, e);
				break;
			case W.BEFORE_HTML:
				Ln(this, e);
				break;
			case W.BEFORE_HEAD:
				zn(this, e);
				break;
			case W.IN_HEAD:
				J(this, e);
				break;
			case W.IN_HEAD_NO_SCRIPT:
				Hn(this, e);
				break;
			case W.AFTER_HEAD:
				Gn(this, e);
				break;
			case W.IN_BODY:
				Z(this, e);
				break;
			case W.IN_TABLE:
				Q(this, e);
				break;
			case W.IN_TABLE_TEXT:
				ri(this, e);
				break;
			case W.IN_CAPTION:
				ai(this, e);
				break;
			case W.IN_COLUMN_GROUP:
				si(this, e);
				break;
			case W.IN_TABLE_BODY:
				ui(this, e);
				break;
			case W.IN_ROW:
				fi(this, e);
				break;
			case W.IN_CELL:
				mi(this, e);
				break;
			case W.IN_SELECT:
				gi(this, e);
				break;
			case W.IN_SELECT_IN_TABLE:
				vi(this, e);
				break;
			case W.IN_TEMPLATE:
				bi(this, e);
				break;
			case W.AFTER_BODY:
				Ci(this, e);
				break;
			case W.IN_FRAMESET:
				Ei(this, e);
				break;
			case W.AFTER_FRAMESET:
				Oi(this, e);
				break;
			case W.AFTER_AFTER_BODY:
				Ai(this, e);
				break;
			case W.AFTER_AFTER_FRAMESET:
				Mi(this, e);
				break;
		}
	}
	onEndTag(e) {
		this.skipNextNewLine = !1, this.currentToken = e, this.currentNotInHTML ? Li(this, e) : this._endTagOutsideForeignContent(e);
	}
	_endTagOutsideForeignContent(e) {
		switch (this.insertionMode) {
			case W.INITIAL:
				G(this, e);
				break;
			case W.BEFORE_HTML:
				Rn(this, e);
				break;
			case W.BEFORE_HEAD:
				Bn(this, e);
				break;
			case W.IN_HEAD:
				Vn(this, e);
				break;
			case W.IN_HEAD_NO_SCRIPT:
				Un(this, e);
				break;
			case W.AFTER_HEAD:
				Kn(this, e);
				break;
			case W.IN_BODY:
				Br(this, e);
				break;
			case W.TEXT:
				Hr(this, e);
				break;
			case W.IN_TABLE:
				$r(this, e);
				break;
			case W.IN_TABLE_TEXT:
				ri(this, e);
				break;
			case W.IN_CAPTION:
				oi(this, e);
				break;
			case W.IN_COLUMN_GROUP:
				ci(this, e);
				break;
			case W.IN_TABLE_BODY:
				di(this, e);
				break;
			case W.IN_ROW:
				pi(this, e);
				break;
			case W.IN_CELL:
				hi(this, e);
				break;
			case W.IN_SELECT:
				_i(this, e);
				break;
			case W.IN_SELECT_IN_TABLE:
				yi(this, e);
				break;
			case W.IN_TEMPLATE:
				xi(this, e);
				break;
			case W.AFTER_BODY:
				wi(this, e);
				break;
			case W.IN_FRAMESET:
				Di(this, e);
				break;
			case W.AFTER_FRAMESET:
				ki(this, e);
				break;
			case W.AFTER_AFTER_BODY:
				ji(this, e);
				break;
		}
	}
	onEof(e) {
		switch (this.insertionMode) {
			case W.INITIAL:
				G(this, e);
				break;
			case W.BEFORE_HTML:
				K(this, e);
				break;
			case W.BEFORE_HEAD:
				q(this, e);
				break;
			case W.IN_HEAD:
				X(this, e);
				break;
			case W.IN_HEAD_NO_SCRIPT:
				Wn(this, e);
				break;
			case W.AFTER_HEAD:
				qn(this, e);
				break;
			case W.IN_BODY:
			case W.IN_TABLE:
			case W.IN_CAPTION:
			case W.IN_COLUMN_GROUP:
			case W.IN_TABLE_BODY:
			case W.IN_ROW:
			case W.IN_CELL:
			case W.IN_SELECT:
			case W.IN_SELECT_IN_TABLE:
				Vr(this, e);
				break;
			case W.TEXT:
				Ur(this, e);
				break;
			case W.IN_TABLE_TEXT:
				ri(this, e);
				break;
			case W.IN_TEMPLATE:
				Si(this, e);
				break;
			case W.AFTER_BODY:
			case W.IN_FRAMESET:
			case W.AFTER_FRAMESET:
			case W.AFTER_AFTER_BODY:
			case W.AFTER_AFTER_FRAMESET:
				Fn(this, e);
				break;
		}
	}
	onWhitespaceCharacter(e) {
		if (this.skipNextNewLine && (this.skipNextNewLine = !1, e.chars.charCodeAt(0) === C.LINE_FEED)) {
			if (e.chars.length === 1) return;
			e.chars = e.chars.substr(1);
		}
		if (this.tokenizer.inForeignNode) {
			this._insertCharacters(e);
			return;
		}
		switch (this.insertionMode) {
			case W.IN_HEAD:
			case W.IN_HEAD_NO_SCRIPT:
			case W.AFTER_HEAD:
			case W.TEXT:
			case W.IN_COLUMN_GROUP:
			case W.IN_SELECT:
			case W.IN_SELECT_IN_TABLE:
			case W.IN_FRAMESET:
			case W.AFTER_FRAMESET:
				this._insertCharacters(e);
				break;
			case W.IN_BODY:
			case W.IN_CAPTION:
			case W.IN_CELL:
			case W.IN_TEMPLATE:
			case W.AFTER_BODY:
			case W.AFTER_AFTER_BODY:
			case W.AFTER_AFTER_FRAMESET:
				Yn(this, e);
				break;
			case W.IN_TABLE:
			case W.IN_TABLE_BODY:
			case W.IN_ROW:
				Wr(this, e);
				break;
			case W.IN_TABLE_TEXT:
				ti(this, e);
				break;
		}
	}
};
function Tn(e, t) {
	let n = e.activeFormattingElements.getElementEntryInScopeWithTagName(t.tagName);
	return n ? e.openElements.contains(n.element) ? e.openElements.hasInScope(t.tagID) || (n = null) : (e.activeFormattingElements.removeEntry(n), n = null) : zr(e, t), n;
}
function En(e, t) {
	let n = null, r = e.openElements.stackTop;
	for (; r >= 0; r--) {
		let i = e.openElements.items[r];
		if (i === t.element) break;
		e._isSpecialElement(i, e.openElements.tagIDs[r]) && (n = i);
	}
	return n || (e.openElements.shortenToLength(Math.max(r, 0)), e.activeFormattingElements.removeEntry(t)), n;
}
function Dn(e, t, n) {
	let r = t, i = e.openElements.getCommonAncestor(t);
	for (let a = 0, o = i; o !== n; a++, o = i) {
		i = e.openElements.getCommonAncestor(o);
		let n = e.activeFormattingElements.getElementEntry(o), s = n && a >= bn;
		!n || s ? (s && e.activeFormattingElements.removeEntry(n), e.openElements.remove(o)) : (o = On(e, n), r === t && (e.activeFormattingElements.bookmark = n), e.treeAdapter.detachNode(r), e.treeAdapter.appendChild(o, r), r = o);
	}
	return r;
}
function On(e, t) {
	let n = e.treeAdapter.getNamespaceURI(t.element), r = e.treeAdapter.createElement(t.token.tagName, n, t.token.attrs);
	return e.openElements.replace(t.element, r), t.element = r, r;
}
function kn(e, t, n) {
	let r = I(e.treeAdapter.getTagName(t));
	if (e._isElementCausesFosterParenting(r)) e._fosterParentElement(n);
	else {
		let i = e.treeAdapter.getNamespaceURI(t);
		r === F.TEMPLATE && i === j.HTML && (t = e.treeAdapter.getTemplateContent(t)), e.treeAdapter.appendChild(t, n);
	}
}
function An(e, t, n) {
	let r = e.treeAdapter.getNamespaceURI(n.element), { token: i } = n, a = e.treeAdapter.createElement(i.tagName, r, i.attrs);
	e._adoptNodes(t, a), e.treeAdapter.appendChild(t, a), e.activeFormattingElements.insertElementAfterBookmark(a, i), e.activeFormattingElements.removeEntry(n), e.openElements.remove(n.element), e.openElements.insertAfter(t, a, i.tagID);
}
function jn(e, t) {
	for (let n = 0; n < yn; n++) {
		let n = Tn(e, t);
		if (!n) break;
		let r = En(e, n);
		if (!r) break;
		e.activeFormattingElements.bookmark = n;
		let i = Dn(e, r, n.element), a = e.openElements.getCommonAncestor(n.element);
		e.treeAdapter.detachNode(i), a && kn(e, a, i), An(e, r, n);
	}
}
function Mn(e, t) {
	e._appendCommentNode(t, e.openElements.currentTmplContentOrNode);
}
function Nn(e, t) {
	e._appendCommentNode(t, e.openElements.items[0]);
}
function Pn(e, t) {
	e._appendCommentNode(t, e.document);
}
function Fn(e, t) {
	if (e.stopped = !0, t.location) {
		let n = e.fragmentContext ? 0 : 2;
		for (let r = e.openElements.stackTop; r >= n; r--) e._setEndLocation(e.openElements.items[r], t);
		if (!e.fragmentContext && e.openElements.stackTop >= 0) {
			let n = e.openElements.items[0], r = e.treeAdapter.getNodeSourceCodeLocation(n);
			if (r && !r.endTag && (e._setEndLocation(n, t), e.openElements.stackTop >= 1)) {
				let n = e.openElements.items[1], r = e.treeAdapter.getNodeSourceCodeLocation(n);
				r && !r.endTag && e._setEndLocation(n, t);
			}
		}
	}
}
function In(e, t) {
	e._setDocumentType(t);
	let n = t.forceQuirks ? N.QUIRKS : tn(t);
	en(t) || e._err(t, T.nonConformingDoctype), e.treeAdapter.setDocumentMode(e.document, n), e.insertionMode = W.BEFORE_HTML;
}
function G(e, t) {
	e._err(t, T.missingDoctype, !0), e.treeAdapter.setDocumentMode(e.document, N.QUIRKS), e.insertionMode = W.BEFORE_HTML, e._processToken(t);
}
function Ln(e, t) {
	t.tagID === F.HTML ? (e._insertElement(t, j.HTML), e.insertionMode = W.BEFORE_HEAD) : K(e, t);
}
function Rn(e, t) {
	let n = t.tagID;
	(n === F.HTML || n === F.HEAD || n === F.BODY || n === F.BR) && K(e, t);
}
function K(e, t) {
	e._insertFakeRootElement(), e.insertionMode = W.BEFORE_HEAD, e._processToken(t);
}
function zn(e, t) {
	switch (t.tagID) {
		case F.HTML:
			Z(e, t);
			break;
		case F.HEAD:
			e._insertElement(t, j.HTML), e.headElement = e.openElements.current, e.insertionMode = W.IN_HEAD;
			break;
		default: q(e, t);
	}
}
function Bn(e, t) {
	let n = t.tagID;
	n === F.HEAD || n === F.BODY || n === F.HTML || n === F.BR ? q(e, t) : e._err(t, T.endTagWithoutMatchingOpenElement);
}
function q(e, t) {
	e._insertFakeElement(P.HEAD, F.HEAD), e.headElement = e.openElements.current, e.insertionMode = W.IN_HEAD, e._processToken(t);
}
function J(e, t) {
	switch (t.tagID) {
		case F.HTML:
			Z(e, t);
			break;
		case F.BASE:
		case F.BASEFONT:
		case F.BGSOUND:
		case F.LINK:
		case F.META:
			e._appendElement(t, j.HTML), t.ackSelfClosing = !0;
			break;
		case F.TITLE:
			e._switchToTextParsing(t, z.RCDATA);
			break;
		case F.NOSCRIPT:
			e.options.scriptingEnabled ? e._switchToTextParsing(t, z.RAWTEXT) : (e._insertElement(t, j.HTML), e.insertionMode = W.IN_HEAD_NO_SCRIPT);
			break;
		case F.NOFRAMES:
		case F.STYLE:
			e._switchToTextParsing(t, z.RAWTEXT);
			break;
		case F.SCRIPT:
			e._switchToTextParsing(t, z.SCRIPT_DATA);
			break;
		case F.TEMPLATE:
			e._insertTemplate(t), e.activeFormattingElements.insertMarker(), e.framesetOk = !1, e.insertionMode = W.IN_TEMPLATE, e.tmplInsertionModeStack.unshift(W.IN_TEMPLATE);
			break;
		case F.HEAD:
			e._err(t, T.misplacedStartTagForHeadElement);
			break;
		default: X(e, t);
	}
}
function Vn(e, t) {
	switch (t.tagID) {
		case F.HEAD:
			e.openElements.pop(), e.insertionMode = W.AFTER_HEAD;
			break;
		case F.BODY:
		case F.BR:
		case F.HTML:
			X(e, t);
			break;
		case F.TEMPLATE:
			Y(e, t);
			break;
		default: e._err(t, T.endTagWithoutMatchingOpenElement);
	}
}
function Y(e, t) {
	e.openElements.tmplCount > 0 ? (e.openElements.generateImpliedEndTagsThoroughly(), e.openElements.currentTagId !== F.TEMPLATE && e._err(t, T.closingOfElementWithOpenChildElements), e.openElements.popUntilTagNamePopped(F.TEMPLATE), e.activeFormattingElements.clearToLastMarker(), e.tmplInsertionModeStack.shift(), e._resetInsertionMode()) : e._err(t, T.endTagWithoutMatchingOpenElement);
}
function X(e, t) {
	e.openElements.pop(), e.insertionMode = W.AFTER_HEAD, e._processToken(t);
}
function Hn(e, t) {
	switch (t.tagID) {
		case F.HTML:
			Z(e, t);
			break;
		case F.BASEFONT:
		case F.BGSOUND:
		case F.HEAD:
		case F.LINK:
		case F.META:
		case F.NOFRAMES:
		case F.STYLE:
			J(e, t);
			break;
		case F.NOSCRIPT:
			e._err(t, T.nestedNoscriptInHead);
			break;
		default: Wn(e, t);
	}
}
function Un(e, t) {
	switch (t.tagID) {
		case F.NOSCRIPT:
			e.openElements.pop(), e.insertionMode = W.IN_HEAD;
			break;
		case F.BR:
			Wn(e, t);
			break;
		default: e._err(t, T.endTagWithoutMatchingOpenElement);
	}
}
function Wn(e, t) {
	let n = t.type === E.EOF ? T.openElementsLeftAfterEof : T.disallowedContentInNoscriptInHead;
	e._err(t, n), e.openElements.pop(), e.insertionMode = W.IN_HEAD, e._processToken(t);
}
function Gn(e, t) {
	switch (t.tagID) {
		case F.HTML:
			Z(e, t);
			break;
		case F.BODY:
			e._insertElement(t, j.HTML), e.framesetOk = !1, e.insertionMode = W.IN_BODY;
			break;
		case F.FRAMESET:
			e._insertElement(t, j.HTML), e.insertionMode = W.IN_FRAMESET;
			break;
		case F.BASE:
		case F.BASEFONT:
		case F.BGSOUND:
		case F.LINK:
		case F.META:
		case F.NOFRAMES:
		case F.SCRIPT:
		case F.STYLE:
		case F.TEMPLATE:
		case F.TITLE:
			e._err(t, T.abandonedHeadElementChild), e.openElements.push(e.headElement, F.HEAD), J(e, t), e.openElements.remove(e.headElement);
			break;
		case F.HEAD:
			e._err(t, T.misplacedStartTagForHeadElement);
			break;
		default: qn(e, t);
	}
}
function Kn(e, t) {
	switch (t.tagID) {
		case F.BODY:
		case F.HTML:
		case F.BR:
			qn(e, t);
			break;
		case F.TEMPLATE:
			Y(e, t);
			break;
		default: e._err(t, T.endTagWithoutMatchingOpenElement);
	}
}
function qn(e, t) {
	e._insertFakeElement(P.BODY, F.BODY), e.insertionMode = W.IN_BODY, Jn(e, t);
}
function Jn(e, t) {
	switch (t.type) {
		case E.CHARACTER:
			Xn(e, t);
			break;
		case E.WHITESPACE_CHARACTER:
			Yn(e, t);
			break;
		case E.COMMENT:
			Mn(e, t);
			break;
		case E.START_TAG:
			Z(e, t);
			break;
		case E.END_TAG:
			Br(e, t);
			break;
		case E.EOF:
			Vr(e, t);
			break;
	}
}
function Yn(e, t) {
	e._reconstructActiveFormattingElements(), e._insertCharacters(t);
}
function Xn(e, t) {
	e._reconstructActiveFormattingElements(), e._insertCharacters(t), e.framesetOk = !1;
}
function Zn(e, t) {
	e.openElements.tmplCount === 0 && e.treeAdapter.adoptAttributes(e.openElements.items[0], t.attrs);
}
function Qn(e, t) {
	let n = e.openElements.tryPeekProperlyNestedBodyElement();
	n && e.openElements.tmplCount === 0 && (e.framesetOk = !1, e.treeAdapter.adoptAttributes(n, t.attrs));
}
function $n(e, t) {
	let n = e.openElements.tryPeekProperlyNestedBodyElement();
	e.framesetOk && n && (e.treeAdapter.detachNode(n), e.openElements.popAllUpToHtmlElement(), e._insertElement(t, j.HTML), e.insertionMode = W.IN_FRAMESET);
}
function er(e, t) {
	e.openElements.hasInButtonScope(F.P) && e._closePElement(), e._insertElement(t, j.HTML);
}
function tr(e, t) {
	e.openElements.hasInButtonScope(F.P) && e._closePElement(), e.openElements.currentTagId !== void 0 && xt.has(e.openElements.currentTagId) && e.openElements.pop(), e._insertElement(t, j.HTML);
}
function nr(e, t) {
	e.openElements.hasInButtonScope(F.P) && e._closePElement(), e._insertElement(t, j.HTML), e.skipNextNewLine = !0, e.framesetOk = !1;
}
function rr(e, t) {
	let n = e.openElements.tmplCount > 0;
	(!e.formElement || n) && (e.openElements.hasInButtonScope(F.P) && e._closePElement(), e._insertElement(t, j.HTML), n || (e.formElement = e.openElements.current));
}
function ir(e, t) {
	e.framesetOk = !1;
	let n = t.tagID;
	for (let t = e.openElements.stackTop; t >= 0; t--) {
		let r = e.openElements.tagIDs[t];
		if (n === F.LI && r === F.LI || (n === F.DD || n === F.DT) && (r === F.DD || r === F.DT)) {
			e.openElements.generateImpliedEndTagsWithExclusion(r), e.openElements.popUntilTagNamePopped(r);
			break;
		}
		if (r !== F.ADDRESS && r !== F.DIV && r !== F.P && e._isSpecialElement(e.openElements.items[t], r)) break;
	}
	e.openElements.hasInButtonScope(F.P) && e._closePElement(), e._insertElement(t, j.HTML);
}
function ar(e, t) {
	e.openElements.hasInButtonScope(F.P) && e._closePElement(), e._insertElement(t, j.HTML), e.tokenizer.state = z.PLAINTEXT;
}
function or(e, t) {
	e.openElements.hasInScope(F.BUTTON) && (e.openElements.generateImpliedEndTags(), e.openElements.popUntilTagNamePopped(F.BUTTON)), e._reconstructActiveFormattingElements(), e._insertElement(t, j.HTML), e.framesetOk = !1;
}
function sr(e, t) {
	let n = e.activeFormattingElements.getElementEntryInScopeWithTagName(P.A);
	n && (jn(e, t), e.openElements.remove(n.element), e.activeFormattingElements.removeEntry(n)), e._reconstructActiveFormattingElements(), e._insertElement(t, j.HTML), e.activeFormattingElements.pushElement(e.openElements.current, t);
}
function cr(e, t) {
	e._reconstructActiveFormattingElements(), e._insertElement(t, j.HTML), e.activeFormattingElements.pushElement(e.openElements.current, t);
}
function lr(e, t) {
	e._reconstructActiveFormattingElements(), e.openElements.hasInScope(F.NOBR) && (jn(e, t), e._reconstructActiveFormattingElements()), e._insertElement(t, j.HTML), e.activeFormattingElements.pushElement(e.openElements.current, t);
}
function ur(e, t) {
	e._reconstructActiveFormattingElements(), e._insertElement(t, j.HTML), e.activeFormattingElements.insertMarker(), e.framesetOk = !1;
}
function dr(e, t) {
	e.treeAdapter.getDocumentMode(e.document) !== N.QUIRKS && e.openElements.hasInButtonScope(F.P) && e._closePElement(), e._insertElement(t, j.HTML), e.framesetOk = !1, e.insertionMode = W.IN_TABLE;
}
function fr(e, t) {
	e._reconstructActiveFormattingElements(), e._appendElement(t, j.HTML), e.framesetOk = !1, t.ackSelfClosing = !0;
}
function pr(e) {
	let t = ct(e, M.TYPE);
	return t != null && t.toLowerCase() === vn;
}
function mr(e, t) {
	e._reconstructActiveFormattingElements(), e._appendElement(t, j.HTML), pr(t) || (e.framesetOk = !1), t.ackSelfClosing = !0;
}
function hr(e, t) {
	e._appendElement(t, j.HTML), t.ackSelfClosing = !0;
}
function gr(e, t) {
	e.openElements.hasInButtonScope(F.P) && e._closePElement(), e._appendElement(t, j.HTML), e.framesetOk = !1, t.ackSelfClosing = !0;
}
function _r(e, t) {
	t.tagName = P.IMG, t.tagID = F.IMG, fr(e, t);
}
function vr(e, t) {
	e._insertElement(t, j.HTML), e.skipNextNewLine = !0, e.tokenizer.state = z.RCDATA, e.originalInsertionMode = e.insertionMode, e.framesetOk = !1, e.insertionMode = W.TEXT;
}
function yr(e, t) {
	e.openElements.hasInButtonScope(F.P) && e._closePElement(), e._reconstructActiveFormattingElements(), e.framesetOk = !1, e._switchToTextParsing(t, z.RAWTEXT);
}
function br(e, t) {
	e.framesetOk = !1, e._switchToTextParsing(t, z.RAWTEXT);
}
function xr(e, t) {
	e._switchToTextParsing(t, z.RAWTEXT);
}
function Sr(e, t) {
	e._reconstructActiveFormattingElements(), e._insertElement(t, j.HTML), e.framesetOk = !1, e.insertionMode = e.insertionMode === W.IN_TABLE || e.insertionMode === W.IN_CAPTION || e.insertionMode === W.IN_TABLE_BODY || e.insertionMode === W.IN_ROW || e.insertionMode === W.IN_CELL ? W.IN_SELECT_IN_TABLE : W.IN_SELECT;
}
function Cr(e, t) {
	e.openElements.currentTagId === F.OPTION && e.openElements.pop(), e._reconstructActiveFormattingElements(), e._insertElement(t, j.HTML);
}
function wr(e, t) {
	e.openElements.hasInScope(F.RUBY) && e.openElements.generateImpliedEndTags(), e._insertElement(t, j.HTML);
}
function Tr(e, t) {
	e.openElements.hasInScope(F.RUBY) && e.openElements.generateImpliedEndTagsWithExclusion(F.RTC), e._insertElement(t, j.HTML);
}
function Er(e, t) {
	e._reconstructActiveFormattingElements(), dn(t), pn(t), t.selfClosing ? e._appendElement(t, j.MATHML) : e._insertElement(t, j.MATHML), t.ackSelfClosing = !0;
}
function Dr(e, t) {
	e._reconstructActiveFormattingElements(), fn(t), pn(t), t.selfClosing ? e._appendElement(t, j.SVG) : e._insertElement(t, j.SVG), t.ackSelfClosing = !0;
}
function Or(e, t) {
	e._reconstructActiveFormattingElements(), e._insertElement(t, j.HTML);
}
function Z(e, t) {
	switch (t.tagID) {
		case F.I:
		case F.S:
		case F.B:
		case F.U:
		case F.EM:
		case F.TT:
		case F.BIG:
		case F.CODE:
		case F.FONT:
		case F.SMALL:
		case F.STRIKE:
		case F.STRONG:
			cr(e, t);
			break;
		case F.A:
			sr(e, t);
			break;
		case F.H1:
		case F.H2:
		case F.H3:
		case F.H4:
		case F.H5:
		case F.H6:
			tr(e, t);
			break;
		case F.P:
		case F.DL:
		case F.OL:
		case F.UL:
		case F.DIV:
		case F.DIR:
		case F.NAV:
		case F.MAIN:
		case F.MENU:
		case F.ASIDE:
		case F.CENTER:
		case F.FIGURE:
		case F.FOOTER:
		case F.HEADER:
		case F.HGROUP:
		case F.DIALOG:
		case F.DETAILS:
		case F.ADDRESS:
		case F.ARTICLE:
		case F.SEARCH:
		case F.SECTION:
		case F.SUMMARY:
		case F.FIELDSET:
		case F.BLOCKQUOTE:
		case F.FIGCAPTION:
			er(e, t);
			break;
		case F.LI:
		case F.DD:
		case F.DT:
			ir(e, t);
			break;
		case F.BR:
		case F.IMG:
		case F.WBR:
		case F.AREA:
		case F.EMBED:
		case F.KEYGEN:
			fr(e, t);
			break;
		case F.HR:
			gr(e, t);
			break;
		case F.RB:
		case F.RTC:
			wr(e, t);
			break;
		case F.RT:
		case F.RP:
			Tr(e, t);
			break;
		case F.PRE:
		case F.LISTING:
			nr(e, t);
			break;
		case F.XMP:
			yr(e, t);
			break;
		case F.SVG:
			Dr(e, t);
			break;
		case F.HTML:
			Zn(e, t);
			break;
		case F.BASE:
		case F.LINK:
		case F.META:
		case F.STYLE:
		case F.TITLE:
		case F.SCRIPT:
		case F.BGSOUND:
		case F.BASEFONT:
		case F.TEMPLATE:
			J(e, t);
			break;
		case F.BODY:
			Qn(e, t);
			break;
		case F.FORM:
			rr(e, t);
			break;
		case F.NOBR:
			lr(e, t);
			break;
		case F.MATH:
			Er(e, t);
			break;
		case F.TABLE:
			dr(e, t);
			break;
		case F.INPUT:
			mr(e, t);
			break;
		case F.PARAM:
		case F.TRACK:
		case F.SOURCE:
			hr(e, t);
			break;
		case F.IMAGE:
			_r(e, t);
			break;
		case F.BUTTON:
			or(e, t);
			break;
		case F.APPLET:
		case F.OBJECT:
		case F.MARQUEE:
			ur(e, t);
			break;
		case F.IFRAME:
			br(e, t);
			break;
		case F.SELECT:
			Sr(e, t);
			break;
		case F.OPTION:
		case F.OPTGROUP:
			Cr(e, t);
			break;
		case F.NOEMBED:
		case F.NOFRAMES:
			xr(e, t);
			break;
		case F.FRAMESET:
			$n(e, t);
			break;
		case F.TEXTAREA:
			vr(e, t);
			break;
		case F.NOSCRIPT:
			e.options.scriptingEnabled ? xr(e, t) : Or(e, t);
			break;
		case F.PLAINTEXT:
			ar(e, t);
			break;
		case F.COL:
		case F.TH:
		case F.TD:
		case F.TR:
		case F.HEAD:
		case F.FRAME:
		case F.TBODY:
		case F.TFOOT:
		case F.THEAD:
		case F.CAPTION:
		case F.COLGROUP: break;
		default: Or(e, t);
	}
}
function kr(e, t) {
	if (e.openElements.hasInScope(F.BODY) && (e.insertionMode = W.AFTER_BODY, e.options.sourceCodeLocationInfo)) {
		let n = e.openElements.tryPeekProperlyNestedBodyElement();
		n && e._setEndLocation(n, t);
	}
}
function Ar(e, t) {
	e.openElements.hasInScope(F.BODY) && (e.insertionMode = W.AFTER_BODY, wi(e, t));
}
function jr(e, t) {
	let n = t.tagID;
	e.openElements.hasInScope(n) && (e.openElements.generateImpliedEndTags(), e.openElements.popUntilTagNamePopped(n));
}
function Mr(e) {
	let t = e.openElements.tmplCount > 0, { formElement: n } = e;
	t || (e.formElement = null), (n || t) && e.openElements.hasInScope(F.FORM) && (e.openElements.generateImpliedEndTags(), t ? e.openElements.popUntilTagNamePopped(F.FORM) : n && e.openElements.remove(n));
}
function Nr(e) {
	e.openElements.hasInButtonScope(F.P) || e._insertFakeElement(P.P, F.P), e._closePElement();
}
function Pr(e) {
	e.openElements.hasInListItemScope(F.LI) && (e.openElements.generateImpliedEndTagsWithExclusion(F.LI), e.openElements.popUntilTagNamePopped(F.LI));
}
function Fr(e, t) {
	let n = t.tagID;
	e.openElements.hasInScope(n) && (e.openElements.generateImpliedEndTagsWithExclusion(n), e.openElements.popUntilTagNamePopped(n));
}
function Ir(e) {
	e.openElements.hasNumberedHeaderInScope() && (e.openElements.generateImpliedEndTags(), e.openElements.popUntilNumberedHeaderPopped());
}
function Lr(e, t) {
	let n = t.tagID;
	e.openElements.hasInScope(n) && (e.openElements.generateImpliedEndTags(), e.openElements.popUntilTagNamePopped(n), e.activeFormattingElements.clearToLastMarker());
}
function Rr(e) {
	e._reconstructActiveFormattingElements(), e._insertFakeElement(P.BR, F.BR), e.openElements.pop(), e.framesetOk = !1;
}
function zr(e, t) {
	let n = t.tagName, r = t.tagID;
	for (let t = e.openElements.stackTop; t > 0; t--) {
		let i = e.openElements.items[t], a = e.openElements.tagIDs[t];
		if (r === a && (r !== F.UNKNOWN || e.treeAdapter.getTagName(i) === n)) {
			e.openElements.generateImpliedEndTagsWithExclusion(r), e.openElements.stackTop >= t && e.openElements.shortenToLength(t);
			break;
		}
		if (e._isSpecialElement(i, a)) break;
	}
}
function Br(e, t) {
	switch (t.tagID) {
		case F.A:
		case F.B:
		case F.I:
		case F.S:
		case F.U:
		case F.EM:
		case F.TT:
		case F.BIG:
		case F.CODE:
		case F.FONT:
		case F.NOBR:
		case F.SMALL:
		case F.STRIKE:
		case F.STRONG:
			jn(e, t);
			break;
		case F.P:
			Nr(e);
			break;
		case F.DL:
		case F.UL:
		case F.OL:
		case F.DIR:
		case F.DIV:
		case F.NAV:
		case F.PRE:
		case F.MAIN:
		case F.MENU:
		case F.ASIDE:
		case F.BUTTON:
		case F.CENTER:
		case F.FIGURE:
		case F.FOOTER:
		case F.HEADER:
		case F.HGROUP:
		case F.DIALOG:
		case F.ADDRESS:
		case F.ARTICLE:
		case F.DETAILS:
		case F.SEARCH:
		case F.SECTION:
		case F.SUMMARY:
		case F.LISTING:
		case F.FIELDSET:
		case F.BLOCKQUOTE:
		case F.FIGCAPTION:
			jr(e, t);
			break;
		case F.LI:
			Pr(e);
			break;
		case F.DD:
		case F.DT:
			Fr(e, t);
			break;
		case F.H1:
		case F.H2:
		case F.H3:
		case F.H4:
		case F.H5:
		case F.H6:
			Ir(e);
			break;
		case F.BR:
			Rr(e);
			break;
		case F.BODY:
			kr(e, t);
			break;
		case F.HTML:
			Ar(e, t);
			break;
		case F.FORM:
			Mr(e);
			break;
		case F.APPLET:
		case F.OBJECT:
		case F.MARQUEE:
			Lr(e, t);
			break;
		case F.TEMPLATE:
			Y(e, t);
			break;
		default: zr(e, t);
	}
}
function Vr(e, t) {
	e.tmplInsertionModeStack.length > 0 ? Si(e, t) : Fn(e, t);
}
function Hr(e, t) {
	var n;
	t.tagID === F.SCRIPT && ((n = e.scriptHandler) == null || n.call(e, e.openElements.current)), e.openElements.pop(), e.insertionMode = e.originalInsertionMode;
}
function Ur(e, t) {
	e._err(t, T.eofInElementThatCanContainOnlyText), e.openElements.pop(), e.insertionMode = e.originalInsertionMode, e.onEof(t);
}
function Wr(e, t) {
	if (e.openElements.currentTagId !== void 0 && Sn.has(e.openElements.currentTagId)) switch (e.pendingCharacterTokens.length = 0, e.hasNonWhitespacePendingCharacterToken = !1, e.originalInsertionMode = e.insertionMode, e.insertionMode = W.IN_TABLE_TEXT, t.type) {
		case E.CHARACTER:
			ni(e, t);
			break;
		case E.WHITESPACE_CHARACTER:
			ti(e, t);
			break;
	}
	else ei(e, t);
}
function Gr(e, t) {
	e.openElements.clearBackToTableContext(), e.activeFormattingElements.insertMarker(), e._insertElement(t, j.HTML), e.insertionMode = W.IN_CAPTION;
}
function Kr(e, t) {
	e.openElements.clearBackToTableContext(), e._insertElement(t, j.HTML), e.insertionMode = W.IN_COLUMN_GROUP;
}
function qr(e, t) {
	e.openElements.clearBackToTableContext(), e._insertFakeElement(P.COLGROUP, F.COLGROUP), e.insertionMode = W.IN_COLUMN_GROUP, si(e, t);
}
function Jr(e, t) {
	e.openElements.clearBackToTableContext(), e._insertElement(t, j.HTML), e.insertionMode = W.IN_TABLE_BODY;
}
function Yr(e, t) {
	e.openElements.clearBackToTableContext(), e._insertFakeElement(P.TBODY, F.TBODY), e.insertionMode = W.IN_TABLE_BODY, ui(e, t);
}
function Xr(e, t) {
	e.openElements.hasInTableScope(F.TABLE) && (e.openElements.popUntilTagNamePopped(F.TABLE), e._resetInsertionMode(), e._processStartTag(t));
}
function Zr(e, t) {
	pr(t) ? e._appendElement(t, j.HTML) : ei(e, t), t.ackSelfClosing = !0;
}
function Qr(e, t) {
	!e.formElement && e.openElements.tmplCount === 0 && (e._insertElement(t, j.HTML), e.formElement = e.openElements.current, e.openElements.pop());
}
function Q(e, t) {
	switch (t.tagID) {
		case F.TD:
		case F.TH:
		case F.TR:
			Yr(e, t);
			break;
		case F.STYLE:
		case F.SCRIPT:
		case F.TEMPLATE:
			J(e, t);
			break;
		case F.COL:
			qr(e, t);
			break;
		case F.FORM:
			Qr(e, t);
			break;
		case F.TABLE:
			Xr(e, t);
			break;
		case F.TBODY:
		case F.TFOOT:
		case F.THEAD:
			Jr(e, t);
			break;
		case F.INPUT:
			Zr(e, t);
			break;
		case F.CAPTION:
			Gr(e, t);
			break;
		case F.COLGROUP:
			Kr(e, t);
			break;
		default: ei(e, t);
	}
}
function $r(e, t) {
	switch (t.tagID) {
		case F.TABLE:
			e.openElements.hasInTableScope(F.TABLE) && (e.openElements.popUntilTagNamePopped(F.TABLE), e._resetInsertionMode());
			break;
		case F.TEMPLATE:
			Y(e, t);
			break;
		case F.BODY:
		case F.CAPTION:
		case F.COL:
		case F.COLGROUP:
		case F.HTML:
		case F.TBODY:
		case F.TD:
		case F.TFOOT:
		case F.TH:
		case F.THEAD:
		case F.TR: break;
		default: ei(e, t);
	}
}
function ei(e, t) {
	let n = e.fosterParentingEnabled;
	e.fosterParentingEnabled = !0, Jn(e, t), e.fosterParentingEnabled = n;
}
function ti(e, t) {
	e.pendingCharacterTokens.push(t);
}
function ni(e, t) {
	e.pendingCharacterTokens.push(t), e.hasNonWhitespacePendingCharacterToken = !0;
}
function ri(e, t) {
	let n = 0;
	if (e.hasNonWhitespacePendingCharacterToken) for (; n < e.pendingCharacterTokens.length; n++) ei(e, e.pendingCharacterTokens[n]);
	else for (; n < e.pendingCharacterTokens.length; n++) e._insertCharacters(e.pendingCharacterTokens[n]);
	e.insertionMode = e.originalInsertionMode, e._processToken(t);
}
var ii = /* @__PURE__ */ new Set([
	F.CAPTION,
	F.COL,
	F.COLGROUP,
	F.TBODY,
	F.TD,
	F.TFOOT,
	F.TH,
	F.THEAD,
	F.TR
]);
function ai(e, t) {
	let n = t.tagID;
	ii.has(n) ? e.openElements.hasInTableScope(F.CAPTION) && (e.openElements.generateImpliedEndTags(), e.openElements.popUntilTagNamePopped(F.CAPTION), e.activeFormattingElements.clearToLastMarker(), e.insertionMode = W.IN_TABLE, Q(e, t)) : Z(e, t);
}
function oi(e, t) {
	let n = t.tagID;
	switch (n) {
		case F.CAPTION:
		case F.TABLE:
			e.openElements.hasInTableScope(F.CAPTION) && (e.openElements.generateImpliedEndTags(), e.openElements.popUntilTagNamePopped(F.CAPTION), e.activeFormattingElements.clearToLastMarker(), e.insertionMode = W.IN_TABLE, n === F.TABLE && $r(e, t));
			break;
		case F.BODY:
		case F.COL:
		case F.COLGROUP:
		case F.HTML:
		case F.TBODY:
		case F.TD:
		case F.TFOOT:
		case F.TH:
		case F.THEAD:
		case F.TR: break;
		default: Br(e, t);
	}
}
function si(e, t) {
	switch (t.tagID) {
		case F.HTML:
			Z(e, t);
			break;
		case F.COL:
			e._appendElement(t, j.HTML), t.ackSelfClosing = !0;
			break;
		case F.TEMPLATE:
			J(e, t);
			break;
		default: li(e, t);
	}
}
function ci(e, t) {
	switch (t.tagID) {
		case F.COLGROUP:
			e.openElements.currentTagId === F.COLGROUP && (e.openElements.pop(), e.insertionMode = W.IN_TABLE);
			break;
		case F.TEMPLATE:
			Y(e, t);
			break;
		case F.COL: break;
		default: li(e, t);
	}
}
function li(e, t) {
	e.openElements.currentTagId === F.COLGROUP && (e.openElements.pop(), e.insertionMode = W.IN_TABLE, e._processToken(t));
}
function ui(e, t) {
	switch (t.tagID) {
		case F.TR:
			e.openElements.clearBackToTableBodyContext(), e._insertElement(t, j.HTML), e.insertionMode = W.IN_ROW;
			break;
		case F.TH:
		case F.TD:
			e.openElements.clearBackToTableBodyContext(), e._insertFakeElement(P.TR, F.TR), e.insertionMode = W.IN_ROW, fi(e, t);
			break;
		case F.CAPTION:
		case F.COL:
		case F.COLGROUP:
		case F.TBODY:
		case F.TFOOT:
		case F.THEAD:
			e.openElements.hasTableBodyContextInTableScope() && (e.openElements.clearBackToTableBodyContext(), e.openElements.pop(), e.insertionMode = W.IN_TABLE, Q(e, t));
			break;
		default: Q(e, t);
	}
}
function di(e, t) {
	let n = t.tagID;
	switch (t.tagID) {
		case F.TBODY:
		case F.TFOOT:
		case F.THEAD:
			e.openElements.hasInTableScope(n) && (e.openElements.clearBackToTableBodyContext(), e.openElements.pop(), e.insertionMode = W.IN_TABLE);
			break;
		case F.TABLE:
			e.openElements.hasTableBodyContextInTableScope() && (e.openElements.clearBackToTableBodyContext(), e.openElements.pop(), e.insertionMode = W.IN_TABLE, $r(e, t));
			break;
		case F.BODY:
		case F.CAPTION:
		case F.COL:
		case F.COLGROUP:
		case F.HTML:
		case F.TD:
		case F.TH:
		case F.TR: break;
		default: $r(e, t);
	}
}
function fi(e, t) {
	switch (t.tagID) {
		case F.TH:
		case F.TD:
			e.openElements.clearBackToTableRowContext(), e._insertElement(t, j.HTML), e.insertionMode = W.IN_CELL, e.activeFormattingElements.insertMarker();
			break;
		case F.CAPTION:
		case F.COL:
		case F.COLGROUP:
		case F.TBODY:
		case F.TFOOT:
		case F.THEAD:
		case F.TR:
			e.openElements.hasInTableScope(F.TR) && (e.openElements.clearBackToTableRowContext(), e.openElements.pop(), e.insertionMode = W.IN_TABLE_BODY, ui(e, t));
			break;
		default: Q(e, t);
	}
}
function pi(e, t) {
	switch (t.tagID) {
		case F.TR:
			e.openElements.hasInTableScope(F.TR) && (e.openElements.clearBackToTableRowContext(), e.openElements.pop(), e.insertionMode = W.IN_TABLE_BODY);
			break;
		case F.TABLE:
			e.openElements.hasInTableScope(F.TR) && (e.openElements.clearBackToTableRowContext(), e.openElements.pop(), e.insertionMode = W.IN_TABLE_BODY, di(e, t));
			break;
		case F.TBODY:
		case F.TFOOT:
		case F.THEAD:
			(e.openElements.hasInTableScope(t.tagID) || e.openElements.hasInTableScope(F.TR)) && (e.openElements.clearBackToTableRowContext(), e.openElements.pop(), e.insertionMode = W.IN_TABLE_BODY, di(e, t));
			break;
		case F.BODY:
		case F.CAPTION:
		case F.COL:
		case F.COLGROUP:
		case F.HTML:
		case F.TD:
		case F.TH: break;
		default: $r(e, t);
	}
}
function mi(e, t) {
	let n = t.tagID;
	ii.has(n) ? (e.openElements.hasInTableScope(F.TD) || e.openElements.hasInTableScope(F.TH)) && (e._closeTableCell(), fi(e, t)) : Z(e, t);
}
function hi(e, t) {
	let n = t.tagID;
	switch (n) {
		case F.TD:
		case F.TH:
			e.openElements.hasInTableScope(n) && (e.openElements.generateImpliedEndTags(), e.openElements.popUntilTagNamePopped(n), e.activeFormattingElements.clearToLastMarker(), e.insertionMode = W.IN_ROW);
			break;
		case F.TABLE:
		case F.TBODY:
		case F.TFOOT:
		case F.THEAD:
		case F.TR:
			e.openElements.hasInTableScope(n) && (e._closeTableCell(), pi(e, t));
			break;
		case F.BODY:
		case F.CAPTION:
		case F.COL:
		case F.COLGROUP:
		case F.HTML: break;
		default: Br(e, t);
	}
}
function gi(e, t) {
	switch (t.tagID) {
		case F.HTML:
			Z(e, t);
			break;
		case F.OPTION:
			e.openElements.currentTagId === F.OPTION && e.openElements.pop(), e._insertElement(t, j.HTML);
			break;
		case F.OPTGROUP:
			e.openElements.currentTagId === F.OPTION && e.openElements.pop(), e.openElements.currentTagId === F.OPTGROUP && e.openElements.pop(), e._insertElement(t, j.HTML);
			break;
		case F.HR:
			e.openElements.currentTagId === F.OPTION && e.openElements.pop(), e.openElements.currentTagId === F.OPTGROUP && e.openElements.pop(), e._appendElement(t, j.HTML), t.ackSelfClosing = !0;
			break;
		case F.INPUT:
		case F.KEYGEN:
		case F.TEXTAREA:
		case F.SELECT:
			e.openElements.hasInSelectScope(F.SELECT) && (e.openElements.popUntilTagNamePopped(F.SELECT), e._resetInsertionMode(), t.tagID !== F.SELECT && e._processStartTag(t));
			break;
		case F.SCRIPT:
		case F.TEMPLATE:
			J(e, t);
			break;
	}
}
function _i(e, t) {
	switch (t.tagID) {
		case F.OPTGROUP:
			e.openElements.stackTop > 0 && e.openElements.currentTagId === F.OPTION && e.openElements.tagIDs[e.openElements.stackTop - 1] === F.OPTGROUP && e.openElements.pop(), e.openElements.currentTagId === F.OPTGROUP && e.openElements.pop();
			break;
		case F.OPTION:
			e.openElements.currentTagId === F.OPTION && e.openElements.pop();
			break;
		case F.SELECT:
			e.openElements.hasInSelectScope(F.SELECT) && (e.openElements.popUntilTagNamePopped(F.SELECT), e._resetInsertionMode());
			break;
		case F.TEMPLATE:
			Y(e, t);
			break;
	}
}
function vi(e, t) {
	let n = t.tagID;
	n === F.CAPTION || n === F.TABLE || n === F.TBODY || n === F.TFOOT || n === F.THEAD || n === F.TR || n === F.TD || n === F.TH ? (e.openElements.popUntilTagNamePopped(F.SELECT), e._resetInsertionMode(), e._processStartTag(t)) : gi(e, t);
}
function yi(e, t) {
	let n = t.tagID;
	n === F.CAPTION || n === F.TABLE || n === F.TBODY || n === F.TFOOT || n === F.THEAD || n === F.TR || n === F.TD || n === F.TH ? e.openElements.hasInTableScope(n) && (e.openElements.popUntilTagNamePopped(F.SELECT), e._resetInsertionMode(), e.onEndTag(t)) : _i(e, t);
}
function bi(e, t) {
	switch (t.tagID) {
		case F.BASE:
		case F.BASEFONT:
		case F.BGSOUND:
		case F.LINK:
		case F.META:
		case F.NOFRAMES:
		case F.SCRIPT:
		case F.STYLE:
		case F.TEMPLATE:
		case F.TITLE:
			J(e, t);
			break;
		case F.CAPTION:
		case F.COLGROUP:
		case F.TBODY:
		case F.TFOOT:
		case F.THEAD:
			e.tmplInsertionModeStack[0] = W.IN_TABLE, e.insertionMode = W.IN_TABLE, Q(e, t);
			break;
		case F.COL:
			e.tmplInsertionModeStack[0] = W.IN_COLUMN_GROUP, e.insertionMode = W.IN_COLUMN_GROUP, si(e, t);
			break;
		case F.TR:
			e.tmplInsertionModeStack[0] = W.IN_TABLE_BODY, e.insertionMode = W.IN_TABLE_BODY, ui(e, t);
			break;
		case F.TD:
		case F.TH:
			e.tmplInsertionModeStack[0] = W.IN_ROW, e.insertionMode = W.IN_ROW, fi(e, t);
			break;
		default: e.tmplInsertionModeStack[0] = W.IN_BODY, e.insertionMode = W.IN_BODY, Z(e, t);
	}
}
function xi(e, t) {
	t.tagID === F.TEMPLATE && Y(e, t);
}
function Si(e, t) {
	e.openElements.tmplCount > 0 ? (e.openElements.popUntilTagNamePopped(F.TEMPLATE), e.activeFormattingElements.clearToLastMarker(), e.tmplInsertionModeStack.shift(), e._resetInsertionMode(), e.onEof(t)) : Fn(e, t);
}
function Ci(e, t) {
	t.tagID === F.HTML ? Z(e, t) : Ti(e, t);
}
function wi(e, t) {
	var n;
	if (t.tagID === F.HTML) {
		if (e.fragmentContext || (e.insertionMode = W.AFTER_AFTER_BODY), e.options.sourceCodeLocationInfo && e.openElements.tagIDs[0] === F.HTML) {
			e._setEndLocation(e.openElements.items[0], t);
			let r = e.openElements.items[1];
			r && !((n = e.treeAdapter.getNodeSourceCodeLocation(r)) != null && n.endTag) && e._setEndLocation(r, t);
		}
	} else Ti(e, t);
}
function Ti(e, t) {
	e.insertionMode = W.IN_BODY, Jn(e, t);
}
function Ei(e, t) {
	switch (t.tagID) {
		case F.HTML:
			Z(e, t);
			break;
		case F.FRAMESET:
			e._insertElement(t, j.HTML);
			break;
		case F.FRAME:
			e._appendElement(t, j.HTML), t.ackSelfClosing = !0;
			break;
		case F.NOFRAMES:
			J(e, t);
			break;
	}
}
function Di(e, t) {
	t.tagID === F.FRAMESET && !e.openElements.isRootHtmlElementCurrent() && (e.openElements.pop(), !e.fragmentContext && e.openElements.currentTagId !== F.FRAMESET && (e.insertionMode = W.AFTER_FRAMESET));
}
function Oi(e, t) {
	switch (t.tagID) {
		case F.HTML:
			Z(e, t);
			break;
		case F.NOFRAMES:
			J(e, t);
			break;
	}
}
function ki(e, t) {
	t.tagID === F.HTML && (e.insertionMode = W.AFTER_AFTER_FRAMESET);
}
function Ai(e, t) {
	t.tagID === F.HTML ? Z(e, t) : ji(e, t);
}
function ji(e, t) {
	e.insertionMode = W.IN_BODY, Jn(e, t);
}
function Mi(e, t) {
	switch (t.tagID) {
		case F.HTML:
			Z(e, t);
			break;
		case F.NOFRAMES:
			J(e, t);
			break;
	}
}
function Ni(e, t) {
	t.chars = S, e._insertCharacters(t);
}
function Pi(e, t) {
	e._insertCharacters(t), e.framesetOk = !1;
}
function Fi(e) {
	for (; e.treeAdapter.getNamespaceURI(e.openElements.current) !== j.HTML && e.openElements.currentTagId !== void 0 && !e._isIntegrationPoint(e.openElements.currentTagId, e.openElements.current);) e.openElements.pop();
}
function Ii(e, t) {
	if (un(t)) Fi(e), e._startTagOutsideForeignContent(t);
	else {
		let n = e._getAdjustedCurrentElement(), r = e.treeAdapter.getNamespaceURI(n);
		r === j.MATHML ? dn(t) : r === j.SVG && (mn(t), fn(t)), pn(t), t.selfClosing ? e._appendElement(t, r) : e._insertElement(t, r), t.ackSelfClosing = !0;
	}
}
function Li(e, t) {
	if (t.tagID === F.P || t.tagID === F.BR) {
		Fi(e), e._endTagOutsideForeignContent(t);
		return;
	}
	for (let n = e.openElements.stackTop; n > 0; n--) {
		let r = e.openElements.items[n];
		if (e.treeAdapter.getNamespaceURI(r) === j.HTML) {
			e._endTagOutsideForeignContent(t);
			break;
		}
		let i = e.treeAdapter.getTagName(r);
		if (i.toLowerCase() === t.tagName) {
			t.tagName = i, e.openElements.shortenToLength(n);
			break;
		}
	}
}
P.AREA, P.BASE, P.BASEFONT, P.BGSOUND, P.BR, P.COL, P.EMBED, P.FRAME, P.HR, P.IMG, P.INPUT, P.KEYGEN, P.LINK, P.META, P.PARAM, P.SOURCE, P.TRACK, P.WBR;
function Ri(e, t, r, i) {
	let a, o, s;
	o = t, s = r, a = i, n(e, o, c, a);
	function c(e, t) {
		let n = t[t.length - 1], r = n ? n.children.indexOf(e) : void 0;
		return s(e, r, n);
	}
}
var zi = /<(\/?)(iframe|noembed|noframes|plaintext|script|style|textarea|title|xmp)(?=[\t\n\f\r />])/gi, Bi = /* @__PURE__ */ new Set([
	"mdxFlowExpression",
	"mdxJsxFlowElement",
	"mdxJsxTextElement",
	"mdxTextExpression",
	"mdxjsEsm"
]), Vi = {
	sourceCodeLocationInfo: !0,
	scriptingEnabled: !1
};
function Hi(e, t) {
	let n = ta(e), i = ie("type", {
		handlers: {
			root: Wi,
			element: Gi,
			text: Ki,
			comment: Yi,
			doctype: qi,
			raw: Xi
		},
		unknown: Zi
	}), a = {
		parser: n ? new wn(Vi) : wn.getFragmentParser(void 0, Vi),
		handle(e) {
			i(e, a);
		},
		stitches: !1,
		options: t || {}
	};
	i(e, a), $(a, r());
	let o = le(n ? a.parser.document : a.parser.getFragment(), { file: a.options.file });
	return a.stitches && Ri(o, "comment", function(e, t, n) {
		let r = e;
		if (r.value.stitch && n && t !== void 0) {
			let e = n.children;
			return e[t] = r.value.stitch, t;
		}
	}), o.type === "root" && o.children.length === 1 && o.children[0].type === e.type ? o.children[0] : o;
}
function Ui(e, t) {
	let n = -1;
	if (e) for (; ++n < e.length;) t.handle(e[n]);
}
function Wi(e, t) {
	Ui(e.children, t);
}
function Gi(e, t) {
	$i(e, t), Ui(e.children, t), ea(e, t);
}
function Ki(e, t) {
	t.parser.tokenizer.state > 4 && (t.parser.tokenizer.state = 0);
	let n = {
		type: E.CHARACTER,
		chars: e.value,
		location: na(e)
	};
	$(t, r(e)), t.parser.currentToken = n, t.parser._processToken(t.parser.currentToken);
}
function qi(e, t) {
	let n = {
		type: E.DOCTYPE,
		name: "html",
		forceQuirks: !1,
		publicId: "",
		systemId: "",
		location: na(e)
	};
	$(t, r(e)), t.parser.currentToken = n, t.parser._processToken(t.parser.currentToken);
}
function Ji(e, t) {
	t.stitches = !0;
	let n = ra(e);
	"children" in e && "children" in n && (n.children = Hi({
		type: "root",
		children: e.children
	}, t.options).children), Yi({
		type: "comment",
		value: { stitch: n }
	}, t);
}
function Yi(e, t) {
	let n = e.value, i = {
		type: E.COMMENT,
		data: n,
		location: na(e)
	};
	$(t, r(e)), t.parser.currentToken = i, t.parser._processToken(t.parser.currentToken);
}
function Xi(e, t) {
	if (t.parser.tokenizer.preprocessor.html = "", t.parser.tokenizer.preprocessor.pos = -1, t.parser.tokenizer.preprocessor.lastGapPos = -2, t.parser.tokenizer.preprocessor.gapStack = [], t.parser.tokenizer.preprocessor.skipNextNewLine = !1, t.parser.tokenizer.preprocessor.lastChunkWritten = !1, t.parser.tokenizer.preprocessor.endOfChunkHit = !1, t.parser.tokenizer.preprocessor.isEol = !1, Qi(t, r(e)), t.parser.tokenizer.write(t.options.tagfilter ? e.value.replace(zi, "&lt;$1$2") : e.value, !1), t.parser.tokenizer._runParsingLoop(), t.parser.tokenizer.state === 72 || t.parser.tokenizer.state === 78) {
		t.parser.tokenizer.preprocessor.lastChunkWritten = !0;
		let e = t.parser.tokenizer._consume();
		t.parser.tokenizer._callState(e);
	}
}
function Zi(e, t) {
	let n = e;
	if (t.options.passThrough && t.options.passThrough.includes(n.type)) Ji(n, t);
	else {
		let e = "";
		throw Bi.has(n.type) && (e = ". It looks like you are using MDX nodes with `hast-util-raw` (or `rehype-raw`). If you use this because you are using remark or rehype plugins that inject `'html'` nodes, then please raise an issue with that plugin, as its a bad and slow idea. If you use this because you are using markdown syntax, then you have to configure this utility (or plugin) to pass through these nodes (see `passThrough` in docs), but you can also migrate to use the MDX syntax"), /* @__PURE__ */ Error("Cannot compile `" + n.type + "` node" + e);
	}
}
function $(e, t) {
	Qi(e, t);
	let n = e.parser.tokenizer.currentCharacterToken;
	n && n.location && (n.location.endLine = e.parser.tokenizer.preprocessor.line, n.location.endCol = e.parser.tokenizer.preprocessor.col + 1, n.location.endOffset = e.parser.tokenizer.preprocessor.offset + 1, e.parser.currentToken = n, e.parser._processToken(e.parser.currentToken)), e.parser.tokenizer.paused = !1, e.parser.tokenizer.inLoop = !1, e.parser.tokenizer.active = !1, e.parser.tokenizer.returnState = z.DATA, e.parser.tokenizer.charRefCode = -1, e.parser.tokenizer.consumedAfterSnapshot = -1, e.parser.tokenizer.currentLocation = null, e.parser.tokenizer.currentCharacterToken = null, e.parser.tokenizer.currentToken = null, e.parser.tokenizer.currentAttr = {
		name: "",
		value: ""
	};
}
function Qi(e, t) {
	if (t && t.offset !== void 0) {
		let n = {
			startLine: t.line,
			startCol: t.column,
			startOffset: t.offset,
			endLine: -1,
			endCol: -1,
			endOffset: -1
		};
		e.parser.tokenizer.preprocessor.lineStartPos = -t.column + 1, e.parser.tokenizer.preprocessor.droppedBufferSize = t.offset, e.parser.tokenizer.preprocessor.line = t.line, e.parser.tokenizer.currentLocation = n;
	}
}
function $i(e, t) {
	let n = e.tagName.toLowerCase();
	if (t.parser.tokenizer.state === z.PLAINTEXT) return;
	$(t, r(e));
	let i = t.parser.openElements.current, a = "namespaceURI" in i ? i.namespaceURI : l.html;
	a === l.html && n === "svg" && (a = l.svg);
	let o = We({
		...e,
		children: []
	}, { space: a === l.svg ? "svg" : "html" }), s = {
		type: E.START_TAG,
		tagName: n,
		tagID: I(n),
		selfClosing: !1,
		ackSelfClosing: !1,
		/* c8 ignore next */
		attrs: "attrs" in o ? o.attrs : [],
		location: na(e)
	};
	t.parser.currentToken = s, t.parser._processToken(t.parser.currentToken), t.parser.tokenizer.lastStartTagName = n;
}
function ea(t, n) {
	let r = t.tagName.toLowerCase();
	if (!n.parser.tokenizer.inForeignNode && $e.includes(r) || n.parser.tokenizer.state === z.PLAINTEXT) return;
	$(n, e(t));
	let i = {
		type: E.END_TAG,
		tagName: r,
		tagID: I(r),
		selfClosing: !1,
		ackSelfClosing: !1,
		attrs: [],
		location: na(t)
	};
	n.parser.currentToken = i, n.parser._processToken(n.parser.currentToken), r === n.parser.tokenizer.lastStartTagName && (n.parser.tokenizer.state === z.RCDATA || n.parser.tokenizer.state === z.RAWTEXT || n.parser.tokenizer.state === z.SCRIPT_DATA) && (n.parser.tokenizer.state = z.DATA);
}
function ta(e) {
	let t = e.type === "root" ? e.children[0] : e;
	return !!(t && (t.type === "doctype" || t.type === "element" && t.tagName.toLowerCase() === "html"));
}
function na(t) {
	let n = r(t) || {
		line: void 0,
		column: void 0,
		offset: void 0
	}, i = e(t) || {
		line: void 0,
		column: void 0,
		offset: void 0
	};
	return {
		startLine: n.line,
		startCol: n.column,
		startOffset: n.offset,
		endLine: i.line,
		endCol: i.column,
		endOffset: i.offset
	};
}
function ra(e) {
	return "children" in e ? a({
		...e,
		children: []
	}) : a(e);
}
function ia(e) {
	return function(t, n) {
		return Hi(t, {
			...e,
			file: n
		});
	};
}
//#endregion
export { ia as default };

//# sourceMappingURL=index-B7jxgHEF-DSFM4mVH.js.map