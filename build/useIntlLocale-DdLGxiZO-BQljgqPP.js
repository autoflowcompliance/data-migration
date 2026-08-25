import { $i as e, $n as t, At as n, B as r, Ca as i, Ha as a, It as o, Ka as s, Kn as c, Ln as l, M as u, Rn as d, Ua as f, X as p, di as m, er as h, fi as g, ia as _, jr as v, q as y, t as b, tr as x } from "./index-Dl4ETd_L-D2oMd1k2.js";
import { a as S } from "./base-input-Drzzu2Q6-DCOO1-b4.js";
import { n as C } from "./stateful-menu-CW-YE2l8-DNHb-gL3.js";
import { i as w, r as T } from "./select-DyvsciAf-DTdJ1yfK.js";
import { n as E, r as D, t as O } from "./timepicker-Bp949u0W-KUvR56zU.js";
import { t as k } from "./input-CClPhvPt-C_5WYNdx.js";
//#region ../react/build/useIntlLocale-DdLGxiZO.js
var A = /* @__PURE__ */ s(f(), 1), ee = /* @__PURE__ */ s(a(), 1), te = [
	"title",
	"size",
	"color",
	"overrides"
];
function ne() {
	return ne = Object.assign ? Object.assign.bind() : function(e) {
		for (var t = 1; t < arguments.length; t++) {
			var n = arguments[t];
			for (var r in n) Object.prototype.hasOwnProperty.call(n, r) && (e[r] = n[r]);
		}
		return e;
	}, ne.apply(this, arguments);
}
function re(e, t) {
	if (e == null) return {};
	var n = ie(e, t), r, i;
	if (Object.getOwnPropertySymbols) {
		var a = Object.getOwnPropertySymbols(e);
		for (i = 0; i < a.length; i++) r = a[i], !(t.indexOf(r) >= 0) && Object.prototype.propertyIsEnumerable.call(e, r) && (n[r] = e[r]);
	}
	return n;
}
function ie(e, t) {
	if (e == null) return {};
	var n = {}, r = Object.keys(e), i, a;
	for (a = 0; a < r.length; a++) i = r[a], !(t.indexOf(i) >= 0) && (n[i] = e[i]);
	return n;
}
function ae(e, t) {
	return ue(e) || le(e, t) || se(e, t) || oe();
}
function oe() {
	throw TypeError("Invalid attempt to destructure non-iterable instance.\nIn order to be iterable, non-array objects must have a [Symbol.iterator]() method.");
}
function se(e, t) {
	if (e) {
		if (typeof e == "string") return ce(e, t);
		var n = Object.prototype.toString.call(e).slice(8, -1);
		if (n === "Object" && e.constructor && (n = e.constructor.name), n === "Map" || n === "Set") return Array.from(e);
		if (n === "Arguments" || /^(?:Ui|I)nt(?:8|16|32)(?:Clamped)?Array$/.test(n)) return ce(e, t);
	}
}
function ce(e, t) {
	(t == null || t > e.length) && (t = e.length);
	for (var n = 0, r = Array(t); n < t; n++) r[n] = e[n];
	return r;
}
function le(e, t) {
	var n = e == null ? null : typeof Symbol < "u" && e[Symbol.iterator] || e["@@iterator"];
	if (n != null) {
		var r = [], i = !0, a = !1, o, s;
		try {
			for (n = n.call(e); !(i = (o = n.next()).done) && (r.push(o.value), !(t && r.length === t)); i = !0);
		} catch (e) {
			a = !0, s = e;
		} finally {
			try {
				!i && n.return != null && n.return();
			} finally {
				if (a) throw s;
			}
		}
		return r;
	}
}
function ue(e) {
	if (Array.isArray(e)) return e;
}
function de(e, t) {
	var n = ae(i(), 2)[1], r = e.title, a = r === void 0 ? "Left" : r, o = e.size, s = e.color, c = e.overrides, l = c === void 0 ? {} : c, d = re(e, te), f = m({ component: n.icons && n.icons.ChevronLeft ? n.icons.ChevronLeft : null }, l && l.Svg ? _(l.Svg) : {});
	return /* @__PURE__ */ A.createElement(u, ne({
		viewBox: "0 0 24 24",
		ref: t,
		title: a,
		size: o,
		color: s,
		overrides: { Svg: f }
	}, d), /* @__PURE__ */ A.createElement("path", {
		fillRule: "evenodd",
		clipRule: "evenodd",
		d: "M9 12C9 12.2652 9.10536 12.5196 9.29289 12.7071L13.2929 16.7071C13.6834 17.0976 14.3166 17.0976 14.7071 16.7071C15.0976 16.3166 15.0976 15.6834 14.7071 15.2929L11.4142 12L14.7071 8.70711C15.0976 8.31658 15.0976 7.68342 14.7071 7.29289C14.3166 6.90237 13.6834 6.90237 13.2929 7.29289L9.29289 11.2929C9.10536 11.4804 9 11.7348 9 12Z"
	}));
}
var fe = /* @__PURE__ */ A.forwardRef(de), pe = [
	"title",
	"size",
	"color",
	"overrides"
];
function me() {
	return me = Object.assign ? Object.assign.bind() : function(e) {
		for (var t = 1; t < arguments.length; t++) {
			var n = arguments[t];
			for (var r in n) Object.prototype.hasOwnProperty.call(n, r) && (e[r] = n[r]);
		}
		return e;
	}, me.apply(this, arguments);
}
function he(e, t) {
	if (e == null) return {};
	var n = ge(e, t), r, i;
	if (Object.getOwnPropertySymbols) {
		var a = Object.getOwnPropertySymbols(e);
		for (i = 0; i < a.length; i++) r = a[i], !(t.indexOf(r) >= 0) && Object.prototype.propertyIsEnumerable.call(e, r) && (n[r] = e[r]);
	}
	return n;
}
function ge(e, t) {
	if (e == null) return {};
	var n = {}, r = Object.keys(e), i, a;
	for (a = 0; a < r.length; a++) i = r[a], !(t.indexOf(i) >= 0) && (n[i] = e[i]);
	return n;
}
function _e(e, t) {
	return Se(e) || xe(e, t) || ye(e, t) || ve();
}
function ve() {
	throw TypeError("Invalid attempt to destructure non-iterable instance.\nIn order to be iterable, non-array objects must have a [Symbol.iterator]() method.");
}
function ye(e, t) {
	if (e) {
		if (typeof e == "string") return be(e, t);
		var n = Object.prototype.toString.call(e).slice(8, -1);
		if (n === "Object" && e.constructor && (n = e.constructor.name), n === "Map" || n === "Set") return Array.from(e);
		if (n === "Arguments" || /^(?:Ui|I)nt(?:8|16|32)(?:Clamped)?Array$/.test(n)) return be(e, t);
	}
}
function be(e, t) {
	(t == null || t > e.length) && (t = e.length);
	for (var n = 0, r = Array(t); n < t; n++) r[n] = e[n];
	return r;
}
function xe(e, t) {
	var n = e == null ? null : typeof Symbol < "u" && e[Symbol.iterator] || e["@@iterator"];
	if (n != null) {
		var r = [], i = !0, a = !1, o, s;
		try {
			for (n = n.call(e); !(i = (o = n.next()).done) && (r.push(o.value), !(t && r.length === t)); i = !0);
		} catch (e) {
			a = !0, s = e;
		} finally {
			try {
				!i && n.return != null && n.return();
			} finally {
				if (a) throw s;
			}
		}
		return r;
	}
}
function Se(e) {
	if (Array.isArray(e)) return e;
}
function Ce(e, t) {
	var n = _e(i(), 2)[1], r = e.title, a = r === void 0 ? "Right" : r, o = e.size, s = e.color, c = e.overrides, l = c === void 0 ? {} : c, d = he(e, pe), f = m({ component: n.icons && n.icons.ChevronRight ? n.icons.ChevronRight : null }, l && l.Svg ? _(l.Svg) : {});
	return /* @__PURE__ */ A.createElement(u, me({
		viewBox: "0 0 24 24",
		ref: t,
		title: a,
		size: o,
		color: s,
		overrides: { Svg: f }
	}, d), /* @__PURE__ */ A.createElement("path", {
		fillRule: "evenodd",
		clipRule: "evenodd",
		d: "M9.29289 7.29289C8.90237 7.68342 8.90237 8.31658 9.29289 8.70711L12.5858 12L9.29289 15.2929C8.90237 15.6834 8.90237 16.3166 9.29289 16.7071C9.68342 17.0976 10.3166 17.0976 10.7071 16.7071L14.7071 12.7071C14.8946 12.5196 15 12.2652 15 12C15 11.7348 14.8946 11.4804 14.7071 11.2929L10.7071 7.29289C10.3166 6.90237 9.68342 6.90237 9.29289 7.29289Z"
	}));
}
var we = /* @__PURE__ */ A.forwardRef(Ce), Te = { exports: {} }, Ee, De;
function Oe() {
	if (De) return Ee;
	De = 1;
	function e(e) {
		return e && typeof e == "object" && "default" in e ? e.default : e;
	}
	var t = e(A.default), n = ee.default;
	function r(e, t) {
		for (var n = Object.getOwnPropertyNames(t), r = 0; r < n.length; r++) {
			var i = n[r], a = Object.getOwnPropertyDescriptor(t, i);
			a && a.configurable && e[i] === void 0 && Object.defineProperty(e, i, a);
		}
		return e;
	}
	function i() {
		return (i = Object.assign || function(e) {
			for (var t = 1; t < arguments.length; t++) {
				var n = arguments[t];
				for (var r in n) Object.prototype.hasOwnProperty.call(n, r) && (e[r] = n[r]);
			}
			return e;
		}).apply(this, arguments);
	}
	function a(e, t) {
		e.prototype = Object.create(t.prototype), r(e.prototype.constructor = e, t);
	}
	function o(e, t) {
		if (e == null) return {};
		var n, r, i = {}, a = Object.keys(e);
		for (r = 0; r < a.length; r++) n = a[r], 0 <= t.indexOf(n) || (i[n] = e[n]);
		return i;
	}
	function s(e) {
		if (e === void 0) throw ReferenceError("this hasn't been initialised - super() hasn't been called");
		return e;
	}
	var c = function(e, t, n, r, i, a, o, s) {
		if (!e) {
			var c;
			if (t === void 0) c = /* @__PURE__ */ Error("Minified exception occurred; use the non-minified dev environment for the full error message and additional helpful warnings.");
			else {
				var l = [
					n,
					r,
					i,
					a,
					o,
					s
				], u = 0;
				(c = Error(t.replace(/%s/g, function() {
					return l[u++];
				}))).name = "Invariant Violation";
			}
			throw c.framesToPop = 1, c;
		}
	};
	function l(e, t, n) {
		if ("selectionStart" in e && "selectionEnd" in e) e.selectionStart = t, e.selectionEnd = n;
		else {
			var r = e.createTextRange();
			r.collapse(!0), r.moveStart("character", t), r.moveEnd("character", n - t), r.select();
		}
	}
	function u(e) {
		var t = 0, n = 0;
		if ("selectionStart" in e && "selectionEnd" in e) t = e.selectionStart, n = e.selectionEnd;
		else {
			var r = document.selection.createRange();
			r.parentElement() === e && (t = -r.moveStart("character", -e.value.length), n = -r.moveEnd("character", -e.value.length));
		}
		return {
			start: t,
			end: n,
			length: n - t
		};
	}
	var d = {
		9: "[0-9]",
		a: "[A-Za-z]",
		"*": "[A-Za-z0-9]"
	}, f = "_";
	function p(e, t, n) {
		var r = "", i = "", a = null, o = [];
		if (t === void 0 && (t = f), n ??= d, !e || typeof e != "string") return {
			maskChar: t,
			formatChars: n,
			mask: null,
			prefix: null,
			lastEditablePosition: null,
			permanents: []
		};
		var s = !1;
		return e.split("").forEach(function(e) {
			s = !s && e === "\\" || (s || !n[e] ? (o.push(r.length), r.length === o.length - 1 && (i += e)) : a = r.length + 1, r += e, !1);
		}), {
			maskChar: t,
			formatChars: n,
			prefix: i,
			mask: r,
			lastEditablePosition: a,
			permanents: o
		};
	}
	function m(e, t) {
		return e.permanents.indexOf(t) !== -1;
	}
	function h(e, t, n) {
		var r = e.mask, i = e.formatChars;
		if (!n) return !1;
		if (m(e, t)) return r[t] === n;
		var a = i[r[t]];
		return new RegExp(a).test(n);
	}
	function g(e, t) {
		return t.split("").every(function(t, n) {
			return m(e, n) || !h(e, n, t);
		});
	}
	function _(e, t) {
		var n = e.maskChar, r = e.prefix;
		if (!n) {
			for (; t.length > r.length && m(e, t.length - 1);) t = t.slice(0, t.length - 1);
			return t.length;
		}
		for (var i = r.length, a = t.length; a >= r.length; a--) {
			var o = t[a];
			if (!m(e, a) && h(e, a, o)) {
				i = a + 1;
				break;
			}
		}
		return i;
	}
	function v(e, t) {
		return _(e, t) === e.mask.length;
	}
	function y(e, t) {
		var n = e.maskChar, r = e.mask, i = e.prefix;
		if (!n) {
			for ((t = x(e, "", t, 0)).length < i.length && (t = i); t.length < r.length && m(e, t.length);) t += r[t.length];
			return t;
		}
		if (t) return x(e, y(e, ""), t, 0);
		for (var a = 0; a < r.length; a++) m(e, a) ? t += r[a] : t += n;
		return t;
	}
	function b(e, t, n, r) {
		var i = n + r, a = e.maskChar, o = e.mask, s = e.prefix, c = t.split("");
		if (a) return c.map(function(t, r) {
			return r < n || i <= r ? t : m(e, r) ? o[r] : a;
		}).join("");
		for (var l = i; l < c.length; l++) m(e, l) && (c[l] = "");
		return n = Math.max(s.length, n), c.splice(n, i - n), t = c.join(""), y(e, t);
	}
	function x(e, t, n, r) {
		var i = e.mask, a = e.maskChar, o = e.prefix, s = n.split(""), c = v(e, t);
		return !a && r > t.length && (t += i.slice(t.length, r)), s.every(function(n) {
			for (; d = n, m(e, u = r) && d !== i[u];) {
				if (r >= t.length && (t += i[r]), s = n, l = r, a && m(e, l) && s === a) return !0;
				if (++r >= i.length) return !1;
			}
			var s, l, u, d;
			return !h(e, r, n) && n !== a || (r < t.length ? t = a || c || r < o.length ? t.slice(0, r) + n + t.slice(r + 1) : (t = t.slice(0, r) + n + t.slice(r), y(e, t)) : a || (t += n), ++r < i.length);
		}), t;
	}
	function S(e, t, n, r) {
		var i = e.mask, a = e.maskChar, o = n.split(""), s = r;
		return o.every(function(t) {
			for (; o = t, m(e, n = r) && o !== i[n];) if (++r >= i.length) return !1;
			var n, o;
			return (h(e, r, t) || t === a) && r++, r < i.length;
		}), r - s;
	}
	function C(e, t) {
		for (var n = t; 0 <= n; --n) if (!m(e, n)) return n;
		return null;
	}
	function w(e, t) {
		for (var n = e.mask, r = t; r < n.length; ++r) if (!m(e, r)) return r;
		return null;
	}
	function T(e) {
		return e || e === 0 ? e + "" : "";
	}
	function E(e, t, n, r, i) {
		var a = e.mask, o = e.prefix, s = e.lastEditablePosition, c = t, l = "", u = 0, d = 0, f = Math.min(i.start, n.start);
		return n.end > i.start ? d = (u = S(e, r, l = c.slice(i.start, n.end), f)) ? i.length : 0 : c.length < r.length && (d = r.length - c.length), c = r, d && (d === 1 && !i.length && (f = i.start === n.start ? w(e, n.start) : C(e, n.start)), c = b(e, c, f, d)), c = x(e, c, l, f), (f += u) >= a.length ? f = a.length : f < o.length && !u ? f = o.length : f >= o.length && f < s && u && (f = w(e, f)), l ||= null, {
			value: c = y(e, c),
			enteredString: l,
			selection: {
				start: f,
				end: f
			}
		};
	}
	function D() {
		var e = /* @__PURE__ */ RegExp("windows", "i"), t = /* @__PURE__ */ RegExp("phone", "i"), n = navigator.userAgent;
		return e.test(n) && t.test(n);
	}
	function O(e) {
		return typeof e == "function";
	}
	function k() {
		return window.requestAnimationFrame || window.webkitRequestAnimationFrame || window.mozRequestAnimationFrame;
	}
	function te() {
		return window.cancelAnimationFrame || window.webkitCancelRequestAnimationFrame || window.webkitCancelAnimationFrame || window.mozCancelAnimationFrame;
	}
	function ne(e) {
		return (te() ? k() : function() {
			return setTimeout(e, 1e3 / 60);
		})(e);
	}
	function re(e) {
		(te() || clearTimeout)(e);
	}
	return Ee = function(e) {
		function r(t) {
			var r = e.call(this, t) || this;
			r.focused = !1, r.mounted = !1, r.previousSelection = null, r.selectionDeferId = null, r.saveSelectionLoopDeferId = null, r.saveSelectionLoop = function() {
				r.previousSelection = r.getSelection(), r.saveSelectionLoopDeferId = ne(r.saveSelectionLoop);
			}, r.runSaveSelectionLoop = function() {
				r.saveSelectionLoopDeferId === null && r.saveSelectionLoop();
			}, r.stopSaveSelectionLoop = function() {
				r.saveSelectionLoopDeferId !== null && (re(r.saveSelectionLoopDeferId), r.saveSelectionLoopDeferId = null, r.previousSelection = null);
			}, r.getInputDOMNode = function() {
				if (!r.mounted) return null;
				var e = n.findDOMNode(s(s(r))), t = typeof window < "u" && e instanceof window.Element;
				if (e && !t) return null;
				if (e.nodeName !== "INPUT" && (e = e.querySelector("input")), !e) throw Error("react-input-mask: inputComponent doesn't contain input node");
				return e;
			}, r.getInputValue = function() {
				var e = r.getInputDOMNode();
				return e ? e.value : null;
			}, r.setInputValue = function(e) {
				var t = r.getInputDOMNode();
				t && (r.value = e, t.value = e);
			}, r.setCursorToEnd = function() {
				var e = _(r.maskOptions, r.value), t = w(r.maskOptions, e);
				t !== null && r.setCursorPosition(t);
			}, r.setSelection = function(e, t, n) {
				n === void 0 && (n = {});
				var i = r.getInputDOMNode(), a = r.isFocused();
				i && a && (n.deferred || l(i, e, t), r.selectionDeferId !== null && re(r.selectionDeferId), r.selectionDeferId = ne(function() {
					r.selectionDeferId = null, l(i, e, t);
				}), r.previousSelection = {
					start: e,
					end: t,
					length: Math.abs(t - e)
				});
			}, r.getSelection = function() {
				return u(r.getInputDOMNode());
			}, r.getCursorPosition = function() {
				return r.getSelection().start;
			}, r.setCursorPosition = function(e) {
				r.setSelection(e, e);
			}, r.isFocused = function() {
				return r.focused;
			}, r.getBeforeMaskedValueChangeConfig = function() {
				var e = r.maskOptions, t = e.mask, n = e.maskChar, i = e.permanents, a = e.formatChars;
				return {
					mask: t,
					maskChar: n,
					permanents: i,
					alwaysShowMask: !!r.props.alwaysShowMask,
					formatChars: a
				};
			}, r.isInputAutofilled = function(e, t, n, i) {
				var a = r.getInputDOMNode();
				try {
					if (a.matches(":-webkit-autofill")) return !0;
				} catch {}
				return !r.focused || i.end < n.length && t.end === e.length;
			}, r.onChange = function(e) {
				var t = s(s(r)).beforePasteState, n = s(s(r)).previousSelection, i = r.props.beforeMaskedValueChange, a = r.getInputValue(), o = r.value, c = r.getSelection();
				r.isInputAutofilled(a, c, o, n) && (o = y(r.maskOptions, ""), n = {
					start: 0,
					end: 0,
					length: 0
				}), t && (n = t.selection, o = t.value, c = {
					start: n.start + a.length,
					end: n.start + a.length,
					length: 0
				}, a = o.slice(0, n.start) + a + o.slice(n.end), r.beforePasteState = null);
				var l = E(r.maskOptions, a, c, o, n), u = l.enteredString, d = l.selection, f = l.value;
				if (O(i)) {
					var p = i({
						value: f,
						selection: d
					}, {
						value: o,
						selection: n
					}, u, r.getBeforeMaskedValueChangeConfig());
					f = p.value, d = p.selection;
				}
				r.setInputValue(f), O(r.props.onChange) && r.props.onChange(e), r.isWindowsPhoneBrowser ? r.setSelection(d.start, d.end, { deferred: !0 }) : r.setSelection(d.start, d.end);
			}, r.onFocus = function(e) {
				var t = r.props.beforeMaskedValueChange, n = r.maskOptions, i = n.mask, a = n.prefix;
				if (r.focused = !0, r.mounted = !0, i) {
					if (r.value) _(r.maskOptions, r.value) < r.maskOptions.mask.length && r.setCursorToEnd();
					else {
						var o = y(r.maskOptions, a), s = y(r.maskOptions, o), c = _(r.maskOptions, s), l = w(r.maskOptions, c), u = {
							start: l,
							end: l
						};
						if (O(t)) {
							var d = t({
								value: s,
								selection: u
							}, {
								value: r.value,
								selection: null
							}, null, r.getBeforeMaskedValueChangeConfig());
							s = d.value, u = d.selection;
						}
						var f = s !== r.getInputValue();
						f && r.setInputValue(s), f && O(r.props.onChange) && r.props.onChange(e), r.setSelection(u.start, u.end);
					}
					r.runSaveSelectionLoop();
				}
				O(r.props.onFocus) && r.props.onFocus(e);
			}, r.onBlur = function(e) {
				var t = r.props.beforeMaskedValueChange, n = r.maskOptions.mask;
				if (r.stopSaveSelectionLoop(), r.focused = !1, n && !r.props.alwaysShowMask && g(r.maskOptions, r.value)) {
					var i = "";
					O(t) && (i = t({
						value: i,
						selection: null
					}, {
						value: r.value,
						selection: r.previousSelection
					}, null, r.getBeforeMaskedValueChangeConfig()).value);
					var a = i !== r.getInputValue();
					a && r.setInputValue(i), a && O(r.props.onChange) && r.props.onChange(e);
				}
				O(r.props.onBlur) && r.props.onBlur(e);
			}, r.onMouseDown = function(e) {
				!r.focused && document.addEventListener && (r.mouseDownX = e.clientX, r.mouseDownY = e.clientY, r.mouseDownTime = (/* @__PURE__ */ new Date()).getTime(), document.addEventListener("mouseup", function e(t) {
					if (document.removeEventListener("mouseup", e), r.focused) {
						var n = Math.abs(t.clientX - r.mouseDownX), i = Math.abs(t.clientY - r.mouseDownY), a = Math.max(n, i), o = (/* @__PURE__ */ new Date()).getTime() - r.mouseDownTime;
						(a <= 10 && o <= 200 || a <= 5 && o <= 300) && r.setCursorToEnd();
					}
				})), O(r.props.onMouseDown) && r.props.onMouseDown(e);
			}, r.onPaste = function(e) {
				O(r.props.onPaste) && r.props.onPaste(e), e.defaultPrevented || (r.beforePasteState = {
					value: r.getInputValue(),
					selection: r.getSelection()
				}, r.setInputValue(""));
			}, r.handleRef = function(e) {
				r.props.children == null && O(r.props.inputRef) && r.props.inputRef(e);
			};
			var i = t.mask, a = t.maskChar, o = t.formatChars, c = t.alwaysShowMask, d = t.beforeMaskedValueChange, f = t.defaultValue, m = t.value;
			r.maskOptions = p(i, a, o), f ??= "", m ??= f;
			var h = T(m);
			if (r.maskOptions.mask && (c || h) && (h = y(r.maskOptions, h), O(d))) {
				var v = t.value;
				t.value ?? (v = f), h = d({
					value: h,
					selection: null
				}, {
					value: v = T(v),
					selection: null
				}, null, r.getBeforeMaskedValueChangeConfig()).value;
			}
			return r.value = h, r;
		}
		a(r, e);
		var d = r.prototype;
		return d.componentDidMount = function() {
			this.mounted = !0, this.getInputDOMNode() && (this.isWindowsPhoneBrowser = D(), this.maskOptions.mask && this.getInputValue() !== this.value && this.setInputValue(this.value));
		}, d.componentDidUpdate = function() {
			var e = this.previousSelection, t = this.props, n = t.beforeMaskedValueChange, r = t.alwaysShowMask, i = t.mask, a = t.maskChar, o = t.formatChars, s = this.maskOptions, c = r || this.isFocused(), l = this.props.value != null, u = l ? T(this.props.value) : this.value, d = e ? e.start : null;
			if (this.maskOptions = p(i, a, o), this.maskOptions.mask) {
				!s.mask && this.isFocused() && this.runSaveSelectionLoop();
				var f = this.maskOptions.mask && this.maskOptions.mask !== s.mask;
				if (s.mask || l || (u = this.getInputValue()), (f || this.maskOptions.mask && (u || c)) && (u = y(this.maskOptions, u)), f) {
					var m = _(this.maskOptions, u);
					(d === null || m < d) && (d = v(this.maskOptions, u) ? m : w(this.maskOptions, m));
				}
				!this.maskOptions.mask || !g(this.maskOptions, u) || c || l && this.props.value || (u = "");
				var h = {
					start: d,
					end: d
				};
				if (O(n)) {
					var b = n({
						value: u,
						selection: h
					}, {
						value: this.value,
						selection: this.previousSelection
					}, null, this.getBeforeMaskedValueChangeConfig());
					u = b.value, h = b.selection;
				}
				this.value = u;
				var x = this.getInputValue() !== this.value;
				x ? (this.setInputValue(this.value), this.forceUpdate()) : f && this.forceUpdate();
				var S = !1;
				h.start != null && h.end != null && (S = !e || e.start !== h.start || e.end !== h.end), (S || x) && this.setSelection(h.start, h.end);
			} else s.mask && (this.stopSaveSelectionLoop(), this.forceUpdate());
		}, d.componentWillUnmount = function() {
			this.mounted = !1, this.selectionDeferId !== null && re(this.selectionDeferId), this.stopSaveSelectionLoop();
		}, d.render = function() {
			var e, n = this.props, r = (n.mask, n.alwaysShowMask, n.maskChar, n.formatChars, n.inputRef, n.beforeMaskedValueChange, n.children), a = o(n, [
				"mask",
				"alwaysShowMask",
				"maskChar",
				"formatChars",
				"inputRef",
				"beforeMaskedValueChange",
				"children"
			]);
			if (r) {
				O(r) || c(!1);
				var s = [
					"onChange",
					"onPaste",
					"onMouseDown",
					"onFocus",
					"onBlur",
					"value",
					"disabled",
					"readOnly"
				], l = i({}, a);
				s.forEach(function(e) {
					return delete l[e];
				}), e = r(l), s.filter(function(t) {
					return e.props[t] != null && e.props[t] !== a[t];
				}).length && c(!1);
			} else e = t.createElement("input", i({ ref: this.handleRef }, a));
			var u = {
				onFocus: this.onFocus,
				onBlur: this.onBlur
			};
			return this.maskOptions.mask && (a.disabled || a.readOnly || (u.onChange = this.onChange, u.onPaste = this.onPaste, u.onMouseDown = this.onMouseDown), a.value != null && (u.value = this.value)), e = t.cloneElement(e, u);
		}, r;
	}(t.Component), Ee;
}
var ke;
function Ae() {
	return ke || (ke = 1, Te.exports = Oe()), Te.exports;
}
var je = /* @__PURE__ */ c(Ae()), Me = [
	"startEnhancer",
	"endEnhancer",
	"error",
	"positive",
	"onChange",
	"onFocus",
	"onBlur",
	"value",
	"disabled",
	"readOnly"
], Ne = ["Input"], Pe = [
	"mask",
	"maskChar",
	"overrides"
];
function Fe(e, t) {
	var n = Object.keys(e);
	if (Object.getOwnPropertySymbols) {
		var r = Object.getOwnPropertySymbols(e);
		t && (r = r.filter(function(t) {
			return Object.getOwnPropertyDescriptor(e, t).enumerable;
		})), n.push.apply(n, r);
	}
	return n;
}
function Ie(e) {
	for (var t = 1; t < arguments.length; t++) {
		var n = arguments[t] == null ? {} : arguments[t];
		t % 2 ? Fe(Object(n), !0).forEach(function(t) {
			Le(e, t, n[t]);
		}) : Object.getOwnPropertyDescriptors ? Object.defineProperties(e, Object.getOwnPropertyDescriptors(n)) : Fe(Object(n)).forEach(function(t) {
			Object.defineProperty(e, t, Object.getOwnPropertyDescriptor(n, t));
		});
	}
	return e;
}
function Le(e, t, n) {
	return t in e ? Object.defineProperty(e, t, {
		value: n,
		enumerable: !0,
		configurable: !0,
		writable: !0
	}) : e[t] = n, e;
}
function Re(e) {
	"@babel/helpers - typeof";
	return Re = typeof Symbol == "function" && typeof Symbol.iterator == "symbol" ? function(e) {
		return typeof e;
	} : function(e) {
		return e && typeof Symbol == "function" && e.constructor === Symbol && e !== Symbol.prototype ? "symbol" : typeof e;
	}, Re(e);
}
function ze() {
	return ze = Object.assign ? Object.assign.bind() : function(e) {
		for (var t = 1; t < arguments.length; t++) {
			var n = arguments[t];
			for (var r in n) Object.prototype.hasOwnProperty.call(n, r) && (e[r] = n[r]);
		}
		return e;
	}, ze.apply(this, arguments);
}
function Be(e, t) {
	if (e == null) return {};
	var n = Ve(e, t), r, i;
	if (Object.getOwnPropertySymbols) {
		var a = Object.getOwnPropertySymbols(e);
		for (i = 0; i < a.length; i++) r = a[i], !(t.indexOf(r) >= 0) && Object.prototype.propertyIsEnumerable.call(e, r) && (n[r] = e[r]);
	}
	return n;
}
function Ve(e, t) {
	if (e == null) return {};
	var n = {}, r = Object.keys(e), i, a;
	for (a = 0; a < r.length; a++) i = r[a], !(t.indexOf(i) >= 0) && (n[i] = e[i]);
	return n;
}
var He = /* @__PURE__ */ A.forwardRef(function(e, t) {
	e.startEnhancer, e.endEnhancer, e.error, e.positive;
	var n = e.onChange, r = e.onFocus, i = e.onBlur, a = e.value, o = e.disabled, s = e.readOnly, c = Be(e, Me);
	return /* @__PURE__ */ A.createElement(je, ze({
		onChange: n,
		onFocus: r,
		onBlur: i,
		value: a,
		disabled: o,
		readOnly: s
	}, c), function(e) {
		return /* @__PURE__ */ A.createElement(S, ze({
			ref: t,
			onChange: n,
			onFocus: r,
			onBlur: i,
			value: a,
			disabled: o,
			readOnly: s
		}, e));
	});
});
He.displayName = "MaskOverride";
function Ue(e) {
	var t = e.mask, n = e.maskChar, r = e.overrides;
	r = r === void 0 ? {} : r;
	var i = r.Input, a = i === void 0 ? {} : i, o = Be(r, Ne), s = Be(e, Pe), c = He, l = {}, u = {};
	typeof a == "function" ? c = a : Re(a) === "object" && (c = a.component || c, l = a.props || {}, u = a.style || {}), Re(l) === "object" && (l = Ie(Ie({}, l), {}, {
		mask: l.mask || t,
		maskChar: l.maskChar || n
	}));
	var d = Ie({ Input: {
		component: c,
		props: l,
		style: u
	} }, o);
	return /* @__PURE__ */ A.createElement(k, ze({}, s, { overrides: d }));
}
Ue.defaultProps = { maskChar: " " };
var We = Object.freeze({
	horizontal: "horizontal",
	vertical: "vertical"
}), Ge = [
	0,
	1,
	2,
	3,
	4,
	5,
	6
], Ke = [
	0,
	1,
	2,
	3,
	4,
	5,
	6,
	7,
	8,
	9,
	10,
	11
], j = {
	high: "high",
	default: "default"
}, M = {
	startDate: "startDate",
	endDate: "endDate"
}, qe = { locked: "locked" };
function Je(e, t) {
	var n = Object.keys(e);
	if (Object.getOwnPropertySymbols) {
		var r = Object.getOwnPropertySymbols(e);
		t && (r = r.filter(function(t) {
			return Object.getOwnPropertyDescriptor(e, t).enumerable;
		})), n.push.apply(n, r);
	}
	return n;
}
function N(e) {
	for (var t = 1; t < arguments.length; t++) {
		var n = arguments[t] == null ? {} : arguments[t];
		t % 2 ? Je(Object(n), !0).forEach(function(t) {
			Ye(e, t, n[t]);
		}) : Object.getOwnPropertyDescriptors ? Object.defineProperties(e, Object.getOwnPropertyDescriptors(n)) : Je(Object(n)).forEach(function(t) {
			Object.defineProperty(e, t, Object.getOwnPropertyDescriptor(n, t));
		});
	}
	return e;
}
function Ye(e, t, n) {
	return t in e ? Object.defineProperty(e, t, {
		value: n,
		enumerable: !0,
		configurable: !0,
		writable: !0
	}) : e[t] = n, e;
}
var Xe = e("label", function(e) {
	var t = e.$disabled, n = e.$theme, r = n.colors, i = n.typography;
	return N(N({}, i.font250), {}, {
		width: "100%",
		color: t ? r.contentSecondary : r.contentPrimary,
		display: "block",
		paddingTop: 0,
		paddingRight: 0,
		paddingBottom: 0,
		paddingLeft: 0
	});
});
Xe.displayName = "Label", Xe.displayName = "Label";
var Ze = e("span", function(e) {
	var t = e.$theme.sizing;
	return {
		display: "flex",
		width: "100%",
		marginTop: t.scale300,
		marginRight: 0,
		marginBottom: t.scale300,
		marginLeft: 0
	};
});
Ze.displayName = "LabelContainer", Ze.displayName = "LabelContainer";
var Qe = e("span", function(e) {
	var t = e.$disabled, n = e.$counterError, r = e.$theme, i = r.colors, a = r.typography;
	return N(N({}, a.font100), {}, {
		flex: 0,
		width: "100%",
		color: n ? i.negative400 : t ? i.contentSecondary : i.contentPrimary
	});
});
Qe.displayName = "LabelEndEnhancer", Qe.displayName = "LabelEndEnhancer";
var $e = e("div", function(e) {
	var t = e.$error, n = e.$positive, r = e.$theme, i = r.colors, a = r.sizing, o = r.typography, s = i.contentSecondary;
	return t ? s = i.negative400 : n && (s = i.positive400), N(N({}, o.font100), {}, {
		color: s,
		paddingTop: 0,
		paddingRight: 0,
		paddingBottom: 0,
		paddingLeft: 0,
		marginTop: a.scale300,
		marginRight: 0,
		marginBottom: a.scale300,
		marginLeft: 0
	});
});
$e.displayName = "Caption", $e.displayName = "Caption";
var et = e("div", function(e) {
	return {
		width: "100%",
		marginBottom: e.$theme.sizing.scale600
	};
});
et.displayName = "ControlContainer", et.displayName = "ControlContainer";
function P() {
	return P = Object.assign ? Object.assign.bind() : function(e) {
		for (var t = 1; t < arguments.length; t++) {
			var n = arguments[t];
			for (var r in n) Object.prototype.hasOwnProperty.call(n, r) && (e[r] = n[r]);
		}
		return e;
	}, P.apply(this, arguments);
}
function tt(e) {
	"@babel/helpers - typeof";
	return tt = typeof Symbol == "function" && typeof Symbol.iterator == "symbol" ? function(e) {
		return typeof e;
	} : function(e) {
		return e && typeof Symbol == "function" && e.constructor === Symbol && e !== Symbol.prototype ? "symbol" : typeof e;
	}, tt(e);
}
function nt(e, t) {
	if (!(e instanceof t)) throw TypeError("Cannot call a class as a function");
}
function rt(e, t) {
	for (var n = 0; n < t.length; n++) {
		var r = t[n];
		r.enumerable = r.enumerable || !1, r.configurable = !0, "value" in r && (r.writable = !0), Object.defineProperty(e, r.key, r);
	}
}
function it(e, t, n) {
	return t && rt(e.prototype, t), Object.defineProperty(e, "prototype", { writable: !1 }), e;
}
function at(e, t) {
	if (typeof t != "function" && t !== null) throw TypeError("Super expression must either be null or a function");
	e.prototype = Object.create(t && t.prototype, { constructor: {
		value: e,
		writable: !0,
		configurable: !0
	} }), Object.defineProperty(e, "prototype", { writable: !1 }), t && ot(e, t);
}
function ot(e, t) {
	return ot = Object.setPrototypeOf ? Object.setPrototypeOf.bind() : function(e, t) {
		return e.__proto__ = t, e;
	}, ot(e, t);
}
function st(e) {
	var t = ut();
	return function() {
		var n = dt(e), r;
		if (t) {
			var i = dt(this).constructor;
			r = Reflect.construct(n, arguments, i);
		} else r = n.apply(this, arguments);
		return ct(this, r);
	};
}
function ct(e, t) {
	if (t && (tt(t) === "object" || typeof t == "function")) return t;
	if (t !== void 0) throw TypeError("Derived constructors may only return object or undefined");
	return lt(e);
}
function lt(e) {
	if (e === void 0) throw ReferenceError("this hasn't been initialised - super() hasn't been called");
	return e;
}
function ut() {
	if (typeof Reflect > "u" || !Reflect.construct || Reflect.construct.sham) return !1;
	if (typeof Proxy == "function") return !0;
	try {
		return Boolean.prototype.valueOf.call(Reflect.construct(Boolean, [], function() {})), !0;
	} catch {
		return !1;
	}
}
function dt(e) {
	return dt = Object.setPrototypeOf ? Object.getPrototypeOf.bind() : function(e) {
		return e.__proto__ || Object.getPrototypeOf(e);
	}, dt(e);
}
function ft(e, t, n) {
	return t in e ? Object.defineProperty(e, t, {
		value: n,
		enumerable: !0,
		configurable: !0,
		writable: !0
	}) : e[t] = n, e;
}
function pt(e, t, n, r) {
	return t && typeof t != "boolean" ? typeof t == "function" ? t(r) : t : n && typeof n != "boolean" ? typeof n == "function" ? n(r) : n : e ? typeof e == "function" ? e(r) : e : null;
}
var mt = /* @__PURE__ */ function(e) {
	at(r, e);
	var n = st(r);
	function r() {
		return nt(this, r), n.apply(this, arguments);
	}
	return it(r, [{
		key: "render",
		value: function() {
			var e = this.props, n = e.overrides, r = n.Label, i = n.LabelEndEnhancer, a = n.LabelContainer, s = n.Caption, c = n.ControlContainer, l = e.label, u = e.caption, d = e.disabled, f = e.error, p = e.positive, m = e.htmlFor, g = e.children, _ = e.counter, v = A.Children.only(g).props, y = {
				$disabled: !!d,
				$error: !!f,
				$positive: !!p
			}, b = t(r) || Xe, x = t(i) || Qe, S = t(a) || Ze, C = t(s) || $e, w = t(c) || et, T = pt(u, f, p, y), E = this.props.labelEndEnhancer;
			if (_) {
				var D = null, O = null, k = null;
				tt(_) === "object" && (O = _.length, D = _.maxLength, k = _.error), D ||= v.maxLength, O == null && typeof v.value == "string" && (O = v.value.length), O ??= 0, y.$length = O, D == null ? E ||= `${O}` : (y.$maxLength = O, E ||= `${O}/${D}`, O > D && k == null && (k = !0)), k && (y.$error = !0, y.$counterError = !0);
			}
			return /* @__PURE__ */ A.createElement(A.Fragment, null, l && /* @__PURE__ */ A.createElement(S, P({}, y, h(a)), /* @__PURE__ */ A.createElement(b, P({
				"data-baseweb": "form-control-label",
				htmlFor: m || v.id
			}, y, h(r)), typeof l == "function" ? l(y) : l), !!E && /* @__PURE__ */ A.createElement(x, P({}, y, h(i)), typeof E == "function" ? E(y) : E)), /* @__PURE__ */ A.createElement(o, null, function(e) {
				return /* @__PURE__ */ A.createElement(w, P({ "data-baseweb": "form-control-container" }, y, h(c)), A.Children.map(g, function(t, n) {
					if (t) {
						var r = t.key || String(n);
						return /* @__PURE__ */ A.cloneElement(t, {
							key: r,
							"aria-errormessage": f ? e : null,
							"aria-describedby": u || p ? e : null,
							disabled: v.disabled || d,
							error: typeof v.error < "u" ? v.error : y.$error,
							positive: typeof v.positive < "u" ? v.positive : y.$positive
						});
					}
				}), (!!u || !!f || p) && /* @__PURE__ */ A.createElement(C, P({
					"data-baseweb": "form-control-caption",
					id: e
				}, y, h(s)), T));
			}));
		}
	}]), r;
}(A.Component);
ft(mt, "defaultProps", {
	overrides: {},
	label: null,
	caption: null,
	disabled: !1,
	counter: !1
});
function ht(e, t) {
	var n = Object.keys(e);
	if (Object.getOwnPropertySymbols) {
		var r = Object.getOwnPropertySymbols(e);
		t && (r = r.filter(function(t) {
			return Object.getOwnPropertyDescriptor(e, t).enumerable;
		})), n.push.apply(n, r);
	}
	return n;
}
function gt(e) {
	for (var t = 1; t < arguments.length; t++) {
		var n = arguments[t] == null ? {} : arguments[t];
		t % 2 ? ht(Object(n), !0).forEach(function(t) {
			_t(e, t, n[t]);
		}) : Object.getOwnPropertyDescriptors ? Object.defineProperties(e, Object.getOwnPropertyDescriptors(n)) : ht(Object(n)).forEach(function(t) {
			Object.defineProperty(e, t, Object.getOwnPropertyDescriptor(n, t));
		});
	}
	return e;
}
function _t(e, t, n) {
	return t in e ? Object.defineProperty(e, t, {
		value: n,
		enumerable: !0,
		configurable: !0,
		writable: !0
	}) : e[t] = n, e;
}
var vt = function(e) {
	return Ke.map(function(t) {
		return {
			id: t.toString(),
			label: e(t)
		};
	});
}, yt = function(e, t) {
	return e.map(function(e) {
		return t.includes(Number(e.id)) ? e : gt(gt({}, e), {}, { disabled: !0 });
	});
}, bt = function(e) {
	var t = e.filterMonthsList, n = e.formatMonthLabel, r = vt(n);
	return t && (r = yt(r, t)), r;
};
function xt(e) {
	var t = e.$range, n = t === void 0 ? !1 : t, r = e.$disabled, i = r === void 0 ? !1 : r, a = e.$isHighlighted, o = a === void 0 ? !1 : a, s = e.$isHovered, c = s === void 0 ? !1 : s, l = e.$selected, u = l === void 0 ? !1 : l, d = e.$hasRangeSelected, f = d === void 0 ? !1 : d, p = e.$startDate, m = p === void 0 ? !1 : p, h = e.$endDate, g = h === void 0 ? !1 : h, _ = e.$pseudoSelected, v = _ === void 0 ? !1 : _, y = e.$hasRangeHighlighted, b = y === void 0 ? !1 : y, x = e.$pseudoHighlighted, S = x === void 0 ? !1 : x, C = e.$hasRangeOnRight, w = C === void 0 ? !1 : C, T = e.$startOfMonth, E = T === void 0 ? !1 : T, D = e.$endOfMonth, O = D === void 0 ? !1 : D, k = e.$outsideMonth, A = k === void 0 ? !1 : k;
	return "".concat(+n, +i, +(o || c), +u, +f, +m, +g, +v, +b, +S, +(b && !S && w), +(b && !S && !w), +E, +O, +A);
}
function St(e, t) {
	return Dt(e) || Et(e, t) || wt(e, t) || Ct();
}
function Ct() {
	throw TypeError("Invalid attempt to destructure non-iterable instance.\nIn order to be iterable, non-array objects must have a [Symbol.iterator]() method.");
}
function wt(e, t) {
	if (e) {
		if (typeof e == "string") return Tt(e, t);
		var n = Object.prototype.toString.call(e).slice(8, -1);
		if (n === "Object" && e.constructor && (n = e.constructor.name), n === "Map" || n === "Set") return Array.from(e);
		if (n === "Arguments" || /^(?:Ui|I)nt(?:8|16|32)(?:Clamped)?Array$/.test(n)) return Tt(e, t);
	}
}
function Tt(e, t) {
	(t == null || t > e.length) && (t = e.length);
	for (var n = 0, r = Array(t); n < t; n++) r[n] = e[n];
	return r;
}
function Et(e, t) {
	var n = e == null ? null : typeof Symbol < "u" && e[Symbol.iterator] || e["@@iterator"];
	if (n != null) {
		var r = [], i = !0, a = !1, o, s;
		try {
			for (n = n.call(e); !(i = (o = n.next()).done) && (r.push(o.value), !(t && r.length === t)); i = !0);
		} catch (e) {
			a = !0, s = e;
		} finally {
			try {
				!i && n.return != null && n.return();
			} finally {
				if (a) throw s;
			}
		}
		return r;
	}
}
function Dt(e) {
	if (Array.isArray(e)) return e;
}
function Ot(e, t) {
	var n = Object.keys(e);
	if (Object.getOwnPropertySymbols) {
		var r = Object.getOwnPropertySymbols(e);
		t && (r = r.filter(function(t) {
			return Object.getOwnPropertyDescriptor(e, t).enumerable;
		})), n.push.apply(n, r);
	}
	return n;
}
function F(e) {
	for (var t = 1; t < arguments.length; t++) {
		var n = arguments[t] == null ? {} : arguments[t];
		t % 2 ? Ot(Object(n), !0).forEach(function(t) {
			I(e, t, n[t]);
		}) : Object.getOwnPropertyDescriptors ? Object.defineProperties(e, Object.getOwnPropertyDescriptors(n)) : Ot(Object(n)).forEach(function(t) {
			Object.defineProperty(e, t, Object.getOwnPropertyDescriptor(n, t));
		});
	}
	return e;
}
function I(e, t, n) {
	return t in e ? Object.defineProperty(e, t, {
		value: n,
		enumerable: !0,
		configurable: !0,
		writable: !0
	}) : e[t] = n, e;
}
var kt = e("div", function(e) {
	var t = e.$separateRangeInputs;
	return F({ width: "100%" }, t ? {
		display: "flex",
		justifyContent: "center"
	} : {});
});
kt.displayName = "StyledInputWrapper", kt.displayName = "StyledInputWrapper";
var At = e("div", function(e) {
	var t = e.$theme;
	return F(F({}, t.typography.LabelMedium), {}, { marginBottom: t.sizing.scale300 });
});
At.displayName = "StyledInputLabel", At.displayName = "StyledInputLabel";
var jt = e("div", function(e) {
	return {
		width: "100%",
		marginRight: e.$theme.sizing.scale300
	};
});
jt.displayName = "StyledStartDate", jt.displayName = "StyledStartDate";
var Mt = e("div", function(e) {
	return e.$theme, { width: "100%" };
});
Mt.displayName = "StyledEndDate", Mt.displayName = "StyledEndDate";
var Nt = e("div", function(e) {
	var t = e.$theme, n = t.typography, r = t.colors, i = t.borders;
	return F(F({}, n.font200), {}, {
		color: r.calendarForeground,
		backgroundColor: r.calendarBackground,
		textAlign: "center",
		borderTopLeftRadius: i.surfaceBorderRadius,
		borderTopRightRadius: i.surfaceBorderRadius,
		borderBottomRightRadius: i.surfaceBorderRadius,
		borderBottomLeftRadius: i.surfaceBorderRadius,
		display: "inline-block"
	});
});
Nt.displayName = "StyledRoot", Nt.displayName = "StyledRoot";
var Pt = e("div", function(e) {
	return {
		display: "flex",
		flexDirection: e.$orientation === We.vertical ? "column" : "row"
	};
});
Pt.displayName = "StyledMonthContainer", Pt.displayName = "StyledMonthContainer";
var Ft = e("div", function(e) {
	var t = e.$theme.sizing, n = e.$density;
	return {
		paddingTop: t.scale300,
		paddingBottom: n === j.high ? t.scale400 : t.scale300,
		paddingLeft: t.scale500,
		paddingRight: t.scale500
	};
});
Ft.displayName = "StyledCalendarContainer", Ft.displayName = "StyledCalendarContainer";
var It = e("div", function(e) {
	var t = e.$theme, n = t.direction === "rtl" ? "right" : "left";
	return {
		marginBottom: t.sizing.scale600,
		paddingLeft: t.sizing.scale600,
		paddingRight: t.sizing.scale600,
		textAlign: n
	};
});
It.displayName = "StyledSelectorContainer", It.displayName = "StyledSelectorContainer";
var Lt = e("div", function(e) {
	var t = e.$theme, n = t.typography, r = t.borders, i = t.colors, a = t.sizing, o = e.$density;
	return F(F({}, o === j.high ? n.LabelMedium : n.LabelLarge), {}, {
		color: i.calendarHeaderForeground,
		display: "flex",
		justifyContent: "space-between",
		alignItems: "center",
		paddingTop: a.scale600,
		paddingBottom: a.scale300,
		paddingLeft: a.scale600,
		paddingRight: a.scale600,
		backgroundColor: i.calendarHeaderBackground,
		borderTopLeftRadius: r.surfaceBorderRadius,
		borderTopRightRadius: r.surfaceBorderRadius,
		borderBottomRightRadius: 0,
		borderBottomLeftRadius: 0,
		minHeight: o === j.high ? `calc(${a.scale800} + ${a.scale0})` : a.scale950
	});
});
Lt.displayName = "StyledCalendarHeader", Lt.displayName = "StyledCalendarHeader";
var Rt = e("div", function(e) {
	return {
		color: e.$theme.colors.calendarHeaderForeground,
		backgroundColor: e.$theme.colors.calendarHeaderBackground,
		whiteSpace: "nowrap"
	};
});
Rt.displayName = "StyledMonthHeader", Rt.displayName = "StyledMonthHeader";
var zt = e("button", function(e) {
	var t = e.$theme, n = t.typography, r = t.colors, i = e.$isFocusVisible, a = e.$density;
	return F(F({}, a === j.high ? n.LabelMedium : n.LabelLarge), {}, {
		alignItems: "center",
		backgroundColor: "transparent",
		borderLeftWidth: 0,
		borderRightWidth: 0,
		borderTopWidth: 0,
		borderBottomWidth: 0,
		color: r.calendarHeaderForeground,
		cursor: "pointer",
		display: "flex",
		outline: "none",
		":focus": { boxShadow: i ? `0 0 0 3px ${r.accent}` : "none" }
	});
});
zt.displayName = "StyledMonthYearSelectButton", zt.displayName = "StyledMonthYearSelectButton";
var Bt = e("span", function(e) {
	return I({
		alignItems: "center",
		display: "flex"
	}, e.$theme.direction === "rtl" ? "marginRight" : "marginLeft", e.$theme.sizing.scale500);
});
Bt.displayName = "StyledMonthYearSelectIconContainer", Bt.displayName = "StyledMonthYearSelectIconContainer";
function Vt(e) {
	var t = e.$theme, n = e.$disabled, r = e.$isFocusVisible;
	return {
		boxSizing: "border-box",
		display: "flex",
		color: n ? t.colors.calendarHeaderForegroundDisabled : t.colors.calendarHeaderForeground,
		cursor: n ? "default" : "pointer",
		backgroundColor: "transparent",
		borderLeftWidth: 0,
		borderRightWidth: 0,
		borderTopWidth: 0,
		borderBottomWidth: 0,
		paddingTop: "0",
		paddingBottom: "0",
		paddingLeft: "0",
		paddingRight: "0",
		marginBottom: 0,
		marginTop: 0,
		outline: "none",
		":focus": n ? {} : { boxShadow: r ? `0 0 0 3px ${t.colors.accent}` : "none" }
	};
}
var Ht = e("button", Vt);
Ht.displayName = "StyledPrevButton", Ht.displayName = "StyledPrevButton";
var Ut = e("button", Vt);
Ut.displayName = "StyledNextButton", Ut.displayName = "StyledNextButton";
var Wt = e("div", function(e) {
	return { display: "inline-block" };
});
Wt.displayName = "StyledMonth", Wt.displayName = "StyledMonth";
var Gt = e("div", function(e) {
	return {
		whiteSpace: "nowrap",
		display: "flex",
		marginBottom: e.$theme.sizing.scale0
	};
});
Gt.displayName = "StyledWeek", Gt.displayName = "StyledWeek";
function L(e, t) {
	var n, r = e.substr(0, 12) + "1" + e.substr(13), i = e.substr(0, 13) + "1" + e.substr(14);
	return n = {}, I(n, e, t), I(n, r, t), I(n, i, t), n;
}
function Kt(e, t) {
	var n = t.colors, r = {
		":before": { content: null },
		":after": { content: null }
	}, i = {
		color: n.calendarForegroundDisabled,
		":before": { content: null },
		":after": { content: null }
	}, a = {
		color: n.calendarForegroundDisabled,
		":before": {
			borderTopStyle: "none",
			borderBottomStyle: "none",
			borderLeftStyle: "none",
			borderRightStyle: "none",
			backgroundColor: "transparent"
		},
		":after": {
			borderTopLeftRadius: "0%",
			borderTopRightRadius: "0%",
			borderBottomLeftRadius: "0%",
			borderBottomRightRadius: "0%",
			borderTopColor: "transparent",
			borderBottomColor: "transparent",
			borderRightColor: "transparent",
			borderLeftColor: "transparent"
		}
	}, o = { ":before": { content: null } };
	return e && e[1] === "1" && (r = i), Object.assign({}, L("001000000000000", { color: n.calendarDayForegroundPseudoSelected }), L("000100000000000", { color: n.calendarDayForegroundSelected }), L("001100000000000", { color: n.calendarDayForegroundSelectedHighlighted }), { "010000000000000": {
		color: n.calendarForegroundDisabled,
		":after": { content: null }
	} }, { "011000000000000": {
		color: n.calendarForegroundDisabled,
		":after": { content: null }
	} }, L("000000000000001", a), L("101000000000000", o), L("101010000000000", o), L("100100000000000", { color: n.calendarDayForegroundSelected }), L("101100000000000", {
		color: n.calendarDayForegroundSelectedHighlighted,
		":before": { content: null }
	}), L("100111100000000", {
		color: n.calendarDayForegroundSelected,
		":before": { content: null }
	}), L("101111100000000", {
		color: n.calendarDayForegroundSelectedHighlighted,
		":before": { content: null }
	}), L("100111000000000", { color: n.calendarDayForegroundSelected }), L("100110100000000", {
		color: n.calendarDayForegroundSelected,
		":before": {
			left: null,
			right: "50%"
		}
	}), L("100100001010000", { color: n.calendarDayForegroundSelected }), L("100100001001000", {
		color: n.calendarDayForegroundSelected,
		":before": {
			left: null,
			right: "50%"
		}
	}), L("101000001010000", { ":before": {
		left: null,
		right: "50%"
	} }), { "101000001001000": {} }, { "101000001001100": {} }, { "101000001001010": {} }, L("100010010000000", {
		color: n.calendarDayForegroundPseudoSelected,
		":before": {
			left: "0",
			width: "100%"
		},
		":after": { content: null }
	}), { "101000001100000": {
		color: n.calendarDayForegroundPseudoSelected,
		":before": {
			left: "0",
			width: "100%"
		},
		":after": { content: null }
	} }, L("100000001100000", {
		color: n.calendarDayForegroundPseudoSelected,
		":before": {
			left: "0",
			width: "100%"
		},
		":after": { content: null }
	}), L("101111000000000", { color: n.calendarDayForegroundSelectedHighlighted }), L("101110100000000", {
		color: n.calendarDayForegroundSelectedHighlighted,
		":before": {
			left: null,
			right: "50%"
		}
	}), L("101010010000000", {
		color: n.calendarDayForegroundPseudoSelectedHighlighted,
		":before": {
			left: "0",
			width: "100%"
		}
	}), L("100000000000001", a), L("100000001010001", a), L("100000001001001", a), L("100010000000001", a))[e] || r;
}
var qt = e("div", function(e) {
	var t = e.$disabled, n = e.$isFocusVisible, r = e.$isHighlighted, i = e.$peekNextMonth, a = e.$pseudoSelected, o = e.$range, s = e.$selected, c = e.$outsideMonth, l = e.$outsideMonthWithinRange, u = e.$hasDateLabel, d = e.$density, f = e.$hasLockedBehavior, p = e.$selectedInput, m = e.$value, h = e.$theme, g = h.colors, _ = h.typography, v = h.sizing, y = xt(e), b = u ? d === j.high ? "60px" : "70px" : d === j.high ? "40px" : "48px", x = St(Array.isArray(m) ? m : [m, null], 2), S = x[0], C = x[1], w = p === M.startDate ? C !== null && typeof C < "u" : S !== null && typeof S < "u", T = o && !(f && !w);
	return F(F(F({}, d === j.high ? _.ParagraphSmall : _.ParagraphMedium), {}, {
		boxSizing: "border-box",
		position: "relative",
		cursor: t || !i && c ? "default" : "pointer",
		color: g.calendarForeground,
		display: "inline-block",
		width: d === j.high ? "42px" : "50px",
		height: b,
		lineHeight: d === j.high ? v.scale700 : v.scale900,
		textAlign: "center",
		paddingTop: v.scale300,
		paddingBottom: v.scale300,
		paddingLeft: v.scale300,
		paddingRight: v.scale300,
		marginTop: 0,
		marginBottom: 0,
		marginLeft: 0,
		marginRight: 0,
		outline: "none",
		backgroundColor: "transparent",
		transform: "scale(1)"
	}, Kt(y, e.$theme)), {}, { ":after": F(F({
		zIndex: -1,
		content: "\"\"",
		boxSizing: "border-box",
		display: "inline-block",
		boxShadow: n && (!c || i) ? `0 0 0 3px ${g.accent}` : "none",
		backgroundColor: s ? g.calendarDayBackgroundSelectedHighlighted : a && r ? g.calendarDayBackgroundPseudoSelectedHighlighted : g.calendarBackground,
		height: u ? "100%" : d === j.high ? "42px" : "50px",
		width: "100%",
		position: "absolute",
		top: u ? 0 : "-1px",
		left: 0,
		paddingTop: v.scale200,
		paddingBottom: v.scale200,
		borderLeftWidth: "2px",
		borderRightWidth: "2px",
		borderTopWidth: "2px",
		borderBottomWidth: "2px",
		borderLeftStyle: "solid",
		borderRightStyle: "solid",
		borderTopStyle: "solid",
		borderBottomStyle: "solid",
		borderTopColor: g.borderSelected,
		borderBottomColor: g.borderSelected,
		borderRightColor: g.borderSelected,
		borderLeftColor: g.borderSelected,
		borderTopLeftRadius: u ? v.scale800 : "100%",
		borderTopRightRadius: u ? v.scale800 : "100%",
		borderBottomLeftRadius: u ? v.scale800 : "100%",
		borderBottomRightRadius: u ? v.scale800 : "100%"
	}, Kt(y, e.$theme)[":after"] || {}), l ? { content: null } : {}) }, T ? { ":before": F(F({
		zIndex: -1,
		content: "\"\"",
		boxSizing: "border-box",
		display: "inline-block",
		backgroundColor: g.mono300,
		position: "absolute",
		height: "100%",
		width: "50%",
		top: 0,
		left: "50%",
		borderTopWidth: "2px",
		borderBottomWidth: "2px",
		borderLeftWidth: "0",
		borderRightWidth: "0",
		borderTopStyle: "solid",
		borderBottomStyle: "solid",
		borderLeftStyle: "solid",
		borderRightStyle: "solid",
		borderTopColor: "transparent",
		borderBottomColor: "transparent",
		borderLeftColor: "transparent",
		borderRightColor: "transparent"
	}, Kt(y, e.$theme)[":before"] || {}), l ? {
		backgroundColor: g.mono300,
		left: "0",
		width: "100%",
		content: "\"\""
	} : {}) } : {});
});
qt.displayName = "StyledDay", qt.displayName = "StyledDay";
var Jt = e("div", function(e) {
	var t = e.$theme, n = t.typography, r = t.colors, i = e.$selected;
	return F(F({}, n.ParagraphXSmall), {}, { color: i ? r.contentInverseTertiary : r.contentTertiary });
});
Jt.displayName = "StyledDayLabel", Jt.displayName = "StyledDayLabel";
var Yt = e("div", function(e) {
	var t = e.$theme, n = t.typography, r = t.colors, i = t.sizing, a = e.$density;
	return F(F({}, n.LabelMedium), {}, {
		color: r.contentTertiary,
		boxSizing: "border-box",
		position: "relative",
		cursor: "default",
		display: "inline-block",
		width: a === j.high ? "42px" : "50px",
		height: a === j.high ? "40px" : "48px",
		textAlign: "center",
		lineHeight: i.scale900,
		paddingTop: i.scale300,
		paddingBottom: i.scale300,
		paddingLeft: i.scale200,
		paddingRight: i.scale200,
		marginTop: 0,
		marginBottom: 0,
		marginLeft: 0,
		marginRight: 0,
		backgroundColor: "transparent"
	});
});
Yt.displayName = "StyledWeekdayHeader", Yt.displayName = "StyledWeekdayHeader";
function Xt(e) {
	"@babel/helpers - typeof";
	return Xt = typeof Symbol == "function" && typeof Symbol.iterator == "symbol" ? function(e) {
		return typeof e;
	} : function(e) {
		return e && typeof Symbol == "function" && e.constructor === Symbol && e !== Symbol.prototype ? "symbol" : typeof e;
	}, Xt(e);
}
function R() {
	return R = Object.assign ? Object.assign.bind() : function(e) {
		for (var t = 1; t < arguments.length; t++) {
			var n = arguments[t];
			for (var r in n) Object.prototype.hasOwnProperty.call(n, r) && (e[r] = n[r]);
		}
		return e;
	}, R.apply(this, arguments);
}
function z(e, t) {
	return tn(e) || en(e, t) || Qt(e, t) || Zt();
}
function Zt() {
	throw TypeError("Invalid attempt to destructure non-iterable instance.\nIn order to be iterable, non-array objects must have a [Symbol.iterator]() method.");
}
function Qt(e, t) {
	if (e) {
		if (typeof e == "string") return $t(e, t);
		var n = Object.prototype.toString.call(e).slice(8, -1);
		if (n === "Object" && e.constructor && (n = e.constructor.name), n === "Map" || n === "Set") return Array.from(e);
		if (n === "Arguments" || /^(?:Ui|I)nt(?:8|16|32)(?:Clamped)?Array$/.test(n)) return $t(e, t);
	}
}
function $t(e, t) {
	(t == null || t > e.length) && (t = e.length);
	for (var n = 0, r = Array(t); n < t; n++) r[n] = e[n];
	return r;
}
function en(e, t) {
	var n = e == null ? null : typeof Symbol < "u" && e[Symbol.iterator] || e["@@iterator"];
	if (n != null) {
		var r = [], i = !0, a = !1, o, s;
		try {
			for (n = n.call(e); !(i = (o = n.next()).done) && (r.push(o.value), !(t && r.length === t)); i = !0);
		} catch (e) {
			a = !0, s = e;
		} finally {
			try {
				!i && n.return != null && n.return();
			} finally {
				if (a) throw s;
			}
		}
		return r;
	}
}
function tn(e) {
	if (Array.isArray(e)) return e;
}
function nn(e, t) {
	var n = Object.keys(e);
	if (Object.getOwnPropertySymbols) {
		var r = Object.getOwnPropertySymbols(e);
		t && (r = r.filter(function(t) {
			return Object.getOwnPropertyDescriptor(e, t).enumerable;
		})), n.push.apply(n, r);
	}
	return n;
}
function rn(e) {
	for (var t = 1; t < arguments.length; t++) {
		var n = arguments[t] == null ? {} : arguments[t];
		t % 2 ? nn(Object(n), !0).forEach(function(t) {
			V(e, t, n[t]);
		}) : Object.getOwnPropertyDescriptors ? Object.defineProperties(e, Object.getOwnPropertyDescriptors(n)) : nn(Object(n)).forEach(function(t) {
			Object.defineProperty(e, t, Object.getOwnPropertyDescriptor(n, t));
		});
	}
	return e;
}
function an(e, t) {
	if (!(e instanceof t)) throw TypeError("Cannot call a class as a function");
}
function on(e, t) {
	for (var n = 0; n < t.length; n++) {
		var r = t[n];
		r.enumerable = r.enumerable || !1, r.configurable = !0, "value" in r && (r.writable = !0), Object.defineProperty(e, r.key, r);
	}
}
function sn(e, t, n) {
	return t && on(e.prototype, t), Object.defineProperty(e, "prototype", { writable: !1 }), e;
}
function cn(e, t) {
	if (typeof t != "function" && t !== null) throw TypeError("Super expression must either be null or a function");
	e.prototype = Object.create(t && t.prototype, { constructor: {
		value: e,
		writable: !0,
		configurable: !0
	} }), Object.defineProperty(e, "prototype", { writable: !1 }), t && ln(e, t);
}
function ln(e, t) {
	return ln = Object.setPrototypeOf ? Object.setPrototypeOf.bind() : function(e, t) {
		return e.__proto__ = t, e;
	}, ln(e, t);
}
function un(e) {
	var t = fn();
	return function() {
		var n = pn(e), r;
		if (t) {
			var i = pn(this).constructor;
			r = Reflect.construct(n, arguments, i);
		} else r = n.apply(this, arguments);
		return dn(this, r);
	};
}
function dn(e, t) {
	if (t && (Xt(t) === "object" || typeof t == "function")) return t;
	if (t !== void 0) throw TypeError("Derived constructors may only return object or undefined");
	return B(e);
}
function B(e) {
	if (e === void 0) throw ReferenceError("this hasn't been initialised - super() hasn't been called");
	return e;
}
function fn() {
	if (typeof Reflect > "u" || !Reflect.construct || Reflect.construct.sham) return !1;
	if (typeof Proxy == "function") return !0;
	try {
		return Boolean.prototype.valueOf.call(Reflect.construct(Boolean, [], function() {})), !0;
	} catch {
		return !1;
	}
}
function pn(e) {
	return pn = Object.setPrototypeOf ? Object.getPrototypeOf.bind() : function(e) {
		return e.__proto__ || Object.getPrototypeOf(e);
	}, pn(e);
}
function V(e, t, n) {
	return t in e ? Object.defineProperty(e, t, {
		value: n,
		enumerable: !0,
		configurable: !0,
		writable: !0
	}) : e[t] = n, e;
}
var mn = function(e) {
	return e.$theme, { cursor: "pointer" };
}, hn = 2e3, gn = 2030, _n = 0, vn = 11, yn = {
	NEXT: "next",
	PREVIOUS: "previous"
};
function bn(e) {
	return e.split("-").map(Number);
}
var xn = /* @__PURE__ */ function(e) {
	cn(i, e);
	var t = un(i);
	function i(e) {
		var n;
		return an(this, i), n = t.call(this, e), V(B(n), "dateHelpers", void 0), V(B(n), "monthItems", void 0), V(B(n), "yearItems", void 0), V(B(n), "state", {
			isMonthDropdownOpen: !1,
			isYearDropdownOpen: !1,
			isFocusVisible: !1
		}), V(B(n), "getDateProp", function() {
			return n.props.date || n.dateHelpers.date();
		}), V(B(n), "getYearItems", function() {
			var e = n.getDateProp(), t = n.props.maxDate, r = n.props.minDate, i = t ? n.dateHelpers.getYear(t) : gn, a = r ? n.dateHelpers.getYear(r) : hn, o = n.dateHelpers.getMonth(e);
			n.yearItems = Array.from({ length: i - a + 1 }, function(e, t) {
				return a + t;
			}).map(function(e) {
				return {
					id: e.toString(),
					label: e.toString()
				};
			});
			var s = t ? n.dateHelpers.getMonth(t) : vn, c = r ? n.dateHelpers.getMonth(r) : _n, l = Array.from({ length: s + 1 }, function(e, t) {
				return t;
			}), u = Array.from({ length: 12 - c }, function(e, t) {
				return t + c;
			});
			if (o > l[l.length - 1]) {
				var d = n.yearItems.length - 1;
				n.yearItems[d] = rn(rn({}, n.yearItems[d]), {}, { disabled: !0 });
			}
			o < u[0] && (n.yearItems[0] = rn(rn({}, n.yearItems[0]), {}, { disabled: !0 }));
		}), V(B(n), "getMonthItems", function() {
			var e = n.getDateProp(), t = n.dateHelpers.getYear(e), r = n.props.maxDate, i = n.props.minDate, a = r ? n.dateHelpers.getYear(r) : gn, o = i ? n.dateHelpers.getYear(i) : hn, s = r ? n.dateHelpers.getMonth(r) : vn, c = Array.from({ length: s + 1 }, function(e, t) {
				return t;
			}), l = i ? n.dateHelpers.getMonth(i) : _n, u = Array.from({ length: 12 - l }, function(e, t) {
				return t + l;
			}), d = c.filter(function(e) {
				return u.includes(e);
			});
			n.monthItems = bt({
				filterMonthsList: t === a && t === o ? d : t === a ? c : t === o ? u : null,
				formatMonthLabel: function(e) {
					return n.dateHelpers.getMonthInLocale(e, n.props.locale);
				}
			});
		}), V(B(n), "increaseMonth", function() {
			n.props.onMonthChange && n.props.onMonthChange({ date: n.dateHelpers.addMonths(n.getDateProp(), 1 - n.props.order) });
		}), V(B(n), "decreaseMonth", function() {
			n.props.onMonthChange && n.props.onMonthChange({ date: n.dateHelpers.subMonths(n.getDateProp(), 1) });
		}), V(B(n), "isMultiMonthHorizontal", function() {
			var e = n.props, t = e.monthsShown, r = e.orientation;
			return t ? r === We.horizontal && t > 1 : !1;
		}), V(B(n), "isHiddenPaginationButton", function(e) {
			var t = n.props, r = t.monthsShown, i = t.order;
			return r && n.isMultiMonthHorizontal() ? e === yn.NEXT ? i !== r - 1 : i !== 0 : !1;
		}), V(B(n), "handleFocus", function(e) {
			v(e) && n.setState({ isFocusVisible: !0 });
		}), V(B(n), "handleBlur", function(e) {
			n.state.isFocusVisible !== !1 && n.setState({ isFocusVisible: !1 });
		}), V(B(n), "renderPreviousMonthButton", function(e) {
			var t = e.locale, r = e.theme, i = n.getDateProp(), a = n.props, o = a.overrides, s = o === void 0 ? {} : o, c = a.density, l = n.dateHelpers.monthDisabledBefore(i, n.props), u = !1;
			l && (u = !0);
			var d = n.dateHelpers.subMonths(i, 1), f = n.props.minDate ? n.dateHelpers.getYear(n.props.minDate) : hn;
			n.dateHelpers.getYear(d) < f && (u = !0);
			var p = n.isHiddenPaginationButton(yn.PREVIOUS);
			p && (u = !0);
			var m = z(x(s.PrevButton, Ht), 2), h = m[0], g = m[1], _ = z(x(s.PrevButtonIcon, r.direction === "rtl" ? we : fe), 2), v = _[0], y = _[1], b = n.decreaseMonth;
			return l && (b = null), /* @__PURE__ */ A.createElement(h, R({
				"aria-label": t.datepicker.previousMonth,
				tabIndex: 0,
				onClick: b,
				disabled: u,
				$isFocusVisible: n.state.isFocusVisible,
				type: "button",
				$disabled: u,
				$order: n.props.order
			}, g), p ? null : /* @__PURE__ */ A.createElement(v, R({
				size: c === j.high ? 24 : 36,
				overrides: { Svg: { style: mn } }
			}, y)));
		}), V(B(n), "renderNextMonthButton", function(e) {
			var t = e.locale, r = e.theme, i = n.getDateProp(), a = n.props, o = a.overrides, s = o === void 0 ? {} : o, c = a.density, l = n.dateHelpers.monthDisabledAfter(i, n.props), u = !1;
			l && (u = !0);
			var d = n.dateHelpers.addMonths(i, 1), f = n.props.maxDate ? n.dateHelpers.getYear(n.props.maxDate) : gn;
			n.dateHelpers.getYear(d) > f && (u = !0);
			var p = n.isHiddenPaginationButton(yn.NEXT);
			p && (u = !0);
			var m = z(x(s.NextButton, Ut), 2), h = m[0], g = m[1], _ = z(x(s.NextButtonIcon, r.direction === "rtl" ? fe : we), 2), v = _[0], y = _[1], b = n.increaseMonth;
			return l && (b = null), /* @__PURE__ */ A.createElement(h, R({
				"aria-label": t.datepicker.nextMonth,
				tabIndex: 0,
				onClick: b,
				disabled: u,
				type: "button",
				$disabled: u,
				$isFocusVisible: n.state.isFocusVisible,
				$order: n.props.order
			}, g), p ? null : /* @__PURE__ */ A.createElement(v, R({
				size: c === j.high ? 24 : 36,
				overrides: { Svg: { style: mn } }
			}, y)));
		}), V(B(n), "canArrowsOpenDropdown", function(e) {
			return !n.state.isMonthDropdownOpen && !n.state.isYearDropdownOpen && (e.key === "ArrowUp" || e.key === "ArrowDown");
		}), V(B(n), "renderMonthYearDropdown", function() {
			var e = n.getDateProp(), t = n.dateHelpers.getMonth(e), r = n.dateHelpers.getYear(e), i = n.props, a = i.locale, o = i.overrides, s = o === void 0 ? {} : o, c = i.density, l = z(x(s.MonthYearSelectButton, zt), 2), u = l[0], d = l[1], f = z(x(s.MonthYearSelectIconContainer, Bt), 2), m = f[0], h = f[1], _ = z(x(s.MonthYearSelectPopover, p), 2), v = _[0], y = _[1], b = z(x(s.MonthYearSelectStatefulMenu, C), 2), S = b[0], T = b[1];
			T.overrides = g({ List: { style: {
				height: "auto",
				maxHeight: "257px"
			} } }, T && T.overrides);
			var E = n.monthItems.findIndex(function(t) {
				return t.id === n.dateHelpers.getMonth(e).toString();
			}), D = n.yearItems.findIndex(function(t) {
				return t.id === n.dateHelpers.getYear(e).toString();
			}), O = `${n.dateHelpers.getMonthInLocale(n.dateHelpers.getMonth(e), a)}`, k = `${n.dateHelpers.getYear(e)}`;
			return n.isMultiMonthHorizontal() ? /* @__PURE__ */ A.createElement("div", null, `${O} ${k}`) : /* @__PURE__ */ A.createElement(A.Fragment, null, /* @__PURE__ */ A.createElement(v, R({
				placement: "bottom",
				autoFocus: !0,
				focusLock: !0,
				isOpen: n.state.isMonthDropdownOpen,
				onClick: function() {
					n.setState(function(e) {
						return { isMonthDropdownOpen: !e.isMonthDropdownOpen };
					});
				},
				onClickOutside: function() {
					return n.setState({ isMonthDropdownOpen: !1 });
				},
				onEsc: function() {
					return n.setState({ isMonthDropdownOpen: !1 });
				},
				content: function() {
					return /* @__PURE__ */ A.createElement(S, R({
						initialState: {
							highlightedIndex: E,
							isFocused: !0
						},
						items: n.monthItems,
						onItemSelect: function(t) {
							var i = t.item;
							t.event.preventDefault();
							var a = bn(i.id), o = n.dateHelpers.set(e, {
								year: r,
								month: a
							});
							n.props.onMonthChange && n.props.onMonthChange({ date: o }), n.setState({ isMonthDropdownOpen: !1 });
						}
					}, T));
				}
			}, y), /* @__PURE__ */ A.createElement(u, R({
				"aria-live": "polite",
				type: "button",
				$isFocusVisible: n.state.isFocusVisible,
				$density: c,
				onKeyUp: function(e) {
					n.canArrowsOpenDropdown(e) && n.setState({ isMonthDropdownOpen: !0 });
				},
				onKeyDown: function(e) {
					n.canArrowsOpenDropdown(e) && e.preventDefault(), e.key === "Tab" && n.setState({ isMonthDropdownOpen: !1 });
				}
			}, d), O, /* @__PURE__ */ A.createElement(m, h, /* @__PURE__ */ A.createElement(w, {
				title: "",
				overrides: { Svg: { props: { role: "presentation" } } },
				size: c === j.high ? 16 : 24
			})))), /* @__PURE__ */ A.createElement(v, R({
				placement: "bottom",
				focusLock: !0,
				isOpen: n.state.isYearDropdownOpen,
				onClick: function() {
					n.setState(function(e) {
						return { isYearDropdownOpen: !e.isYearDropdownOpen };
					});
				},
				onClickOutside: function() {
					return n.setState({ isYearDropdownOpen: !1 });
				},
				onEsc: function() {
					return n.setState({ isYearDropdownOpen: !1 });
				},
				content: function() {
					return /* @__PURE__ */ A.createElement(S, R({
						initialState: {
							highlightedIndex: D,
							isFocused: !0
						},
						items: n.yearItems,
						onItemSelect: function(r) {
							var i = r.item;
							r.event.preventDefault();
							var a = bn(i.id), o = n.dateHelpers.set(e, {
								year: a,
								month: t
							});
							n.props.onYearChange && n.props.onYearChange({ date: o }), n.setState({ isYearDropdownOpen: !1 });
						}
					}, T));
				}
			}, y), /* @__PURE__ */ A.createElement(u, R({
				"aria-live": "polite",
				type: "button",
				$isFocusVisible: n.state.isFocusVisible,
				$density: c,
				onKeyUp: function(e) {
					n.canArrowsOpenDropdown(e) && n.setState({ isYearDropdownOpen: !0 });
				},
				onKeyDown: function(e) {
					n.canArrowsOpenDropdown(e) && e.preventDefault(), e.key === "Tab" && n.setState({ isYearDropdownOpen: !1 });
				}
			}, d), k, /* @__PURE__ */ A.createElement(m, h, /* @__PURE__ */ A.createElement(w, {
				title: "",
				overrides: { Svg: { props: { role: "presentation" } } },
				size: c === j.high ? 16 : 24
			})))));
		}), n.dateHelpers = new O(e.adapter), n.monthItems = [], n.yearItems = [], n;
	}
	return sn(i, [
		{
			key: "componentDidMount",
			value: function() {
				this.getYearItems(), this.getMonthItems();
			}
		},
		{
			key: "componentDidUpdate",
			value: function(e) {
				var t = this.dateHelpers.getMonth(this.props.date) !== this.dateHelpers.getMonth(e.date), n = this.dateHelpers.getYear(this.props.date) !== this.dateHelpers.getYear(e.date);
				t && this.getYearItems(), n && this.getMonthItems();
			}
		},
		{
			key: "render",
			value: function() {
				var e = this, t = this.props, i = t.overrides, a = i === void 0 ? {} : i, o = t.density, s = z(x(a.CalendarHeader, Lt), 2), c = s[0], u = s[1], f = z(x(a.MonthHeader, Rt), 2), p = f[0], m = f[1], h = z(x(a.WeekdayHeader, Yt), 2), g = h[0], _ = h[1], v = this.dateHelpers.getStartOfWeek(this.getDateProp(), this.props.locale);
				return /* @__PURE__ */ A.createElement(n.Consumer, null, function(t) {
					return /* @__PURE__ */ A.createElement(r.Consumer, null, function(n) {
						return /* @__PURE__ */ A.createElement(A.Fragment, null, /* @__PURE__ */ A.createElement(c, R({}, u, {
							$density: e.props.density,
							onFocus: d(u, e.handleFocus),
							onBlur: l(u, e.handleBlur)
						}), e.renderPreviousMonthButton({
							locale: n,
							theme: t
						}), e.renderMonthYearDropdown(), e.renderNextMonthButton({
							locale: n,
							theme: t
						})), /* @__PURE__ */ A.createElement(p, R({ role: "presentation" }, m), Ge.map(function(t) {
							var n = e.dateHelpers.addDays(v, t);
							return /* @__PURE__ */ A.createElement(g, R({
								key: t,
								alt: e.dateHelpers.getWeekdayInLocale(n, e.props.locale)
							}, _, { $density: o }), e.dateHelpers.getWeekdayMinInLocale(n, e.props.locale));
						})));
					});
				});
			}
		}
	]), i;
}(A.Component);
V(xn, "defaultProps", {
	adapter: D,
	locale: null,
	maxDate: null,
	minDate: null,
	onYearChange: function() {},
	overrides: {}
});
function Sn(e) {
	"@babel/helpers - typeof";
	return Sn = typeof Symbol == "function" && typeof Symbol.iterator == "symbol" ? function(e) {
		return typeof e;
	} : function(e) {
		return e && typeof Symbol == "function" && e.constructor === Symbol && e !== Symbol.prototype ? "symbol" : typeof e;
	}, Sn(e);
}
function H() {
	return H = Object.assign ? Object.assign.bind() : function(e) {
		for (var t = 1; t < arguments.length; t++) {
			var n = arguments[t];
			for (var r in n) Object.prototype.hasOwnProperty.call(n, r) && (e[r] = n[r]);
		}
		return e;
	}, H.apply(this, arguments);
}
function Cn(e, t) {
	return On(e) || Dn(e, t) || Tn(e, t) || wn();
}
function wn() {
	throw TypeError("Invalid attempt to destructure non-iterable instance.\nIn order to be iterable, non-array objects must have a [Symbol.iterator]() method.");
}
function Tn(e, t) {
	if (e) {
		if (typeof e == "string") return En(e, t);
		var n = Object.prototype.toString.call(e).slice(8, -1);
		if (n === "Object" && e.constructor && (n = e.constructor.name), n === "Map" || n === "Set") return Array.from(e);
		if (n === "Arguments" || /^(?:Ui|I)nt(?:8|16|32)(?:Clamped)?Array$/.test(n)) return En(e, t);
	}
}
function En(e, t) {
	(t == null || t > e.length) && (t = e.length);
	for (var n = 0, r = Array(t); n < t; n++) r[n] = e[n];
	return r;
}
function Dn(e, t) {
	var n = e == null ? null : typeof Symbol < "u" && e[Symbol.iterator] || e["@@iterator"];
	if (n != null) {
		var r = [], i = !0, a = !1, o, s;
		try {
			for (n = n.call(e); !(i = (o = n.next()).done) && (r.push(o.value), !(t && r.length === t)); i = !0);
		} catch (e) {
			a = !0, s = e;
		} finally {
			try {
				!i && n.return != null && n.return();
			} finally {
				if (a) throw s;
			}
		}
		return r;
	}
}
function On(e) {
	if (Array.isArray(e)) return e;
}
function kn(e, t) {
	if (!(e instanceof t)) throw TypeError("Cannot call a class as a function");
}
function An(e, t) {
	for (var n = 0; n < t.length; n++) {
		var r = t[n];
		r.enumerable = r.enumerable || !1, r.configurable = !0, "value" in r && (r.writable = !0), Object.defineProperty(e, r.key, r);
	}
}
function jn(e, t, n) {
	return t && An(e.prototype, t), Object.defineProperty(e, "prototype", { writable: !1 }), e;
}
function Mn(e, t) {
	if (typeof t != "function" && t !== null) throw TypeError("Super expression must either be null or a function");
	e.prototype = Object.create(t && t.prototype, { constructor: {
		value: e,
		writable: !0,
		configurable: !0
	} }), Object.defineProperty(e, "prototype", { writable: !1 }), t && Nn(e, t);
}
function Nn(e, t) {
	return Nn = Object.setPrototypeOf ? Object.setPrototypeOf.bind() : function(e, t) {
		return e.__proto__ = t, e;
	}, Nn(e, t);
}
function Pn(e) {
	var t = In();
	return function() {
		var n = Ln(e), r;
		if (t) {
			var i = Ln(this).constructor;
			r = Reflect.construct(n, arguments, i);
		} else r = n.apply(this, arguments);
		return Fn(this, r);
	};
}
function Fn(e, t) {
	if (t && (Sn(t) === "object" || typeof t == "function")) return t;
	if (t !== void 0) throw TypeError("Derived constructors may only return object or undefined");
	return U(e);
}
function U(e) {
	if (e === void 0) throw ReferenceError("this hasn't been initialised - super() hasn't been called");
	return e;
}
function In() {
	if (typeof Reflect > "u" || !Reflect.construct || Reflect.construct.sham) return !1;
	if (typeof Proxy == "function") return !0;
	try {
		return Boolean.prototype.valueOf.call(Reflect.construct(Boolean, [], function() {})), !0;
	} catch {
		return !1;
	}
}
function Ln(e) {
	return Ln = Object.setPrototypeOf ? Object.getPrototypeOf.bind() : function(e) {
		return e.__proto__ || Object.getPrototypeOf(e);
	}, Ln(e);
}
function W(e, t, n) {
	return t in e ? Object.defineProperty(e, t, {
		value: n,
		enumerable: !0,
		configurable: !0,
		writable: !0
	}) : e[t] = n, e;
}
var Rn = /* @__PURE__ */ function(e) {
	Mn(n, e);
	var t = Pn(n);
	function n(e) {
		var r;
		return kn(this, n), r = t.call(this, e), W(U(r), "dayElm", void 0), W(U(r), "state", {
			isHovered: !1,
			isFocusVisible: !1
		}), W(U(r), "dateHelpers", void 0), W(U(r), "getDateProp", function() {
			return r.props.date === void 0 ? r.dateHelpers.date() : r.props.date;
		}), W(U(r), "getMonthProp", function() {
			return r.props.month === void 0 || r.props.month === null ? r.dateHelpers.getMonth(r.getDateProp()) : r.props.month;
		}), W(U(r), "onSelect", function(e) {
			var t = r.props, n = t.range, i = t.value, a;
			if (Array.isArray(i) && n && r.props.hasLockedBehavior) {
				var o = r.props.value, s = null, c = null;
				r.props.selectedInput === M.startDate ? (s = e, c = Array.isArray(o) && o[1] ? o[1] : null) : r.props.selectedInput === M.endDate && (s = Array.isArray(o) && o[0] ? o[0] : null, c = e), a = [s], c && a.push(c);
			} else if (Array.isArray(i) && n && !r.props.hasLockedBehavior) {
				var l = Cn(i, 2), u = l[0], d = l[1];
				a = !u && !d || u && d ? [e, null] : !u && d && r.dateHelpers.isAfter(d, e) ? [e, d] : !u && d && r.dateHelpers.isAfter(e, d) ? [d, e] : u && !d && r.dateHelpers.isAfter(e, u) ? [u, e] : [e, u];
			} else a = e;
			r.props.onSelect({ date: a });
		}), W(U(r), "onKeyDown", function(e) {
			var t = r.getDateProp(), n = r.props, i = n.highlighted, a = n.disabled;
			e.key === "Enter" && i && !a && (e.preventDefault(), r.onSelect(t));
		}), W(U(r), "onClick", function(e) {
			var t = r.getDateProp();
			r.props.disabled || (r.props.onClick({
				event: e,
				date: t
			}), r.onSelect(t));
		}), W(U(r), "onFocus", function(e) {
			v(e) && r.setState({ isFocusVisible: !0 }), r.props.onFocus({
				event: e,
				date: r.getDateProp()
			});
		}), W(U(r), "onBlur", function(e) {
			r.state.isFocusVisible !== !1 && r.setState({ isFocusVisible: !1 }), r.props.onBlur({
				event: e,
				date: r.getDateProp()
			});
		}), W(U(r), "onMouseOver", function(e) {
			r.setState({ isHovered: !0 }), r.props.onMouseOver({
				event: e,
				date: r.getDateProp()
			});
		}), W(U(r), "onMouseLeave", function(e) {
			r.setState({ isHovered: !1 }), r.props.onMouseLeave({
				event: e,
				date: r.getDateProp()
			});
		}), W(U(r), "isOutsideMonth", function() {
			var e = r.getMonthProp();
			return e !== void 0 && e !== r.dateHelpers.getMonth(r.getDateProp());
		}), W(U(r), "getOrderedDates", function() {
			var e = r.props, t = e.highlightedDate, n = e.value;
			if (!n || !Array.isArray(n) || !n[0] || !n[1] && !t) return [];
			var i = n[0], a = n.length > 1 && n[1] ? n[1] : t;
			if (!i || !a) return [];
			var o = r.clampToDayStart(i), s = r.clampToDayStart(a);
			return r.dateHelpers.isAfter(o, s) ? [s, o] : [o, s];
		}), W(U(r), "isOutsideOfMonthButWithinRange", function() {
			var e = r.clampToDayStart(r.getDateProp()), t = r.getOrderedDates();
			if (t.length < 2 || r.dateHelpers.isSameDay(t[0], t[1])) return !1;
			if (r.dateHelpers.getDate(e) > 15) {
				var n = r.clampToDayStart(r.dateHelpers.addDays(r.dateHelpers.getEndOfMonth(e), 1));
				return r.dateHelpers.isOnOrBeforeDay(t[0], r.dateHelpers.getEndOfMonth(e)) && r.dateHelpers.isOnOrAfterDay(t[1], n);
			} else {
				var i = r.clampToDayStart(r.dateHelpers.subDays(r.dateHelpers.getStartOfMonth(e), 1));
				return r.dateHelpers.isOnOrAfterDay(t[1], r.dateHelpers.getStartOfMonth(e)) && r.dateHelpers.isOnOrBeforeDay(t[0], i);
			}
		}), W(U(r), "clampToDayStart", function(e) {
			var t = r.dateHelpers, n = t.setSeconds, i = t.setMinutes, a = t.setHours;
			return n(i(a(e, 0), 0), 0);
		}), r.dateHelpers = new O(e.adapter), r;
	}
	return jn(n, [
		{
			key: "componentDidMount",
			value: function() {
				this.dayElm && this.props.focusedCalendar && (this.props.highlighted || !this.props.highlightedDate && this.isSelected()) && this.dayElm.focus();
			}
		},
		{
			key: "componentDidUpdate",
			value: function(e) {
				this.dayElm && this.props.focusedCalendar && (this.props.highlighted || !this.props.highlightedDate && this.isSelected()) && this.dayElm.focus();
			}
		},
		{
			key: "isSelected",
			value: function() {
				var e = this.getDateProp(), t = this.props.value;
				return Array.isArray(t) ? this.dateHelpers.isSameDay(e, t[0]) || this.dateHelpers.isSameDay(e, t[1]) : this.dateHelpers.isSameDay(e, t);
			}
		},
		{
			key: "isPseudoSelected",
			value: function() {
				var e = this.getDateProp(), t = this.props.value;
				if (Array.isArray(t)) {
					var n = Cn(t, 2), r = n[0], i = n[1];
					if (!r && !i) return !1;
					if (r && i) return this.dateHelpers.isDayInRange(this.clampToDayStart(e), this.clampToDayStart(r), this.clampToDayStart(i));
				}
			}
		},
		{
			key: "isPseudoHighlighted",
			value: function() {
				var e = this.getDateProp(), t = this.props, n = t.value, r = t.highlightedDate;
				if (Array.isArray(n)) {
					var i = Cn(n, 2), a = i[0], o = i[1];
					if (!a && !o) return !1;
					if (r && a && !o) return this.dateHelpers.isAfter(r, a) ? this.dateHelpers.isDayInRange(this.clampToDayStart(e), this.clampToDayStart(a), this.clampToDayStart(r)) : this.dateHelpers.isDayInRange(this.clampToDayStart(e), this.clampToDayStart(r), this.clampToDayStart(a));
					if (r && !a && o) return this.dateHelpers.isAfter(r, o) ? this.dateHelpers.isDayInRange(this.clampToDayStart(e), this.clampToDayStart(o), this.clampToDayStart(r)) : this.dateHelpers.isDayInRange(this.clampToDayStart(e), this.clampToDayStart(r), this.clampToDayStart(o));
				}
			}
		},
		{
			key: "getSharedProps",
			value: function() {
				var e = this.getDateProp(), t = this.props, n = t.value, r = t.highlightedDate, i = t.range, a = t.highlighted, o = t.peekNextMonth, s = a, c = this.isSelected(), l = !!(Array.isArray(n) && i && r && (n[0] && !n[1] && !this.dateHelpers.isSameDay(n[0], r) || !n[0] && n[1] && !this.dateHelpers.isSameDay(n[1], r))), u = !o && this.isOutsideMonth(), d = !!(Array.isArray(n) && i && u && !o && this.isOutsideOfMonthButWithinRange());
				return {
					$date: e,
					$density: this.props.density,
					$disabled: this.props.disabled,
					$endDate: Array.isArray(n) && !!(n[0] && n[1]) && i && c && this.dateHelpers.isSameDay(e, n[1]) || !1,
					$hasDateLabel: !!this.props.dateLabel,
					$hasRangeHighlighted: l,
					$hasRangeOnRight: Array.isArray(n) && l && r && (n[0] && this.dateHelpers.isAfter(r, n[0]) || n[1] && this.dateHelpers.isAfter(r, n[1])),
					$hasRangeSelected: Array.isArray(n) ? !!(n[0] && n[1]) : !1,
					$highlightedDate: r,
					$isHighlighted: s,
					$isHovered: this.state.isHovered,
					$isFocusVisible: this.state.isFocusVisible,
					$startOfMonth: this.dateHelpers.isStartOfMonth(e),
					$endOfMonth: this.dateHelpers.isEndOfMonth(e),
					$month: this.getMonthProp(),
					$outsideMonth: u,
					$outsideMonthWithinRange: d,
					$peekNextMonth: o,
					$pseudoHighlighted: i && !s && !c ? this.isPseudoHighlighted() : !1,
					$pseudoSelected: i && !c ? this.isPseudoSelected() : !1,
					$range: i,
					$selected: c,
					$startDate: Array.isArray(n) && n[0] && n[1] && i && c ? this.dateHelpers.isSameDay(e, n[0]) : !1,
					$hasLockedBehavior: this.props.hasLockedBehavior,
					$selectedInput: this.props.selectedInput,
					$value: this.props.value
				};
			}
		},
		{
			key: "getAriaLabel",
			value: function(e, t) {
				var n = this.getDateProp();
				return `${e.$selected ? e.$range ? e.$endDate ? t.datepicker.selectedEndDateLabel : t.datepicker.selectedStartDateLabel : t.datepicker.selectedLabel : e.$disabled ? t.datepicker.dateNotAvailableLabel : t.datepicker.chooseLabel} ${this.dateHelpers.format(n, "fullOrdinalWeek", this.props.locale)}. ${e.$disabled ? "" : t.datepicker.dateAvailableLabel}`;
			}
		},
		{
			key: "render",
			value: function() {
				var e = this, t = this.getDateProp(), n = this.props, i = n.peekNextMonth, a = n.overrides, o = a === void 0 ? {} : a, s = this.getSharedProps(), c = Cn(x(o.Day, qt), 2), l = c[0], u = c[1], d = Cn(x(o.DayLabel, Jt), 2), f = d[0], p = d[1], m = this.props.dateLabel && this.props.dateLabel(t);
				return !i && s.$outsideMonth ? /* @__PURE__ */ A.createElement(l, H({ role: "gridcell" }, s, u, {
					onFocus: this.onFocus,
					onBlur: this.onBlur
				})) : /* @__PURE__ */ A.createElement(r.Consumer, null, function(n) {
					return /* @__PURE__ */ A.createElement(l, H({
						"aria-label": e.getAriaLabel(s, n),
						ref: function(t) {
							e.dayElm = t;
						},
						role: "gridcell",
						"aria-roledescription": "button",
						tabIndex: e.props.highlighted || !e.props.highlightedDate && e.isSelected() ? 0 : -1
					}, s, u, {
						onFocus: e.onFocus,
						onBlur: e.onBlur,
						onClick: e.onClick,
						onKeyDown: e.onKeyDown,
						onMouseOver: e.onMouseOver,
						onMouseLeave: e.onMouseLeave
					}), /* @__PURE__ */ A.createElement("div", null, e.dateHelpers.getDate(t)), m ? /* @__PURE__ */ A.createElement(f, H({}, s, p), m) : null);
				});
			}
		}
	]), n;
}(A.Component);
W(Rn, "defaultProps", {
	disabled: !1,
	highlighted: !1,
	range: !1,
	adapter: D,
	onClick: function() {},
	onSelect: function() {},
	onFocus: function() {},
	onBlur: function() {},
	onMouseOver: function() {},
	onMouseLeave: function() {},
	overrides: {},
	peekNextMonth: !0,
	value: null
});
function zn(e) {
	"@babel/helpers - typeof";
	return zn = typeof Symbol == "function" && typeof Symbol.iterator == "symbol" ? function(e) {
		return typeof e;
	} : function(e) {
		return e && typeof Symbol == "function" && e.constructor === Symbol && e !== Symbol.prototype ? "symbol" : typeof e;
	}, zn(e);
}
function Bn() {
	return Bn = Object.assign ? Object.assign.bind() : function(e) {
		for (var t = 1; t < arguments.length; t++) {
			var n = arguments[t];
			for (var r in n) Object.prototype.hasOwnProperty.call(n, r) && (e[r] = n[r]);
		}
		return e;
	}, Bn.apply(this, arguments);
}
function Vn(e, t) {
	return Kn(e) || Gn(e, t) || Un(e, t) || Hn();
}
function Hn() {
	throw TypeError("Invalid attempt to destructure non-iterable instance.\nIn order to be iterable, non-array objects must have a [Symbol.iterator]() method.");
}
function Un(e, t) {
	if (e) {
		if (typeof e == "string") return Wn(e, t);
		var n = Object.prototype.toString.call(e).slice(8, -1);
		if (n === "Object" && e.constructor && (n = e.constructor.name), n === "Map" || n === "Set") return Array.from(e);
		if (n === "Arguments" || /^(?:Ui|I)nt(?:8|16|32)(?:Clamped)?Array$/.test(n)) return Wn(e, t);
	}
}
function Wn(e, t) {
	(t == null || t > e.length) && (t = e.length);
	for (var n = 0, r = Array(t); n < t; n++) r[n] = e[n];
	return r;
}
function Gn(e, t) {
	var n = e == null ? null : typeof Symbol < "u" && e[Symbol.iterator] || e["@@iterator"];
	if (n != null) {
		var r = [], i = !0, a = !1, o, s;
		try {
			for (n = n.call(e); !(i = (o = n.next()).done) && (r.push(o.value), !(t && r.length === t)); i = !0);
		} catch (e) {
			a = !0, s = e;
		} finally {
			try {
				!i && n.return != null && n.return();
			} finally {
				if (a) throw s;
			}
		}
		return r;
	}
}
function Kn(e) {
	if (Array.isArray(e)) return e;
}
function qn(e, t) {
	if (!(e instanceof t)) throw TypeError("Cannot call a class as a function");
}
function Jn(e, t) {
	for (var n = 0; n < t.length; n++) {
		var r = t[n];
		r.enumerable = r.enumerable || !1, r.configurable = !0, "value" in r && (r.writable = !0), Object.defineProperty(e, r.key, r);
	}
}
function Yn(e, t, n) {
	return t && Jn(e.prototype, t), Object.defineProperty(e, "prototype", { writable: !1 }), e;
}
function Xn(e, t) {
	if (typeof t != "function" && t !== null) throw TypeError("Super expression must either be null or a function");
	e.prototype = Object.create(t && t.prototype, { constructor: {
		value: e,
		writable: !0,
		configurable: !0
	} }), Object.defineProperty(e, "prototype", { writable: !1 }), t && Zn(e, t);
}
function Zn(e, t) {
	return Zn = Object.setPrototypeOf ? Object.setPrototypeOf.bind() : function(e, t) {
		return e.__proto__ = t, e;
	}, Zn(e, t);
}
function Qn(e) {
	var t = tr();
	return function() {
		var n = nr(e), r;
		if (t) {
			var i = nr(this).constructor;
			r = Reflect.construct(n, arguments, i);
		} else r = n.apply(this, arguments);
		return $n(this, r);
	};
}
function $n(e, t) {
	if (t && (zn(t) === "object" || typeof t == "function")) return t;
	if (t !== void 0) throw TypeError("Derived constructors may only return object or undefined");
	return er(e);
}
function er(e) {
	if (e === void 0) throw ReferenceError("this hasn't been initialised - super() hasn't been called");
	return e;
}
function tr() {
	if (typeof Reflect > "u" || !Reflect.construct || Reflect.construct.sham) return !1;
	if (typeof Proxy == "function") return !0;
	try {
		return Boolean.prototype.valueOf.call(Reflect.construct(Boolean, [], function() {})), !0;
	} catch {
		return !1;
	}
}
function nr(e) {
	return nr = Object.setPrototypeOf ? Object.getPrototypeOf.bind() : function(e) {
		return e.__proto__ || Object.getPrototypeOf(e);
	}, nr(e);
}
function rr(e, t, n) {
	return t in e ? Object.defineProperty(e, t, {
		value: n,
		enumerable: !0,
		configurable: !0,
		writable: !0
	}) : e[t] = n, e;
}
var ir = /* @__PURE__ */ function(e) {
	Xn(n, e);
	var t = Qn(n);
	function n(e) {
		var r;
		return qn(this, n), r = t.call(this, e), rr(er(r), "dateHelpers", void 0), rr(er(r), "renderDays", function() {
			var e = r.dateHelpers.getStartOfWeek(r.props.date || r.dateHelpers.date(), r.props.locale);
			return [].concat(Ge.map(function(t) {
				var n = r.dateHelpers.addDays(e, t);
				return /* @__PURE__ */ A.createElement(Rn, {
					adapter: r.props.adapter,
					date: n,
					dateLabel: r.props.dateLabel,
					density: r.props.density,
					disabled: r.dateHelpers.isDayDisabled(n, r.props),
					excludeDates: r.props.excludeDates,
					filterDate: r.props.filterDate,
					highlightedDate: r.props.highlightedDate,
					highlighted: r.dateHelpers.isSameDay(n, r.props.highlightedDate),
					includeDates: r.props.includeDates,
					focusedCalendar: r.props.focusedCalendar,
					range: r.props.range,
					key: t,
					locale: r.props.locale,
					minDate: r.props.minDate,
					maxDate: r.props.maxDate,
					month: r.props.month,
					onSelect: r.props.onChange,
					onBlur: r.props.onDayBlur,
					onFocus: r.props.onDayFocus,
					onClick: r.props.onDayClick,
					onMouseOver: r.props.onDayMouseOver,
					onMouseLeave: r.props.onDayMouseLeave,
					overrides: r.props.overrides,
					peekNextMonth: r.props.peekNextMonth,
					value: r.props.value,
					hasLockedBehavior: r.props.hasLockedBehavior,
					selectedInput: r.props.selectedInput
				});
			}));
		}), r.dateHelpers = new O(e.adapter), r;
	}
	return Yn(n, [{
		key: "render",
		value: function() {
			var e = this.props.overrides, t = Vn(x((e === void 0 ? {} : e).Week, Gt), 2), n = t[0], r = t[1];
			return /* @__PURE__ */ A.createElement(n, Bn({ role: "row" }, r), this.renderDays());
		}
	}]), n;
}(A.Component);
rr(ir, "defaultProps", {
	adapter: D,
	highlightedDate: null,
	onDayClick: function() {},
	onDayFocus: function() {},
	onDayBlur: function() {},
	onDayMouseOver: function() {},
	onDayMouseLeave: function() {},
	onChange: function() {},
	overrides: {},
	peekNextMonth: !1
});
function ar(e) {
	"@babel/helpers - typeof";
	return ar = typeof Symbol == "function" && typeof Symbol.iterator == "symbol" ? function(e) {
		return typeof e;
	} : function(e) {
		return e && typeof Symbol == "function" && e.constructor === Symbol && e !== Symbol.prototype ? "symbol" : typeof e;
	}, ar(e);
}
function or(e, t) {
	return dr(e) || ur(e, t) || cr(e, t) || sr();
}
function sr() {
	throw TypeError("Invalid attempt to destructure non-iterable instance.\nIn order to be iterable, non-array objects must have a [Symbol.iterator]() method.");
}
function cr(e, t) {
	if (e) {
		if (typeof e == "string") return lr(e, t);
		var n = Object.prototype.toString.call(e).slice(8, -1);
		if (n === "Object" && e.constructor && (n = e.constructor.name), n === "Map" || n === "Set") return Array.from(e);
		if (n === "Arguments" || /^(?:Ui|I)nt(?:8|16|32)(?:Clamped)?Array$/.test(n)) return lr(e, t);
	}
}
function lr(e, t) {
	(t == null || t > e.length) && (t = e.length);
	for (var n = 0, r = Array(t); n < t; n++) r[n] = e[n];
	return r;
}
function ur(e, t) {
	var n = e == null ? null : typeof Symbol < "u" && e[Symbol.iterator] || e["@@iterator"];
	if (n != null) {
		var r = [], i = !0, a = !1, o, s;
		try {
			for (n = n.call(e); !(i = (o = n.next()).done) && (r.push(o.value), !(t && r.length === t)); i = !0);
		} catch (e) {
			a = !0, s = e;
		} finally {
			try {
				!i && n.return != null && n.return();
			} finally {
				if (a) throw s;
			}
		}
		return r;
	}
}
function dr(e) {
	if (Array.isArray(e)) return e;
}
function fr(e, t) {
	if (!(e instanceof t)) throw TypeError("Cannot call a class as a function");
}
function pr(e, t) {
	for (var n = 0; n < t.length; n++) {
		var r = t[n];
		r.enumerable = r.enumerable || !1, r.configurable = !0, "value" in r && (r.writable = !0), Object.defineProperty(e, r.key, r);
	}
}
function mr(e, t, n) {
	return t && pr(e.prototype, t), Object.defineProperty(e, "prototype", { writable: !1 }), e;
}
function hr(e, t) {
	if (typeof t != "function" && t !== null) throw TypeError("Super expression must either be null or a function");
	e.prototype = Object.create(t && t.prototype, { constructor: {
		value: e,
		writable: !0,
		configurable: !0
	} }), Object.defineProperty(e, "prototype", { writable: !1 }), t && gr(e, t);
}
function gr(e, t) {
	return gr = Object.setPrototypeOf ? Object.setPrototypeOf.bind() : function(e, t) {
		return e.__proto__ = t, e;
	}, gr(e, t);
}
function _r(e) {
	var t = br();
	return function() {
		var n = xr(e), r;
		if (t) {
			var i = xr(this).constructor;
			r = Reflect.construct(n, arguments, i);
		} else r = n.apply(this, arguments);
		return vr(this, r);
	};
}
function vr(e, t) {
	if (t && (ar(t) === "object" || typeof t == "function")) return t;
	if (t !== void 0) throw TypeError("Derived constructors may only return object or undefined");
	return yr(e);
}
function yr(e) {
	if (e === void 0) throw ReferenceError("this hasn't been initialised - super() hasn't been called");
	return e;
}
function br() {
	if (typeof Reflect > "u" || !Reflect.construct || Reflect.construct.sham) return !1;
	if (typeof Proxy == "function") return !0;
	try {
		return Boolean.prototype.valueOf.call(Reflect.construct(Boolean, [], function() {})), !0;
	} catch {
		return !1;
	}
}
function xr(e) {
	return xr = Object.setPrototypeOf ? Object.getPrototypeOf.bind() : function(e) {
		return e.__proto__ || Object.getPrototypeOf(e);
	}, xr(e);
}
function Sr(e, t, n) {
	return t in e ? Object.defineProperty(e, t, {
		value: n,
		enumerable: !0,
		configurable: !0,
		writable: !0
	}) : e[t] = n, e;
}
var Cr = {
	dateLabel: null,
	density: j.high,
	excludeDates: null,
	filterDate: null,
	highlightDates: null,
	includeDates: null,
	locale: null,
	maxDate: null,
	minDate: null,
	month: null,
	adapter: D,
	onDayClick: function() {},
	onDayFocus: function() {},
	onDayBlur: function() {},
	onDayMouseOver: function() {},
	onDayMouseLeave: function() {},
	overrides: {},
	peekNextMonth: !1,
	value: null
}, wr = 6, Tr = /* @__PURE__ */ function(e) {
	hr(n, e);
	var t = _r(n);
	function n(e) {
		var r;
		return fr(this, n), r = t.call(this, e), Sr(yr(r), "dateHelpers", void 0), Sr(yr(r), "getDateProp", function() {
			return r.props.date || r.dateHelpers.date();
		}), Sr(yr(r), "isWeekInMonth", function(e) {
			var t = r.getDateProp(), n = r.dateHelpers.addDays(e, 6);
			return r.dateHelpers.isSameMonth(e, t) || r.dateHelpers.isSameMonth(n, t);
		}), Sr(yr(r), "renderWeeks", function() {
			for (var e = [], t = r.dateHelpers.getStartOfWeek(r.dateHelpers.getStartOfMonth(r.getDateProp()), r.props.locale), n = 0, i = !0; i || r.props.fixedHeight && r.props.peekNextMonth && n < wr;) e.push(/* @__PURE__ */ A.createElement(ir, {
				adapter: r.props.adapter,
				date: t,
				dateLabel: r.props.dateLabel,
				density: r.props.density,
				excludeDates: r.props.excludeDates,
				filterDate: r.props.filterDate,
				highlightedDate: r.props.highlightedDate,
				includeDates: r.props.includeDates,
				focusedCalendar: r.props.focusedCalendar,
				range: r.props.range,
				key: n,
				locale: r.props.locale,
				minDate: r.props.minDate,
				maxDate: r.props.maxDate,
				month: r.dateHelpers.getMonth(r.getDateProp()),
				onDayBlur: r.props.onDayBlur,
				onDayFocus: r.props.onDayFocus,
				onDayClick: r.props.onDayClick,
				onDayMouseOver: r.props.onDayMouseOver,
				onDayMouseLeave: r.props.onDayMouseLeave,
				onChange: r.props.onChange,
				overrides: r.props.overrides,
				peekNextMonth: r.props.peekNextMonth,
				value: r.props.value,
				hasLockedBehavior: r.props.hasLockedBehavior,
				selectedInput: r.props.selectedInput
			})), n++, t = r.dateHelpers.addWeeks(t, 1), i = r.isWeekInMonth(t);
			return e;
		}), r.dateHelpers = new O(e.adapter), r;
	}
	return mr(n, [{
		key: "render",
		value: function() {
			var e = this.props.overrides, t = or(x((e === void 0 ? {} : e).Month, Wt), 2), n = t[0], r = t[1];
			return /* @__PURE__ */ A.createElement(n, r, this.renderWeeks());
		}
	}]), n;
}(A.Component);
Sr(Tr, "defaultProps", Cr);
function Er(e) {
	"@babel/helpers - typeof";
	return Er = typeof Symbol == "function" && typeof Symbol.iterator == "symbol" ? function(e) {
		return typeof e;
	} : function(e) {
		return e && typeof Symbol == "function" && e.constructor === Symbol && e !== Symbol.prototype ? "symbol" : typeof e;
	}, Er(e);
}
var Dr = ["overrides"];
function Or(e, t) {
	if (e == null) return {};
	var n = kr(e, t), r, i;
	if (Object.getOwnPropertySymbols) {
		var a = Object.getOwnPropertySymbols(e);
		for (i = 0; i < a.length; i++) r = a[i], !(t.indexOf(r) >= 0) && Object.prototype.propertyIsEnumerable.call(e, r) && (n[r] = e[r]);
	}
	return n;
}
function kr(e, t) {
	if (e == null) return {};
	var n = {}, r = Object.keys(e), i, a;
	for (a = 0; a < r.length; a++) i = r[a], !(t.indexOf(i) >= 0) && (n[i] = e[i]);
	return n;
}
function G(e, t) {
	return Mr(e) || jr(e, t) || Fr(e, t) || Ar();
}
function Ar() {
	throw TypeError("Invalid attempt to destructure non-iterable instance.\nIn order to be iterable, non-array objects must have a [Symbol.iterator]() method.");
}
function jr(e, t) {
	var n = e == null ? null : typeof Symbol < "u" && e[Symbol.iterator] || e["@@iterator"];
	if (n != null) {
		var r = [], i = !0, a = !1, o, s;
		try {
			for (n = n.call(e); !(i = (o = n.next()).done) && (r.push(o.value), !(t && r.length === t)); i = !0);
		} catch (e) {
			a = !0, s = e;
		} finally {
			try {
				!i && n.return != null && n.return();
			} finally {
				if (a) throw s;
			}
		}
		return r;
	}
}
function Mr(e) {
	if (Array.isArray(e)) return e;
}
function Nr(e) {
	return Lr(e) || Ir(e) || Fr(e) || Pr();
}
function Pr() {
	throw TypeError("Invalid attempt to spread non-iterable instance.\nIn order to be iterable, non-array objects must have a [Symbol.iterator]() method.");
}
function Fr(e, t) {
	if (e) {
		if (typeof e == "string") return Rr(e, t);
		var n = Object.prototype.toString.call(e).slice(8, -1);
		if (n === "Object" && e.constructor && (n = e.constructor.name), n === "Map" || n === "Set") return Array.from(e);
		if (n === "Arguments" || /^(?:Ui|I)nt(?:8|16|32)(?:Clamped)?Array$/.test(n)) return Rr(e, t);
	}
}
function Ir(e) {
	if (typeof Symbol < "u" && e[Symbol.iterator] != null || e["@@iterator"] != null) return Array.from(e);
}
function Lr(e) {
	if (Array.isArray(e)) return Rr(e);
}
function Rr(e, t) {
	(t == null || t > e.length) && (t = e.length);
	for (var n = 0, r = Array(t); n < t; n++) r[n] = e[n];
	return r;
}
function K() {
	return K = Object.assign ? Object.assign.bind() : function(e) {
		for (var t = 1; t < arguments.length; t++) {
			var n = arguments[t];
			for (var r in n) Object.prototype.hasOwnProperty.call(n, r) && (e[r] = n[r]);
		}
		return e;
	}, K.apply(this, arguments);
}
function zr(e, t) {
	if (!(e instanceof t)) throw TypeError("Cannot call a class as a function");
}
function Br(e, t) {
	for (var n = 0; n < t.length; n++) {
		var r = t[n];
		r.enumerable = r.enumerable || !1, r.configurable = !0, "value" in r && (r.writable = !0), Object.defineProperty(e, r.key, r);
	}
}
function Vr(e, t, n) {
	return t && Br(e.prototype, t), Object.defineProperty(e, "prototype", { writable: !1 }), e;
}
function Hr(e, t) {
	if (typeof t != "function" && t !== null) throw TypeError("Super expression must either be null or a function");
	e.prototype = Object.create(t && t.prototype, { constructor: {
		value: e,
		writable: !0,
		configurable: !0
	} }), Object.defineProperty(e, "prototype", { writable: !1 }), t && Ur(e, t);
}
function Ur(e, t) {
	return Ur = Object.setPrototypeOf ? Object.setPrototypeOf.bind() : function(e, t) {
		return e.__proto__ = t, e;
	}, Ur(e, t);
}
function Wr(e) {
	var t = Kr();
	return function() {
		var n = qr(e), r;
		if (t) {
			var i = qr(this).constructor;
			r = Reflect.construct(n, arguments, i);
		} else r = n.apply(this, arguments);
		return Gr(this, r);
	};
}
function Gr(e, t) {
	if (t && (Er(t) === "object" || typeof t == "function")) return t;
	if (t !== void 0) throw TypeError("Derived constructors may only return object or undefined");
	return q(e);
}
function q(e) {
	if (e === void 0) throw ReferenceError("this hasn't been initialised - super() hasn't been called");
	return e;
}
function Kr() {
	if (typeof Reflect > "u" || !Reflect.construct || Reflect.construct.sham) return !1;
	if (typeof Proxy == "function") return !0;
	try {
		return Boolean.prototype.valueOf.call(Reflect.construct(Boolean, [], function() {})), !0;
	} catch {
		return !1;
	}
}
function qr(e) {
	return qr = Object.setPrototypeOf ? Object.getPrototypeOf.bind() : function(e) {
		return e.__proto__ || Object.getPrototypeOf(e);
	}, qr(e);
}
function J(e, t, n) {
	return t in e ? Object.defineProperty(e, t, {
		value: n,
		enumerable: !0,
		configurable: !0,
		writable: !0
	}) : e[t] = n, e;
}
var Jr = /* @__PURE__ */ function(e) {
	Hr(n, e);
	var t = Wr(n);
	function n(e) {
		var i;
		zr(this, n), i = t.call(this, e), J(q(i), "dateHelpers", void 0), J(q(i), "calendar", void 0), J(q(i), "getDateInView", function() {
			var e = i.props, t = e.highlightedDate, n = e.value, r = i.dateHelpers.getEffectiveMinDate(i.props), a = i.dateHelpers.getEffectiveMaxDate(i.props), o = i.dateHelpers.date();
			return i.getSingleDate(n) || t || (r && i.dateHelpers.isBefore(o, r) ? r : a && i.dateHelpers.isAfter(o, a) ? a : o);
		}), J(q(i), "handleMonthChange", function(e) {
			i.setHighlightedDate(i.dateHelpers.getStartOfMonth(e)), i.props.onMonthChange && i.props.onMonthChange({ date: e });
		}), J(q(i), "handleYearChange", function(e) {
			i.setHighlightedDate(e), i.props.onYearChange && i.props.onYearChange({ date: e });
		}), J(q(i), "changeMonth", function(e) {
			var t = e.date;
			i.setState({ date: t }, function() {
				return i.handleMonthChange(i.state.date);
			});
		}), J(q(i), "changeYear", function(e) {
			var t = e.date;
			i.setState({ date: t }, function() {
				return i.handleYearChange(i.state.date);
			});
		}), J(q(i), "renderCalendarHeader", function() {
			var e = arguments.length > 0 && arguments[0] !== void 0 ? arguments[0] : i.state.date, t = arguments.length > 1 ? arguments[1] : void 0;
			return /* @__PURE__ */ A.createElement(xn, K({}, i.props, {
				key: `month-header-${t}`,
				date: e,
				order: t,
				onMonthChange: i.changeMonth,
				onYearChange: i.changeYear
			}));
		}), J(q(i), "onKeyDown", function(e) {
			switch (e.key) {
				case "ArrowUp":
				case "ArrowDown":
				case "ArrowLeft":
				case "ArrowRight":
				case "Home":
				case "End":
				case "PageUp":
				case "PageDown":
					i.handleArrowKey(e.key), e.preventDefault(), e.stopPropagation();
					break;
			}
		}), J(q(i), "handleArrowKey", function(e) {
			var t = i.state.highlightedDate, n = i.dateHelpers.date();
			switch (e) {
				case "ArrowLeft":
					t = i.dateHelpers.subDays(t || n, 1);
					break;
				case "ArrowRight":
					t = i.dateHelpers.addDays(t || n, 1);
					break;
				case "ArrowUp":
					t = i.dateHelpers.subWeeks(t || n, 1);
					break;
				case "ArrowDown":
					t = i.dateHelpers.addWeeks(t || n, 1);
					break;
				case "Home":
					t = i.dateHelpers.getStartOfWeek(t || n);
					break;
				case "End":
					t = i.dateHelpers.getEndOfWeek(t || n);
					break;
				case "PageUp":
					t = i.dateHelpers.subMonths(t || n, 1);
					break;
				case "PageDown":
					t = i.dateHelpers.addMonths(t || n, 1);
					break;
			}
			i.setState({
				highlightedDate: t,
				date: t
			});
		}), J(q(i), "focusCalendar", function() {
			i.state.focused || i.setState({ focused: !0 });
		}), J(q(i), "blurCalendar", function() {
			if (typeof document < "u") {
				var e = document.activeElement;
				i.calendar && !i.calendar.contains(e) && i.setState({ focused: !1 });
			}
		}), J(q(i), "handleTabbing", function(e) {
			if (typeof document < "u" && e.keyCode === 9) {
				var t = document.activeElement, n = i.state.rootElement ? i.state.rootElement.querySelectorAll("[tabindex=\"0\"]") : null, r = n ? n.length : 0;
				e.shiftKey ? n && t === n[0] && (e.preventDefault(), n[r - 1].focus()) : n && t === n[r - 1] && (e.preventDefault(), n[0].focus());
			}
		}), J(q(i), "onDayFocus", function(e) {
			var t = e.date;
			i.setState({ highlightedDate: t }), i.focusCalendar(), i.props.onDayFocus && i.props.onDayFocus(e);
		}), J(q(i), "onDayMouseOver", function(e) {
			var t = e.date;
			i.setState({ highlightedDate: t }), i.props.onDayMouseOver && i.props.onDayMouseOver(e);
		}), J(q(i), "onDayMouseLeave", function(e) {
			var t = e.date, n = i.props.value, r = i.getSingleDate(n);
			i.setState({ highlightedDate: r || t }), i.props.onDayMouseLeave && i.props.onDayMouseLeave(e);
		}), J(q(i), "handleDateChange", function(e) {
			var t = i.props.onChange, n = t === void 0 ? function(e) {} : t, r = e.date;
			if (Array.isArray(e.date)) {
				var a = Nr(i.state.time), o = e.date[0] ? i.dateHelpers.applyDateToTime(a[0], e.date[0]) : null, s = e.date[1] ? i.dateHelpers.applyDateToTime(a[1], e.date[1]) : null;
				a[0] = o, s ? (r = [o, s], a[1] = s) : r = [o], i.setState({ time: a });
			} else if (!Array.isArray(i.props.value) && e.date) {
				var c = i.dateHelpers.applyDateToTime(i.state.time[0], e.date);
				r = c, i.setState({ time: [c] });
			}
			n({ date: r });
		}), J(q(i), "handleTimeChange", function(e, t) {
			var n = i.props.onChange, r = n === void 0 ? function(e) {} : n, a = Nr(i.state.time);
			if (a[t] = i.dateHelpers.applyTimeToDate(a[t], e), i.setState({ time: a }), Array.isArray(i.props.value)) {
				var o = i.props.value.map(function(n, r) {
					return n && t === r ? i.dateHelpers.applyTimeToDate(n, e) : n;
				});
				r({ date: [o[0], o[1]] });
			} else r({ date: i.dateHelpers.applyTimeToDate(i.props.value, e) });
		}), J(q(i), "renderMonths", function(e) {
			for (var t = i.props, n = t.overrides, r = n === void 0 ? {} : n, a = t.orientation, o = [], s = G(x(r.CalendarContainer, Ft), 2), c = s[0], l = s[1], u = G(x(r.MonthContainer, Pt), 2), d = u[0], f = u[1], p = 0; p < (i.props.monthsShown || 1); ++p) {
				var m = [], h = i.dateHelpers.addMonths(i.state.date, p), g = `month-${p}`;
				m.push(i.renderCalendarHeader(h, p)), m.push(/* @__PURE__ */ A.createElement(c, K({
					key: g,
					ref: function(e) {
						i.calendar = e;
					},
					role: "grid",
					"aria-roledescription": e.ariaRoleDescCalMonth,
					"aria-multiselectable": i.props.range || null,
					onKeyDown: i.onKeyDown
				}, l, { $density: i.props.density }), /* @__PURE__ */ A.createElement(Tr, {
					adapter: i.props.adapter,
					date: h,
					dateLabel: i.props.dateLabel,
					density: i.props.density,
					excludeDates: i.props.excludeDates,
					filterDate: i.props.filterDate,
					highlightedDate: i.state.highlightedDate,
					includeDates: i.props.includeDates,
					focusedCalendar: i.state.focused,
					range: i.props.range,
					locale: i.props.locale,
					maxDate: i.props.maxDate,
					minDate: i.props.minDate,
					month: i.dateHelpers.getMonth(i.state.date),
					onDayBlur: i.blurCalendar,
					onDayFocus: i.onDayFocus,
					onDayClick: i.props.onDayClick,
					onDayMouseOver: i.onDayMouseOver,
					onDayMouseLeave: i.onDayMouseLeave,
					onChange: i.handleDateChange,
					overrides: r,
					value: i.props.value,
					peekNextMonth: i.props.peekNextMonth,
					fixedHeight: i.props.fixedHeight,
					hasLockedBehavior: !!i.props.hasLockedBehavior,
					selectedInput: i.props.selectedInput
				}))), o.push(/* @__PURE__ */ A.createElement("div", { key: `month-component-${p}` }, m));
			}
			return /* @__PURE__ */ A.createElement(d, K({ $orientation: a }, f), o);
		}), J(q(i), "renderTimeSelect", function(e, t, n) {
			var r = i.props.overrides, a = r === void 0 ? {} : r, o = G(x(a.TimeSelectContainer, It), 2), s = o[0], c = o[1], l = G(x(a.TimeSelectFormControl, mt), 2), u = l[0], d = l[1], f = G(x(a.TimeSelect, E), 2), p = f[0], m = f[1];
			return /* @__PURE__ */ A.createElement(s, c, /* @__PURE__ */ A.createElement(u, K({ label: n }, d), /* @__PURE__ */ A.createElement(p, K({
				value: e && i.dateHelpers.date(e),
				onChange: t,
				nullable: !0
			}, m))));
		}), J(q(i), "renderQuickSelect", function() {
			var e = i.props.overrides, t = e === void 0 ? {} : e, n = G(x(t.QuickSelectContainer, It), 2), a = n[0], o = n[1], s = G(x(t.QuickSelectFormControl, mt), 2), c = s[0], l = s[1], u = G(x(t.QuickSelect, T), 2), d = u[0], f = u[1], p = f.overrides, m = Or(f, Dr);
			if (!i.props.quickSelect) return null;
			var h = i.dateHelpers.set(i.dateHelpers.date(), {
				hours: 12,
				minutes: 0,
				seconds: 0
			});
			return /* @__PURE__ */ A.createElement(r.Consumer, null, function(e) {
				return /* @__PURE__ */ A.createElement(a, o, /* @__PURE__ */ A.createElement(c, K({ label: e.datepicker.quickSelectLabel }, l), /* @__PURE__ */ A.createElement(d, K({
					"aria-label": e.datepicker.quickSelectAriaLabel,
					labelKey: "id",
					onChange: function(e) {
						e.option ? (i.setState({ quickSelectId: e.option.id }), i.props.onChange && (i.props.range ? i.props.onChange({ date: [e.option.beginDate, e.option.endDate || h] }) : i.props.onChange({ date: e.option.beginDate }))) : (i.setState({ quickSelectId: null }), i.props.onChange && i.props.onChange({ date: [] })), i.props.onQuickSelectChange && i.props.onQuickSelectChange(e.option);
					},
					options: i.props.quickSelectOptions || [
						{
							id: e.datepicker.pastWeek,
							beginDate: i.dateHelpers.subWeeks(h, 1)
						},
						{
							id: e.datepicker.pastMonth,
							beginDate: i.dateHelpers.subMonths(h, 1)
						},
						{
							id: e.datepicker.pastThreeMonths,
							beginDate: i.dateHelpers.subMonths(h, 3)
						},
						{
							id: e.datepicker.pastSixMonths,
							beginDate: i.dateHelpers.subMonths(h, 6)
						},
						{
							id: e.datepicker.pastYear,
							beginDate: i.dateHelpers.subYears(h, 1)
						},
						{
							id: e.datepicker.pastTwoYears,
							beginDate: i.dateHelpers.subYears(h, 2)
						}
					],
					placeholder: e.datepicker.quickSelectPlaceholder,
					value: i.state.quickSelectId && [{ id: i.state.quickSelectId }],
					overrides: g({ Dropdown: { style: { textAlign: "start" } } }, p)
				}, m))));
			});
		});
		var a = i.props, o = a.highlightedDate, s = a.value, c = a.adapter;
		i.dateHelpers = new O(c);
		var l = i.getDateInView(), u = [];
		return Array.isArray(s) ? u = Nr(s) : s && (u = [s]), i.state = {
			highlightedDate: i.getSingleDate(s) || (o && i.dateHelpers.isSameMonth(l, o) ? o : i.dateHelpers.date()),
			focused: !1,
			date: l,
			quickSelectId: null,
			rootElement: null,
			time: u
		}, i;
	}
	return Vr(n, [
		{
			key: "componentDidMount",
			value: function() {
				this.props.autoFocusCalendar && this.focusCalendar();
			}
		},
		{
			key: "componentDidUpdate",
			value: function(e) {
				if (this.props.highlightedDate && !this.dateHelpers.isSameDay(this.props.highlightedDate, e.highlightedDate) && this.setState({ date: this.props.highlightedDate }), this.props.autoFocusCalendar && this.props.autoFocusCalendar !== e.autoFocusCalendar && this.focusCalendar(), e.value !== this.props.value) {
					var t = this.getDateInView();
					this.isInView(t) || this.setState({ date: t });
				}
			}
		},
		{
			key: "isInView",
			value: function(e) {
				var t = this.state.date, n = (this.dateHelpers.getYear(e) - this.dateHelpers.getYear(t)) * 12 + this.dateHelpers.getMonth(e) - this.dateHelpers.getMonth(t);
				return n >= 0 && n < (this.props.monthsShown || 1);
			}
		},
		{
			key: "getSingleDate",
			value: function(e) {
				return Array.isArray(e) ? e[0] || null : e;
			}
		},
		{
			key: "setHighlightedDate",
			value: function(e) {
				var t = this.props.value, n = this.getSingleDate(t), r = n && this.dateHelpers.isSameMonth(n, e) && this.dateHelpers.isSameYear(n, e) ? { highlightedDate: n } : { highlightedDate: e };
				this.setState(r);
			}
		},
		{
			key: "render",
			value: function() {
				var e = this, t = this.props.overrides, n = G(x((t === void 0 ? {} : t).Root, Nt), 2), i = n[0], a = n[1], o = G([].concat(this.props.value), 2), s = o[0], c = o[1];
				return /* @__PURE__ */ A.createElement(r.Consumer, null, function(t) {
					return /* @__PURE__ */ A.createElement(i, K({
						$density: e.props.density,
						"data-baseweb": "calendar",
						role: "application",
						"aria-roledescription": "datepicker",
						ref: function(t) {
							t && t instanceof HTMLElement && !e.state.rootElement && e.setState({ rootElement: t });
						},
						"aria-label": t.datepicker.ariaLabelCalendar,
						onKeyDown: e.props.trapTabbing ? e.handleTabbing : null
					}, a), e.renderMonths({ ariaRoleDescCalMonth: t.datepicker.ariaRoleDescriptionCalendarMonth }), e.props.timeSelectStart && e.renderTimeSelect(s, function(t) {
						return e.handleTimeChange(t, 0);
					}, t.datepicker.timeSelectStartLabel), e.props.timeSelectEnd && e.props.range && e.renderTimeSelect(c, function(t) {
						return e.handleTimeChange(t, 1);
					}, t.datepicker.timeSelectEndLabel), e.renderQuickSelect());
				});
			}
		}
	]), n;
}(A.Component);
J(Jr, "defaultProps", {
	autoFocusCalendar: !1,
	dateLabel: null,
	density: j.default,
	excludeDates: null,
	filterDate: null,
	highlightedDate: null,
	includeDates: null,
	range: !1,
	locale: null,
	maxDate: null,
	minDate: null,
	onDayClick: function() {},
	onDayFocus: function() {},
	onDayMouseOver: function() {},
	onDayMouseLeave: function() {},
	onMonthChange: function() {},
	onYearChange: function() {},
	onChange: function() {},
	orientation: We.horizontal,
	overrides: {},
	peekNextMonth: !1,
	adapter: D,
	value: null,
	trapTabbing: !1
});
function Yr(e) {
	var t = arguments.length > 1 && arguments[1] !== void 0 ? arguments[1] : {};
	return e.replace(/\${(.*?)}/g, function(e, n) {
		return t[n] === void 0 ? "${" + n + "}" : t[n];
	});
}
function Xr(e) {
	"@babel/helpers - typeof";
	return Xr = typeof Symbol == "function" && typeof Symbol.iterator == "symbol" ? function(e) {
		return typeof e;
	} : function(e) {
		return e && typeof Symbol == "function" && e.constructor === Symbol && e !== Symbol.prototype ? "symbol" : typeof e;
	}, Xr(e);
}
function Y() {
	return Y = Object.assign ? Object.assign.bind() : function(e) {
		for (var t = 1; t < arguments.length; t++) {
			var n = arguments[t];
			for (var r in n) Object.prototype.hasOwnProperty.call(n, r) && (e[r] = n[r]);
		}
		return e;
	}, Y.apply(this, arguments);
}
function Zr(e, t) {
	var n = Object.keys(e);
	if (Object.getOwnPropertySymbols) {
		var r = Object.getOwnPropertySymbols(e);
		t && (r = r.filter(function(t) {
			return Object.getOwnPropertyDescriptor(e, t).enumerable;
		})), n.push.apply(n, r);
	}
	return n;
}
function Qr(e) {
	for (var t = 1; t < arguments.length; t++) {
		var n = arguments[t] == null ? {} : arguments[t];
		t % 2 ? Zr(Object(n), !0).forEach(function(t) {
			Z(e, t, n[t]);
		}) : Object.getOwnPropertyDescriptors ? Object.defineProperties(e, Object.getOwnPropertyDescriptors(n)) : Zr(Object(n)).forEach(function(t) {
			Object.defineProperty(e, t, Object.getOwnPropertyDescriptor(n, t));
		});
	}
	return e;
}
function $r(e) {
	return ni(e) || ti(e) || pi(e) || ei();
}
function ei() {
	throw TypeError("Invalid attempt to spread non-iterable instance.\nIn order to be iterable, non-array objects must have a [Symbol.iterator]() method.");
}
function ti(e) {
	if (typeof Symbol < "u" && e[Symbol.iterator] != null || e["@@iterator"] != null) return Array.from(e);
}
function ni(e) {
	if (Array.isArray(e)) return mi(e);
}
function ri(e, t) {
	if (!(e instanceof t)) throw TypeError("Cannot call a class as a function");
}
function ii(e, t) {
	for (var n = 0; n < t.length; n++) {
		var r = t[n];
		r.enumerable = r.enumerable || !1, r.configurable = !0, "value" in r && (r.writable = !0), Object.defineProperty(e, r.key, r);
	}
}
function ai(e, t, n) {
	return t && ii(e.prototype, t), Object.defineProperty(e, "prototype", { writable: !1 }), e;
}
function oi(e, t) {
	if (typeof t != "function" && t !== null) throw TypeError("Super expression must either be null or a function");
	e.prototype = Object.create(t && t.prototype, { constructor: {
		value: e,
		writable: !0,
		configurable: !0
	} }), Object.defineProperty(e, "prototype", { writable: !1 }), t && si(e, t);
}
function si(e, t) {
	return si = Object.setPrototypeOf ? Object.setPrototypeOf.bind() : function(e, t) {
		return e.__proto__ = t, e;
	}, si(e, t);
}
function ci(e) {
	var t = ui();
	return function() {
		var n = di(e), r;
		if (t) {
			var i = di(this).constructor;
			r = Reflect.construct(n, arguments, i);
		} else r = n.apply(this, arguments);
		return li(this, r);
	};
}
function li(e, t) {
	if (t && (Xr(t) === "object" || typeof t == "function")) return t;
	if (t !== void 0) throw TypeError("Derived constructors may only return object or undefined");
	return X(e);
}
function X(e) {
	if (e === void 0) throw ReferenceError("this hasn't been initialised - super() hasn't been called");
	return e;
}
function ui() {
	if (typeof Reflect > "u" || !Reflect.construct || Reflect.construct.sham) return !1;
	if (typeof Proxy == "function") return !0;
	try {
		return Boolean.prototype.valueOf.call(Reflect.construct(Boolean, [], function() {})), !0;
	} catch {
		return !1;
	}
}
function di(e) {
	return di = Object.setPrototypeOf ? Object.getPrototypeOf.bind() : function(e) {
		return e.__proto__ || Object.getPrototypeOf(e);
	}, di(e);
}
function Z(e, t, n) {
	return t in e ? Object.defineProperty(e, t, {
		value: n,
		enumerable: !0,
		configurable: !0,
		writable: !0
	}) : e[t] = n, e;
}
function Q(e, t) {
	return gi(e) || hi(e, t) || pi(e, t) || fi();
}
function fi() {
	throw TypeError("Invalid attempt to destructure non-iterable instance.\nIn order to be iterable, non-array objects must have a [Symbol.iterator]() method.");
}
function pi(e, t) {
	if (e) {
		if (typeof e == "string") return mi(e, t);
		var n = Object.prototype.toString.call(e).slice(8, -1);
		if (n === "Object" && e.constructor && (n = e.constructor.name), n === "Map" || n === "Set") return Array.from(e);
		if (n === "Arguments" || /^(?:Ui|I)nt(?:8|16|32)(?:Clamped)?Array$/.test(n)) return mi(e, t);
	}
}
function mi(e, t) {
	(t == null || t > e.length) && (t = e.length);
	for (var n = 0, r = Array(t); n < t; n++) r[n] = e[n];
	return r;
}
function hi(e, t) {
	var n = e == null ? null : typeof Symbol < "u" && e[Symbol.iterator] || e["@@iterator"];
	if (n != null) {
		var r = [], i = !0, a = !1, o, s;
		try {
			for (n = n.call(e); !(i = (o = n.next()).done) && (r.push(o.value), !(t && r.length === t)); i = !0);
		} catch (e) {
			a = !0, s = e;
		} finally {
			try {
				!i && n.return != null && n.return();
			} finally {
				if (a) throw s;
			}
		}
		return r;
	}
}
function gi(e) {
	if (Array.isArray(e)) return e;
}
var _i = "yyyy/MM/dd", $ = "–", vi = function(e) {
	var t = arguments.length > 1 && arguments[1] !== void 0 ? arguments[1] : "", n = arguments.length > 2 ? arguments[2] : void 0, r = e, i = Q(t.split(` ${$} `), 2), a = i[0], o = a === void 0 ? "" : a, s = i[1], c = s === void 0 ? "" : s;
	return n === M.startDate && c && (r = `${r} ${$} ${c}`), n === M.endDate && (r = `${o} ${$} ${r}`), r;
}, yi = /* @__PURE__ */ function(e) {
	oi(n, e);
	var t = ci(n);
	function n(e) {
		var r;
		return ri(this, n), r = t.call(this, e), Z(X(r), "calendar", void 0), Z(X(r), "dateHelpers", void 0), Z(X(r), "handleChange", function(e) {
			var t = r.props.onChange, n = r.props.onRangeChange;
			Array.isArray(e) ? (t && e.every(Boolean) && t({ date: e }), n && n({ date: $r(e) })) : (t && t({ date: e }), n && n({ date: e }));
		}), Z(X(r), "onCalendarSelect", function(e) {
			var t = !1, n = !1, i = !1, a = e.date;
			if (Array.isArray(a) && r.props.range) {
				if (!a[0] || !a[1]) t = !0, n = !0, i = null;
				else if (a[0] && a[1]) {
					var o = Q(a, 2), s = o[0], c = o[1];
					r.dateHelpers.isAfter(s, c) ? r.hasLockedBehavior() ? (a = r.props.value, t = !0) : a = [s, s] : r.dateHelpers.dateRangeIncludesDates(a, r.props.excludeDates) && (a = r.props.value, t = !0), r.state.lastActiveElm && r.state.lastActiveElm.focus();
				}
			} else r.state.lastActiveElm && r.state.lastActiveElm.focus();
			var l = function(e, t) {
				return !e || !t ? !1 : r.dateHelpers.format(e, "keyboardDate") === r.dateHelpers.format(t, "keyboardDate") ? r.dateHelpers.getHours(e) !== r.dateHelpers.getHours(t) || r.dateHelpers.getMinutes(e) !== r.dateHelpers.getMinutes(t) : !1;
			}, u = r.props.value;
			Array.isArray(a) && Array.isArray(u) ? a.some(function(e, t) {
				return l(u[t], e);
			}) && (t = !0) : !Array.isArray(a) && !Array.isArray(u) && l(u, a) && (t = !0), r.setState(Qr(Qr({
				isOpen: t,
				isPseudoFocused: n
			}, i === null ? {} : { calendarFocused: i }), {}, { inputValue: r.formatDisplayValue(a) })), r.handleChange(a);
		}), Z(X(r), "formatDisplayValue", function(e) {
			var t = r.props, n = t.displayValueAtRangeIndex, i = t.formatDisplayValue;
			t.range;
			var a = r.normalizeDashes(r.props.formatString);
			if (typeof n == "number" && e && Array.isArray(e)) {
				var o = e[n];
				return i ? i(o, a) : r.formatDate(o, a);
			}
			return i ? i(e, a) : r.formatDate(e, a);
		}), Z(X(r), "open", function(e) {
			r.setState({
				isOpen: !0,
				isPseudoFocused: !0,
				calendarFocused: !1,
				selectedInput: e
			}, r.props.onOpen);
		}), Z(X(r), "close", function() {
			r.setState({
				isOpen: !1,
				selectedInput: null,
				isPseudoFocused: !1,
				calendarFocused: !1
			}, r.props.onClose);
		}), Z(X(r), "handleEsc", function() {
			r.state.lastActiveElm && r.state.lastActiveElm.focus(), r.close();
		}), Z(X(r), "handleInputBlur", function() {
			r.state.isPseudoFocused || r.close();
		}), Z(X(r), "getMask", function() {
			var e = r.props, t = e.formatString, n = e.mask, i = e.range, a = e.separateRangeInputs;
			return n === null || n === void 0 && t !== _i ? null : n ? r.normalizeDashes(n) : i && !a ? `9999/99/99 ${$} 9999/99/99` : "9999/99/99";
		}), Z(X(r), "handleInputChange", function(e, t) {
			var n = r.props.range && r.props.separateRangeInputs ? vi(e.currentTarget.value, r.state.inputValue, t) : e.currentTarget.value, i = r.getMask(), a = r.normalizeDashes(r.props.formatString);
			(typeof i == "string" && n === i.replace(/9/g, " ") || n.length === 0) && (r.props.range ? r.handleChange([]) : r.handleChange(null)), r.setState({ inputValue: n });
			var o = function(e) {
				return a === _i ? r.dateHelpers.parse(e, "slashDate", r.props.locale) : r.dateHelpers.parseString(e, a, r.props.locale);
			};
			if (r.props.range && typeof r.props.displayValueAtRangeIndex != "number") {
				var s = Q(r.normalizeDashes(n).split(` ${$} `), 2), c = s[0], l = s[1], u = r.dateHelpers.date(c), d = r.dateHelpers.date(l);
				a && (u = o(c), d = o(l));
				var f = r.dateHelpers.isValid(u) && r.dateHelpers.isValid(d), p = r.dateHelpers.isAfter(d, u) || r.dateHelpers.isEqual(u, d);
				f && p && r.handleChange([u, d]);
			} else {
				var m = r.normalizeDashes(n), h = r.dateHelpers.date(m), g = r.props.formatString;
				h = m.replace(/(\s)*/g, "").length < g.replace(/(\s)*/g, "").length ? null : o(m);
				var _ = r.props, v = _.displayValueAtRangeIndex, y = _.range, b = _.value;
				if (h && r.dateHelpers.isValid(h)) if (y && Array.isArray(b) && typeof v == "number") {
					var x = Q(b, 2), S = x[0], C = x[1];
					v === 0 ? (S = h, C ? r.dateHelpers.isAfter(C, S) || r.dateHelpers.isEqual(S, C) ? r.handleChange([S, C]) : r.handleChange($r(b)) : r.handleChange([S])) : v === 1 && (C = h, S ? r.dateHelpers.isAfter(C, S) || r.dateHelpers.isEqual(S, C) ? r.handleChange([S, C]) : r.handleChange($r(b)) : r.handleChange([C, C]));
				} else r.handleChange(h);
			}
		}), Z(X(r), "handleKeyDown", function(e) {
			!r.state.isOpen && e.keyCode === 40 ? r.open() : r.state.isOpen && e.key === "ArrowDown" ? (e.preventDefault(), r.focusCalendar()) : r.state.isOpen && e.keyCode === 9 && r.close();
		}), Z(X(r), "focusCalendar", function() {
			if (typeof document < "u") {
				var e = document.activeElement;
				r.setState({
					calendarFocused: !0,
					lastActiveElm: e
				});
			}
		}), Z(X(r), "normalizeDashes", function(e) {
			return e.replace(/-/g, $).replace(/—/g, $);
		}), Z(X(r), "hasLockedBehavior", function() {
			return r.props.rangedCalendarBehavior === qe.locked && r.props.range && r.props.separateRangeInputs;
		}), r.dateHelpers = new O(e.adapter), r.state = {
			calendarFocused: !1,
			isOpen: !1,
			selectedInput: null,
			isPseudoFocused: !1,
			lastActiveElm: null,
			inputValue: r.formatDisplayValue(e.value) || ""
		}, r;
	}
	return ai(n, [
		{
			key: "getNullDatePlaceholder",
			value: function(e) {
				return (this.getMask() || e).split($)[0].replace(/[0-9]|[a-z]/g, " ");
			}
		},
		{
			key: "formatDate",
			value: function(e, t) {
				var n = this, r = function(e) {
					return t === _i ? n.dateHelpers.format(e, "slashDate", n.props.locale) : n.dateHelpers.formatDate(e, t, n.props.locale);
				};
				if (e) {
					if (Array.isArray(e) && !e[0] && !e[1]) return "";
					if (Array.isArray(e) && !e[0] && e[1]) {
						var i = r(e[1]);
						return [this.getNullDatePlaceholder(t), i].join(` ${$} `);
					} else return Array.isArray(e) ? e.map(function(e) {
						return e ? r(e) : "";
					}).join(` ${$} `) : r(e);
				} else return "";
			}
		},
		{
			key: "componentDidUpdate",
			value: function(e) {
				e.value !== this.props.value && this.setState({ inputValue: this.formatDisplayValue(this.props.value) });
			}
		},
		{
			key: "renderInputComponent",
			value: function(e, t) {
				var n = this, r = this.props.overrides, i = Q(x((r === void 0 ? {} : r).Input, Ue), 2), a = i[0], o = i[1], s = this.props.placeholder || this.props.placeholder === "" ? this.props.placeholder : this.props.range && !this.props.separateRangeInputs ? `YYYY/MM/DD ${$} YYYY/MM/DD` : "YYYY/MM/DD", c = Q((this.state.inputValue || "").split(` ${$} `), 2), l = c[0], u = l === void 0 ? "" : l, d = c[1], f = d === void 0 ? "" : d, p = t === M.startDate ? u : t === M.endDate ? f : this.state.inputValue;
				return /* @__PURE__ */ A.createElement(a, Y({
					"aria-disabled": this.props.disabled,
					"aria-label": this.props["aria-label"] || (this.props.range ? e.datepicker.ariaLabelRange : e.datepicker.ariaLabel),
					error: this.props.error,
					positive: this.props.positive,
					"aria-describedby": this.props["aria-describedby"],
					"aria-labelledby": this.props["aria-labelledby"],
					"aria-required": this.props.required || null,
					disabled: this.props.disabled,
					size: this.props.size,
					value: p,
					onFocus: function() {
						return n.open(t);
					},
					onBlur: this.handleInputBlur,
					onKeyDown: this.handleKeyDown,
					onChange: function(e) {
						return n.handleInputChange(e, t);
					},
					placeholder: s,
					mask: this.getMask(),
					required: this.props.required,
					clearable: this.props.clearable
				}, o));
			}
		},
		{
			key: "render",
			value: function() {
				var e = this, t = this.props, n = t.overrides, i = n === void 0 ? {} : n, a = t.startDateLabel, o = a === void 0 ? "Start Date" : a, s = t.endDateLabel, c = s === void 0 ? "End Date" : s, l = Q(x(i.Popover, p), 2), u = l[0], d = l[1], f = Q(x(i.InputWrapper, kt), 2), m = f[0], h = f[1], g = Q(x(i.StartDate, jt), 2), _ = g[0], v = g[1], S = Q(x(i.EndDate, Mt), 2), C = S[0], w = S[1], T = Q(x(i.InputLabel, At), 2), E = T[0], D = T[1];
				return /* @__PURE__ */ A.createElement(r.Consumer, null, function(t) {
					return /* @__PURE__ */ A.createElement(A.Fragment, null, /* @__PURE__ */ A.createElement(u, Y({
						accessibilityType: b.none,
						focusLock: !1,
						autoFocus: !1,
						mountNode: e.props.mountNode,
						placement: y.bottom,
						isOpen: e.state.isOpen,
						onClickOutside: e.close,
						onEsc: e.handleEsc,
						content: /* @__PURE__ */ A.createElement(Jr, Y({
							adapter: e.props.adapter,
							autoFocusCalendar: e.state.calendarFocused,
							trapTabbing: !0,
							value: e.props.value
						}, e.props, {
							onChange: e.onCalendarSelect,
							selectedInput: e.state.selectedInput,
							hasLockedBehavior: e.hasLockedBehavior()
						}))
					}, d), /* @__PURE__ */ A.createElement(m, Y({}, h, { $separateRangeInputs: e.props.range && e.props.separateRangeInputs }), e.props.range && e.props.separateRangeInputs ? /* @__PURE__ */ A.createElement(A.Fragment, null, /* @__PURE__ */ A.createElement(_, v, /* @__PURE__ */ A.createElement(E, D, o), e.renderInputComponent(t, M.startDate)), /* @__PURE__ */ A.createElement(C, w, /* @__PURE__ */ A.createElement(E, D, c), e.renderInputComponent(t, M.endDate))) : /* @__PURE__ */ A.createElement(A.Fragment, null, e.renderInputComponent(t)))), /* @__PURE__ */ A.createElement("p", {
						id: e.props["aria-describedby"],
						style: {
							position: "fixed",
							width: "0px",
							height: "0px",
							borderLeftWidth: 0,
							borderRightWidth: 0,
							borderTopWidth: 0,
							borderBottomWidth: 0,
							padding: 0,
							overflow: "hidden",
							clip: "rect(0, 0, 0, 0)",
							clipPath: "inset(100%)"
						}
					}, t.datepicker.screenReaderMessageInput), /* @__PURE__ */ A.createElement("p", {
						"aria-live": "assertive",
						style: {
							position: "fixed",
							width: "0px",
							height: "0px",
							borderLeftWidth: 0,
							borderRightWidth: 0,
							borderTopWidth: 0,
							borderBottomWidth: 0,
							padding: 0,
							overflow: "hidden",
							clip: "rect(0, 0, 0, 0)",
							clipPath: "inset(100%)"
						}
					}, !e.props.value || Array.isArray(e.props.value) && !e.props.value[0] && !e.props.value[1] ? "" : Array.isArray(e.props.value) ? e.props.value[0] && e.props.value[1] ? Yr(t.datepicker.selectedDateRange, {
						startDate: e.formatDisplayValue(e.props.value[0]),
						endDate: e.formatDisplayValue(e.props.value[1])
					}) : `${Yr(t.datepicker.selectedDate, { date: e.formatDisplayValue(e.props.value[0]) })} ${t.datepicker.selectSecondDatePrompt}` : Yr(t.datepicker.selectedDate, { date: e.state.inputValue || "" })));
				});
			}
		}
	]), n;
}(A.Component);
Z(yi, "defaultProps", {
	"aria-describedby": "datepicker--screenreader--message--input",
	value: null,
	formatString: _i,
	adapter: D
});
var bi = {
	lessThanXSeconds: {
		one: "less than a second",
		other: "less than {{count}} seconds"
	},
	xSeconds: {
		one: "1 second",
		other: "{{count}} seconds"
	},
	halfAMinute: "half a minute",
	lessThanXMinutes: {
		one: "less than a minute",
		other: "less than {{count}} minutes"
	},
	xMinutes: {
		one: "1 minute",
		other: "{{count}} minutes"
	},
	aboutXHours: {
		one: "about 1 hour",
		other: "about {{count}} hours"
	},
	xHours: {
		one: "1 hour",
		other: "{{count}} hours"
	},
	xDays: {
		one: "1 day",
		other: "{{count}} days"
	},
	aboutXWeeks: {
		one: "about 1 week",
		other: "about {{count}} weeks"
	},
	xWeeks: {
		one: "1 week",
		other: "{{count}} weeks"
	},
	aboutXMonths: {
		one: "about 1 month",
		other: "about {{count}} months"
	},
	xMonths: {
		one: "1 month",
		other: "{{count}} months"
	},
	aboutXYears: {
		one: "about 1 year",
		other: "about {{count}} years"
	},
	xYears: {
		one: "1 year",
		other: "{{count}} years"
	},
	overXYears: {
		one: "over 1 year",
		other: "over {{count}} years"
	},
	almostXYears: {
		one: "almost 1 year",
		other: "almost {{count}} years"
	}
}, xi = (e, t, n) => {
	let r, i = bi[e];
	return r = typeof i == "string" ? i : t === 1 ? i.one : i.other.replace("{{count}}", t.toString()), n?.addSuffix ? n.comparison && n.comparison > 0 ? "in " + r : r + " ago" : r;
};
function Si(e) {
	return (t = {}) => {
		let n = t.width ? String(t.width) : e.defaultWidth;
		return e.formats[n] || e.formats[e.defaultWidth];
	};
}
var Ci = {
	date: Si({
		formats: {
			full: "EEEE, MMMM do, y",
			long: "MMMM do, y",
			medium: "MMM d, y",
			short: "MM/dd/yyyy"
		},
		defaultWidth: "full"
	}),
	time: Si({
		formats: {
			full: "h:mm:ss a zzzz",
			long: "h:mm:ss a z",
			medium: "h:mm:ss a",
			short: "h:mm a"
		},
		defaultWidth: "full"
	}),
	dateTime: Si({
		formats: {
			full: "{{date}} 'at' {{time}}",
			long: "{{date}} 'at' {{time}}",
			medium: "{{date}}, {{time}}",
			short: "{{date}}, {{time}}"
		},
		defaultWidth: "full"
	})
}, wi = {
	lastWeek: "'last' eeee 'at' p",
	yesterday: "'yesterday at' p",
	today: "'today at' p",
	tomorrow: "'tomorrow at' p",
	nextWeek: "eeee 'at' p",
	other: "P"
}, Ti = (e, t, n, r) => wi[e];
function Ei(e) {
	return (t, n) => {
		let r = n?.context ? String(n.context) : "standalone", i;
		if (r === "formatting" && e.formattingValues) {
			let t = e.defaultFormattingWidth || e.defaultWidth, r = n?.width ? String(n.width) : t;
			i = e.formattingValues[r] || e.formattingValues[t];
		} else {
			let t = e.defaultWidth, r = n?.width ? String(n.width) : e.defaultWidth;
			i = e.values[r] || e.values[t];
		}
		let a = e.argumentCallback ? e.argumentCallback(t) : t;
		return i[a];
	};
}
var Di = {
	ordinalNumber: (e, t) => {
		let n = Number(e), r = n % 100;
		if (r > 20 || r < 10) switch (r % 10) {
			case 1: return n + "st";
			case 2: return n + "nd";
			case 3: return n + "rd";
		}
		return n + "th";
	},
	era: Ei({
		values: {
			narrow: ["B", "A"],
			abbreviated: ["BC", "AD"],
			wide: ["Before Christ", "Anno Domini"]
		},
		defaultWidth: "wide"
	}),
	quarter: Ei({
		values: {
			narrow: [
				"1",
				"2",
				"3",
				"4"
			],
			abbreviated: [
				"Q1",
				"Q2",
				"Q3",
				"Q4"
			],
			wide: [
				"1st quarter",
				"2nd quarter",
				"3rd quarter",
				"4th quarter"
			]
		},
		defaultWidth: "wide",
		argumentCallback: (e) => e - 1
	}),
	month: Ei({
		values: {
			narrow: [
				"J",
				"F",
				"M",
				"A",
				"M",
				"J",
				"J",
				"A",
				"S",
				"O",
				"N",
				"D"
			],
			abbreviated: [
				"Jan",
				"Feb",
				"Mar",
				"Apr",
				"May",
				"Jun",
				"Jul",
				"Aug",
				"Sep",
				"Oct",
				"Nov",
				"Dec"
			],
			wide: [
				"January",
				"February",
				"March",
				"April",
				"May",
				"June",
				"July",
				"August",
				"September",
				"October",
				"November",
				"December"
			]
		},
		defaultWidth: "wide"
	}),
	day: Ei({
		values: {
			narrow: [
				"S",
				"M",
				"T",
				"W",
				"T",
				"F",
				"S"
			],
			short: [
				"Su",
				"Mo",
				"Tu",
				"We",
				"Th",
				"Fr",
				"Sa"
			],
			abbreviated: [
				"Sun",
				"Mon",
				"Tue",
				"Wed",
				"Thu",
				"Fri",
				"Sat"
			],
			wide: [
				"Sunday",
				"Monday",
				"Tuesday",
				"Wednesday",
				"Thursday",
				"Friday",
				"Saturday"
			]
		},
		defaultWidth: "wide"
	}),
	dayPeriod: Ei({
		values: {
			narrow: {
				am: "a",
				pm: "p",
				midnight: "mi",
				noon: "n",
				morning: "morning",
				afternoon: "afternoon",
				evening: "evening",
				night: "night"
			},
			abbreviated: {
				am: "AM",
				pm: "PM",
				midnight: "midnight",
				noon: "noon",
				morning: "morning",
				afternoon: "afternoon",
				evening: "evening",
				night: "night"
			},
			wide: {
				am: "a.m.",
				pm: "p.m.",
				midnight: "midnight",
				noon: "noon",
				morning: "morning",
				afternoon: "afternoon",
				evening: "evening",
				night: "night"
			}
		},
		defaultWidth: "wide",
		formattingValues: {
			narrow: {
				am: "a",
				pm: "p",
				midnight: "mi",
				noon: "n",
				morning: "in the morning",
				afternoon: "in the afternoon",
				evening: "in the evening",
				night: "at night"
			},
			abbreviated: {
				am: "AM",
				pm: "PM",
				midnight: "midnight",
				noon: "noon",
				morning: "in the morning",
				afternoon: "in the afternoon",
				evening: "in the evening",
				night: "at night"
			},
			wide: {
				am: "a.m.",
				pm: "p.m.",
				midnight: "midnight",
				noon: "noon",
				morning: "in the morning",
				afternoon: "in the afternoon",
				evening: "in the evening",
				night: "at night"
			}
		},
		defaultFormattingWidth: "wide"
	})
};
function Oi(e) {
	return (t, n = {}) => {
		let r = n.width, i = r && e.matchPatterns[r] || e.matchPatterns[e.defaultMatchWidth], a = t.match(i);
		if (!a) return null;
		let o = a[0], s = r && e.parsePatterns[r] || e.parsePatterns[e.defaultParseWidth], c = Array.isArray(s) ? Ai(s, (e) => e.test(o)) : ki(s, (e) => e.test(o)), l;
		l = e.valueCallback ? e.valueCallback(c) : c, l = n.valueCallback ? n.valueCallback(l) : l;
		let u = t.slice(o.length);
		return {
			value: l,
			rest: u
		};
	};
}
function ki(e, t) {
	for (let n in e) if (Object.prototype.hasOwnProperty.call(e, n) && t(e[n])) return n;
}
function Ai(e, t) {
	for (let n = 0; n < e.length; n++) if (t(e[n])) return n;
}
function ji(e) {
	return (t, n = {}) => {
		let r = t.match(e.matchPattern);
		if (!r) return null;
		let i = r[0], a = t.match(e.parsePattern);
		if (!a) return null;
		let o = e.valueCallback ? e.valueCallback(a[0]) : a[0];
		o = n.valueCallback ? n.valueCallback(o) : o;
		let s = t.slice(i.length);
		return {
			value: o,
			rest: s
		};
	};
}
var Mi = {
	code: "en-US",
	formatDistance: xi,
	formatLong: Ci,
	formatRelative: Ti,
	localize: Di,
	match: {
		ordinalNumber: ji({
			matchPattern: /^(\d+)(th|st|nd|rd)?/i,
			parsePattern: /\d+/i,
			valueCallback: (e) => parseInt(e, 10)
		}),
		era: Oi({
			matchPatterns: {
				narrow: /^(b|a)/i,
				abbreviated: /^(b\.?\s?c\.?|b\.?\s?c\.?\s?e\.?|a\.?\s?d\.?|c\.?\s?e\.?)/i,
				wide: /^(before christ|before common era|anno domini|common era)/i
			},
			defaultMatchWidth: "wide",
			parsePatterns: { any: [/^b/i, /^(a|c)/i] },
			defaultParseWidth: "any"
		}),
		quarter: Oi({
			matchPatterns: {
				narrow: /^[1234]/i,
				abbreviated: /^q[1234]/i,
				wide: /^[1234](th|st|nd|rd)? quarter/i
			},
			defaultMatchWidth: "wide",
			parsePatterns: { any: [
				/1/i,
				/2/i,
				/3/i,
				/4/i
			] },
			defaultParseWidth: "any",
			valueCallback: (e) => e + 1
		}),
		month: Oi({
			matchPatterns: {
				narrow: /^[jfmasond]/i,
				abbreviated: /^(jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)/i,
				wide: /^(january|february|march|april|may|june|july|august|september|october|november|december)/i
			},
			defaultMatchWidth: "wide",
			parsePatterns: {
				narrow: [
					/^j/i,
					/^f/i,
					/^m/i,
					/^a/i,
					/^m/i,
					/^j/i,
					/^j/i,
					/^a/i,
					/^s/i,
					/^o/i,
					/^n/i,
					/^d/i
				],
				any: [
					/^ja/i,
					/^f/i,
					/^mar/i,
					/^ap/i,
					/^may/i,
					/^jun/i,
					/^jul/i,
					/^au/i,
					/^s/i,
					/^o/i,
					/^n/i,
					/^d/i
				]
			},
			defaultParseWidth: "any"
		}),
		day: Oi({
			matchPatterns: {
				narrow: /^[smtwf]/i,
				short: /^(su|mo|tu|we|th|fr|sa)/i,
				abbreviated: /^(sun|mon|tue|wed|thu|fri|sat)/i,
				wide: /^(sunday|monday|tuesday|wednesday|thursday|friday|saturday)/i
			},
			defaultMatchWidth: "wide",
			parsePatterns: {
				narrow: [
					/^s/i,
					/^m/i,
					/^t/i,
					/^w/i,
					/^t/i,
					/^f/i,
					/^s/i
				],
				any: [
					/^su/i,
					/^m/i,
					/^tu/i,
					/^w/i,
					/^th/i,
					/^f/i,
					/^sa/i
				]
			},
			defaultParseWidth: "any"
		}),
		dayPeriod: Oi({
			matchPatterns: {
				narrow: /^(a|p|mi|n|(in the|at) (morning|afternoon|evening|night))/i,
				any: /^([ap]\.?\s?m\.?|midnight|noon|(in the|at) (morning|afternoon|evening|night))/i
			},
			defaultMatchWidth: "any",
			parsePatterns: { any: {
				am: /^a/i,
				pm: /^p/i,
				midnight: /^mi/i,
				noon: /^no/i,
				morning: /morning/i,
				afternoon: /afternoon/i,
				evening: /evening/i,
				night: /night/i
			} },
			defaultParseWidth: "any"
		})
	},
	options: {
		weekStartsOn: 0,
		firstWeekContainsDate: 1
	}
}, Ni = (e) => {
	let t = e;
	return t?.getWeekInfo?.() ?? t?.weekInfo ?? null;
}, Pi = (e) => {
	let t = (0, A.useMemo)(() => {
		try {
			return Ni(new Intl.Locale(e));
		} catch {
			return Ni(new Intl.Locale("en-US"));
		}
	}, [e]);
	if (!t) return Mi;
	let n = t.firstDay >= 1 && t.firstDay <= 7 ? t.firstDay : 7, r = n === 7 ? 0 : n;
	return {
		...Mi,
		options: {
			...Mi.options,
			weekStartsOn: r
		}
	};
};
//#endregion
export { j as i, yi as n, Mi as r, Pi as t };

//# sourceMappingURL=useIntlLocale-DdLGxiZO-BQljgqPP.js.map