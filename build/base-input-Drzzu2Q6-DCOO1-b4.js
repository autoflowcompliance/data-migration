import { $i as e, Ca as t, Ka as n, Ln as r, M as i, Rn as a, Ua as o, di as s, ia as c, jr as l, tr as u } from "./index-Dl4ETd_L-D2oMd1k2.js";
import { a as d, i as f, r as p, t as m } from "./constants-yZa2TGaZ-D7s59a3V.js";
//#region ../react/build/base-input-Drzzu2Q6.js
var h = /* @__PURE__ */ n(o(), 1), g = [
	"title",
	"size",
	"color",
	"overrides"
];
function _() {
	return _ = Object.assign ? Object.assign.bind() : function(e) {
		for (var t = 1; t < arguments.length; t++) {
			var n = arguments[t];
			for (var r in n) Object.prototype.hasOwnProperty.call(n, r) && (e[r] = n[r]);
		}
		return e;
	}, _.apply(this, arguments);
}
function v(e, t) {
	if (e == null) return {};
	var n = y(e, t), r, i;
	if (Object.getOwnPropertySymbols) {
		var a = Object.getOwnPropertySymbols(e);
		for (i = 0; i < a.length; i++) r = a[i], !(t.indexOf(r) >= 0) && Object.prototype.propertyIsEnumerable.call(e, r) && (n[r] = e[r]);
	}
	return n;
}
function y(e, t) {
	if (e == null) return {};
	var n = {}, r = Object.keys(e), i, a;
	for (a = 0; a < r.length; a++) i = r[a], !(t.indexOf(i) >= 0) && (n[i] = e[i]);
	return n;
}
function b(e, t) {
	return te(e) || ee(e, t) || S(e, t) || x();
}
function x() {
	throw TypeError("Invalid attempt to destructure non-iterable instance.\nIn order to be iterable, non-array objects must have a [Symbol.iterator]() method.");
}
function S(e, t) {
	if (e) {
		if (typeof e == "string") return C(e, t);
		var n = Object.prototype.toString.call(e).slice(8, -1);
		if (n === "Object" && e.constructor && (n = e.constructor.name), n === "Map" || n === "Set") return Array.from(e);
		if (n === "Arguments" || /^(?:Ui|I)nt(?:8|16|32)(?:Clamped)?Array$/.test(n)) return C(e, t);
	}
}
function C(e, t) {
	(t == null || t > e.length) && (t = e.length);
	for (var n = 0, r = Array(t); n < t; n++) r[n] = e[n];
	return r;
}
function ee(e, t) {
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
function te(e) {
	if (Array.isArray(e)) return e;
}
function ne(e, n) {
	var r = b(t(), 2)[1], a = e.title, o = a === void 0 ? "Hide" : a, l = e.size, u = e.color, d = e.overrides, f = d === void 0 ? {} : d, p = v(e, g), m = s({ component: r.icons && r.icons.Hide ? r.icons.Hide : null }, f && f.Svg ? c(f.Svg) : {});
	return /* @__PURE__ */ h.createElement(i, _({
		viewBox: "0 0 20 20",
		ref: n,
		title: o,
		size: l,
		color: u,
		overrides: { Svg: m }
	}, p), /* @__PURE__ */ h.createElement("path", { d: "M12.81 4.36l-1.77 1.78a4 4 0 00-4.9 4.9l-2.76 2.75C2.06 12.79.96 11.49.2 10a11 11 0 0112.6-5.64zm3.8 1.85c1.33 1 2.43 2.3 3.2 3.79a11 11 0 01-12.62 5.64l1.77-1.78a4 4 0 004.9-4.9l2.76-2.75zm-.25-3.99l1.42 1.42L3.64 17.78l-1.42-1.42L16.36 2.22z" }));
}
var re = /* @__PURE__ */ h.forwardRef(ne), ie = [
	"title",
	"size",
	"color",
	"overrides"
];
function w() {
	return w = Object.assign ? Object.assign.bind() : function(e) {
		for (var t = 1; t < arguments.length; t++) {
			var n = arguments[t];
			for (var r in n) Object.prototype.hasOwnProperty.call(n, r) && (e[r] = n[r]);
		}
		return e;
	}, w.apply(this, arguments);
}
function ae(e, t) {
	if (e == null) return {};
	var n = oe(e, t), r, i;
	if (Object.getOwnPropertySymbols) {
		var a = Object.getOwnPropertySymbols(e);
		for (i = 0; i < a.length; i++) r = a[i], !(t.indexOf(r) >= 0) && Object.prototype.propertyIsEnumerable.call(e, r) && (n[r] = e[r]);
	}
	return n;
}
function oe(e, t) {
	if (e == null) return {};
	var n = {}, r = Object.keys(e), i, a;
	for (a = 0; a < r.length; a++) i = r[a], !(t.indexOf(i) >= 0) && (n[i] = e[i]);
	return n;
}
function se(e, t) {
	return E(e) || ue(e, t) || le(e, t) || ce();
}
function ce() {
	throw TypeError("Invalid attempt to destructure non-iterable instance.\nIn order to be iterable, non-array objects must have a [Symbol.iterator]() method.");
}
function le(e, t) {
	if (e) {
		if (typeof e == "string") return T(e, t);
		var n = Object.prototype.toString.call(e).slice(8, -1);
		if (n === "Object" && e.constructor && (n = e.constructor.name), n === "Map" || n === "Set") return Array.from(e);
		if (n === "Arguments" || /^(?:Ui|I)nt(?:8|16|32)(?:Clamped)?Array$/.test(n)) return T(e, t);
	}
}
function T(e, t) {
	(t == null || t > e.length) && (t = e.length);
	for (var n = 0, r = Array(t); n < t; n++) r[n] = e[n];
	return r;
}
function ue(e, t) {
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
function E(e) {
	if (Array.isArray(e)) return e;
}
function de(e, n) {
	var r = se(t(), 2)[1], a = e.title, o = a === void 0 ? "Show" : a, l = e.size, u = e.color, d = e.overrides, f = d === void 0 ? {} : d, p = ae(e, ie), m = s({ component: r.icons && r.icons.Show ? r.icons.Show : null }, f && f.Svg ? c(f.Svg) : {});
	return /* @__PURE__ */ h.createElement(i, w({
		viewBox: "0 0 20 20",
		ref: n,
		title: o,
		size: l,
		color: u,
		overrides: { Svg: m }
	}, p), /* @__PURE__ */ h.createElement("path", { d: "M.2 10a11 11 0 0119.6 0A11 11 0 01.2 10zm9.8 4a4 4 0 100-8 4 4 0 000 8zm0-2a2 2 0 110-4 2 2 0 010 4z" }));
}
var fe = /* @__PURE__ */ h.forwardRef(de);
function D(e, t) {
	var n = e.disabled, r = e.error, i = e.positive, a = e.adjoined, o = e.size, s = e.required, c = e.resize, l = e.readOnly;
	return {
		$isFocused: t.isFocused,
		$disabled: n,
		$error: r,
		$positive: i,
		$adjoined: a,
		$size: o,
		$required: s,
		$resize: c,
		$isReadOnly: l
	};
}
function O(e, t) {
	var n = Object.keys(e);
	if (Object.getOwnPropertySymbols) {
		var r = Object.getOwnPropertySymbols(e);
		t && (r = r.filter(function(t) {
			return Object.getOwnPropertyDescriptor(e, t).enumerable;
		})), n.push.apply(n, r);
	}
	return n;
}
function k(e) {
	for (var t = 1; t < arguments.length; t++) {
		var n = arguments[t] == null ? {} : arguments[t];
		t % 2 ? O(Object(n), !0).forEach(function(t) {
			A(e, t, n[t]);
		}) : Object.getOwnPropertyDescriptors ? Object.defineProperties(e, Object.getOwnPropertyDescriptors(n)) : O(Object(n)).forEach(function(t) {
			Object.defineProperty(e, t, Object.getOwnPropertyDescriptor(n, t));
		});
	}
	return e;
}
function A(e, t, n) {
	return t in e ? Object.defineProperty(e, t, {
		value: n,
		enumerable: !0,
		configurable: !0,
		writable: !0
	}) : e[t] = n, e;
}
var j = e("button", function(e) {
	var t, n = e.$theme, r = e.$size, i = e.$isFocusVisible, a = (t = {}, A(t, m.mini, n.sizing.scale400), A(t, m.compact, n.sizing.scale400), A(t, m.default, n.sizing.scale300), A(t, m.large, n.sizing.scale200), t)[r];
	return {
		display: "flex",
		alignItems: "center",
		borderTopStyle: "none",
		borderBottomStyle: "none",
		borderLeftStyle: "none",
		borderRightStyle: "none",
		background: "none",
		paddingLeft: a,
		paddingRight: a,
		outline: i ? `solid 3px ${n.colors.accent}` : "none",
		color: n.colors.contentPrimary
	};
});
j.displayName = "StyledMaskToggleButton", j.displayName = "StyledMaskToggleButton";
var M = e("div", function(e) {
	var t, n = e.$alignTop, r = n === void 0 ? !1 : n, i = e.$size, a = e.$theme, o = (t = {}, A(t, m.mini, a.sizing.scale200), A(t, m.compact, a.sizing.scale200), A(t, m.default, a.sizing.scale100), A(t, m.large, a.sizing.scale0), t)[i];
	return {
		display: "flex",
		alignItems: r ? "flex-start" : "center",
		paddingLeft: o,
		paddingRight: o,
		paddingTop: r ? a.sizing.scale500 : "0px",
		color: a.colors.contentPrimary
	};
});
M.displayName = "StyledClearIconContainer", M.displayName = "StyledClearIconContainer";
var N = e(f, function(e) {
	var t = e.$theme;
	return {
		cursor: "pointer",
		outline: e.$isFocusVisible ? `solid 3px ${t.colors.accent}` : "none"
	};
});
N.displayName = "StyledClearIcon", N.displayName = "StyledClearIcon";
function pe(e, t) {
	var n;
	return (n = {}, A(n, m.mini, {
		paddingTop: t.scale100,
		paddingBottom: t.scale100,
		paddingLeft: t.scale550,
		paddingRight: t.scale550
	}), A(n, m.compact, {
		paddingTop: t.scale200,
		paddingBottom: t.scale200,
		paddingLeft: t.scale550,
		paddingRight: t.scale550
	}), A(n, m.default, {
		paddingTop: t.scale400,
		paddingBottom: t.scale400,
		paddingLeft: t.scale550,
		paddingRight: t.scale550
	}), A(n, m.large, {
		paddingTop: t.scale550,
		paddingBottom: t.scale550,
		paddingLeft: t.scale550,
		paddingRight: t.scale550
	}), n)[e];
}
function me(e, t, n, r, i) {
	var a = e === d.both || e === d.left && r !== "rtl" || e === d.right && r === "rtl" || i && r === "rtl", o = e === d.both || e === d.right && r !== "rtl" || e === d.left && r === "rtl" || i && r !== "rtl";
	return {
		paddingLeft: a ? n.scale550 : "0px",
		paddingRight: o ? n.scale550 : "0px"
	};
}
function P(e, t) {
	var n;
	return (n = {}, A(n, m.mini, t.font100), A(n, m.compact, t.font200), A(n, m.default, t.font300), A(n, m.large, t.font400), n)[e];
}
function he(e, t, n) {
	var r = arguments.length > 3 && arguments[3] !== void 0 ? arguments[3] : !1, i = arguments.length > 4 ? arguments[4] : void 0;
	return e ? {
		borderLeftColor: i.inputFillDisabled,
		borderRightColor: i.inputFillDisabled,
		borderTopColor: i.inputFillDisabled,
		borderBottomColor: i.inputFillDisabled,
		backgroundColor: i.inputFillDisabled
	} : t ? {
		borderLeftColor: i.borderSelected,
		borderRightColor: i.borderSelected,
		borderTopColor: i.borderSelected,
		borderBottomColor: i.borderSelected,
		backgroundColor: i.inputFillActive
	} : n ? {
		borderLeftColor: i.inputBorderError,
		borderRightColor: i.inputBorderError,
		borderTopColor: i.inputBorderError,
		borderBottomColor: i.inputBorderError,
		backgroundColor: i.inputFillError
	} : r ? {
		borderLeftColor: i.inputBorderPositive,
		borderRightColor: i.inputBorderPositive,
		borderTopColor: i.inputBorderPositive,
		borderBottomColor: i.inputBorderPositive,
		backgroundColor: i.inputFillPositive
	} : {
		borderLeftColor: i.inputBorder,
		borderRightColor: i.inputBorder,
		borderTopColor: i.inputBorder,
		borderBottomColor: i.inputBorder,
		backgroundColor: i.inputFill
	};
}
function ge(e, t) {
	var n = t.inputBorderRadius;
	return e === m.mini && (n = t.inputBorderRadiusMini), {
		borderTopLeftRadius: n,
		borderBottomLeftRadius: n,
		borderTopRightRadius: n,
		borderBottomRightRadius: n
	};
}
var F = function(e) {
	var t = e.$isFocused, n = e.$adjoined, r = e.$error, i = e.$disabled, a = e.$positive, o = e.$size, s = e.$theme, c = e.$theme, l = c.borders, u = c.colors, d = c.sizing, f = c.typography, p = c.animation, m = e.$hasIconTrailing;
	return k(k(k(k({
		boxSizing: "border-box",
		display: "flex",
		overflow: "hidden",
		width: "100%",
		borderLeftWidth: "2px",
		borderRightWidth: "2px",
		borderTopWidth: "2px",
		borderBottomWidth: "2px",
		borderLeftStyle: "solid",
		borderRightStyle: "solid",
		borderTopStyle: "solid",
		borderBottomStyle: "solid",
		transitionProperty: "border",
		transitionDuration: p.timing200,
		transitionTimingFunction: p.easeOutCurve
	}, ge(o, l)), P(o, f)), he(i, t, r, a, u)), me(n, o, d, s.direction, m));
}, I = e("div", F);
I.displayName = "Root", I.displayName = "Root";
function L(e, t) {
	var n;
	return (n = {}, A(n, m.mini, {
		paddingRight: t.scale400,
		paddingLeft: t.scale400
	}), A(n, m.compact, {
		paddingRight: t.scale400,
		paddingLeft: t.scale400
	}), A(n, m.default, {
		paddingRight: t.scale300,
		paddingLeft: t.scale300
	}), A(n, m.large, {
		paddingRight: t.scale200,
		paddingLeft: t.scale200
	}), n)[e];
}
function _e(e, t, n, r, i) {
	return e ? {
		color: i.inputEnhancerTextDisabled,
		backgroundColor: i.inputFillDisabled
	} : t ? {
		color: i.contentPrimary,
		backgroundColor: i.inputFillActive
	} : n ? {
		color: i.contentPrimary,
		backgroundColor: i.inputFillError
	} : r ? {
		color: i.contentPrimary,
		backgroundColor: i.inputFillPositive
	} : {
		color: i.contentPrimary,
		backgroundColor: i.inputFill
	};
}
var R = e("div", function(e) {
	var t = e.$size, n = e.$disabled, r = e.$isFocused, i = e.$error, a = e.$positive, o = e.$theme, s = o.colors, c = o.sizing, l = o.typography, u = o.animation;
	return k(k(k({
		display: "flex",
		alignItems: "center",
		justifyContent: "center",
		transitionProperty: "color, background-color",
		transitionDuration: u.timing200,
		transitionTimingFunction: u.easeOutCurve
	}, P(t, l)), L(t, c)), _e(n, r, i, a, s));
});
R.displayName = "InputEnhancer", R.displayName = "InputEnhancer";
function ve(e, t, n, r, i) {
	return e ? {
		color: i.inputTextDisabled,
		backgroundColor: i.inputFillDisabled
	} : t ? {
		color: i.contentPrimary,
		backgroundColor: i.inputFillActive
	} : n ? {
		color: i.contentPrimary,
		backgroundColor: i.inputFillError
	} : r ? {
		color: i.contentPrimary,
		backgroundColor: i.inputFillPositive
	} : {
		color: i.contentPrimary,
		backgroundColor: i.inputFill
	};
}
var z = function(e) {
	var t = e.$isFocused, n = e.$error, r = e.$disabled, i = e.$positive, a = e.$size, o = e.$theme, s = o.colors, c = o.typography, l = o.animation;
	return k(k({
		display: "flex",
		width: "100%",
		transitionProperty: "background-color",
		transitionDuration: l.timing200,
		transitionTimingFunction: l.easeOutCurve
	}, P(a, c)), ve(r, t, n, i, s));
}, B = e("div", z);
B.displayName = "InputContainer", B.displayName = "InputContainer";
function ye(e, t, n, r) {
	return e ? {
		color: r.inputTextDisabled,
		"-webkit-text-fill-color": r.inputTextDisabled,
		caretColor: r.contentPrimary,
		"::placeholder": { color: r.inputPlaceholderDisabled }
	} : {
		color: r.contentPrimary,
		caretColor: r.contentPrimary,
		"::placeholder": { color: r.inputPlaceholder }
	};
}
var V = function(e) {
	var t = e.$disabled, n = e.$isFocused, r = e.$error, i = e.$size, a = e.$theme, o = a.colors, s = a.sizing, c = a.typography;
	return k(k(k({
		boxSizing: "border-box",
		backgroundColor: "transparent",
		borderLeftWidth: 0,
		borderRightWidth: 0,
		borderTopWidth: 0,
		borderBottomWidth: 0,
		borderLeftStyle: "none",
		borderRightStyle: "none",
		borderTopStyle: "none",
		borderBottomStyle: "none",
		outline: "none",
		width: "100%",
		minWidth: 0,
		maxWidth: "100%",
		cursor: t ? "not-allowed" : "text",
		margin: "0",
		paddingTop: "0",
		paddingBottom: "0",
		paddingLeft: "0",
		paddingRight: "0"
	}, P(i, c)), pe(i, s)), ye(t, n, r, o));
}, H = e("input", V);
H.displayName = "Input", H.displayName = "Input";
function be(e) {
	var t;
	return typeof window.Event == "function" ? t = new window.Event(e, {
		bubbles: !0,
		cancelable: !0
	}) : (t = document.createEvent("Event"), t.initEvent(e, !0, !0)), t;
}
function U(e) {
	"@babel/helpers - typeof";
	return U = typeof Symbol == "function" && typeof Symbol.iterator == "symbol" ? function(e) {
		return typeof e;
	} : function(e) {
		return e && typeof Symbol == "function" && e.constructor === Symbol && e !== Symbol.prototype ? "symbol" : typeof e;
	}, U(e);
}
function W() {
	return W = Object.assign ? Object.assign.bind() : function(e) {
		for (var t = 1; t < arguments.length; t++) {
			var n = arguments[t];
			for (var r in n) Object.prototype.hasOwnProperty.call(n, r) && (e[r] = n[r]);
		}
		return e;
	}, W.apply(this, arguments);
}
function G(e, t) {
	return we(e) || Ce(e, t) || Se(e, t) || xe();
}
function xe() {
	throw TypeError("Invalid attempt to destructure non-iterable instance.\nIn order to be iterable, non-array objects must have a [Symbol.iterator]() method.");
}
function Se(e, t) {
	if (e) {
		if (typeof e == "string") return K(e, t);
		var n = Object.prototype.toString.call(e).slice(8, -1);
		if (n === "Object" && e.constructor && (n = e.constructor.name), n === "Map" || n === "Set") return Array.from(e);
		if (n === "Arguments" || /^(?:Ui|I)nt(?:8|16|32)(?:Clamped)?Array$/.test(n)) return K(e, t);
	}
}
function K(e, t) {
	(t == null || t > e.length) && (t = e.length);
	for (var n = 0, r = Array(t); n < t; n++) r[n] = e[n];
	return r;
}
function Ce(e, t) {
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
function we(e) {
	if (Array.isArray(e)) return e;
}
function Te(e, t) {
	if (!(e instanceof t)) throw TypeError("Cannot call a class as a function");
}
function Ee(e, t) {
	for (var n = 0; n < t.length; n++) {
		var r = t[n];
		r.enumerable = r.enumerable || !1, r.configurable = !0, "value" in r && (r.writable = !0), Object.defineProperty(e, r.key, r);
	}
}
function q(e, t, n) {
	return t && Ee(e.prototype, t), Object.defineProperty(e, "prototype", { writable: !1 }), e;
}
function De(e, t) {
	if (typeof t != "function" && t !== null) throw TypeError("Super expression must either be null or a function");
	e.prototype = Object.create(t && t.prototype, { constructor: {
		value: e,
		writable: !0,
		configurable: !0
	} }), Object.defineProperty(e, "prototype", { writable: !1 }), t && J(e, t);
}
function J(e, t) {
	return J = Object.setPrototypeOf ? Object.setPrototypeOf.bind() : function(e, t) {
		return e.__proto__ = t, e;
	}, J(e, t);
}
function Oe(e) {
	var t = Ae();
	return function() {
		var n = X(e), r;
		if (t) {
			var i = X(this).constructor;
			r = Reflect.construct(n, arguments, i);
		} else r = n.apply(this, arguments);
		return ke(this, r);
	};
}
function ke(e, t) {
	if (t && (U(t) === "object" || typeof t == "function")) return t;
	if (t !== void 0) throw TypeError("Derived constructors may only return object or undefined");
	return Y(e);
}
function Y(e) {
	if (e === void 0) throw ReferenceError("this hasn't been initialised - super() hasn't been called");
	return e;
}
function Ae() {
	if (typeof Reflect > "u" || !Reflect.construct || Reflect.construct.sham) return !1;
	if (typeof Proxy == "function") return !0;
	try {
		return Boolean.prototype.valueOf.call(Reflect.construct(Boolean, [], function() {})), !0;
	} catch {
		return !1;
	}
}
function X(e) {
	return X = Object.setPrototypeOf ? Object.getPrototypeOf.bind() : function(e) {
		return e.__proto__ || Object.getPrototypeOf(e);
	}, X(e);
}
function Z(e, t, n) {
	return t in e ? Object.defineProperty(e, t, {
		value: n,
		enumerable: !0,
		configurable: !0,
		writable: !0
	}) : e[t] = n, e;
}
var Q = function() {
	return null;
}, $ = /* @__PURE__ */ function(e) {
	De(n, e);
	var t = Oe(n);
	function n() {
		var e;
		Te(this, n);
		var r = [...arguments];
		return e = t.call.apply(t, [this].concat(r)), Z(Y(e), "inputRef", e.props.inputRef || /* @__PURE__ */ h.createRef()), Z(Y(e), "state", {
			isFocused: e.props.autoFocus || !1,
			isMasked: e.props.type === "password",
			initialType: e.props.type,
			isFocusVisibleForClear: !1,
			isFocusVisibleForMaskToggle: !1
		}), Z(Y(e), "onInputKeyDown", function(t) {
			e.props.clearOnEscape && t.key === "Escape" && e.inputRef.current && !e.props.readOnly && (e.clearValue(), t.stopPropagation());
		}), Z(Y(e), "onClearIconClick", function() {
			e.inputRef.current && e.clearValue(), e.inputRef.current && e.inputRef.current.focus();
		}), Z(Y(e), "onFocus", function(t) {
			e.setState({ isFocused: !0 }), e.props.onFocus(t);
		}), Z(Y(e), "onBlur", function(t) {
			e.setState({ isFocused: !1 }), e.props.onBlur(t);
		}), Z(Y(e), "handleFocusForMaskToggle", function(t) {
			l(t) && e.setState({ isFocusVisibleForMaskToggle: !0 });
		}), Z(Y(e), "handleBlurForMaskToggle", function(t) {
			e.state.isFocusVisibleForMaskToggle !== !1 && e.setState({ isFocusVisibleForMaskToggle: !1 });
		}), Z(Y(e), "handleFocusForClear", function(t) {
			l(t) && e.setState({ isFocusVisibleForClear: !0 });
		}), Z(Y(e), "handleBlurForClear", function(t) {
			e.state.isFocusVisibleForClear !== !1 && e.setState({ isFocusVisibleForClear: !1 });
		}), e;
	}
	return q(n, [
		{
			key: "componentDidMount",
			value: function() {
				var e = this.props, t = e.autoFocus, n = e.clearable;
				this.inputRef.current && (t && this.inputRef.current.focus(), n && this.inputRef.current.addEventListener("keydown", this.onInputKeyDown));
			}
		},
		{
			key: "componentWillUnmount",
			value: function() {
				this.props.clearable && this.inputRef.current && this.inputRef.current.removeEventListener("keydown", this.onInputKeyDown);
			}
		},
		{
			key: "clearValue",
			value: function() {
				var e = this.inputRef.current;
				if (e) {
					var t = Object.getOwnPropertyDescriptor(this.props.type === p.textarea ? HTMLTextAreaElement.prototype : HTMLInputElement.prototype, "value");
					if (t) {
						var n = t.set;
						if (n) {
							n.call(e, "");
							var r = be("input");
							e.dispatchEvent(r);
						}
					}
				}
			}
		},
		{
			key: "getInputType",
			value: function() {
				return this.props.type === "password" ? this.state.isMasked ? "password" : "text" : this.props.type;
			}
		},
		{
			key: "renderMaskToggle",
			value: function() {
				var e, t = this;
				if (this.props.type !== "password") return null;
				var n = G(u(this.props.overrides.MaskToggleButton, j), 2), i = n[0], o = n[1], s = G(u(this.props.overrides.MaskToggleShowIcon, fe), 2), c = s[0], l = s[1], d = G(u(this.props.overrides.MaskToggleHideIcon, re), 2), f = d[0], p = d[1], g = this.state.isMasked ? "Show password text" : "Hide password text", _ = (e = {}, Z(e, m.mini, "12px"), Z(e, m.compact, "16px"), Z(e, m.default, "20px"), Z(e, m.large, "24px"), e)[this.props.size];
				return /* @__PURE__ */ h.createElement(i, W({
					$size: this.props.size,
					$isFocusVisible: this.state.isFocusVisibleForMaskToggle,
					"aria-label": g,
					onClick: function() {
						return t.setState(function(e) {
							return { isMasked: !e.isMasked };
						});
					},
					title: g,
					type: "button"
				}, o, {
					onFocus: a(o, this.handleFocusForMaskToggle),
					onBlur: r(o, this.handleBlurForMaskToggle)
				}), this.state.isMasked ? /* @__PURE__ */ h.createElement(c, W({
					size: _,
					title: g
				}, l)) : /* @__PURE__ */ h.createElement(f, W({
					size: _,
					title: g
				}, p)));
			}
		},
		{
			key: "renderClear",
			value: function() {
				var e, t = this, n = this.props, i = n.clearable, o = n.value, s = n.disabled, c = n.readOnly, l = n.overrides, d = l === void 0 ? {} : l;
				if (s || c || !i || o == null || typeof o == "string" && o.length === 0) return null;
				var f = G(u(d.ClearIconContainer, M), 2), g = f[0], _ = f[1], v = G(u(d.ClearIcon, N), 2), y = v[0], b = v[1], x = "Clear value", S = D(this.props, this.state), C = (e = {}, Z(e, m.mini, "14px"), Z(e, m.compact, "14px"), Z(e, m.default, "16px"), Z(e, m.large, "22px"), e)[this.props.size];
				return /* @__PURE__ */ h.createElement(g, W({ $alignTop: this.props.type === p.textarea }, S, _), /* @__PURE__ */ h.createElement(y, W({
					size: C,
					tabIndex: 0,
					title: x,
					"aria-label": x,
					onClick: this.onClearIconClick,
					onKeyDown: function(e) {
						e.key && (e.key === "Enter" || e.key === " ") && (e.preventDefault(), t.onClearIconClick());
					},
					role: "button",
					$isFocusVisible: this.state.isFocusVisibleForClear
				}, S, b, {
					onFocus: a(b, this.handleFocusForClear),
					onBlur: r(b, this.handleBlurForClear)
				})));
			}
		},
		{
			key: "render",
			value: function() {
				var e = this.props.overrides, t = e.InputContainer, r = e.Input, i = e.Before, a = e.After, o = this.state.initialType === "password" && this.props.autoComplete === n.defaultProps.autoComplete ? "new-password" : this.props.autoComplete, s = D(this.props, this.state), c = G(u(t, B), 2), l = c[0], d = c[1], f = G(u(r, H), 2), m = f[0], g = f[1], _ = G(u(i, Q), 2), v = _[0], y = _[1], b = G(u(a, Q), 2), x = b[0], S = b[1];
				return /* @__PURE__ */ h.createElement(l, W({ "data-baseweb": this.props["data-baseweb"] || "base-input" }, s, d), /* @__PURE__ */ h.createElement(v, W({}, s, y)), /* @__PURE__ */ h.createElement(m, W({
					ref: this.inputRef,
					"aria-activedescendant": this.props["aria-activedescendant"],
					"aria-autocomplete": this.props["aria-autocomplete"],
					"aria-controls": this.props["aria-controls"],
					"aria-errormessage": this.props["aria-errormessage"],
					"aria-haspopup": this.props["aria-haspopup"],
					"aria-label": this.props["aria-label"],
					"aria-labelledby": this.props["aria-labelledby"],
					"aria-describedby": this.props["aria-describedby"],
					"aria-invalid": this.props.error,
					"aria-required": this.props.required,
					autoComplete: o,
					disabled: this.props.disabled,
					readOnly: this.props.readOnly,
					id: this.props.id,
					inputMode: this.props.inputMode,
					maxLength: this.props.maxLength,
					name: this.props.name,
					onBlur: this.onBlur,
					onChange: this.props.onChange,
					onFocus: this.onFocus,
					onKeyDown: this.props.onKeyDown,
					onKeyPress: this.props.onKeyPress,
					onKeyUp: this.props.onKeyUp,
					pattern: this.props.pattern,
					placeholder: this.props.placeholder,
					type: this.getInputType(),
					required: this.props.required,
					role: this.props.role,
					value: this.props.value,
					min: this.props.min,
					max: this.props.max,
					step: this.props.step,
					rows: this.props.type === p.textarea ? this.props.rows : null
				}, s, g)), this.renderClear(), this.renderMaskToggle(), /* @__PURE__ */ h.createElement(x, W({}, s, S)));
			}
		}
	]), n;
}(h.Component);
Z($, "defaultProps", {
	"aria-activedescendant": null,
	"aria-autocomplete": null,
	"aria-controls": null,
	"aria-errormessage": null,
	"aria-haspopup": null,
	"aria-label": null,
	"aria-labelledby": null,
	"aria-describedby": null,
	adjoined: d.none,
	autoComplete: "on",
	autoFocus: !1,
	disabled: !1,
	error: !1,
	positive: !1,
	name: "",
	inputMode: "text",
	onBlur: function() {},
	onChange: function() {},
	onKeyDown: function() {},
	onKeyPress: function() {},
	onKeyUp: function() {},
	onFocus: function() {},
	onClear: function() {},
	clearable: !1,
	clearOnEscape: !0,
	overrides: {},
	pattern: null,
	placeholder: "",
	required: !1,
	role: null,
	size: m.default,
	type: "text",
	readOnly: !1
});
//#endregion
export { H as a, R as c, D as i, z as n, I as o, V as r, $ as s, F as t };

//# sourceMappingURL=base-input-Drzzu2Q6-DCOO1-b4.js.map