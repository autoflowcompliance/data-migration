import { En as e, Ka as t, Ua as n, ti as r } from "./index-Dl4ETd_L-D2oMd1k2.js";
//#region ../react/build/Html-B0_sFMha.js
var i = /* @__PURE__ */ t(n(), 1);
function a(e, t) {
	(t == null || t > e.length) && (t = e.length);
	for (var n = 0, r = Array(t); n < t; n++) r[n] = e[n];
	return r;
}
function o(e) {
	if (Array.isArray(e)) return e;
}
function s(e, t) {
	var n = e == null ? null : typeof Symbol < "u" && e[Symbol.iterator] || e["@@iterator"];
	if (n != null) {
		var r, i, a, o, s = [], c = !0, l = !1;
		try {
			if (a = (n = n.call(e)).next, t !== 0) for (; !(c = (r = a.call(n)).done) && (s.push(r.value), s.length !== t); c = !0);
		} catch (e) {
			l = !0, i = e;
		} finally {
			try {
				if (!c && n.return != null && (o = n.return(), Object(o) !== o)) return;
			} finally {
				if (l) throw i;
			}
		}
		return s;
	}
}
function c() {
	throw TypeError("Invalid attempt to destructure non-iterable instance.\nIn order to be iterable, non-array objects must have a [Symbol.iterator]() method.");
}
function l(e, t) {
	return o(e) || s(e, t) || u(e, t) || c();
}
function u(e, t) {
	if (e) {
		if (typeof e == "string") return a(e, t);
		var n = {}.toString.call(e).slice(8, -1);
		return n === "Object" && e.constructor && (n = e.constructor.name), n === "Map" || n === "Set" ? Array.from(e) : n === "Arguments" || /^(?:Ui|I)nt(?:8|16|32)(?:Clamped)?Array$/.test(n) ? a(e, t) : void 0;
	}
}
var d = Object.entries, f = Object.setPrototypeOf, ee = Object.isFrozen, te = Object.getPrototypeOf, p = Object.getOwnPropertyDescriptor, m = Object.freeze, h = Object.seal, g = Object.create, ne = typeof Reflect < "u" && Reflect, re = ne.apply, ie = ne.construct;
m ||= function(e) {
	return e;
}, h ||= function(e) {
	return e;
}, re ||= function(e, t) {
	var n = [...arguments].slice(2);
	return e.apply(t, n);
}, ie ||= function(e) {
	return new e(...[...arguments].slice(1));
};
var _ = E(Array.prototype.forEach), ae = E(Array.prototype.lastIndexOf), oe = E(Array.prototype.pop), v = E(Array.prototype.push), se = E(Array.prototype.splice), y = Array.isArray, ce = E(String.prototype.toLowerCase), le = E(String.prototype.toString), ue = E(String.prototype.match), b = E(String.prototype.replace), de = E(String.prototype.indexOf), fe = E(String.prototype.trim), pe = E(Number.prototype.toString), x = E(Boolean.prototype.toString), me = typeof BigInt > "u" ? null : E(BigInt.prototype.toString), S = typeof Symbol > "u" ? null : E(Symbol.prototype.toString), C = E(Object.prototype.hasOwnProperty), w = E(Object.prototype.toString), T = E(RegExp.prototype.test), he = ge(TypeError);
function E(e) {
	return function(t) {
		t instanceof RegExp && (t.lastIndex = 0);
		var n = [...arguments].slice(1);
		return re(e, t, n);
	};
}
function ge(e) {
	return function() {
		return ie(e, [...arguments]);
	};
}
function D(e, t) {
	let n = arguments.length > 2 && arguments[2] !== void 0 ? arguments[2] : ce;
	if (f && f(e, null), !y(t)) return e;
	let r = t.length;
	for (; r--;) {
		let i = t[r];
		if (typeof i == "string") {
			let e = n(i);
			e !== i && (ee(t) || (t[r] = e), i = e);
		}
		e[i] = !0;
	}
	return e;
}
function _e(e) {
	for (let t = 0; t < e.length; t++) C(e, t) || (e[t] = null);
	return e;
}
function O(e) {
	let t = g(null);
	for (let r of d(e)) {
		var n = l(r, 2);
		let i = n[0], a = n[1];
		C(e, i) && (y(a) ? t[i] = _e(a) : a && typeof a == "object" && a.constructor === Object ? t[i] = O(a) : t[i] = a);
	}
	return t;
}
function ve(e) {
	switch (typeof e) {
		case "string": return e;
		case "number": return pe(e);
		case "boolean": return x(e);
		case "bigint": return me ? me(e) : "0";
		case "symbol": return S ? S(e) : "Symbol()";
		case "undefined": return w(e);
		case "function":
		case "object": {
			if (e === null) return w(e);
			let t = e, n = k(t, "toString");
			if (typeof n == "function") {
				let e = n(t);
				return typeof e == "string" ? e : w(e);
			}
			return w(e);
		}
		default: return w(e);
	}
}
function k(e, t) {
	for (; e !== null;) {
		let n = p(e, t);
		if (n) {
			if (n.get) return E(n.get);
			if (typeof n.value == "function") return E(n.value);
		}
		e = te(e);
	}
	function n() {
		return null;
	}
	return n;
}
function ye(e) {
	try {
		return T(e, ""), !0;
	} catch {
		return !1;
	}
}
var be = m(/* @__PURE__ */ "a.abbr.acronym.address.area.article.aside.audio.b.bdi.bdo.big.blink.blockquote.body.br.button.canvas.caption.center.cite.code.col.colgroup.content.data.datalist.dd.decorator.del.details.dfn.dialog.dir.div.dl.dt.element.em.fieldset.figcaption.figure.font.footer.form.h1.h2.h3.h4.h5.h6.head.header.hgroup.hr.html.i.img.input.ins.kbd.label.legend.li.main.map.mark.marquee.menu.menuitem.meter.nav.nobr.ol.optgroup.option.output.p.picture.pre.progress.q.rp.rt.ruby.s.samp.search.section.select.shadow.slot.small.source.spacer.span.strike.strong.style.sub.summary.sup.table.tbody.td.template.textarea.tfoot.th.thead.time.tr.track.tt.u.ul.var.video.wbr".split(".")), xe = m(/* @__PURE__ */ "svg.a.altglyph.altglyphdef.altglyphitem.animatecolor.animatemotion.animatetransform.circle.clippath.defs.desc.ellipse.enterkeyhint.exportparts.filter.font.g.glyph.glyphref.hkern.image.inputmode.line.lineargradient.marker.mask.metadata.mpath.part.path.pattern.polygon.polyline.radialgradient.rect.stop.style.switch.symbol.text.textpath.title.tref.tspan.view.vkern".split(".")), Se = m([
	"feBlend",
	"feColorMatrix",
	"feComponentTransfer",
	"feComposite",
	"feConvolveMatrix",
	"feDiffuseLighting",
	"feDisplacementMap",
	"feDistantLight",
	"feDropShadow",
	"feFlood",
	"feFuncA",
	"feFuncB",
	"feFuncG",
	"feFuncR",
	"feGaussianBlur",
	"feImage",
	"feMerge",
	"feMergeNode",
	"feMorphology",
	"feOffset",
	"fePointLight",
	"feSpecularLighting",
	"feSpotLight",
	"feTile",
	"feTurbulence"
]), Ce = m([
	"animate",
	"color-profile",
	"cursor",
	"discard",
	"font-face",
	"font-face-format",
	"font-face-name",
	"font-face-src",
	"font-face-uri",
	"foreignobject",
	"hatch",
	"hatchpath",
	"mesh",
	"meshgradient",
	"meshpatch",
	"meshrow",
	"missing-glyph",
	"script",
	"set",
	"solidcolor",
	"unknown",
	"use"
]), we = m(/* @__PURE__ */ "math.menclose.merror.mfenced.mfrac.mglyph.mi.mlabeledtr.mmultiscripts.mn.mo.mover.mpadded.mphantom.mroot.mrow.ms.mspace.msqrt.mstyle.msub.msup.msubsup.mtable.mtd.mtext.mtr.munder.munderover.mprescripts".split(".")), Te = m([
	"maction",
	"maligngroup",
	"malignmark",
	"mlongdiv",
	"mscarries",
	"mscarry",
	"msgroup",
	"mstack",
	"msline",
	"msrow",
	"semantics",
	"annotation",
	"annotation-xml",
	"mprescripts",
	"none"
]), Ee = m(["#text"]), De = m(/* @__PURE__ */ "accept.action.align.alt.autocapitalize.autocomplete.autopictureinpicture.autoplay.background.bgcolor.border.capture.cellpadding.cellspacing.checked.cite.class.clear.color.cols.colspan.command.commandfor.controls.controlslist.coords.crossorigin.datetime.decoding.default.dir.disabled.disablepictureinpicture.disableremoteplayback.download.draggable.enctype.enterkeyhint.exportparts.face.for.headers.height.hidden.high.href.hreflang.id.inert.inputmode.integrity.ismap.kind.label.lang.list.loading.loop.low.max.maxlength.media.method.min.minlength.multiple.muted.name.nonce.noshade.novalidate.nowrap.open.optimum.part.pattern.placeholder.playsinline.popover.popovertarget.popovertargetaction.poster.preload.pubdate.radiogroup.readonly.rel.required.rev.reversed.role.rows.rowspan.spellcheck.scope.selected.shape.size.sizes.slot.span.srclang.start.src.srcset.step.style.summary.tabindex.title.translate.type.usemap.valign.value.width.wrap.xmlns".split(".")), Oe = m(/* @__PURE__ */ "accent-height.accumulate.additive.alignment-baseline.amplitude.ascent.attributename.attributetype.azimuth.basefrequency.baseline-shift.begin.bias.by.class.clip.clippathunits.clip-path.clip-rule.color.color-interpolation.color-interpolation-filters.color-profile.color-rendering.cx.cy.d.dx.dy.diffuseconstant.direction.display.divisor.dur.edgemode.elevation.end.exponent.fill.fill-opacity.fill-rule.filter.filterunits.flood-color.flood-opacity.font-family.font-size.font-size-adjust.font-stretch.font-style.font-variant.font-weight.fx.fy.g1.g2.glyph-name.glyphref.gradientunits.gradienttransform.height.href.id.image-rendering.in.in2.intercept.k.k1.k2.k3.k4.kerning.keypoints.keysplines.keytimes.lang.lengthadjust.letter-spacing.kernelmatrix.kernelunitlength.lighting-color.local.marker-end.marker-mid.marker-start.markerheight.markerunits.markerwidth.maskcontentunits.maskunits.max.mask.mask-type.media.method.mode.min.name.numoctaves.offset.operator.opacity.order.orient.orientation.origin.overflow.paint-order.path.pathlength.patterncontentunits.patterntransform.patternunits.points.preservealpha.preserveaspectratio.primitiveunits.r.rx.ry.radius.refx.refy.repeatcount.repeatdur.restart.result.rotate.scale.seed.shape-rendering.slope.specularconstant.specularexponent.spreadmethod.startoffset.stddeviation.stitchtiles.stop-color.stop-opacity.stroke-dasharray.stroke-dashoffset.stroke-linecap.stroke-linejoin.stroke-miterlimit.stroke-opacity.stroke.stroke-width.style.surfacescale.systemlanguage.tabindex.tablevalues.targetx.targety.transform.transform-origin.text-anchor.text-decoration.text-rendering.textlength.type.u1.u2.unicode.values.viewbox.visibility.version.vert-adv-y.vert-origin-x.vert-origin-y.width.word-spacing.wrap.writing-mode.xchannelselector.ychannelselector.x.x1.x2.xmlns.y.y1.y2.z.zoomandpan".split(".")), ke = m(/* @__PURE__ */ "accent.accentunder.align.bevelled.close.columnalign.columnlines.columnspacing.columnspan.denomalign.depth.dir.display.displaystyle.encoding.fence.frame.height.href.id.largeop.length.linethickness.lquote.lspace.mathbackground.mathcolor.mathsize.mathvariant.maxsize.minsize.movablelimits.notation.numalign.open.rowalign.rowlines.rowspacing.rowspan.rspace.rquote.scriptlevel.scriptminsize.scriptsizemultiplier.selection.separator.separators.stretchy.subscriptshift.supscriptshift.symmetric.voffset.width.xmlns".split(".")), Ae = m([
	"xlink:href",
	"xml:id",
	"xlink:title",
	"xml:space",
	"xmlns:xlink"
]), je = h(/{{[\w\W]*|^[\w\W]*}}/g), Me = h(/<%[\w\W]*|^[\w\W]*%>/g), Ne = h(/\${[\w\W]*/g), Pe = h(/^data-[\-\w.\u00B7-\uFFFF]+$/), Fe = h(/^aria-[\-\w]+$/), Ie = h(/^(?:(?:(?:f|ht)tps?|mailto|tel|callto|sms|cid|xmpp|matrix):|[^a-z]|[a-z+.\-]+(?:[^a-z+.\-:]|$))/i), Le = h(/^(?:\w+script|data):/i), Re = h(/[\u0000-\u0020\u00A0\u1680\u180E\u2000-\u2029\u205F\u3000]/g), ze = h(/^html$/i), Be = h(/^[a-z][.\w]*(-[.\w]+)+$/i), A = {
	element: 1,
	text: 3,
	progressingInstruction: 7,
	comment: 8,
	document: 9
}, Ve = function() {
	return typeof window > "u" ? null : window;
}, He = function(e, t) {
	if (typeof e != "object" || typeof e.createPolicy != "function") return null;
	let n = null, r = "data-tt-policy-suffix";
	t && t.hasAttribute(r) && (n = t.getAttribute(r));
	let i = "dompurify" + (n ? "#" + n : "");
	try {
		return e.createPolicy(i, {
			createHTML(e) {
				return e;
			},
			createScriptURL(e) {
				return e;
			}
		});
	} catch {
		return console.warn("TrustedTypes policy " + i + " could not be created."), null;
	}
}, Ue = function() {
	return {
		afterSanitizeAttributes: [],
		afterSanitizeElements: [],
		afterSanitizeShadowDOM: [],
		beforeSanitizeAttributes: [],
		beforeSanitizeElements: [],
		beforeSanitizeShadowDOM: [],
		uponSanitizeAttribute: [],
		uponSanitizeElement: [],
		uponSanitizeShadowNode: []
	};
};
function We() {
	let e = arguments.length > 0 && arguments[0] !== void 0 ? arguments[0] : Ve(), t = (e) => We(e);
	if (t.version = "3.4.5", t.removed = [], !e || !e.document || e.document.nodeType !== A.document || !e.Element) return t.isSupported = !1, t;
	let n = e.document, r = n, i = r.currentScript, a = e.DocumentFragment, o = e.HTMLTemplateElement, s = e.Node, c = e.Element, l = e.NodeFilter, u = e.NamedNodeMap, f = u === void 0 ? e.NamedNodeMap || e.MozNamedAttrMap : u, ee = e.HTMLFormElement, te = e.DOMParser, p = e.trustedTypes, h = c.prototype, ne = k(h, "cloneNode"), re = k(h, "remove"), ie = k(h, "nextSibling"), pe = k(h, "childNodes"), x = k(h, "parentNode"), me = s && s.prototype ? k(s.prototype, "nodeType") : null;
	if (typeof o == "function") {
		let e = n.createElement("template");
		e.content && e.content.ownerDocument && (n = e.content.ownerDocument);
	}
	let S, w = "", E = n, ge = E.implementation, _e = E.createNodeIterator, j = E.createDocumentFragment, Ge = E.getElementsByTagName, Ke = r.importNode, M = Ue();
	t.isSupported = typeof d == "function" && typeof x == "function" && ge && ge.createHTMLDocument !== void 0;
	let N = je, P = Me, F = Ne, qe = Pe, Je = Fe, Ye = Le, Xe = Re, Ze = Be, Qe = Ie, I = null, $e = D({}, [
		...be,
		...xe,
		...Se,
		...we,
		...Ee
	]), L = null, et = D({}, [
		...De,
		...Oe,
		...ke,
		...Ae
	]), R = Object.seal(g(null, {
		tagNameCheck: {
			writable: !0,
			configurable: !1,
			enumerable: !0,
			value: null
		},
		attributeNameCheck: {
			writable: !0,
			configurable: !1,
			enumerable: !0,
			value: null
		},
		allowCustomizedBuiltInElements: {
			writable: !0,
			configurable: !1,
			enumerable: !0,
			value: !1
		}
	})), z = null, tt = null, B = Object.seal(g(null, {
		tagCheck: {
			writable: !0,
			configurable: !1,
			enumerable: !0,
			value: null
		},
		attributeCheck: {
			writable: !0,
			configurable: !1,
			enumerable: !0,
			value: null
		}
	})), nt = !0, rt = !0, it = !1, at = !0, V = !1, H = !0, U = !1, ot = !1, st = !1, W = !1, ct = !1, lt = !1, ut = !0, dt = !1, ft = "user-content-", pt = !0, mt = !1, G = {}, K = null, ht = D({}, [
		"annotation-xml",
		"audio",
		"colgroup",
		"desc",
		"foreignobject",
		"head",
		"iframe",
		"math",
		"mi",
		"mn",
		"mo",
		"ms",
		"mtext",
		"noembed",
		"noframes",
		"noscript",
		"plaintext",
		"script",
		"style",
		"svg",
		"template",
		"thead",
		"title",
		"video",
		"xmp"
	]), gt = null, _t = D({}, [
		"audio",
		"video",
		"img",
		"source",
		"image",
		"track"
	]), vt = null, yt = D({}, [
		"alt",
		"class",
		"for",
		"id",
		"label",
		"name",
		"pattern",
		"placeholder",
		"role",
		"summary",
		"title",
		"value",
		"style",
		"xmlns"
	]), bt = "http://www.w3.org/1998/Math/MathML", xt = "http://www.w3.org/2000/svg", q = "http://www.w3.org/1999/xhtml", J = q, St = !1, Ct = null, wt = D({}, [
		bt,
		xt,
		q
	], le), Tt = D({}, [
		"mi",
		"mo",
		"mn",
		"ms",
		"mtext"
	]), Et = D({}, ["annotation-xml"]), Dt = D({}, [
		"title",
		"style",
		"font",
		"a",
		"script"
	]), Ot = null, kt = ["application/xhtml+xml", "text/html"], Y = null, X = null, At = n.createElement("form"), jt = function(e) {
		return e instanceof RegExp || e instanceof Function;
	}, Mt = function() {
		let e = arguments.length > 0 && arguments[0] !== void 0 ? arguments[0] : {};
		if (X && X === e) return;
		(!e || typeof e != "object") && (e = {}), e = O(e), Ot = kt.indexOf(e.PARSER_MEDIA_TYPE) === -1 ? "text/html" : e.PARSER_MEDIA_TYPE, Y = Ot === "application/xhtml+xml" ? le : ce, I = C(e, "ALLOWED_TAGS") && y(e.ALLOWED_TAGS) ? D({}, e.ALLOWED_TAGS, Y) : $e, L = C(e, "ALLOWED_ATTR") && y(e.ALLOWED_ATTR) ? D({}, e.ALLOWED_ATTR, Y) : et, Ct = C(e, "ALLOWED_NAMESPACES") && y(e.ALLOWED_NAMESPACES) ? D({}, e.ALLOWED_NAMESPACES, le) : wt, vt = C(e, "ADD_URI_SAFE_ATTR") && y(e.ADD_URI_SAFE_ATTR) ? D(O(yt), e.ADD_URI_SAFE_ATTR, Y) : yt, gt = C(e, "ADD_DATA_URI_TAGS") && y(e.ADD_DATA_URI_TAGS) ? D(O(_t), e.ADD_DATA_URI_TAGS, Y) : _t, K = C(e, "FORBID_CONTENTS") && y(e.FORBID_CONTENTS) ? D({}, e.FORBID_CONTENTS, Y) : ht, z = C(e, "FORBID_TAGS") && y(e.FORBID_TAGS) ? D({}, e.FORBID_TAGS, Y) : O({}), tt = C(e, "FORBID_ATTR") && y(e.FORBID_ATTR) ? D({}, e.FORBID_ATTR, Y) : O({}), G = C(e, "USE_PROFILES") ? e.USE_PROFILES && typeof e.USE_PROFILES == "object" ? O(e.USE_PROFILES) : e.USE_PROFILES : !1, nt = e.ALLOW_ARIA_ATTR !== !1, rt = e.ALLOW_DATA_ATTR !== !1, it = e.ALLOW_UNKNOWN_PROTOCOLS || !1, at = e.ALLOW_SELF_CLOSE_IN_ATTR !== !1, V = e.SAFE_FOR_TEMPLATES || !1, H = e.SAFE_FOR_XML !== !1, U = e.WHOLE_DOCUMENT || !1, W = e.RETURN_DOM || !1, ct = e.RETURN_DOM_FRAGMENT || !1, lt = e.RETURN_TRUSTED_TYPE || !1, st = e.FORCE_BODY || !1, ut = e.SANITIZE_DOM !== !1, dt = e.SANITIZE_NAMED_PROPS || !1, pt = e.KEEP_CONTENT !== !1, mt = e.IN_PLACE || !1, Qe = ye(e.ALLOWED_URI_REGEXP) ? e.ALLOWED_URI_REGEXP : Ie, J = typeof e.NAMESPACE == "string" ? e.NAMESPACE : q, Tt = C(e, "MATHML_TEXT_INTEGRATION_POINTS") && e.MATHML_TEXT_INTEGRATION_POINTS && typeof e.MATHML_TEXT_INTEGRATION_POINTS == "object" ? O(e.MATHML_TEXT_INTEGRATION_POINTS) : D({}, [
			"mi",
			"mo",
			"mn",
			"ms",
			"mtext"
		]), Et = C(e, "HTML_INTEGRATION_POINTS") && e.HTML_INTEGRATION_POINTS && typeof e.HTML_INTEGRATION_POINTS == "object" ? O(e.HTML_INTEGRATION_POINTS) : D({}, ["annotation-xml"]);
		let t = C(e, "CUSTOM_ELEMENT_HANDLING") && e.CUSTOM_ELEMENT_HANDLING && typeof e.CUSTOM_ELEMENT_HANDLING == "object" ? O(e.CUSTOM_ELEMENT_HANDLING) : g(null);
		if (R = g(null), C(t, "tagNameCheck") && jt(t.tagNameCheck) && (R.tagNameCheck = t.tagNameCheck), C(t, "attributeNameCheck") && jt(t.attributeNameCheck) && (R.attributeNameCheck = t.attributeNameCheck), C(t, "allowCustomizedBuiltInElements") && typeof t.allowCustomizedBuiltInElements == "boolean" && (R.allowCustomizedBuiltInElements = t.allowCustomizedBuiltInElements), V && (rt = !1), ct && (W = !0), G && (I = D({}, Ee), L = g(null), G.html === !0 && (D(I, be), D(L, De)), G.svg === !0 && (D(I, xe), D(L, Oe), D(L, Ae)), G.svgFilters === !0 && (D(I, Se), D(L, Oe), D(L, Ae)), G.mathMl === !0 && (D(I, we), D(L, ke), D(L, Ae))), B.tagCheck = null, B.attributeCheck = null, C(e, "ADD_TAGS") && (typeof e.ADD_TAGS == "function" ? B.tagCheck = e.ADD_TAGS : y(e.ADD_TAGS) && (I === $e && (I = O(I)), D(I, e.ADD_TAGS, Y))), C(e, "ADD_ATTR") && (typeof e.ADD_ATTR == "function" ? B.attributeCheck = e.ADD_ATTR : y(e.ADD_ATTR) && (L === et && (L = O(L)), D(L, e.ADD_ATTR, Y))), C(e, "ADD_URI_SAFE_ATTR") && y(e.ADD_URI_SAFE_ATTR) && D(vt, e.ADD_URI_SAFE_ATTR, Y), C(e, "FORBID_CONTENTS") && y(e.FORBID_CONTENTS) && (K === ht && (K = O(K)), D(K, e.FORBID_CONTENTS, Y)), C(e, "ADD_FORBID_CONTENTS") && y(e.ADD_FORBID_CONTENTS) && (K === ht && (K = O(K)), D(K, e.ADD_FORBID_CONTENTS, Y)), pt && (I["#text"] = !0), U && D(I, [
			"html",
			"head",
			"body"
		]), I.table && (D(I, ["tbody"]), delete z.tbody), e.TRUSTED_TYPES_POLICY) {
			if (typeof e.TRUSTED_TYPES_POLICY.createHTML != "function") throw he("TRUSTED_TYPES_POLICY configuration option must provide a \"createHTML\" hook.");
			if (typeof e.TRUSTED_TYPES_POLICY.createScriptURL != "function") throw he("TRUSTED_TYPES_POLICY configuration option must provide a \"createScriptURL\" hook.");
			S = e.TRUSTED_TYPES_POLICY, w = S.createHTML("");
		} else S === void 0 && (S = He(p, i)), S !== null && typeof w == "string" && (w = S.createHTML(""));
		m && m(e), X = e;
	}, Nt = D({}, [
		...xe,
		...Se,
		...Ce
	]), Pt = D({}, [...we, ...Te]), Ft = function(e) {
		let t = x(e);
		(!t || !t.tagName) && (t = {
			namespaceURI: J,
			tagName: "template"
		});
		let n = ce(e.tagName), r = ce(t.tagName);
		return Ct[e.namespaceURI] ? e.namespaceURI === xt ? t.namespaceURI === q ? n === "svg" : t.namespaceURI === bt ? n === "svg" && (r === "annotation-xml" || Tt[r]) : !!Nt[n] : e.namespaceURI === bt ? t.namespaceURI === q ? n === "math" : t.namespaceURI === xt ? n === "math" && Et[r] : !!Pt[n] : e.namespaceURI === q ? t.namespaceURI === xt && !Et[r] || t.namespaceURI === bt && !Tt[r] ? !1 : !Pt[n] && (Dt[n] || !Nt[n]) : !!(Ot === "application/xhtml+xml" && Ct[e.namespaceURI]) : !1;
	}, Z = function(e) {
		v(t.removed, { element: e });
		try {
			x(e).removeChild(e);
		} catch {
			re(e);
		}
	}, Q = function(e, n) {
		try {
			v(t.removed, {
				attribute: n.getAttributeNode(e),
				from: n
			});
		} catch {
			v(t.removed, {
				attribute: null,
				from: n
			});
		}
		if (n.removeAttribute(e), e === "is") if (W || ct) try {
			Z(n);
		} catch {}
		else try {
			n.setAttribute(e, "");
		} catch {}
	}, It = function(e) {
		let t = null, r = null;
		if (st) e = "<remove></remove>" + e;
		else {
			let t = ue(e, /^[\r\n\t ]+/);
			r = t && t[0];
		}
		Ot === "application/xhtml+xml" && J === q && (e = "<html xmlns=\"http://www.w3.org/1999/xhtml\"><head></head><body>" + e + "</body></html>");
		let i = S ? S.createHTML(e) : e;
		if (J === q) try {
			t = new te().parseFromString(i, Ot);
		} catch {}
		if (!t || !t.documentElement) {
			t = ge.createDocument(J, "template", null);
			try {
				t.documentElement.innerHTML = St ? w : i;
			} catch {}
		}
		let a = t.body || t.documentElement;
		return e && r && a.insertBefore(n.createTextNode(r), a.childNodes[0] || null), J === q ? Ge.call(t, U ? "html" : "body")[0] : U ? t.documentElement : a;
	}, Lt = function(e) {
		return _e.call(e.ownerDocument || e, e, l.SHOW_ELEMENT | l.SHOW_COMMENT | l.SHOW_TEXT | l.SHOW_PROCESSING_INSTRUCTION | l.SHOW_CDATA_SECTION, null);
	}, Rt = function(e) {
		e.normalize();
		let t = _e.call(e.ownerDocument || e, e, l.SHOW_TEXT | l.SHOW_COMMENT | l.SHOW_CDATA_SECTION | l.SHOW_PROCESSING_INSTRUCTION, null), n = t.nextNode();
		for (; n;) {
			let e = n.data;
			_([
				N,
				P,
				F
			], (t) => {
				e = b(e, t, " ");
			}), n.data = e, n = t.nextNode();
		}
	}, zt = function(e) {
		return e instanceof ee && (typeof e.nodeName != "string" || typeof e.textContent != "string" || typeof e.removeChild != "function" || !(e.attributes instanceof f) || typeof e.removeAttribute != "function" || typeof e.setAttribute != "function" || typeof e.namespaceURI != "string" || typeof e.insertBefore != "function" || typeof e.hasChildNodes != "function");
	}, Bt = function(e) {
		if (!me || typeof e != "object" || !e) return !1;
		try {
			return typeof me(e) == "number";
		} catch {
			return !1;
		}
	};
	function $(e, n, r) {
		_(e, (e) => {
			e.call(t, n, r, X);
		});
	}
	let Vt = function(e) {
		let n = null;
		if ($(M.beforeSanitizeElements, e, null), zt(e)) return Z(e), !0;
		let r = Y(e.nodeName);
		if ($(M.uponSanitizeElement, e, {
			tagName: r,
			allowedTags: I
		}), H && e.hasChildNodes() && !Bt(e.firstElementChild) && T(/<[/\w!]/g, e.innerHTML) && T(/<[/\w!]/g, e.textContent) || H && e.namespaceURI === q && r === "style" && Bt(e.firstElementChild) || e.nodeType === A.progressingInstruction || H && e.nodeType === A.comment && T(/<[/\w]/g, e.data)) return Z(e), !0;
		if (z[r] || !(B.tagCheck instanceof Function && B.tagCheck(r)) && !I[r]) {
			if (!z[r] && Wt(r) && (R.tagNameCheck instanceof RegExp && T(R.tagNameCheck, r) || R.tagNameCheck instanceof Function && R.tagNameCheck(r))) return !1;
			if (pt && !K[r]) {
				let t = x(e) || e.parentNode, n = pe(e) || e.childNodes;
				if (n && t) {
					let r = n.length;
					for (let i = r - 1; i >= 0; --i) {
						let r = ne(n[i], !0);
						t.insertBefore(r, ie(e));
					}
				}
			}
			return Z(e), !0;
		}
		return e instanceof c && !Ft(e) || (r === "noscript" || r === "noembed" || r === "noframes") && T(/<\/no(script|embed|frames)/i, e.innerHTML) ? (Z(e), !0) : (V && e.nodeType === A.text && (n = e.textContent, _([
			N,
			P,
			F
		], (e) => {
			n = b(n, e, " ");
		}), e.textContent !== n && (v(t.removed, { element: e.cloneNode() }), e.textContent = n)), $(M.afterSanitizeElements, e, null), !1);
	}, Ht = function(e, t, r) {
		if (tt[t] || ut && (t === "id" || t === "name") && (r in n || r in At)) return !1;
		let i = L[t] || B.attributeCheck instanceof Function && B.attributeCheck(t, e);
		if (!(rt && !tt[t] && T(qe, t)) && !(nt && T(Je, t))) {
			if (!i || tt[t]) {
				if (!(Wt(e) && (R.tagNameCheck instanceof RegExp && T(R.tagNameCheck, e) || R.tagNameCheck instanceof Function && R.tagNameCheck(e)) && (R.attributeNameCheck instanceof RegExp && T(R.attributeNameCheck, t) || R.attributeNameCheck instanceof Function && R.attributeNameCheck(t, e)) || t === "is" && R.allowCustomizedBuiltInElements && (R.tagNameCheck instanceof RegExp && T(R.tagNameCheck, r) || R.tagNameCheck instanceof Function && R.tagNameCheck(r)))) return !1;
			} else if (!vt[t] && !T(Qe, b(r, Xe, "")) && !((t === "src" || t === "xlink:href" || t === "href") && e !== "script" && de(r, "data:") === 0 && gt[e]) && !(it && !T(Ye, b(r, Xe, ""))) && r) return !1;
		}
		return !0;
	}, Ut = D({}, [
		"annotation-xml",
		"color-profile",
		"font-face",
		"font-face-format",
		"font-face-name",
		"font-face-src",
		"font-face-uri",
		"missing-glyph"
	]), Wt = function(e) {
		return !Ut[ce(e)] && T(Ze, e);
	}, Gt = function(e) {
		$(M.beforeSanitizeAttributes, e, null);
		let n = e.attributes;
		if (!n || zt(e)) return;
		let r = {
			attrName: "",
			attrValue: "",
			keepAttr: !0,
			allowedAttributes: L,
			forceKeepAttr: void 0
		}, i = n.length;
		for (; i--;) {
			let a = n[i], o = a.name, s = a.namespaceURI, c = a.value, l = Y(o), u = c, d = o === "value" ? u : fe(u);
			if (r.attrName = l, r.attrValue = d, r.keepAttr = !0, r.forceKeepAttr = void 0, $(M.uponSanitizeAttribute, e, r), d = r.attrValue, dt && (l === "id" || l === "name") && de(d, ft) !== 0 && (Q(o, e), d = ft + d), H && T(/((--!?|])>)|<\/(style|script|title|xmp|textarea|noscript|iframe|noembed|noframes)/i, d)) {
				Q(o, e);
				continue;
			}
			if (l === "attributename" && ue(d, "href")) {
				Q(o, e);
				continue;
			}
			if (r.forceKeepAttr) continue;
			if (!r.keepAttr) {
				Q(o, e);
				continue;
			}
			if (!at && T(/\/>/i, d)) {
				Q(o, e);
				continue;
			}
			V && _([
				N,
				P,
				F
			], (e) => {
				d = b(d, e, " ");
			});
			let f = Y(e.nodeName);
			if (!Ht(f, l, d)) {
				Q(o, e);
				continue;
			}
			if (S && typeof p == "object" && typeof p.getAttributeType == "function" && !s) switch (p.getAttributeType(f, l)) {
				case "TrustedHTML":
					d = S.createHTML(d);
					break;
				case "TrustedScriptURL":
					d = S.createScriptURL(d);
					break;
			}
			if (d !== u) try {
				s ? e.setAttributeNS(s, o, d) : e.setAttribute(o, d), zt(e) ? Z(e) : oe(t.removed);
			} catch {
				Q(o, e);
			}
		}
		$(M.afterSanitizeAttributes, e, null);
	}, Kt = function(e) {
		let t = null, n = Lt(e);
		for ($(M.beforeSanitizeShadowDOM, e, null); t = n.nextNode();) $(M.uponSanitizeShadowNode, t, null), Vt(t), Gt(t), t.content instanceof a && Kt(t.content);
		$(M.afterSanitizeShadowDOM, e, null);
	}, qt = function(e) {
		if (e.nodeType === A.element && e.shadowRoot instanceof a) {
			let t = e.shadowRoot;
			qt(t), Kt(t);
		}
		let t = e.childNodes;
		if (!t) return;
		let n = [];
		_(t, (e) => {
			v(n, e);
		});
		for (let e of n) qt(e);
	};
	return t.sanitize = function(e) {
		let n = arguments.length > 1 && arguments[1] !== void 0 ? arguments[1] : {}, i = null, o = null, s = null, c = null;
		if (St = !e, St && (e = "<!-->"), typeof e != "string" && !Bt(e) && (e = ve(e), typeof e != "string")) throw he("dirty is not a string, aborting");
		if (!t.isSupported) return e;
		if (ot || Mt(n), t.removed = [], typeof e == "string" && (mt = !1), mt) {
			let t = e.nodeName;
			if (typeof t == "string") {
				let e = Y(t);
				if (!I[e] || z[e]) throw he("root node is forbidden and cannot be sanitized in-place");
			}
			qt(e);
		} else if (Bt(e)) i = It("<!---->"), o = i.ownerDocument.importNode(e, !0), o.nodeType === A.element && o.nodeName === "BODY" || o.nodeName === "HTML" ? i = o : i.appendChild(o), qt(o);
		else {
			if (!W && !V && !U && e.indexOf("<") === -1) return S && lt ? S.createHTML(e) : e;
			if (i = It(e), !i) return W ? null : lt ? w : "";
		}
		i && st && Z(i.firstChild);
		let l = Lt(mt ? e : i);
		for (; s = l.nextNode();) Vt(s), Gt(s), s.content instanceof a && Kt(s.content);
		if (mt) return V && Rt(e), e;
		if (W) {
			if (V && Rt(i), ct) for (c = j.call(i.ownerDocument); i.firstChild;) c.appendChild(i.firstChild);
			else c = i;
			return (L.shadowroot || L.shadowrootmode) && (c = Ke.call(r, c, !0)), c;
		}
		let u = U ? i.outerHTML : i.innerHTML;
		return U && I["!doctype"] && i.ownerDocument && i.ownerDocument.doctype && i.ownerDocument.doctype.name && T(ze, i.ownerDocument.doctype.name) && (u = "<!DOCTYPE " + i.ownerDocument.doctype.name + ">\n" + u), V && _([
			N,
			P,
			F
		], (e) => {
			u = b(u, e, " ");
		}), S && lt ? S.createHTML(u) : u;
	}, t.setConfig = function() {
		Mt(arguments.length > 0 && arguments[0] !== void 0 ? arguments[0] : {}), ot = !0;
	}, t.clearConfig = function() {
		X = null, ot = !1;
	}, t.isValidAttribute = function(e, t, n) {
		return X || Mt({}), Ht(Y(e), Y(t), n);
	}, t.addHook = function(e, t) {
		typeof t == "function" && v(M[e], t);
	}, t.removeHook = function(e, t) {
		if (t !== void 0) {
			let n = ae(M[e], t);
			return n === -1 ? void 0 : se(M[e], n, 1)[0];
		}
		return oe(M[e]);
	}, t.removeHooks = function(e) {
		M[e] = [];
	}, t.removeAllHooks = function() {
		M = Ue();
	}, t;
}
var j = We(), Ge = "data-temp-href-target";
j.addHook("beforeSanitizeAttributes", function(e) {
	e instanceof HTMLElement && e.hasAttribute("target") && e.getAttribute("target") === "_blank" && e.setAttribute(Ge, "_blank");
}), j.addHook("afterSanitizeAttributes", function(e) {
	e instanceof HTMLElement && e.hasAttribute(Ge) && (e.setAttribute("target", "_blank"), e.setAttribute("rel", "noopener noreferrer"), e.removeAttribute(Ge));
});
var Ke = {
	USE_PROFILES: { html: !0 },
	FORCE_BODY: !0
}, M = /* @__PURE__ */ e("div", { target: "e18540fl0" })(({ theme: e }) => ({
	width: "100%",
	"ul, ol, dl": { paddingLeft: e.spacing.threeXL }
}), ""), N = (0, i.forwardRef)(function(e, t) {
	return /* @__PURE__ */ r.jsx(M, {
		className: "stHtml",
		"data-testid": "stHtml",
		ref: t,
		...e
	});
}), P = {
	...Ke,
	ADD_TAGS: ["script", "style"],
	ADD_ATTR: [
		"src",
		"type",
		"async",
		"defer",
		"nonce",
		"crossorigin",
		"referrerpolicy",
		"integrity"
	]
};
function F(e) {
	return j.sanitize(e, P);
}
var qe = (0, i.memo)(({ body: e }) => {
	let t = (0, i.useRef)(null), n = (0, i.useMemo)(() => F(e), [e]);
	return (0, i.useEffect)(() => {
		let e = t.current;
		return e ? (e.innerHTML = n, Array.from(e.querySelectorAll("script")).forEach((e) => {
			let t = document.createElement("script");
			for (let { name: n, value: r } of Array.from(e.attributes)) try {
				t.setAttribute(n, r);
			} catch {}
			e.src || (t.textContent = e.textContent), e.parentNode?.replaceChild(t, e);
		}), () => {
			e.innerHTML = "";
		}) : void 0;
	}, [n]), /* @__PURE__ */ r.jsx(N, { ref: t });
});
function Je(e) {
	return j.sanitize(e, Ke);
}
function Ye({ body: e }) {
	let t = (0, i.useMemo)(() => Je(e), [e]);
	return t ? /* @__PURE__ */ r.jsx(N, { dangerouslySetInnerHTML: { __html: t } }) : null;
}
var Xe = (0, i.memo)(Ye);
function Ze({ element: e }) {
	let { body: t, unsafeAllowJavascript: n } = e;
	return n ? /* @__PURE__ */ r.jsx(qe, { body: t }) : /* @__PURE__ */ r.jsx(Xe, { body: t });
}
var Qe = (0, i.memo)(Ze);
//#endregion
export { Qe as default };

//# sourceMappingURL=Html-B0_sFMha-DlJCdFoi.js.map