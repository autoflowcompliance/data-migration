import { $i as e, $n as t, Ka as n, Ua as r, er as i, jr as a } from "./index-Dl4ETd_L-D2oMd1k2.js";
//#region ../react/build/checkbox-BlFkpHIT.js
var o = /* @__PURE__ */ n(r(), 1), s = Object.freeze({
	default: "default",
	toggle: "toggle",
	toggle_round: "toggle"
}), c = Object.freeze({
	top: "top",
	right: "right",
	bottom: "bottom",
	left: "left"
});
function l(e, t) {
	var n = Object.keys(e);
	if (Object.getOwnPropertySymbols) {
		var r = Object.getOwnPropertySymbols(e);
		t && (r = r.filter(function(t) {
			return Object.getOwnPropertyDescriptor(e, t).enumerable;
		})), n.push.apply(n, r);
	}
	return n;
}
function u(e) {
	for (var t = 1; t < arguments.length; t++) {
		var n = arguments[t] == null ? {} : arguments[t];
		t % 2 ? l(Object(n), !0).forEach(function(t) {
			d(e, t, n[t]);
		}) : Object.getOwnPropertyDescriptors ? Object.defineProperties(e, Object.getOwnPropertyDescriptors(n)) : l(Object(n)).forEach(function(t) {
			Object.defineProperty(e, t, Object.getOwnPropertyDescriptor(n, t));
		});
	}
	return e;
}
function d(e, t, n) {
	return t in e ? Object.defineProperty(e, t, {
		value: n,
		enumerable: !0,
		configurable: !0,
		writable: !0
	}) : e[t] = n, e;
}
function f(e) {
	var t = e.$disabled, n = e.$checked, r = e.$error, i = e.$isIndeterminate, a = e.$theme, o = e.$isFocusVisible, s = a.colors;
	return t ? s.tickFillDisabled : n || i ? "transparent" : r ? s.borderNegative : o ? s.borderSelected : s.tickBorder;
}
function p(e) {
	var t = e.$labelPlacement, n = t === void 0 ? "" : t, r = e.$theme, i = r.sizing.scale300, a;
	switch (n) {
		case "top":
			a = "Bottom";
			break;
		case "bottom":
			a = "Top";
			break;
		case "left":
			a = "Right";
			break;
		default:
		case "right":
			a = "Left";
			break;
	}
	return r.direction === "rtl" && a === "Left" ? a = "Right" : r.direction === "rtl" && a === "Right" && (a = "Left"), d({}, `padding${a}`, i);
}
function m(e) {
	var t = e.$disabled, n = e.$checked, r = e.$isIndeterminate, i = e.$error, a = e.$isHovered, o = e.$isActive, s = e.$theme.colors;
	return t ? n || r ? s.tickFillDisabled : s.tickFill : i && (r || n) ? o ? s.tickFillErrorSelectedHoverActive : a ? s.tickFillErrorSelectedHover : s.tickFillErrorSelected : i ? o ? s.tickFillErrorHoverActive : a ? s.tickFillErrorHover : s.tickFillError : r || n ? o ? s.tickFillSelectedHoverActive : a ? s.tickFillSelectedHover : s.tickFillSelected : o ? s.tickFillActive : a ? s.tickFillHover : s.tickFill;
}
function h(e) {
	var t = e.$disabled, n = e.$theme.colors;
	return t ? n.contentSecondary : n.contentPrimary;
}
var g = e("label", function(e) {
	var t = e.$disabled, n = e.$labelPlacement;
	return {
		flexDirection: n === "top" || n === "bottom" ? "column" : "row",
		display: "flex",
		alignItems: n === "top" || n === "bottom" ? "center" : "flex-start",
		cursor: t ? "not-allowed" : "pointer",
		userSelect: "none"
	};
});
g.displayName = "Root", g.displayName = "Root";
var _ = e("span", function(e) {
	var t = e.$checked, n = e.$disabled, r = e.$error, i = e.$isIndeterminate, a = e.$theme, o = e.$isFocusVisible, s = a.sizing, c = a.animation, l = n ? a.colors.tickMarkFillDisabled : r ? a.colors.tickMarkFillError : a.colors.tickMarkFill, u = encodeURIComponent(`
    <svg width="14" height="4" viewBox="0 0 14 4" fill="none" xmlns="http://www.w3.org/2000/svg">
      <path d="M14 0.5H0V3.5H14V0.5Z" fill="${l}"/>
    </svg>
  `), d = encodeURIComponent(`
    <svg width="17" height="13" viewBox="0 0 17 13" fill="none" xmlns="http://www.w3.org/2000/svg">
      <path d="M6.50002 12.6L0.400024 6.60002L2.60002 4.40002L6.50002 8.40002L13.9 0.900024L16.1 3.10002L6.50002 12.6Z" fill="${l}"/>
    </svg>
  `), p = a.borders.checkboxBorderRadius, h = f(e);
	return {
		flex: "0 0 auto",
		transitionDuration: c.timing200,
		transitionTimingFunction: c.easeOutCurve,
		transitionProperty: "background-image, border-color, background-color",
		width: s.scale700,
		height: s.scale700,
		left: "4px",
		top: "4px",
		boxSizing: "border-box",
		borderLeftStyle: "solid",
		borderRightStyle: "solid",
		borderTopStyle: "solid",
		borderBottomStyle: "solid",
		borderLeftWidth: "3px",
		borderRightWidth: "3px",
		borderTopWidth: "3px",
		borderBottomWidth: "3px",
		borderLeftColor: h,
		borderRightColor: h,
		borderTopColor: h,
		borderBottomColor: h,
		borderTopLeftRadius: p,
		borderTopRightRadius: p,
		borderBottomRightRadius: p,
		borderBottomLeftRadius: p,
		outline: o && t ? `3px solid ${a.colors.accent}` : "none",
		display: "inline-block",
		verticalAlign: "middle",
		backgroundImage: i ? `url('data:image/svg+xml,${u}');` : t ? `url('data:image/svg+xml,${d}');` : null,
		backgroundColor: m(e),
		backgroundRepeat: "no-repeat",
		backgroundPosition: "center",
		backgroundSize: "contain",
		marginTop: a.sizing.scale0,
		marginBottom: a.sizing.scale0,
		marginLeft: a.sizing.scale0,
		marginRight: a.sizing.scale0
	};
});
_.displayName = "Checkmark", _.displayName = "Checkmark";
var v = e("div", function(e) {
	var t = e.$theme.typography;
	return u(u(u({ verticalAlign: "middle" }, p(e)), {}, { color: h(e) }, t.LabelMedium), {}, { lineHeight: "24px" });
});
v.displayName = "Label", v.displayName = "Label";
var y = e("input", {
	opacity: 0,
	width: 0,
	height: 0,
	overflow: "hidden",
	margin: 0,
	padding: 0,
	position: "absolute"
});
y.displayName = "Input", y.displayName = "Input";
var b = e("div", function(e) {
	var t = e.$theme.colors.toggleFill;
	return e.$disabled ? t = e.$theme.colors.toggleFillDisabled : e.$checked && e.$error ? t = e.$theme.colors.tickFillErrorSelected : e.$checked && (t = e.$theme.colors.toggleFillChecked), {
		backgroundColor: t,
		borderTopLeftRadius: "50%",
		borderTopRightRadius: "50%",
		borderBottomRightRadius: "50%",
		borderBottomLeftRadius: "50%",
		boxShadow: e.$isFocusVisible ? `0 0 0 3px ${e.$theme.colors.accent}` : e.$isHovered && !e.$disabled ? e.$theme.lighting.shadow500 : e.$theme.lighting.shadow400,
		outline: "none",
		height: e.$theme.sizing.scale700,
		width: e.$theme.sizing.scale700,
		transform: e.$checked ? `translateX(${e.$theme.direction === "rtl" ? "-100%" : "100%"})` : null,
		transition: `transform ${e.$theme.animation.timing200}`
	};
});
b.displayName = "Toggle", b.displayName = "Toggle";
var x = e("div", function(e) {
	var t = e.$theme.colors.toggleTrackFill;
	return e.$disabled ? t = e.$theme.colors.toggleTrackFillDisabled : e.$error && e.$checked && (t = e.$theme.colors.tickFillError), {
		alignItems: "center",
		backgroundColor: t,
		borderTopLeftRadius: "7px",
		borderTopRightRadius: "7px",
		borderBottomRightRadius: "7px",
		borderBottomLeftRadius: "7px",
		display: "flex",
		height: e.$theme.sizing.scale550,
		marginTop: e.$theme.sizing.scale200,
		marginBottom: e.$theme.sizing.scale100,
		marginLeft: e.$theme.sizing.scale200,
		marginRight: e.$theme.sizing.scale100,
		width: e.$theme.sizing.scale1000
	};
});
x.displayName = "ToggleTrack", x.displayName = "ToggleTrack";
function S(e) {
	"@babel/helpers - typeof";
	return S = typeof Symbol == "function" && typeof Symbol.iterator == "symbol" ? function(e) {
		return typeof e;
	} : function(e) {
		return e && typeof Symbol == "function" && e.constructor === Symbol && e !== Symbol.prototype ? "symbol" : typeof e;
	}, S(e);
}
function C() {
	return C = Object.assign ? Object.assign.bind() : function(e) {
		for (var t = 1; t < arguments.length; t++) {
			var n = arguments[t];
			for (var r in n) Object.prototype.hasOwnProperty.call(n, r) && (e[r] = n[r]);
		}
		return e;
	}, C.apply(this, arguments);
}
function w(e, t) {
	if (!(e instanceof t)) throw TypeError("Cannot call a class as a function");
}
function T(e, t) {
	for (var n = 0; n < t.length; n++) {
		var r = t[n];
		r.enumerable = r.enumerable || !1, r.configurable = !0, "value" in r && (r.writable = !0), Object.defineProperty(e, r.key, r);
	}
}
function E(e, t, n) {
	return t && T(e.prototype, t), Object.defineProperty(e, "prototype", { writable: !1 }), e;
}
function D(e, t) {
	if (typeof t != "function" && t !== null) throw TypeError("Super expression must either be null or a function");
	e.prototype = Object.create(t && t.prototype, { constructor: {
		value: e,
		writable: !0,
		configurable: !0
	} }), Object.defineProperty(e, "prototype", { writable: !1 }), t && O(e, t);
}
function O(e, t) {
	return O = Object.setPrototypeOf ? Object.setPrototypeOf.bind() : function(e, t) {
		return e.__proto__ = t, e;
	}, O(e, t);
}
function k(e) {
	var t = M();
	return function() {
		var n = N(e), r;
		if (t) {
			var i = N(this).constructor;
			r = Reflect.construct(n, arguments, i);
		} else r = n.apply(this, arguments);
		return A(this, r);
	};
}
function A(e, t) {
	if (t && (S(t) === "object" || typeof t == "function")) return t;
	if (t !== void 0) throw TypeError("Derived constructors may only return object or undefined");
	return j(e);
}
function j(e) {
	if (e === void 0) throw ReferenceError("this hasn't been initialised - super() hasn't been called");
	return e;
}
function M() {
	if (typeof Reflect > "u" || !Reflect.construct || Reflect.construct.sham) return !1;
	if (typeof Proxy == "function") return !0;
	try {
		return Boolean.prototype.valueOf.call(Reflect.construct(Boolean, [], function() {})), !0;
	} catch {
		return !1;
	}
}
function N(e) {
	return N = Object.setPrototypeOf ? Object.getPrototypeOf.bind() : function(e) {
		return e.__proto__ || Object.getPrototypeOf(e);
	}, N(e);
}
function P(e, t, n) {
	return t in e ? Object.defineProperty(e, t, {
		value: n,
		enumerable: !0,
		configurable: !0,
		writable: !0
	}) : e[t] = n, e;
}
var F = function(e) {
	return e.stopPropagation();
}, I = /* @__PURE__ */ function(e) {
	D(r, e);
	var n = k(r);
	function r() {
		var e;
		w(this, r);
		var t = [...arguments];
		return e = n.call.apply(n, [this].concat(t)), P(j(e), "state", {
			isFocused: e.props.autoFocus || !1,
			isFocusVisible: !1,
			isHovered: !1,
			isActive: !1
		}), P(j(e), "onMouseEnter", function(t) {
			e.setState({ isHovered: !0 }), e.props.onMouseEnter(t);
		}), P(j(e), "onMouseLeave", function(t) {
			e.setState({
				isHovered: !1,
				isActive: !1
			}), e.props.onMouseLeave(t);
		}), P(j(e), "onMouseDown", function(t) {
			e.setState({ isActive: !0 }), e.props.onMouseDown(t);
		}), P(j(e), "onMouseUp", function(t) {
			e.setState({ isActive: !1 }), e.props.onMouseUp(t);
		}), P(j(e), "onFocus", function(t) {
			e.setState({ isFocused: !0 }), e.props.onFocus(t), a(t) && e.setState({ isFocusVisible: !0 });
		}), P(j(e), "onBlur", function(t) {
			e.setState({ isFocused: !1 }), e.props.onBlur(t), e.state.isFocusVisible !== !1 && e.setState({ isFocusVisible: !1 });
		}), e;
	}
	return E(r, [{
		key: "componentDidMount",
		value: function() {
			var e = this.props, t = e.autoFocus, n = e.inputRef;
			t && n.current && n.current.focus();
		}
	}, {
		key: "render",
		value: function() {
			var e = this.props, n = e.overrides, r = n === void 0 ? {} : n, a = e.onChange, c = e.labelPlacement, l = c === void 0 ? this.props.checkmarkType === s.toggle ? "left" : "right" : c, u = e.inputRef, d = e.isIndeterminate, f = e.error, p = e.disabled, m = e.value, h = e.name, S = e.type, w = e.checked, T = e.children, E = e.required, D = e.title, O = r.Root, k = r.Checkmark, A = r.Label, j = r.Input, M = r.Toggle, N = r.ToggleTrack, P = t(O) || g, I = t(k) || _, L = t(A) || v, R = t(j) || y, z = t(M) || b, B = t(N) || x, V = {
				onChange: a,
				onFocus: this.onFocus,
				onBlur: this.onBlur
			}, H = {
				onMouseEnter: this.onMouseEnter,
				onMouseLeave: this.onMouseLeave,
				onMouseDown: this.onMouseDown,
				onMouseUp: this.onMouseUp
			}, U = {
				$isFocused: this.state.isFocused,
				$isFocusVisible: this.state.isFocusVisible,
				$isHovered: this.state.isHovered,
				$isActive: this.state.isActive,
				$error: f,
				$checked: w,
				$isIndeterminate: d,
				$required: E,
				$disabled: p,
				$value: m
			}, W = T && /* @__PURE__ */ o.createElement(L, C({ $labelPlacement: l }, U, i(A)), this.props.containsInteractiveElement ? /* @__PURE__ */ o.createElement("div", { onClick: function(e) {
				return e.preventDefault();
			} }, T) : T);
			return /* @__PURE__ */ o.createElement(P, C({
				"data-baseweb": "checkbox",
				title: D || null,
				$labelPlacement: l
			}, U, H, i(O)), (l === "top" || l === "left") && W, this.props.checkmarkType === s.toggle ? /* @__PURE__ */ o.createElement(B, C({}, U, i(N)), /* @__PURE__ */ o.createElement(z, C({}, U, i(M)))) : /* @__PURE__ */ o.createElement(I, C({}, U, i(k))), /* @__PURE__ */ o.createElement(R, C({
				value: m,
				name: h,
				checked: w,
				required: E,
				"aria-label": this.props["aria-label"] || this.props.ariaLabel,
				"aria-checked": d ? "mixed" : w,
				"aria-describedby": this.props["aria-describedby"],
				"aria-errormessage": this.props["aria-errormessage"],
				"aria-invalid": f || null,
				"aria-required": E || null,
				disabled: p,
				type: S,
				ref: u,
				onClick: F
			}, U, V, i(j))), (l === "bottom" || l === "right") && W);
		}
	}]), r;
}(o.Component);
P(I, "defaultProps", {
	overrides: {},
	checked: !1,
	containsInteractiveElement: !1,
	disabled: !1,
	autoFocus: !1,
	isIndeterminate: !1,
	inputRef: /* @__PURE__ */ o.createRef(),
	error: !1,
	type: "checkbox",
	checkmarkType: s.default,
	onChange: function() {},
	onMouseEnter: function() {},
	onMouseLeave: function() {},
	onMouseDown: function() {},
	onMouseUp: function() {},
	onFocus: function() {},
	onBlur: function() {}
});
//#endregion
export { I as n, c as r, s as t };

//# sourceMappingURL=checkbox-BlFkpHIT-CZhSzhvC.js.map