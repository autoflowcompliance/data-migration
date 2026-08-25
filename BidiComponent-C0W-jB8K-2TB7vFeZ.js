import { $t as e, C as t, En as n, Ia as r, Ka as i, Mn as a, Ua as o, ma as s, oa as c, oi as l, pa as u, ta as d, ti as f, va as p } from "./index-Dl4ETd_L-D2oMd1k2.js";
//#region ../react/build/BidiComponent-C0W-jB8K.js
var m = /* @__PURE__ */ i(o(), 1);
function h(e, t, n, r) {
	for (var i = -1, a = e == null ? 0 : e.length; ++i < a;) n = t(n, e[i], i, e);
	return n;
}
function g(e) {
	return function(t) {
		return e?.[t];
	};
}
var _ = g({
	À: "A",
	Á: "A",
	Â: "A",
	Ã: "A",
	Ä: "A",
	Å: "A",
	à: "a",
	á: "a",
	â: "a",
	ã: "a",
	ä: "a",
	å: "a",
	Ç: "C",
	ç: "c",
	Ð: "D",
	ð: "d",
	È: "E",
	É: "E",
	Ê: "E",
	Ë: "E",
	è: "e",
	é: "e",
	ê: "e",
	ë: "e",
	Ì: "I",
	Í: "I",
	Î: "I",
	Ï: "I",
	ì: "i",
	í: "i",
	î: "i",
	ï: "i",
	Ñ: "N",
	ñ: "n",
	Ò: "O",
	Ó: "O",
	Ô: "O",
	Õ: "O",
	Ö: "O",
	Ø: "O",
	ò: "o",
	ó: "o",
	ô: "o",
	õ: "o",
	ö: "o",
	ø: "o",
	Ù: "U",
	Ú: "U",
	Û: "U",
	Ü: "U",
	ù: "u",
	ú: "u",
	û: "u",
	ü: "u",
	Ý: "Y",
	ý: "y",
	ÿ: "y",
	Æ: "Ae",
	æ: "ae",
	Þ: "Th",
	þ: "th",
	ß: "ss",
	Ā: "A",
	Ă: "A",
	Ą: "A",
	ā: "a",
	ă: "a",
	ą: "a",
	Ć: "C",
	Ĉ: "C",
	Ċ: "C",
	Č: "C",
	ć: "c",
	ĉ: "c",
	ċ: "c",
	č: "c",
	Ď: "D",
	Đ: "D",
	ď: "d",
	đ: "d",
	Ē: "E",
	Ĕ: "E",
	Ė: "E",
	Ę: "E",
	Ě: "E",
	ē: "e",
	ĕ: "e",
	ė: "e",
	ę: "e",
	ě: "e",
	Ĝ: "G",
	Ğ: "G",
	Ġ: "G",
	Ģ: "G",
	ĝ: "g",
	ğ: "g",
	ġ: "g",
	ģ: "g",
	Ĥ: "H",
	Ħ: "H",
	ĥ: "h",
	ħ: "h",
	Ĩ: "I",
	Ī: "I",
	Ĭ: "I",
	Į: "I",
	İ: "I",
	ĩ: "i",
	ī: "i",
	ĭ: "i",
	į: "i",
	ı: "i",
	Ĵ: "J",
	ĵ: "j",
	Ķ: "K",
	ķ: "k",
	ĸ: "k",
	Ĺ: "L",
	Ļ: "L",
	Ľ: "L",
	Ŀ: "L",
	Ł: "L",
	ĺ: "l",
	ļ: "l",
	ľ: "l",
	ŀ: "l",
	ł: "l",
	Ń: "N",
	Ņ: "N",
	Ň: "N",
	Ŋ: "N",
	ń: "n",
	ņ: "n",
	ň: "n",
	ŋ: "n",
	Ō: "O",
	Ŏ: "O",
	Ő: "O",
	ō: "o",
	ŏ: "o",
	ő: "o",
	Ŕ: "R",
	Ŗ: "R",
	Ř: "R",
	ŕ: "r",
	ŗ: "r",
	ř: "r",
	Ś: "S",
	Ŝ: "S",
	Ş: "S",
	Š: "S",
	ś: "s",
	ŝ: "s",
	ş: "s",
	š: "s",
	Ţ: "T",
	Ť: "T",
	Ŧ: "T",
	ţ: "t",
	ť: "t",
	ŧ: "t",
	Ũ: "U",
	Ū: "U",
	Ŭ: "U",
	Ů: "U",
	Ű: "U",
	Ų: "U",
	ũ: "u",
	ū: "u",
	ŭ: "u",
	ů: "u",
	ű: "u",
	ų: "u",
	Ŵ: "W",
	ŵ: "w",
	Ŷ: "Y",
	ŷ: "y",
	Ÿ: "Y",
	Ź: "Z",
	Ż: "Z",
	Ž: "Z",
	ź: "z",
	ż: "z",
	ž: "z",
	Ĳ: "IJ",
	ĳ: "ij",
	Œ: "Oe",
	œ: "oe",
	ŉ: "'n",
	ſ: "s"
}), v = /[\xc0-\xd6\xd8-\xf6\xf8-\xff\u0100-\u017f]/g, y = RegExp("[\\u0300-\\u036f\\ufe20-\\ufe2f\\u20d0-\\u20ff]", "g");
function b(e) {
	return e = c(e), e && e.replace(v, _).replace(y, "");
}
var x = /[^\x00-\x2f\x3a-\x40\x5b-\x60\x7b-\x7f]+/g;
function S(e) {
	return e.match(x) || [];
}
var C = /[a-z][A-Z]|[A-Z]{2}[a-z]|[0-9][a-zA-Z]|[a-zA-Z][0-9]|[^a-zA-Z0-9 ]/;
function w(e) {
	return C.test(e);
}
var T = "\\ud800-\\udfff", E = "\\u0300-\\u036f\\ufe20-\\ufe2f\\u20d0-\\u20ff", D = "\\u2700-\\u27bf", O = "a-z\\xdf-\\xf6\\xf8-\\xff", ee = "\\xac\\xb1\\xd7\\xf7", te = "\\x00-\\x2f\\x3a-\\x40\\x5b-\\x60\\x7b-\\xbf", ne = "\\u2000-\\u206f", re = " \\t\\x0b\\f\\xa0\\ufeff\\n\\r\\u2028\\u2029\\u1680\\u180e\\u2000\\u2001\\u2002\\u2003\\u2004\\u2005\\u2006\\u2007\\u2008\\u2009\\u200a\\u202f\\u205f\\u3000", k = "A-Z\\xc0-\\xd6\\xd8-\\xde", ie = "\\ufe0e\\ufe0f", A = ee + te + ne + re, j = "['’]", M = "[" + A + "]", ae = "[" + E + "]", N = "\\d+", oe = "[" + D + "]", P = "[" + O + "]", F = "[^" + T + A + N + D + O + k + "]", se = "(?:" + ae + "|\\ud83c[\\udffb-\\udfff])", ce = "[^" + T + "]", I = "(?:\\ud83c[\\udde6-\\uddff]){2}", L = "[\\ud800-\\udbff][\\udc00-\\udfff]", R = "[" + k + "]", le = "\\u200d", z = "(?:" + P + "|" + F + ")", ue = "(?:" + R + "|" + F + ")", B = "(?:" + j + "(?:d|ll|m|re|s|t|ve))?", V = "(?:" + j + "(?:D|LL|M|RE|S|T|VE))?", H = se + "?", U = "[" + ie + "]?", de = "(?:" + le + "(?:" + [
	ce,
	I,
	L
].join("|") + ")" + U + H + ")*", fe = "\\d*(?:1st|2nd|3rd|(?![123])\\dth)(?=\\b|[A-Z_])", pe = "\\d*(?:1ST|2ND|3RD|(?![123])\\dTH)(?=\\b|[a-z_])", me = U + H + de, he = "(?:" + [
	oe,
	I,
	L
].join("|") + ")" + me, ge = RegExp([
	R + "?" + P + "+" + B + "(?=" + [
		M,
		R,
		"$"
	].join("|") + ")",
	ue + "+" + V + "(?=" + [
		M,
		R + z,
		"$"
	].join("|") + ")",
	R + "?" + z + "+" + B,
	R + "+" + V,
	pe,
	fe,
	N,
	he
].join("|"), "g");
function _e(e) {
	return e.match(ge) || [];
}
function ve(e, t, n) {
	return e = c(e), t = t, t === void 0 ? w(e) ? _e(e) : S(e) : e.match(t) || [];
}
var ye = RegExp("['’]", "g");
function be(e) {
	return function(t) {
		return h(ve(b(t).replace(ye, "")), e, "");
	};
}
var xe = be(function(e, t, n) {
	return e + (n ? "-" : "") + t.toLowerCase();
}), W = (0, m.createContext)(null);
W.displayName = "BidiComponentContext";
var G = l.getLogger("BidiComponent"), K = "__", q = "__streamlit_arrow_ref__", Se = "$$STREAMLIT_INTERNAL_KEY", Ce = (e, t) => {
	if (e && typeof e == "object" && !Array.isArray(e)) {
		if (typeof e[q] == "string") {
			let n = t[e[q]];
			if (n) try {
				return d(n);
			} catch {
				return null;
			}
			return null;
		}
		let n = {};
		for (let [r, i] of Object.entries(e)) if (i && typeof i == "object" && !Array.isArray(i) && typeof i[q] == "string") {
			let e = t[i[q]];
			if (e) try {
				n[r] = d(e);
			} catch {
				n[r] = null;
			}
			else n[r] = null;
		} else n[r] = i;
		return n;
	}
	return e;
}, we = ({ arrowBlobs: t, arrowData: n, bytes: r, data: i, json: a, mixedJson: o }) => {
	switch (i) {
		case "json": return a ? JSON.parse(a) : null;
		case "arrowData": return n ?? null;
		case "bytes": return r ?? null;
		case "mixed":
			if (o && t) {
				let e = JSON.parse(o), n = {};
				return Object.entries(t).forEach(([e, t]) => {
					t?.data && (n[e] = t.data);
				}), Ce(e, n);
			}
			return null;
		case "any":
		case void 0: return null;
		default: e(i);
	}
}, Te = (e, t = "--st") => {
	let n = {};
	return Object.entries(e).forEach(([e, r]) => {
		let i = `${t}-${xe(e)}`;
		if (typeof r == "boolean") {
			n[i] = r ? "1" : "0";
			return;
		}
		if (r == null) {
			n[i] = "unset";
			return;
		}
		if (Array.isArray(r)) {
			n[i] = r.join(",");
			return;
		}
		if (typeof r == "number" || typeof r == "string") {
			n[i] = String(r);
			return;
		}
		n[i] = "unset";
	}), n;
}, Ee = (e) => {
	let t = [
		e.fontSizes.h1FontSize,
		e.fontSizes.h2FontSize,
		e.fontSizes.h3FontSize,
		e.fontSizes.h4FontSize,
		e.fontSizes.h5FontSize,
		e.fontSizes.h6FontSize
	], n = [
		e.fontWeights.h1FontWeight,
		e.fontWeights.h2FontWeight,
		e.fontWeights.h3FontWeight,
		e.fontWeights.h4FontWeight,
		e.fontWeights.h5FontWeight,
		e.fontWeights.h6FontWeight
	];
	return {
		primaryColor: e.colors.primary,
		backgroundColor: e.colors.bgColor,
		secondaryBackgroundColor: e.colors.secondaryBg,
		textColor: e.colors.bodyText,
		linkColor: e.colors.link,
		linkUnderline: e.linkUnderline,
		headingFont: e.genericFonts.headingFont,
		codeFont: e.genericFonts.codeFont,
		baseRadius: e.radii.default,
		buttonRadius: e.radii.button,
		baseFontSize: typeof e.fontSizes.baseFontSize == "number" ? `${e.fontSizes.baseFontSize}px` : String(e.fontSizes.baseFontSize),
		baseFontWeight: e.fontWeights.normal,
		codeFontWeight: e.fontWeights.code,
		codeFontSize: e.fontSizes.codeFontSize,
		headingFontSizes: t,
		headingFontSize1: t[0],
		headingFontSize2: t[1],
		headingFontSize3: t[2],
		headingFontSize4: t[3],
		headingFontSize5: t[4],
		headingFontSize6: t[5],
		headingFontWeights: n,
		headingFontWeight1: n[0],
		headingFontWeight2: n[1],
		headingFontWeight3: n[2],
		headingFontWeight4: n[3],
		headingFontWeight5: n[4],
		headingFontWeight6: n[5],
		borderColor: e.colors.borderColor,
		dataframeBorderColor: e.colors.dataframeBorderColor,
		dataframeHeaderBackgroundColor: e.colors.dataframeHeaderBackgroundColor,
		codeBackgroundColor: e.colors.codeBackgroundColor,
		font: e.genericFonts.bodyFont,
		chartCategoricalColors: e.colors.chartCategoricalColors,
		chartSequentialColors: e.colors.chartSequentialColors,
		chartDivergingColors: e.colors.chartDivergingColors,
		headingColor: e.colors.headingColor,
		borderColorLight: e.colors.borderColorLight,
		codeTextColor: e.colors.codeTextColor,
		widgetBorderColor: e.colors.widgetBorderColor || "transparent",
		redColor: e.colors.redColor,
		orangeColor: e.colors.orangeColor,
		yellowColor: e.colors.yellowColor,
		blueColor: e.colors.blueColor,
		greenColor: e.colors.greenColor,
		violetColor: e.colors.violetColor,
		grayColor: e.colors.grayColor,
		redBackgroundColor: e.colors.redBackgroundColor,
		orangeBackgroundColor: e.colors.orangeBackgroundColor,
		yellowBackgroundColor: e.colors.yellowBackgroundColor,
		blueBackgroundColor: e.colors.blueBackgroundColor,
		greenBackgroundColor: e.colors.greenBackgroundColor,
		violetBackgroundColor: e.colors.violetBackgroundColor,
		grayBackgroundColor: e.colors.grayBackgroundColor,
		redTextColor: e.colors.redTextColor,
		orangeTextColor: e.colors.orangeTextColor,
		yellowTextColor: e.colors.yellowTextColor,
		blueTextColor: e.colors.blueTextColor,
		greenTextColor: e.colors.greenTextColor,
		violetTextColor: e.colors.violetTextColor,
		grayTextColor: e.colors.grayTextColor,
		metricValueFontSize: e.fontSizes.metricValueFontSize,
		metricValueFontWeight: e.fontWeights.metricValueFontWeight
	};
}, De = (0, m.memo)(({ element: e, children: t, widgetMgr: n, fragmentId: r, componentRegistry: i }) => {
	let { arrowData: o, bytes: c, componentName: l, cssContent: u, cssSourcePath: d, data: p, htmlContent: h, id: g, jsContent: _, json: v, jsSourcePath: y, mixed: b } = e, x = (0, m.useMemo)(() => ({
		id: e.id,
		formId: e.formId
	}), [e.id, e.formId]), S = (0, m.useCallback)(() => {
		let e = n.getJsonValue(x);
		if (!e) return {};
		try {
			return JSON.parse(e);
		} catch (e) {
			let t = a(e);
			return G.warn("Failed to parse widget JSON value; returning empty object.", {
				widgetId: x.id,
				formId: x.formId,
				error: t.message
			}), {};
		}
	}, [x, n]), C = (0, m.useMemo)(() => we({
		arrowBlobs: b?.arrowBlobs || void 0,
		arrowData: o?.data || void 0,
		bytes: c,
		data: p,
		json: v,
		mixedJson: b?.json || void 0
	}), [
		p,
		v,
		o?.data,
		c,
		b?.json,
		b?.arrowBlobs
	]), w = s(), T = (0, m.useMemo)(() => Ee(w), [w]), E = (0, m.useMemo)(() => ({
		componentName: l,
		componentRegistry: i,
		cssContent: u?.trim(),
		cssSourcePath: d || void 0,
		data: C,
		fragmentId: r,
		getWidgetValue: S,
		htmlContent: h?.trim(),
		id: g,
		formId: e.formId || void 0,
		jsContent: _ || void 0,
		jsSourcePath: y || void 0,
		theme: T,
		widgetMgr: n
	}), [
		l,
		i,
		u,
		d,
		r,
		S,
		h,
		g,
		e.formId,
		_,
		y,
		C,
		T,
		n
	]);
	return /* @__PURE__ */ f.jsx(W.Provider, {
		value: E,
		children: t
	});
}), J = (e, t) => {
	if (e instanceof Error) return e;
	let n = t ? `${t}: ${String(e)}` : String(e);
	return Error(n);
}, Y = (e, t, n) => {
	let r = J(e, n);
	G.error(`BidiComponent Error: ${r.message}`, e), t(r);
}, Oe = (e, t) => {
	try {
		let n = document.createRange().createContextualFragment(e);
		t.appendChild(n);
	} catch (n) {
		G.warn("createContextualFragment failed, falling back to innerHTML", n), t.innerHTML = e;
	}
}, X = ({ containerRef: e, setError: t, skip: n = !1 }) => {
	let r = (0, m.useRef)(null), { htmlContent: i, cssContent: a, cssSourcePath: o, componentName: s, componentRegistry: { getBidiComponentURL: c } } = p(W), l = (0, m.useMemo)(() => {
		if (o) return c(s, o);
	}, [
		s,
		o,
		c
	]), d = u(l);
	return (0, m.useEffect)(() => {
		if (n) return;
		let o = e.current;
		if (o) try {
			if (r.current?.parentNode === o && o.removeChild(r.current), r.current = document.createElement("div"), i) {
				let e = document.createElement("div");
				Oe(i, e), r.current.appendChild(e);
			}
			if (a) {
				let e = document.createElement("style");
				e.textContent = a, r.current.appendChild(e);
			} else if (l) {
				let e = document.createElement("link");
				e.href = l, e.rel = "stylesheet", d && (e.crossOrigin = d), e.onerror = () => {
					Y(/* @__PURE__ */ Error(`Failed to load CSS from ${l}`), t);
				}, r.current.appendChild(e);
			}
			o.appendChild(r.current);
		} catch (e) {
			Y(e, t, "Failed to process HTML/CSS content");
		}
	}, [
		i,
		a,
		e,
		d,
		l,
		t,
		n
	]), r;
}, ke = new class {
	constructor() {
		this.hashSeed = 2166136261, this.hashPrime = 16777619, this.cache = /* @__PURE__ */ new Map();
	}
	computeHash(e) {
		let t = this.hashSeed;
		for (let n = 0; n < e.length; n++) t ^= e.charCodeAt(n), t = Math.imul(t >>> 0, this.hashPrime) >>> 0;
		return (t >>> 0).toString(16);
	}
	getOrCreateUrlForJs(e, t) {
		let n = this.computeHash(e), r = this.cache.get(n);
		if (r) return {
			url: r,
			hash: n
		};
		let i = `${e}
//# sourceURL=${t}-${n}.js`, a = new Blob([i], { type: "text/javascript" }), o = URL.createObjectURL(a);
		return this.cache.set(n, o), {
			url: o,
			hash: n
		};
	}
}(), Ae = "events";
function je(e) {
	if (e.includes(K)) throw Error("Base component id must not contain the delimiter sequence");
	return `${Se}_${e}${K}${Ae}`;
}
var Z = async ({ componentId: e, componentIdForWidgetMgr: t, componentName: n, data: r, formId: i, fragmentId: a, getWidgetValue: o, moduleUrl: s, parentElement: c, widgetMgr: l }) => {
	let u = await import(s);
	if (!u) throw Error("JS module does not exist.");
	if (!u.default || typeof u.default != "function") throw Error("JS module does not have a default export function.");
	return u.default({
		name: n,
		data: r,
		key: e,
		parentElement: c,
		setStateValue: (e, n) => {
			let r = {};
			try {
				r = {
					...o(),
					[e]: n
				};
			} catch (t) {
				G.error(`Failed to get existing value for ${e}`, t), r = { [e]: n };
			}
			l.setJsonValue({
				id: t,
				formId: i
			}, r, { fromUi: !0 }, a);
		},
		setTriggerValue: (e, n) => {
			if (i) {
				G.warn("BidiComponent: setTriggerValue ignored inside st.form. Triggers are not allowed in forms; use setStateValue and form submit instead.");
				return;
			}
			let r = je(t);
			l.setTriggerValue({
				id: r,
				formId: i
			}, { fromUi: !0 }, a, {
				event: e,
				value: n
			});
		}
	});
}, Q = ({ containerRef: e, setError: t, skip: n = !1 }) => {
	let i = `st-bidi-component-${(0, m.useMemo)(() => r(), [])}`, { componentName: a, data: o, formId: s, fragmentId: c, getWidgetValue: l, id: u, jsContent: d, jsSourcePath: f, theme: h, widgetMgr: g, componentRegistry: { getBidiComponentURL: _ } } = p(W), v = (0, m.useMemo)(() => {
		if (f) return _(a, f);
	}, [
		a,
		f,
		_
	]), y = (0, m.useRef)(), b = (0, m.useRef)(), x = (0, m.useRef)(!1);
	(0, m.useEffect)(() => {
		let { current: r } = e;
		n || !d && !v || !r || (async () => {
			try {
				if (d) {
					let { url: e } = ke.getOrCreateUrlForJs(d, `st-bidi-${a}`);
					y.current = await Z({
						componentId: i,
						componentIdForWidgetMgr: u,
						componentName: a,
						data: o,
						formId: s,
						fragmentId: c,
						getWidgetValue: l,
						moduleUrl: e,
						parentElement: r,
						widgetMgr: g
					});
				} else if (v) {
					let e = v;
					try {
						await new Promise((t, n) => {
							let r = document.createElement("script");
							r.type = "module", r.src = e, r.async = !0, r.onload = () => t(), r.onerror = () => n(/* @__PURE__ */ Error(`Failed to load script from ${v}`)), document.head.appendChild(r), b.current = r;
						}), y.current = await Z({
							componentId: i,
							componentIdForWidgetMgr: u,
							componentName: a,
							data: o,
							formId: s,
							fragmentId: c,
							getWidgetValue: l,
							moduleUrl: e,
							parentElement: r,
							widgetMgr: g
						});
					} catch (e) {
						throw J(e, `Failed to load or execute script from ${v}`);
					}
				}
			} catch (e) {
				x.current || Y(e, t);
			}
		})();
	}, [
		i,
		a,
		e,
		o,
		s,
		c,
		l,
		u,
		d,
		v,
		t,
		n,
		g,
		h
	]), (0, m.useEffect)(() => () => {
		x.current = !0;
		let e = y.current;
		e && Promise.resolve(e).then((e) => {
			e?.();
		}).catch((e) => {
			G.error("Failed to run custom component cleanup", e);
		});
		let t = b.current;
		t?.parentNode && t.parentNode.removeChild(t);
	}, []);
}, Me = /* @__PURE__ */ n("div", { target: "e1tun2hk1" })(({ cssCustomProperties: e }) => ({
	...e,
	display: "contents"
}), ""), $ = /* @__PURE__ */ n("div", { target: "e1tun2hk0" })({
	name: "w1atjl",
	styles: "width:100%;height:100%"
}), Ne = (0, m.memo)(() => {
	let e = (0, m.useRef)(null), n = (0, m.useRef)(null), [r, i] = (0, m.useState)(!1), [a, o] = (0, m.useState)(null), { id: s } = p(W);
	(0, m.useEffect)(() => {
		if (e.current) try {
			if (e.current.shadowRoot) {
				n.current = e.current.shadowRoot, i(!0);
				return;
			}
			n.current = e.current.attachShadow({ mode: "open" }), i(!0);
		} catch (e) {
			Y(e, o, "Failed to create shadow DOM");
		}
	}, [s]);
	let c = !r || !!a;
	return X({
		containerRef: n,
		setError: o,
		skip: c
	}), Q({
		containerRef: n,
		setError: o,
		skip: c
	}), a ? /* @__PURE__ */ f.jsx(t, {
		name: "BidiComponent Error",
		message: a.message,
		stack: a.stack
	}) : /* @__PURE__ */ f.jsx($, {
		ref: e,
		"data-testid": "stBidiComponentIsolated"
	});
}), Pe = (0, m.memo)(() => {
	let e = (0, m.useRef)(null), [n, r] = (0, m.useState)(null), i = !!n;
	return X({
		containerRef: e,
		setError: r,
		skip: i
	}), Q({
		containerRef: e,
		setError: r,
		skip: i
	}), n ? /* @__PURE__ */ f.jsx(t, {
		name: "BidiComponent Error",
		message: n.message,
		stack: n.stack
	}) : /* @__PURE__ */ f.jsx($, {
		ref: e,
		"data-testid": "stBidiComponentRegular"
	});
}), Fe = ({ children: e }) => {
	let { theme: t } = p(W), n = (0, m.useMemo)(() => Te(t), [t]);
	return /* @__PURE__ */ f.jsx(Me, {
		cssCustomProperties: n,
		children: e
	});
}, Ie = (0, m.memo)(({ element: e, widgetMgr: t, fragmentId: n, componentRegistry: r }) => {
	let { isolateStyles: i } = e;
	return /* @__PURE__ */ f.jsx(De, {
		element: e,
		widgetMgr: t,
		fragmentId: n,
		componentRegistry: r,
		children: /* @__PURE__ */ f.jsx($, {
			className: "stBidiComponent",
			children: /* @__PURE__ */ f.jsx(Fe, { children: i ? /* @__PURE__ */ f.jsx(Ne, {}) : /* @__PURE__ */ f.jsx(Pe, {}) })
		})
	});
});
//#endregion
export { Ie as default };

//# sourceMappingURL=BidiComponent-C0W-jB8K-2TB7vFeZ.js.map