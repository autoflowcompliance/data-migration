import { Ka as e, Ua as t, tr as n } from "./index-Dl4ETd_L-D2oMd1k2.js";
import { a as r, n as i, t as a } from "./constants-yZa2TGaZ-D7s59a3V.js";
import { c as o, i as s, o as c, s as l } from "./base-input-Drzzu2Q6-DCOO1-b4.js";
//#region ../react/build/input-CClPhvPt.js
var u = /* @__PURE__ */ e(t(), 1);
function d(e) {
	"@babel/helpers - typeof";
	return d = typeof Symbol == "function" && typeof Symbol.iterator == "symbol" ? function(e) {
		return typeof e;
	} : function(e) {
		return e && typeof Symbol == "function" && e.constructor === Symbol && e !== Symbol.prototype ? "symbol" : typeof e;
	}, d(e);
}
var f = [
	"Root",
	"StartEnhancer",
	"EndEnhancer"
], p = [
	"startEnhancer",
	"endEnhancer",
	"overrides"
];
function m() {
	return m = Object.assign ? Object.assign.bind() : function(e) {
		for (var t = 1; t < arguments.length; t++) {
			var n = arguments[t];
			for (var r in n) Object.prototype.hasOwnProperty.call(n, r) && (e[r] = n[r]);
		}
		return e;
	}, m.apply(this, arguments);
}
function h(e, t) {
	return b(e) || y(e, t) || _(e, t) || g();
}
function g() {
	throw TypeError("Invalid attempt to destructure non-iterable instance.\nIn order to be iterable, non-array objects must have a [Symbol.iterator]() method.");
}
function _(e, t) {
	if (e) {
		if (typeof e == "string") return v(e, t);
		var n = Object.prototype.toString.call(e).slice(8, -1);
		if (n === "Object" && e.constructor && (n = e.constructor.name), n === "Map" || n === "Set") return Array.from(e);
		if (n === "Arguments" || /^(?:Ui|I)nt(?:8|16|32)(?:Clamped)?Array$/.test(n)) return v(e, t);
	}
}
function v(e, t) {
	(t == null || t > e.length) && (t = e.length);
	for (var n = 0, r = Array(t); n < t; n++) r[n] = e[n];
	return r;
}
function y(e, t) {
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
function b(e) {
	if (Array.isArray(e)) return e;
}
function x(e, t) {
	if (e == null) return {};
	var n = S(e, t), r, i;
	if (Object.getOwnPropertySymbols) {
		var a = Object.getOwnPropertySymbols(e);
		for (i = 0; i < a.length; i++) r = a[i], !(t.indexOf(r) >= 0) && Object.prototype.propertyIsEnumerable.call(e, r) && (n[r] = e[r]);
	}
	return n;
}
function S(e, t) {
	if (e == null) return {};
	var n = {}, r = Object.keys(e), i, a;
	for (a = 0; a < r.length; a++) i = r[a], !(t.indexOf(i) >= 0) && (n[i] = e[i]);
	return n;
}
function C(e, t) {
	if (!(e instanceof t)) throw TypeError("Cannot call a class as a function");
}
function w(e, t) {
	for (var n = 0; n < t.length; n++) {
		var r = t[n];
		r.enumerable = r.enumerable || !1, r.configurable = !0, "value" in r && (r.writable = !0), Object.defineProperty(e, r.key, r);
	}
}
function T(e, t, n) {
	return t && w(e.prototype, t), Object.defineProperty(e, "prototype", { writable: !1 }), e;
}
function E(e, t) {
	if (typeof t != "function" && t !== null) throw TypeError("Super expression must either be null or a function");
	e.prototype = Object.create(t && t.prototype, { constructor: {
		value: e,
		writable: !0,
		configurable: !0
	} }), Object.defineProperty(e, "prototype", { writable: !1 }), t && D(e, t);
}
function D(e, t) {
	return D = Object.setPrototypeOf ? Object.setPrototypeOf.bind() : function(e, t) {
		return e.__proto__ = t, e;
	}, D(e, t);
}
function O(e) {
	var t = j();
	return function() {
		var n = M(e), r;
		if (t) {
			var i = M(this).constructor;
			r = Reflect.construct(n, arguments, i);
		} else r = n.apply(this, arguments);
		return k(this, r);
	};
}
function k(e, t) {
	if (t && (d(t) === "object" || typeof t == "function")) return t;
	if (t !== void 0) throw TypeError("Derived constructors may only return object or undefined");
	return A(e);
}
function A(e) {
	if (e === void 0) throw ReferenceError("this hasn't been initialised - super() hasn't been called");
	return e;
}
function j() {
	if (typeof Reflect > "u" || !Reflect.construct || Reflect.construct.sham) return !1;
	if (typeof Proxy == "function") return !0;
	try {
		return Boolean.prototype.valueOf.call(Reflect.construct(Boolean, [], function() {})), !0;
	} catch {
		return !1;
	}
}
function M(e) {
	return M = Object.setPrototypeOf ? Object.getPrototypeOf.bind() : function(e) {
		return e.__proto__ || Object.getPrototypeOf(e);
	}, M(e);
}
function N(e, t, n) {
	return t in e ? Object.defineProperty(e, t, {
		value: n,
		enumerable: !0,
		configurable: !0,
		writable: !0
	}) : e[t] = n, e;
}
var P = /* @__PURE__ */ function(e) {
	E(r, e);
	var t = O(r);
	function r() {
		var e;
		C(this, r);
		var n = [...arguments];
		return e = t.call.apply(t, [this].concat(n)), N(A(e), "state", { isFocused: e.props.autoFocus || !1 }), N(A(e), "onFocus", function(t) {
			e.setState({ isFocused: !0 }), e.props.onFocus(t);
		}), N(A(e), "onBlur", function(t) {
			e.setState({ isFocused: !1 }), e.props.onBlur(t);
		}), e;
	}
	return T(r, [{
		key: "render",
		value: function() {
			var e = this.props, t = e.startEnhancer, r = e.endEnhancer, a = e.overrides, d = a.Root, g = a.StartEnhancer, _ = a.EndEnhancer, v = x(a, f), y = x(e, p), b = h(n(d, c), 2), S = b[0], C = b[1], w = h(n(g, o), 2), T = w[0], E = w[1], D = h(n(_, o), 2), O = D[0], k = D[1], A = s(this.props, this.state);
			return /* @__PURE__ */ u.createElement(S, m({ "data-baseweb": "input" }, A, C, {
				$adjoined: F(t, r),
				$hasIconTrailing: this.props.clearable || this.props.type == "password"
			}), I(t) && /* @__PURE__ */ u.createElement(T, m({}, A, E, { $position: i.start }), typeof t == "function" ? t(A) : t), /* @__PURE__ */ u.createElement(l, m({}, y, {
				overrides: v,
				adjoined: F(t, r),
				onFocus: this.onFocus,
				onBlur: this.onBlur
			})), I(r) && /* @__PURE__ */ u.createElement(O, m({}, A, k, { $position: i.end }), typeof r == "function" ? r(A) : r));
		}
	}]), r;
}(u.Component);
N(P, "defaultProps", {
	autoComplete: "on",
	autoFocus: !1,
	disabled: !1,
	name: "",
	onBlur: function() {},
	onFocus: function() {},
	overrides: {},
	required: !1,
	size: a.default,
	startEnhancer: null,
	endEnhancer: null,
	clearable: !1,
	type: "text",
	readOnly: !1
});
function F(e, t) {
	return I(e) && I(t) ? r.both : I(e) ? r.left : I(t) ? r.right : r.none;
}
function I(e) {
	return !!(e || e === 0);
}
//#endregion
export { P as t };

//# sourceMappingURL=input-CClPhvPt-C_5WYNdx.js.map