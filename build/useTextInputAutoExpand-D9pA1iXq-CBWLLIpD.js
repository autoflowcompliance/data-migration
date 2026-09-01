import { $i as e, Ka as t, Ua as n, fi as r, ma as i, tr as a } from "./index-Dl4ETd_L-D2oMd1k2.js";
import { r as o, t as s } from "./constants-yZa2TGaZ-D7s59a3V.js";
import { n as c, r as l, s as u, t as d } from "./base-input-Drzzu2Q6-DCOO1-b4.js";
//#region ../react/build/useTextInputAutoExpand-D9pA1iXq.js
var f = /* @__PURE__ */ t(n(), 1);
function p(e, t) {
	var n = Object.keys(e);
	if (Object.getOwnPropertySymbols) {
		var r = Object.getOwnPropertySymbols(e);
		t && (r = r.filter(function(t) {
			return Object.getOwnPropertyDescriptor(e, t).enumerable;
		})), n.push.apply(n, r);
	}
	return n;
}
function m(e) {
	for (var t = 1; t < arguments.length; t++) {
		var n = arguments[t] == null ? {} : arguments[t];
		t % 2 ? p(Object(n), !0).forEach(function(t) {
			h(e, t, n[t]);
		}) : Object.getOwnPropertyDescriptors ? Object.defineProperties(e, Object.getOwnPropertyDescriptors(n)) : p(Object(n)).forEach(function(t) {
			Object.defineProperty(e, t, Object.getOwnPropertyDescriptor(n, t));
		});
	}
	return e;
}
function h(e, t, n) {
	return t in e ? Object.defineProperty(e, t, {
		value: n,
		enumerable: !0,
		configurable: !0,
		writable: !0
	}) : e[t] = n, e;
}
var g = e("div", function(e) {
	return m(m({}, d(m(m({ $positive: !1 }, e), {}, { $hasIconTrailing: !1 }))), {}, { width: e.$resize ? "fit-content" : "100%" });
});
g.displayName = "StyledTextAreaRoot", g.displayName = "StyledTextAreaRoot";
var _ = e("div", function(e) {
	return c(m({ $positive: !1 }, e));
});
_.displayName = "StyledTextareaContainer", _.displayName = "StyledTextareaContainer";
var v = e("textarea", function(e) {
	return m(m({}, l(e)), {}, { resize: e.$resize || "none" });
});
v.displayName = "StyledTextarea", v.displayName = "StyledTextarea";
function y(e) {
	"@babel/helpers - typeof";
	return y = typeof Symbol == "function" && typeof Symbol.iterator == "symbol" ? function(e) {
		return typeof e;
	} : function(e) {
		return e && typeof Symbol == "function" && e.constructor === Symbol && e !== Symbol.prototype ? "symbol" : typeof e;
	}, y(e);
}
function b() {
	return b = Object.assign ? Object.assign.bind() : function(e) {
		for (var t = 1; t < arguments.length; t++) {
			var n = arguments[t];
			for (var r in n) Object.prototype.hasOwnProperty.call(n, r) && (e[r] = n[r]);
		}
		return e;
	}, b.apply(this, arguments);
}
function x(e, t) {
	return E(e) || T(e, t) || C(e, t) || S();
}
function S() {
	throw TypeError("Invalid attempt to destructure non-iterable instance.\nIn order to be iterable, non-array objects must have a [Symbol.iterator]() method.");
}
function C(e, t) {
	if (e) {
		if (typeof e == "string") return w(e, t);
		var n = Object.prototype.toString.call(e).slice(8, -1);
		if (n === "Object" && e.constructor && (n = e.constructor.name), n === "Map" || n === "Set") return Array.from(e);
		if (n === "Arguments" || /^(?:Ui|I)nt(?:8|16|32)(?:Clamped)?Array$/.test(n)) return w(e, t);
	}
}
function w(e, t) {
	(t == null || t > e.length) && (t = e.length);
	for (var n = 0, r = Array(t); n < t; n++) r[n] = e[n];
	return r;
}
function T(e, t) {
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
function D(e, t) {
	if (!(e instanceof t)) throw TypeError("Cannot call a class as a function");
}
function O(e, t) {
	for (var n = 0; n < t.length; n++) {
		var r = t[n];
		r.enumerable = r.enumerable || !1, r.configurable = !0, "value" in r && (r.writable = !0), Object.defineProperty(e, r.key, r);
	}
}
function k(e, t, n) {
	return t && O(e.prototype, t), Object.defineProperty(e, "prototype", { writable: !1 }), e;
}
function A(e, t) {
	if (typeof t != "function" && t !== null) throw TypeError("Super expression must either be null or a function");
	e.prototype = Object.create(t && t.prototype, { constructor: {
		value: e,
		writable: !0,
		configurable: !0
	} }), Object.defineProperty(e, "prototype", { writable: !1 }), t && j(e, t);
}
function j(e, t) {
	return j = Object.setPrototypeOf ? Object.setPrototypeOf.bind() : function(e, t) {
		return e.__proto__ = t, e;
	}, j(e, t);
}
function M(e) {
	var t = F();
	return function() {
		var n = I(e), r;
		if (t) {
			var i = I(this).constructor;
			r = Reflect.construct(n, arguments, i);
		} else r = n.apply(this, arguments);
		return N(this, r);
	};
}
function N(e, t) {
	if (t && (y(t) === "object" || typeof t == "function")) return t;
	if (t !== void 0) throw TypeError("Derived constructors may only return object or undefined");
	return P(e);
}
function P(e) {
	if (e === void 0) throw ReferenceError("this hasn't been initialised - super() hasn't been called");
	return e;
}
function F() {
	if (typeof Reflect > "u" || !Reflect.construct || Reflect.construct.sham) return !1;
	if (typeof Proxy == "function") return !0;
	try {
		return Boolean.prototype.valueOf.call(Reflect.construct(Boolean, [], function() {})), !0;
	} catch {
		return !1;
	}
}
function I(e) {
	return I = Object.setPrototypeOf ? Object.getPrototypeOf.bind() : function(e) {
		return e.__proto__ || Object.getPrototypeOf(e);
	}, I(e);
}
function L(e, t, n) {
	return t in e ? Object.defineProperty(e, t, {
		value: n,
		enumerable: !0,
		configurable: !0,
		writable: !0
	}) : e[t] = n, e;
}
var R = /* @__PURE__ */ function(e) {
	A(n, e);
	var t = M(n);
	function n() {
		var e;
		D(this, n);
		var r = [...arguments];
		return e = t.call.apply(t, [this].concat(r)), L(P(e), "state", { isFocused: e.props.autoFocus || !1 }), L(P(e), "onFocus", function(t) {
			e.setState({ isFocused: !0 }), e.props.onFocus(t);
		}), L(P(e), "onBlur", function(t) {
			e.setState({ isFocused: !1 }), e.props.onBlur(t);
		}), e;
	}
	return k(n, [{
		key: "render",
		value: function() {
			var e = this.props.overrides, t = e === void 0 ? {} : e, n = x(a(t.Root, g), 2), i = n[0], s = n[1], c = r({
				Input: { component: v },
				InputContainer: { component: _ }
			}, t);
			return /* @__PURE__ */ f.createElement(i, b({
				"data-baseweb": "textarea",
				$isFocused: this.state.isFocused,
				$isReadOnly: this.props.readOnly,
				$disabled: this.props.disabled,
				$error: this.props.error,
				$positive: this.props.positive,
				$required: this.props.required,
				$resize: this.props.resize
			}, s), /* @__PURE__ */ f.createElement(u, b({}, this.props, {
				type: o.textarea,
				overrides: c,
				onFocus: this.onFocus,
				onBlur: this.onBlur,
				resize: this.props.resize
			})));
		}
	}]), n;
}(f.Component);
L(R, "defaultProps", {
	autoFocus: !1,
	disabled: !1,
	readOnly: !1,
	error: !1,
	name: "",
	onBlur: function() {},
	onChange: function() {},
	onKeyDown: function() {},
	onKeyPress: function() {},
	onKeyUp: function() {},
	onFocus: function() {},
	overrides: {},
	placeholder: "",
	required: !1,
	rows: 3,
	size: s.default
});
var z = 6.5, B = 1, V = (e) => {
	let t = 0, { current: n } = e;
	return n && (n.style.height = "auto", t = n.scrollHeight, n.style.height = ""), t;
}, H = (e, t, n) => e > 0 && n.current ? Math.abs(e - t) > B : !1, U = (e, t) => {
	if (e.current && t.current) {
		let { offsetHeight: n } = e.current;
		t.current.minHeight = n, t.current.maxHeight = n * z;
	}
}, W = (e, t, n) => e ? `${t + B}px` : n ? String(n) : "", G = (e) => e ? `${e}px` : "", K = ({ textareaRef: e, dependencies: t = [] }) => {
	let n = i(), r = (0, f.useRef)({
		minHeight: 0,
		maxHeight: 0
	}), [a, o] = (0, f.useState)(0), [s, c] = (0, f.useState)(!1), l = (0, f.useCallback)(() => {
		o(V(e));
	}, [e, o]), u = (0, f.useCallback)(() => {
		o(0);
	}, [o]);
	(0, f.useLayoutEffect)(() => {
		e.current && U(e, r);
	}, [e]), (0, f.useLayoutEffect)(() => {
		let { minHeight: t } = r.current;
		c(H(a, t, e));
	}, [a, e]), (0, f.useLayoutEffect)(() => {
		l();
	}, [
		e,
		l,
		...t
	]);
	let { maxHeight: d } = r.current, p = n.sizes.minElementHeight;
	return {
		isExtended: s,
		height: W(s, a, p),
		maxHeight: G(d),
		updateScrollHeight: l,
		clearScrollHeight: u
	};
};
//#endregion
export { K as n, R as t };

//# sourceMappingURL=useTextInputAutoExpand-D9pA1iXq-CBWLLIpD.js.map