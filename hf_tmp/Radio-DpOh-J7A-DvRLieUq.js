import { $i as e, Cn as t, J as n, Ka as r, Ua as i, Ur as a, Yt as o, dt as s, ii as c, jr as l, ma as u, ti as d, tr as f } from "./index-Dl4ETd_L-D2oMd1k2.js";
import { t as p } from "./WidgetLabel-CQfHGtry-udktvHE5.js";
import { t as m } from "./WidgetLabelHelpIconInline-BTmzKeRa-CZ4j9Xyg.js";
import { n as h } from "./useBasicWidgetState-D3zHnRUK-Dsaz4YO6.js";
//#region ../react/build/Radio-DpOh-J7A.js
var g = /* @__PURE__ */ r(i(), 1), _ = {
	vertical: "vertical",
	horizontal: "horizontal"
};
function v(e, t) {
	var n = Object.keys(e);
	if (Object.getOwnPropertySymbols) {
		var r = Object.getOwnPropertySymbols(e);
		t && (r = r.filter(function(t) {
			return Object.getOwnPropertyDescriptor(e, t).enumerable;
		})), n.push.apply(n, r);
	}
	return n;
}
function y(e) {
	for (var t = 1; t < arguments.length; t++) {
		var n = arguments[t] == null ? {} : arguments[t];
		t % 2 ? v(Object(n), !0).forEach(function(t) {
			b(e, t, n[t]);
		}) : Object.getOwnPropertyDescriptors ? Object.defineProperties(e, Object.getOwnPropertyDescriptors(n)) : v(Object(n)).forEach(function(t) {
			Object.defineProperty(e, t, Object.getOwnPropertyDescriptor(n, t));
		});
	}
	return e;
}
function b(e, t, n) {
	return t in e ? Object.defineProperty(e, t, {
		value: n,
		enumerable: !0,
		configurable: !0,
		writable: !0
	}) : e[t] = n, e;
}
var x = 0, S = 1, C = 2;
function w(e) {
	return e.$isActive ? C : e.$isHovered ? S : x;
}
function T(e) {
	var t = e.$theme.colors, n = e.$disabled, r = e.$checked, i = e.$isFocusVisible, a = e.$error;
	if (n) return t.tickFillDisabled;
	if (r) if (a) switch (w(e)) {
		case x: return t.tickFillErrorSelected;
		case S: return t.tickFillErrorSelectedHover;
		case C: return t.tickFillErrorSelectedHoverActive;
	}
	else switch (w(e)) {
		case x: return t.tickFillSelected;
		case S: return t.tickFillSelectedHover;
		case C: return t.tickFillSelectedHoverActive;
	}
	else return i ? t.borderSelected : a ? t.tickBorderError : t.tickBorder;
	return null;
}
function E(e) {
	var t = e.$theme.colors;
	if (e.$disabled) return t.tickMarkFillDisabled;
	if (e.$checked) return t.tickMarkFill;
	if (e.$error) switch (w(e)) {
		case x: return t.tickFillError;
		case S: return t.tickFillErrorHover;
		case C: return t.tickFillErrorHoverActive;
	}
	else switch (w(e)) {
		case x: return t.tickFill;
		case S: return t.tickFillHover;
		case C: return t.tickFillActive;
	}
}
function D(e) {
	var t = e.$labelPlacement, n = t === void 0 ? "" : t, r = e.$theme, i;
	switch (n) {
		case "top":
			i = "Bottom";
			break;
		case "bottom":
			i = "Top";
			break;
		case "left":
			i = r.direction === "rtl" ? "Left" : "Right";
			break;
		default:
		case "right":
			i = r.direction === "rtl" ? "Right" : "Left";
			break;
	}
	var a = r.sizing.scale300;
	return b({}, `padding${i}`, a);
}
function ee(e) {
	var t = e.$disabled, n = e.$theme.colors;
	return t ? n.contentSecondary : n.contentPrimary;
}
var O = e("div", function(e) {
	var t = e.$disabled, n = e.$align;
	return {
		display: "flex",
		flexWrap: "wrap",
		flexDirection: n === "horizontal" ? "row" : "column",
		alignItems: n === "horizontal" ? "center" : "flex-start",
		cursor: t ? "not-allowed" : "pointer",
		"-webkit-tap-highlight-color": "transparent"
	};
});
O.displayName = "RadioGroupRoot", O.displayName = "RadioGroupRoot";
var k = e("label", function(e) {
	var t, n = e.$disabled, r = e.$hasDescription, i = e.$labelPlacement, a = e.$theme, o = e.$align, s = a.sizing, c = o === "horizontal", l = a.direction === "rtl" ? "Left" : "Right";
	return t = {
		flexDirection: i === "top" || i === "bottom" ? "column" : "row",
		display: "flex",
		alignItems: "center",
		cursor: n ? "not-allowed" : "pointer",
		marginTop: s.scale200
	}, b(t, `margin${l}`, c ? s.scale200 : null), b(t, "marginBottom", r && !c ? null : s.scale200), t;
});
k.displayName = "Root", k.displayName = "Root";
var A = e("div", function(e) {
	var t = e.$theme, n = t.animation, r = t.sizing;
	return {
		backgroundColor: E(e),
		borderTopLeftRadius: "50%",
		borderTopRightRadius: "50%",
		borderBottomRightRadius: "50%",
		borderBottomLeftRadius: "50%",
		height: e.$checked ? r.scale200 : r.scale550,
		transitionDuration: n.timing200,
		transitionTimingFunction: n.easeOutCurve,
		width: e.$checked ? r.scale200 : r.scale550
	};
});
A.displayName = "RadioMarkInner", A.displayName = "RadioMarkInner";
var j = e("div", function(e) {
	var t = e.$theme, n = t.animation, r = t.sizing;
	return {
		alignItems: "center",
		backgroundColor: T(e),
		borderTopLeftRadius: "50%",
		borderTopRightRadius: "50%",
		borderBottomRightRadius: "50%",
		borderBottomLeftRadius: "50%",
		boxShadow: e.$isFocusVisible && e.$checked ? `0 0 0 3px ${e.$theme.colors.accent}` : "none",
		display: "flex",
		height: r.scale700,
		justifyContent: "center",
		marginTop: r.scale0,
		marginRight: r.scale0,
		marginBottom: r.scale0,
		marginLeft: r.scale0,
		outline: "none",
		verticalAlign: "middle",
		width: r.scale700,
		flexShrink: 0,
		transitionDuration: n.timing200,
		transitionTimingFunction: n.easeOutCurve
	};
});
j.displayName = "RadioMarkOuter", j.displayName = "RadioMarkOuter";
var M = e("div", function(e) {
	var t = e.$theme.typography;
	return y(y({ verticalAlign: "middle" }, D(e)), {}, { color: ee(e) }, t.LabelMedium);
});
M.displayName = "Label", M.displayName = "Label";
var N = e("input", {
	width: 0,
	height: 0,
	marginTop: 0,
	marginRight: 0,
	marginBottom: 0,
	marginLeft: 0,
	paddingTop: 0,
	paddingRight: 0,
	paddingBottom: 0,
	paddingLeft: 0,
	clip: "rect(0 0 0 0)",
	position: "absolute"
});
N.displayName = "Input", N.displayName = "Input";
var P = e("div", function(e) {
	var t, n = e.$theme, r = e.$align, i = r === "horizontal", a = n.direction === "rtl" ? "Right" : "Left", o = n.direction === "rtl" ? "Left" : "Right";
	return y(y({}, n.typography.ParagraphSmall), {}, (t = {
		color: n.colors.contentSecondary,
		cursor: "auto"
	}, b(t, `margin${a}`, r === "horizontal" ? null : n.sizing.scale900), b(t, `margin${o}`, i ? n.sizing.scale200 : null), b(t, "maxWidth", "240px"), t));
});
P.displayName = "Description", P.displayName = "Description";
function F(e) {
	"@babel/helpers - typeof";
	return F = typeof Symbol == "function" && typeof Symbol.iterator == "symbol" ? function(e) {
		return typeof e;
	} : function(e) {
		return e && typeof Symbol == "function" && e.constructor === Symbol && e !== Symbol.prototype ? "symbol" : typeof e;
	}, F(e);
}
function I() {
	return I = Object.assign ? Object.assign.bind() : function(e) {
		for (var t = 1; t < arguments.length; t++) {
			var n = arguments[t];
			for (var r in n) Object.prototype.hasOwnProperty.call(n, r) && (e[r] = n[r]);
		}
		return e;
	}, I.apply(this, arguments);
}
function te(e, t) {
	return ie(e) || R(e, t) || re(e, t) || ne();
}
function ne() {
	throw TypeError("Invalid attempt to destructure non-iterable instance.\nIn order to be iterable, non-array objects must have a [Symbol.iterator]() method.");
}
function re(e, t) {
	if (e) {
		if (typeof e == "string") return L(e, t);
		var n = Object.prototype.toString.call(e).slice(8, -1);
		if (n === "Object" && e.constructor && (n = e.constructor.name), n === "Map" || n === "Set") return Array.from(e);
		if (n === "Arguments" || /^(?:Ui|I)nt(?:8|16|32)(?:Clamped)?Array$/.test(n)) return L(e, t);
	}
}
function L(e, t) {
	(t == null || t > e.length) && (t = e.length);
	for (var n = 0, r = Array(t); n < t; n++) r[n] = e[n];
	return r;
}
function R(e, t) {
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
function ie(e) {
	if (Array.isArray(e)) return e;
}
function ae(e, t) {
	if (!(e instanceof t)) throw TypeError("Cannot call a class as a function");
}
function oe(e, t) {
	for (var n = 0; n < t.length; n++) {
		var r = t[n];
		r.enumerable = r.enumerable || !1, r.configurable = !0, "value" in r && (r.writable = !0), Object.defineProperty(e, r.key, r);
	}
}
function se(e, t, n) {
	return t && oe(e.prototype, t), Object.defineProperty(e, "prototype", { writable: !1 }), e;
}
function ce(e, t) {
	if (typeof t != "function" && t !== null) throw TypeError("Super expression must either be null or a function");
	e.prototype = Object.create(t && t.prototype, { constructor: {
		value: e,
		writable: !0,
		configurable: !0
	} }), Object.defineProperty(e, "prototype", { writable: !1 }), t && z(e, t);
}
function z(e, t) {
	return z = Object.setPrototypeOf ? Object.setPrototypeOf.bind() : function(e, t) {
		return e.__proto__ = t, e;
	}, z(e, t);
}
function le(e) {
	var t = de();
	return function() {
		var n = V(e), r;
		if (t) {
			var i = V(this).constructor;
			r = Reflect.construct(n, arguments, i);
		} else r = n.apply(this, arguments);
		return ue(this, r);
	};
}
function ue(e, t) {
	if (t && (F(t) === "object" || typeof t == "function")) return t;
	if (t !== void 0) throw TypeError("Derived constructors may only return object or undefined");
	return B(e);
}
function B(e) {
	if (e === void 0) throw ReferenceError("this hasn't been initialised - super() hasn't been called");
	return e;
}
function de() {
	if (typeof Reflect > "u" || !Reflect.construct || Reflect.construct.sham) return !1;
	if (typeof Proxy == "function") return !0;
	try {
		return Boolean.prototype.valueOf.call(Reflect.construct(Boolean, [], function() {})), !0;
	} catch {
		return !1;
	}
}
function V(e) {
	return V = Object.setPrototypeOf ? Object.getPrototypeOf.bind() : function(e) {
		return e.__proto__ || Object.getPrototypeOf(e);
	}, V(e);
}
function H(e, t, n) {
	return t in e ? Object.defineProperty(e, t, {
		value: n,
		enumerable: !0,
		configurable: !0,
		writable: !0
	}) : e[t] = n, e;
}
var U = /* @__PURE__ */ function(e) {
	ce(n, e);
	var t = le(n);
	function n() {
		var e;
		ae(this, n);
		var r = [...arguments];
		return e = t.call.apply(t, [this].concat(r)), H(B(e), "state", {
			isFocusVisible: !1,
			focusedRadioIndex: -1
		}), H(B(e), "handleFocus", function(t, n) {
			l(t) && e.setState({ isFocusVisible: !0 }), e.setState({ focusedRadioIndex: n }), e.props.onFocus && e.props.onFocus(t);
		}), H(B(e), "handleBlur", function(t, n) {
			e.state.isFocusVisible !== !1 && e.setState({ isFocusVisible: !1 }), e.setState({ focusedRadioIndex: -1 }), e.props.onBlur && e.props.onBlur(t);
		}), e;
	}
	return se(n, [{
		key: "render",
		value: function() {
			var e = this, t = this.props.overrides, n = te(f((t === void 0 ? {} : t).RadioGroupRoot, O), 2), r = n[0], i = n[1];
			return /* @__PURE__ */ g.createElement(r, I({
				id: this.props.id,
				role: "radiogroup",
				"aria-describedby": this.props["aria-describedby"],
				"aria-errormessage": this.props["aria-errormessage"],
				"aria-invalid": this.props.error || null,
				"aria-label": this.props["aria-label"],
				"aria-labelledby": this.props["aria-labelledby"],
				$align: this.props.align,
				$disabled: this.props.disabled,
				$error: this.props.error,
				$required: this.props.required
			}, i), g.Children.map(this.props.children, function(t, n) {
				if (!/* @__PURE__ */ g.isValidElement(t)) return null;
				var r = e.props.value === t.props.value;
				return /* @__PURE__ */ g.cloneElement(t, {
					align: e.props.align,
					autoFocus: e.props.autoFocus,
					checked: r,
					disabled: e.props.disabled || t.props.disabled,
					error: e.props.error,
					isFocused: e.state.focusedRadioIndex === n,
					isFocusVisible: e.state.isFocusVisible,
					tabIndex: n === 0 && !e.props.value || r ? "0" : "-1",
					labelPlacement: e.props.labelPlacement,
					name: e.props.name,
					onBlur: function(t) {
						return e.handleBlur(t, n);
					},
					onFocus: function(t) {
						return e.handleFocus(t, n);
					},
					onChange: e.props.onChange,
					onMouseEnter: e.props.onMouseEnter,
					onMouseLeave: e.props.onMouseLeave
				});
			}));
		}
	}]), n;
}(g.Component);
H(U, "defaultProps", {
	name: "",
	value: "",
	disabled: !1,
	autoFocus: !1,
	labelPlacement: "right",
	align: "vertical",
	error: !1,
	required: !1,
	onChange: function() {},
	onMouseEnter: function() {},
	onMouseLeave: function() {},
	onFocus: function() {},
	onBlur: function() {},
	overrides: {}
});
function W(e) {
	"@babel/helpers - typeof";
	return W = typeof Symbol == "function" && typeof Symbol.iterator == "symbol" ? function(e) {
		return typeof e;
	} : function(e) {
		return e && typeof Symbol == "function" && e.constructor === Symbol && e !== Symbol.prototype ? "symbol" : typeof e;
	}, W(e);
}
function G() {
	return G = Object.assign ? Object.assign.bind() : function(e) {
		for (var t = 1; t < arguments.length; t++) {
			var n = arguments[t];
			for (var r in n) Object.prototype.hasOwnProperty.call(n, r) && (e[r] = n[r]);
		}
		return e;
	}, G.apply(this, arguments);
}
function K(e, t) {
	return he(e) || me(e, t) || pe(e, t) || fe();
}
function fe() {
	throw TypeError("Invalid attempt to destructure non-iterable instance.\nIn order to be iterable, non-array objects must have a [Symbol.iterator]() method.");
}
function pe(e, t) {
	if (e) {
		if (typeof e == "string") return q(e, t);
		var n = Object.prototype.toString.call(e).slice(8, -1);
		if (n === "Object" && e.constructor && (n = e.constructor.name), n === "Map" || n === "Set") return Array.from(e);
		if (n === "Arguments" || /^(?:Ui|I)nt(?:8|16|32)(?:Clamped)?Array$/.test(n)) return q(e, t);
	}
}
function q(e, t) {
	(t == null || t > e.length) && (t = e.length);
	for (var n = 0, r = Array(t); n < t; n++) r[n] = e[n];
	return r;
}
function me(e, t) {
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
function he(e) {
	if (Array.isArray(e)) return e;
}
function ge(e, t) {
	if (!(e instanceof t)) throw TypeError("Cannot call a class as a function");
}
function _e(e, t) {
	for (var n = 0; n < t.length; n++) {
		var r = t[n];
		r.enumerable = r.enumerable || !1, r.configurable = !0, "value" in r && (r.writable = !0), Object.defineProperty(e, r.key, r);
	}
}
function ve(e, t, n) {
	return t && _e(e.prototype, t), Object.defineProperty(e, "prototype", { writable: !1 }), e;
}
function ye(e, t) {
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
function be(e) {
	var t = Se();
	return function() {
		var n = X(e), r;
		if (t) {
			var i = X(this).constructor;
			r = Reflect.construct(n, arguments, i);
		} else r = n.apply(this, arguments);
		return xe(this, r);
	};
}
function xe(e, t) {
	if (t && (W(t) === "object" || typeof t == "function")) return t;
	if (t !== void 0) throw TypeError("Derived constructors may only return object or undefined");
	return Y(e);
}
function Y(e) {
	if (e === void 0) throw ReferenceError("this hasn't been initialised - super() hasn't been called");
	return e;
}
function Se() {
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
function Ce(e) {
	return e === "top" || e === "left";
}
function we(e) {
	return e === "bottom" || e === "right";
}
var Te = function(e) {
	return e.stopPropagation();
}, Q = /* @__PURE__ */ function(e) {
	ye(n, e);
	var t = be(n);
	function n() {
		var e;
		ge(this, n);
		var r = [...arguments];
		return e = t.call.apply(t, [this].concat(r)), Z(Y(e), "state", {
			isActive: !1,
			isHovered: !1
		}), Z(Y(e), "onMouseEnter", function(t) {
			e.setState({ isHovered: !0 }), e.props.onMouseEnter && e.props.onMouseEnter(t);
		}), Z(Y(e), "onMouseLeave", function(t) {
			e.setState({ isHovered: !1 }), e.props.onMouseLeave && e.props.onMouseLeave(t);
		}), Z(Y(e), "onMouseDown", function(t) {
			e.setState({ isActive: !0 }), e.props.onMouseDown && e.props.onMouseDown(t);
		}), Z(Y(e), "onMouseUp", function(t) {
			e.setState({ isActive: !1 }), e.props.onMouseUp && e.props.onMouseUp(t);
		}), e;
	}
	return ve(n, [{
		key: "componentDidMount",
		value: function() {
			var e;
			this.props.autoFocus && (e = this.props.inputRef) != null && e.current && this.props.inputRef.current.focus();
		}
	}, {
		key: "render",
		value: function() {
			var e = this.props.overrides, t = e === void 0 ? {} : e, n = K(f(t.Root, k), 2), r = n[0], i = n[1], a = K(f(t.Label, M), 2), o = a[0], s = a[1], c = K(f(t.Input, N), 2), l = c[0], u = c[1], d = K(f(t.Description, P), 2), p = d[0], m = d[1], h = K(f(t.RadioMarkInner, A), 2), _ = h[0], v = h[1], y = K(f(t.RadioMarkOuter, j), 2), b = y[0], x = y[1], S = {
				$align: this.props.align,
				$checked: this.props.checked,
				$disabled: this.props.disabled,
				$hasDescription: !!this.props.description,
				$isActive: this.state.isActive,
				$error: this.props.error,
				$isFocused: this.props.isFocused,
				$isFocusVisible: this.props.isFocused && this.props.isFocusVisible,
				$isHovered: this.state.isHovered,
				$labelPlacement: this.props.labelPlacement,
				$required: this.props.required,
				$value: this.props.value
			}, C = /* @__PURE__ */ g.createElement(o, G({}, S, s), this.props.containsInteractiveElement ? /* @__PURE__ */ g.createElement("div", { onClick: function(e) {
				return e.preventDefault();
			} }, this.props.children) : this.props.children);
			return /* @__PURE__ */ g.createElement(g.Fragment, null, /* @__PURE__ */ g.createElement(r, G({
				"data-baseweb": "radio",
				onMouseEnter: this.onMouseEnter,
				onMouseLeave: this.onMouseLeave,
				onMouseDown: this.onMouseDown,
				onMouseUp: this.onMouseUp
			}, S, i), Ce(this.props.labelPlacement) && C, /* @__PURE__ */ g.createElement(b, G({}, S, x), /* @__PURE__ */ g.createElement(_, G({}, S, v))), /* @__PURE__ */ g.createElement(l, G({
				"aria-invalid": this.props.error || null,
				checked: this.props.checked,
				disabled: this.props.disabled,
				name: this.props.name,
				onBlur: this.props.onBlur,
				onFocus: this.props.onFocus,
				onClick: Te,
				onChange: this.props.onChange,
				ref: this.props.inputRef,
				required: this.props.required,
				tabIndex: this.props.tabIndex,
				type: "radio",
				value: this.props.value
			}, S, u)), we(this.props.labelPlacement) && C), !!this.props.description && /* @__PURE__ */ g.createElement(p, G({}, S, m), this.props.description));
		}
	}]), n;
}(g.Component);
Z(Q, "defaultProps", {
	overrides: {},
	containsInteractiveElement: !1,
	checked: !1,
	disabled: !1,
	autoFocus: !1,
	inputRef: /* @__PURE__ */ g.createRef(),
	align: "vertical",
	error: !1,
	onChange: function() {},
	onMouseEnter: function() {},
	onMouseLeave: function() {},
	onMouseDown: function() {},
	onMouseUp: function() {},
	onFocus: function() {},
	onBlur: function() {}
});
function Ee(e) {
	let n = parseFloat(e.sizes.checkbox), r = parseFloat(e.spacing.threeXS), i = t(n.toString()), a = Math.round(i * .375), s = Math.round(t((n - r).toString()));
	return s >= i && --s, [o(a, "px"), o(s, "px")];
}
function $({ disabled: e, horizontal: t, value: r, onChange: i, options: a, captions: o, label: c, labelVisibility: l, help: f }) {
	let [h, v] = (0, g.useState)(r ?? null);
	(0, g.useEffect)(() => {
		r !== h && v(r ?? null);
	}, [r]);
	let y = (0, g.useCallback)((e) => {
		let t = parseInt(e.target.value, 10);
		v(t), i(t);
	}, [i]), b = u(), x = o.length > 0, S = a.length > 0, C = S ? a : ["No options to select."], w = e || !S, T = (e) => e == "" && t && x ? "&nbsp;" : e, [E, D] = Ee(b);
	return /* @__PURE__ */ d.jsxs("div", {
		className: "stRadio",
		"data-testid": "stRadio",
		children: [/* @__PURE__ */ d.jsx(p, {
			label: c,
			disabled: w,
			labelVisibility: l,
			children: f && /* @__PURE__ */ d.jsx(m, {
				content: f,
				placement: n.TOP_RIGHT,
				label: c
			})
		}), /* @__PURE__ */ d.jsx(U, {
			onChange: y,
			value: h === null ? void 0 : h.toString(),
			disabled: w,
			align: t ? _.horizontal : _.vertical,
			"aria-label": c,
			"data-testid": "stRadioGroup",
			overrides: { RadioGroupRoot: { style: {
				gap: x ? b.spacing.sm : b.spacing.none,
				minHeight: b.sizes.minElementHeight
			} } },
			children: C.map((e, t) => /* @__PURE__ */ d.jsxs(Q, {
				value: t.toString(),
				overrides: {
					Root: { style: ({ $isFocusVisible: e }) => ({
						marginBottom: b.spacing.none,
						marginTop: b.spacing.none,
						marginRight: x ? b.spacing.sm : b.spacing.lg,
						paddingLeft: b.spacing.none,
						alignItems: "start",
						paddingRight: b.spacing.threeXS,
						backgroundColor: e ? b.colors.darkenedBgMix25 : ""
					}) },
					RadioMarkOuter: { style: ({ $checked: e }) => ({
						width: b.sizes.checkbox,
						height: b.sizes.checkbox,
						marginTop: "0.35rem",
						marginRight: b.spacing.none,
						marginLeft: b.spacing.none,
						backgroundColor: e && !w ? b.colors.primary : b.colors.borderColor
					}) },
					RadioMarkInner: { style: ({ $checked: e }) => ({
						height: e ? E : D,
						width: e ? E : D
					}) },
					Label: { style: {
						color: w ? b.colors.fadedText40 : b.colors.bodyText,
						position: "relative",
						top: b.spacing.px
					} }
				},
				children: [/* @__PURE__ */ d.jsx(s, {
					source: e,
					allowHTML: !1,
					isLabel: !0,
					largerLabel: !0
				}), x && /* @__PURE__ */ d.jsx(s, {
					source: T(o[t]),
					allowHTML: !1,
					isCaption: !0,
					isLabel: !0
				})]
			}, t))
		})]
	});
}
var De = (0, g.memo)($);
function Oe({ disabled: e, element: t, widgetMgr: n, fragmentId: r }) {
	let [i, o] = h({
		getStateFromWidgetMgr: ke,
		getDefaultStateFromProto: Ae,
		getCurrStateFromProto: je,
		updateWidgetMgrState: Me,
		element: t,
		widgetMgr: n,
		fragmentId: r,
		formClearBehavior: "resetValueOnly",
		queryParamBinding: t.queryParamKey ? {
			paramKey: t.queryParamKey,
			valueType: "string_value",
			clearable: a(t.default)
		} : void 0
	}), { horizontal: s, options: l, captions: u, label: f, labelVisibility: p, help: m } = t, _ = (0, g.useCallback)((e) => {
		o({
			value: l[e] ?? null,
			fromUi: !0
		});
	}, [o, l]), v = (0, g.useMemo)(() => {
		if (i === null) return null;
		let e = l.lastIndexOf(i);
		return e >= 0 ? e : null;
	}, [i, l]);
	return /* @__PURE__ */ d.jsx(De, {
		label: f,
		onChange: _,
		options: l,
		captions: u,
		disabled: e,
		horizontal: s,
		labelVisibility: c(p?.value),
		value: v,
		help: m
	});
}
function ke(e, t) {
	return e.getStringValue(t);
}
function Ae(e) {
	return e.options.length === 0 || a(e.default) ? null : e.options[e.default];
}
function je(e) {
	return e.rawValue ?? null;
}
function Me(e, t, n, r) {
	t.setStringValue(e, n.value, { fromUi: n.fromUi }, r);
}
var Ne = (0, g.memo)(Oe);
//#endregion
export { Ne as default };

//# sourceMappingURL=Radio-DpOh-J7A-DvRLieUq.js.map