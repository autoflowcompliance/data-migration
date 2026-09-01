import { Cn as e, Da as t, Fi as n, Ka as r, Li as i, P as a, Ua as o, Un as s, Ur as c, ii as l, ma as u, nr as d, ti as f, ya as p } from "./index-Dl4ETd_L-D2oMd1k2.js";
import { t as m } from "./WidgetLabel-CQfHGtry-udktvHE5.js";
import { t as h } from "./WidgetLabelHelpIcon-C6IRqJ_I-BBI6AbZ-.js";
import { n as g } from "./useBasicWidgetState-D3zHnRUK-Dsaz4YO6.js";
import { i as _ } from "./select-DyvsciAf-DTdJ1yfK.js";
import { n as v } from "./timepicker-Bp949u0W-KUvR56zU.js";
import { n as y, r as b, t as x } from "./styled-components-CZBaXqHz-DfCZphf1.js";
//#region ../react/build/TimeInput-DuMfskY4.js
var S = /* @__PURE__ */ r(o(), 1), C = {}, w = {}, T;
function E() {
	return T ? w : (T = 1, Object.defineProperty(w, "__esModule", { value: !0 }), w.STATE_CHANGE_TYPE = w.SIZE = w.ENHANCER_POSITION = w.CUSTOM_INPUT_TYPE = w.ADJOINED = void 0, w.STATE_CHANGE_TYPE = { change: "change" }, w.CUSTOM_INPUT_TYPE = { textarea: "textarea" }, w.ADJOINED = {
		none: "none",
		left: "left",
		right: "right",
		both: "both"
	}, w.SIZE = {
		mini: "mini",
		default: "default",
		compact: "compact",
		large: "large"
	}, w.ENHANCER_POSITION = {
		start: "start",
		end: "end"
	}, w);
}
var D = {}, O = {}, k = {}, A;
function j() {
	if (A) return k;
	A = 1, Object.defineProperty(k, "__esModule", { value: !0 }), k.Svg = void 0, k.getSvgStyles = t;
	var e = n;
	function t(e) {
		var t = e.$theme, n = e.$size, r = e.$color, i = t.sizing.scale600;
		n && (i = t.sizing[n] ? t.sizing[n] : typeof n == "number" ? `${n}px` : n);
		var a = "currentColor";
		return r && (a = t.colors[r] ? t.colors[r] : r), {
			display: "inline-block",
			fill: a,
			color: a,
			height: i,
			width: i
		};
	}
	var r = (0, e.styled)("svg", t);
	return k.Svg = r, r.displayName = "Svg", r.displayName = "Svg", k;
}
var M = {}, N;
function P() {
	if (N) return M;
	N = 1, Object.defineProperty(M, "__esModule", { value: !0 }), M.default = e;
	function e(e) {
		var t = {};
		for (var n in e) n[0] !== "$" && (t[n] = e[n]);
		return t;
	}
	return M;
}
var F;
function I() {
	if (F) return O;
	F = 1;
	function e(t) {
		"@babel/helpers - typeof";
		return e = typeof Symbol == "function" && typeof Symbol.iterator == "symbol" ? function(e) {
			return typeof e;
		} : function(e) {
			return e && typeof Symbol == "function" && e.constructor === Symbol && e !== Symbol.prototype ? "symbol" : typeof e;
		}, e(t);
	}
	Object.defineProperty(O, "__esModule", { value: !0 }), O.default = void 0;
	var t = l(S.default), n = /* @__PURE__ */ i(), r = /* @__PURE__ */ j(), a = s(/* @__PURE__ */ P()), o = [
		"children",
		"title",
		"size",
		"color",
		"overrides"
	];
	function s(e) {
		return e && e.__esModule ? e : { default: e };
	}
	function c(e) {
		if (typeof WeakMap != "function") return null;
		var t = /* @__PURE__ */ new WeakMap(), n = /* @__PURE__ */ new WeakMap();
		return (c = function(e) {
			return e ? n : t;
		})(e);
	}
	function l(t, n) {
		if (t && t.__esModule) return t;
		if (t === null || e(t) !== "object" && typeof t != "function") return { default: t };
		var r = c(n);
		if (r && r.has(t)) return r.get(t);
		var i = {}, a = Object.defineProperty && Object.getOwnPropertyDescriptor;
		for (var o in t) if (o !== "default" && Object.prototype.hasOwnProperty.call(t, o)) {
			var s = a ? Object.getOwnPropertyDescriptor(t, o) : null;
			s && (s.get || s.set) ? Object.defineProperty(i, o, s) : i[o] = t[o];
		}
		return i.default = t, r && r.set(t, i), i;
	}
	function u() {
		return u = Object.assign ? Object.assign.bind() : function(e) {
			for (var t = 1; t < arguments.length; t++) {
				var n = arguments[t];
				for (var r in n) Object.prototype.hasOwnProperty.call(n, r) && (e[r] = n[r]);
			}
			return e;
		}, u.apply(this, arguments);
	}
	function d(e, t) {
		var n = Object.keys(e);
		if (Object.getOwnPropertySymbols) {
			var r = Object.getOwnPropertySymbols(e);
			t && (r = r.filter(function(t) {
				return Object.getOwnPropertyDescriptor(e, t).enumerable;
			})), n.push.apply(n, r);
		}
		return n;
	}
	function f(e) {
		for (var t = 1; t < arguments.length; t++) {
			var n = arguments[t] == null ? {} : arguments[t];
			t % 2 ? d(Object(n), !0).forEach(function(t) {
				p(e, t, n[t]);
			}) : Object.getOwnPropertyDescriptors ? Object.defineProperties(e, Object.getOwnPropertyDescriptors(n)) : d(Object(n)).forEach(function(t) {
				Object.defineProperty(e, t, Object.getOwnPropertyDescriptor(n, t));
			});
		}
		return e;
	}
	function p(e, t, n) {
		return t in e ? Object.defineProperty(e, t, {
			value: n,
			enumerable: !0,
			configurable: !0,
			writable: !0
		}) : e[t] = n, e;
	}
	function m(e, t) {
		return y(e) || v(e, t) || g(e, t) || h();
	}
	function h() {
		throw TypeError("Invalid attempt to destructure non-iterable instance.\nIn order to be iterable, non-array objects must have a [Symbol.iterator]() method.");
	}
	function g(e, t) {
		if (e) {
			if (typeof e == "string") return _(e, t);
			var n = Object.prototype.toString.call(e).slice(8, -1);
			if (n === "Object" && e.constructor && (n = e.constructor.name), n === "Map" || n === "Set") return Array.from(e);
			if (n === "Arguments" || /^(?:Ui|I)nt(?:8|16|32)(?:Clamped)?Array$/.test(n)) return _(e, t);
		}
	}
	function _(e, t) {
		(t == null || t > e.length) && (t = e.length);
		for (var n = 0, r = Array(t); n < t; n++) r[n] = e[n];
		return r;
	}
	function v(e, t) {
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
	function y(e) {
		if (Array.isArray(e)) return e;
	}
	function b(e, t) {
		if (e == null) return {};
		var n = x(e, t), r, i;
		if (Object.getOwnPropertySymbols) {
			var a = Object.getOwnPropertySymbols(e);
			for (i = 0; i < a.length; i++) r = a[i], !(t.indexOf(r) >= 0) && Object.prototype.propertyIsEnumerable.call(e, r) && (n[r] = e[r]);
		}
		return n;
	}
	function x(e, t) {
		if (e == null) return {};
		var n = {}, r = Object.keys(e), i, a;
		for (a = 0; a < r.length; a++) i = r[a], !(t.indexOf(i) >= 0) && (n[i] = e[i]);
		return n;
	}
	return O.default = /* @__PURE__ */ t.forwardRef(function(e, i) {
		var s = e.children, c = e.title, l = e.size, d = e.color, p = e.overrides, h = p === void 0 ? {} : p, g = b(e, o), _ = m((0, n.getOverrides)(h.Svg, r.Svg), 2), v = _[0], y = _[1], x = v.__STYLETRON__ ? f(f({
			title: c,
			$color: d,
			$size: l
		}, g), y) : f(f({
			title: c,
			color: d,
			size: l
		}, (0, a.default)(g)), (0, a.default)(y));
		return /* @__PURE__ */ t.createElement(v, u({
			"data-baseweb": "icon",
			ref: i
		}, x), c ? /* @__PURE__ */ t.createElement("title", null, c) : null, s);
	}), O;
}
var L;
function R() {
	if (L) return D;
	L = 1;
	function e(t) {
		"@babel/helpers - typeof";
		return e = typeof Symbol == "function" && typeof Symbol.iterator == "symbol" ? function(e) {
			return typeof e;
		} : function(e) {
			return e && typeof Symbol == "function" && e.constructor === Symbol && e !== Symbol.prototype ? "symbol" : typeof e;
		}, e(t);
	}
	Object.defineProperty(D, "__esModule", { value: !0 }), D.default = void 0;
	var t = u(S.default), r = n, a = /* @__PURE__ */ i(), o = c(/* @__PURE__ */ I()), s = [
		"title",
		"size",
		"color",
		"overrides"
	];
	function c(e) {
		return e && e.__esModule ? e : { default: e };
	}
	function l(e) {
		if (typeof WeakMap != "function") return null;
		var t = /* @__PURE__ */ new WeakMap(), n = /* @__PURE__ */ new WeakMap();
		return (l = function(e) {
			return e ? n : t;
		})(e);
	}
	function u(t, n) {
		if (t && t.__esModule) return t;
		if (t === null || e(t) !== "object" && typeof t != "function") return { default: t };
		var r = l(n);
		if (r && r.has(t)) return r.get(t);
		var i = {}, a = Object.defineProperty && Object.getOwnPropertyDescriptor;
		for (var o in t) if (o !== "default" && Object.prototype.hasOwnProperty.call(t, o)) {
			var s = a ? Object.getOwnPropertyDescriptor(t, o) : null;
			s && (s.get || s.set) ? Object.defineProperty(i, o, s) : i[o] = t[o];
		}
		return i.default = t, r && r.set(t, i), i;
	}
	function d() {
		return d = Object.assign ? Object.assign.bind() : function(e) {
			for (var t = 1; t < arguments.length; t++) {
				var n = arguments[t];
				for (var r in n) Object.prototype.hasOwnProperty.call(n, r) && (e[r] = n[r]);
			}
			return e;
		}, d.apply(this, arguments);
	}
	function f(e, t) {
		if (e == null) return {};
		var n = p(e, t), r, i;
		if (Object.getOwnPropertySymbols) {
			var a = Object.getOwnPropertySymbols(e);
			for (i = 0; i < a.length; i++) r = a[i], !(t.indexOf(r) >= 0) && Object.prototype.propertyIsEnumerable.call(e, r) && (n[r] = e[r]);
		}
		return n;
	}
	function p(e, t) {
		if (e == null) return {};
		var n = {}, r = Object.keys(e), i, a;
		for (a = 0; a < r.length; a++) i = r[a], !(t.indexOf(i) >= 0) && (n[i] = e[i]);
		return n;
	}
	function m(e, t) {
		return y(e) || v(e, t) || g(e, t) || h();
	}
	function h() {
		throw TypeError("Invalid attempt to destructure non-iterable instance.\nIn order to be iterable, non-array objects must have a [Symbol.iterator]() method.");
	}
	function g(e, t) {
		if (e) {
			if (typeof e == "string") return _(e, t);
			var n = Object.prototype.toString.call(e).slice(8, -1);
			if (n === "Object" && e.constructor && (n = e.constructor.name), n === "Map" || n === "Set") return Array.from(e);
			if (n === "Arguments" || /^(?:Ui|I)nt(?:8|16|32)(?:Clamped)?Array$/.test(n)) return _(e, t);
		}
	}
	function _(e, t) {
		(t == null || t > e.length) && (t = e.length);
		for (var n = 0, r = Array(t); n < t; n++) r[n] = e[n];
		return r;
	}
	function v(e, t) {
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
	function y(e) {
		if (Array.isArray(e)) return e;
	}
	function b(e, n) {
		var i = m((0, r.useStyletron)(), 2)[1], c = e.title, l = c === void 0 ? "Delete Alt" : c, u = e.size, p = e.color, h = e.overrides, g = h === void 0 ? {} : h, _ = f(e, s), v = (0, a.mergeOverride)({ component: i.icons && i.icons.DeleteAlt ? i.icons.DeleteAlt : null }, g && g.Svg ? (0, a.toObjectOverride)(g.Svg) : {});
		return /* @__PURE__ */ t.createElement(o.default, d({
			viewBox: "0 0 24 24",
			ref: n,
			title: l,
			size: u,
			color: p,
			overrides: { Svg: v }
		}, _), /* @__PURE__ */ t.createElement("path", {
			fillRule: "evenodd",
			clipRule: "evenodd",
			d: "M12 20C16.4183 20 20 16.4183 20 12C20 7.58173 16.4183 4 12 4C7.58173 4 4 7.58173 4 12C4 16.4183 7.58173 20 12 20ZM10.0303 8.96967C9.73743 8.67679 9.26257 8.67679 8.96967 8.96967C8.67676 9.26257 8.67676 9.73743 8.96967 10.0303L10.9393 12L8.96967 13.9697C8.67676 14.2626 8.67676 14.7374 8.96967 15.0303C9.26257 15.3232 9.73743 15.3232 10.0303 15.0303L12 13.0607L13.9697 15.0303C14.2626 15.3232 14.7374 15.3232 15.0303 15.0303C15.3232 14.7374 15.3232 14.2626 15.0303 13.9697L13.0607 12L15.0303 10.0303C15.3232 9.73743 15.3232 9.26257 15.0303 8.96967C14.7374 8.67679 14.2626 8.67679 13.9697 8.96967L12 10.9393L10.0303 8.96967Z"
		}));
	}
	return D.default = /* @__PURE__ */ t.forwardRef(b), D;
}
var z;
function B() {
	if (z) return C;
	z = 1, Object.defineProperty(C, "__esModule", { value: !0 }), C.getRootStyles = C.getInputStyles = C.getInputContainerStyles = C.StyledMaskToggleButton = C.StyledClearIconContainer = C.StyledClearIcon = C.Root = C.InputEnhancer = C.InputContainer = C.Input = void 0;
	var e = n, t = /* @__PURE__ */ E(), r = i(/* @__PURE__ */ R());
	function i(e) {
		return e && e.__esModule ? e : { default: e };
	}
	function a(e, t) {
		var n = Object.keys(e);
		if (Object.getOwnPropertySymbols) {
			var r = Object.getOwnPropertySymbols(e);
			t && (r = r.filter(function(t) {
				return Object.getOwnPropertyDescriptor(e, t).enumerable;
			})), n.push.apply(n, r);
		}
		return n;
	}
	function o(e) {
		for (var t = 1; t < arguments.length; t++) {
			var n = arguments[t] == null ? {} : arguments[t];
			t % 2 ? a(Object(n), !0).forEach(function(t) {
				s(e, t, n[t]);
			}) : Object.getOwnPropertyDescriptors ? Object.defineProperties(e, Object.getOwnPropertyDescriptors(n)) : a(Object(n)).forEach(function(t) {
				Object.defineProperty(e, t, Object.getOwnPropertyDescriptor(n, t));
			});
		}
		return e;
	}
	function s(e, t, n) {
		return t in e ? Object.defineProperty(e, t, {
			value: n,
			enumerable: !0,
			configurable: !0,
			writable: !0
		}) : e[t] = n, e;
	}
	var c = (0, e.styled)("button", function(e) {
		var n, r = e.$theme, i = e.$size, a = e.$isFocusVisible, o = (n = {}, s(n, t.SIZE.mini, r.sizing.scale400), s(n, t.SIZE.compact, r.sizing.scale400), s(n, t.SIZE.default, r.sizing.scale300), s(n, t.SIZE.large, r.sizing.scale200), n)[i];
		return {
			display: "flex",
			alignItems: "center",
			borderTopStyle: "none",
			borderBottomStyle: "none",
			borderLeftStyle: "none",
			borderRightStyle: "none",
			background: "none",
			paddingLeft: o,
			paddingRight: o,
			outline: a ? `solid 3px ${r.colors.accent}` : "none",
			color: r.colors.contentPrimary
		};
	});
	C.StyledMaskToggleButton = c, c.displayName = "StyledMaskToggleButton", c.displayName = "StyledMaskToggleButton";
	var l = (0, e.styled)("div", function(e) {
		var n, r = e.$alignTop, i = r === void 0 ? !1 : r, a = e.$size, o = e.$theme, c = (n = {}, s(n, t.SIZE.mini, o.sizing.scale200), s(n, t.SIZE.compact, o.sizing.scale200), s(n, t.SIZE.default, o.sizing.scale100), s(n, t.SIZE.large, o.sizing.scale0), n)[a];
		return {
			display: "flex",
			alignItems: i ? "flex-start" : "center",
			paddingLeft: c,
			paddingRight: c,
			paddingTop: i ? o.sizing.scale500 : "0px",
			color: o.colors.contentPrimary
		};
	});
	C.StyledClearIconContainer = l, l.displayName = "StyledClearIconContainer", l.displayName = "StyledClearIconContainer";
	var u = (0, e.styled)(r.default, function(e) {
		var t = e.$theme;
		return {
			cursor: "pointer",
			outline: e.$isFocusVisible ? `solid 3px ${t.colors.accent}` : "none"
		};
	});
	C.StyledClearIcon = u, u.displayName = "StyledClearIcon", u.displayName = "StyledClearIcon";
	function d(e, n) {
		var r;
		return (r = {}, s(r, t.SIZE.mini, {
			paddingTop: n.scale100,
			paddingBottom: n.scale100,
			paddingLeft: n.scale550,
			paddingRight: n.scale550
		}), s(r, t.SIZE.compact, {
			paddingTop: n.scale200,
			paddingBottom: n.scale200,
			paddingLeft: n.scale550,
			paddingRight: n.scale550
		}), s(r, t.SIZE.default, {
			paddingTop: n.scale400,
			paddingBottom: n.scale400,
			paddingLeft: n.scale550,
			paddingRight: n.scale550
		}), s(r, t.SIZE.large, {
			paddingTop: n.scale550,
			paddingBottom: n.scale550,
			paddingLeft: n.scale550,
			paddingRight: n.scale550
		}), r)[e];
	}
	function f(e, n, r, i, a) {
		var o = e === t.ADJOINED.both || e === t.ADJOINED.left && i !== "rtl" || e === t.ADJOINED.right && i === "rtl" || a && i === "rtl", s = e === t.ADJOINED.both || e === t.ADJOINED.right && i !== "rtl" || e === t.ADJOINED.left && i === "rtl" || a && i !== "rtl";
		return {
			paddingLeft: o ? r.scale550 : "0px",
			paddingRight: s ? r.scale550 : "0px"
		};
	}
	function p(e, n) {
		var r;
		return (r = {}, s(r, t.SIZE.mini, n.font100), s(r, t.SIZE.compact, n.font200), s(r, t.SIZE.default, n.font300), s(r, t.SIZE.large, n.font400), r)[e];
	}
	function m(e, t, n) {
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
	function h(e, n) {
		var r = n.inputBorderRadius;
		return e === t.SIZE.mini && (r = n.inputBorderRadiusMini), {
			borderTopLeftRadius: r,
			borderBottomLeftRadius: r,
			borderTopRightRadius: r,
			borderBottomRightRadius: r
		};
	}
	var g = function(e) {
		var t = e.$isFocused, n = e.$adjoined, r = e.$error, i = e.$disabled, a = e.$positive, s = e.$size, c = e.$theme, l = e.$theme, u = l.borders, d = l.colors, g = l.sizing, _ = l.typography, v = l.animation, y = e.$hasIconTrailing;
		return o(o(o(o({
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
			transitionDuration: v.timing200,
			transitionTimingFunction: v.easeOutCurve
		}, h(s, u)), p(s, _)), m(i, t, r, a, d)), f(n, s, g, c.direction, y));
	};
	C.getRootStyles = g;
	var _ = (0, e.styled)("div", g);
	C.Root = _, _.displayName = "Root", _.displayName = "Root";
	function v(e, n) {
		var r;
		return (r = {}, s(r, t.SIZE.mini, {
			paddingRight: n.scale400,
			paddingLeft: n.scale400
		}), s(r, t.SIZE.compact, {
			paddingRight: n.scale400,
			paddingLeft: n.scale400
		}), s(r, t.SIZE.default, {
			paddingRight: n.scale300,
			paddingLeft: n.scale300
		}), s(r, t.SIZE.large, {
			paddingRight: n.scale200,
			paddingLeft: n.scale200
		}), r)[e];
	}
	function y(e, t, n, r, i) {
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
	var b = (0, e.styled)("div", function(e) {
		var t = e.$size, n = e.$disabled, r = e.$isFocused, i = e.$error, a = e.$positive, s = e.$theme, c = s.colors, l = s.sizing, u = s.typography, d = s.animation;
		return o(o(o({
			display: "flex",
			alignItems: "center",
			justifyContent: "center",
			transitionProperty: "color, background-color",
			transitionDuration: d.timing200,
			transitionTimingFunction: d.easeOutCurve
		}, p(t, u)), v(t, l)), y(n, r, i, a, c));
	});
	C.InputEnhancer = b, b.displayName = "InputEnhancer", b.displayName = "InputEnhancer";
	function x(e, t, n, r, i) {
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
	var S = function(e) {
		var t = e.$isFocused, n = e.$error, r = e.$disabled, i = e.$positive, a = e.$size, s = e.$theme, c = s.colors, l = s.typography, u = s.animation;
		return o(o({
			display: "flex",
			width: "100%",
			transitionProperty: "background-color",
			transitionDuration: u.timing200,
			transitionTimingFunction: u.easeOutCurve
		}, p(a, l)), x(r, t, n, i, c));
	};
	C.getInputContainerStyles = S;
	var w = (0, e.styled)("div", S);
	C.InputContainer = w, w.displayName = "InputContainer", w.displayName = "InputContainer";
	function T(e, t, n, r) {
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
	var D = function(e) {
		var t = e.$disabled, n = e.$isFocused, r = e.$error, i = e.$size, a = e.$theme, s = a.colors, c = a.sizing, l = a.typography;
		return o(o(o({
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
		}, p(i, l)), d(i, c)), T(t, n, r, s));
	};
	C.getInputStyles = D;
	var O = (0, e.styled)("input", D);
	return C.Input = O, O.displayName = "Input", O.displayName = "Input", C;
}
var V = /* @__PURE__ */ B(), H = x(y);
function U({ disabled: n, element: r, widgetMgr: i, fragmentId: o }) {
	let [y, x] = g({
		getStateFromWidgetMgr: W,
		getDefaultStateFromProto: G,
		getCurrStateFromProto: K,
		updateWidgetMgrState: q,
		element: r,
		widgetMgr: i,
		fragmentId: o,
		queryParamBinding: r.queryParamKey ? {
			paramKey: r.queryParamKey,
			valueType: "string_value",
			clearable: !r.default
		} : void 0,
		formClearBehavior: "resetValueOnly"
	}), C = (0, S.useContext)(a), w = u(), T = p(), { innerHeight: E } = t(), D = r.step ? Number(r.step) : 900, O = Math.ceil(86400 / D), k = e(w.sizes.dropdownItemHeight), A = Math.min(e(w.sizes.maxDropdownHeight), E * .7), j = O * k > A ? T : 0, M = c(r.default) && !n, N = { Select: { props: {
		disabled: n,
		overrides: {
			ControlContainer: { style: ({ $isFocused: e }) => {
				let t = s(w.colors, e);
				return {
					height: w.sizes.minElementHeight,
					borderLeftWidth: w.sizes.borderWidth,
					borderRightWidth: w.sizes.borderWidth,
					borderTopWidth: w.sizes.borderWidth,
					borderBottomWidth: w.sizes.borderWidth,
					borderTopColor: t,
					borderRightColor: t,
					borderBottomColor: t,
					borderLeftColor: t
				};
			} },
			IconsContainer: { style: () => ({ paddingRight: w.spacing.sm }) },
			ValueContainer: { style: () => ({
				lineHeight: w.lineHeights.inputWidget,
				paddingRight: w.spacing.sm,
				paddingLeft: w.sizes.tagMarginInsideBorder,
				paddingBottom: w.spacing.sm,
				paddingTop: w.spacing.sm,
				marginLeft: w.spacing.sm
			}) },
			SingleValue: {
				style: {
					fontWeight: w.fontWeights.normal,
					marginLeft: w.spacing.none
				},
				props: { "data-testid": "stTimeInputTimeDisplay" }
			},
			Dropdown: { style: () => ({
				paddingTop: w.spacing.none,
				paddingBottom: w.spacing.none,
				paddingLeft: w.spacing.none,
				paddingRight: w.spacing.none,
				boxShadow: "none",
				maxHeight: `min(${w.sizes.maxDropdownHeight}, 70vh)`
			}) },
			DropdownContainer: { style: () => ({
				...d(w),
				overflow: "hidden"
			}) },
			DropdownListItem: { component: H },
			Popover: { props: {
				ignoreBoundary: C,
				popoverMargin: e(w.spacing.twoXS),
				overrides: { Body: { style: () => ({
					overflow: "hidden",
					"--scrollbar-gutter-size": `${j}px`
				}) } }
			} },
			Placeholder: { style: () => ({
				color: w.colors.fadedText60,
				position: "absolute"
			}) },
			Input: { style: {
				position: "relative",
				zIndex: w.zIndices.priority
			} },
			SelectArrow: {
				component: _,
				props: { overrides: { Svg: { style: () => ({
					width: w.iconSizes.xl,
					height: w.iconSizes.xl
				}) } } }
			}
		}
	} } }, P = (0, S.useCallback)((e) => {
		x({
			value: e === null ? null : J(e),
			fromUi: !0
		});
	}, [x]), F = (0, S.useCallback)(() => {
		P(null);
	}, [P]);
	return /* @__PURE__ */ f.jsxs("div", {
		className: "stTimeInput",
		"data-testid": "stTimeInput",
		children: [
			/* @__PURE__ */ f.jsx(m, {
				label: r.label,
				disabled: n,
				labelVisibility: l(r.labelVisibility?.value),
				children: r.help && /* @__PURE__ */ f.jsx(h, {
					content: r.help,
					label: r.label
				})
			}),
			/* @__PURE__ */ f.jsx(v, {
				format: "24",
				step: D,
				value: c(y) ? void 0 : Y(y),
				onChange: P,
				overrides: N,
				nullable: M,
				creatable: !0,
				"aria-label": r.label
			}),
			M && !c(y) && /* @__PURE__ */ f.jsx(b, {
				onClick: F,
				"data-testid": "stTimeInputClearButton",
				children: /* @__PURE__ */ f.jsx(V.StyledClearIcon, {
					overrides: { Svg: { style: {
						color: w.colors.grayTextColor,
						padding: w.spacing.threeXS,
						height: w.sizes.clearIconSize,
						width: w.sizes.clearIconSize,
						":hover": { fill: w.colors.bodyText }
					} } },
					$isFocusVisible: !1
				})
			})
		]
	});
}
function W(e, t) {
	let n = e.getStringValue(t);
	if (n !== void 0) return n ?? null;
}
function G(e) {
	return e.default ?? null;
}
function K(e) {
	return e.value ?? null;
}
function q(e, t, n, r) {
	t.setStringValue(e, n.value, { fromUi: n.fromUi }, r);
}
function J(e) {
	return `${e.getHours().toString().padStart(2, "0")}:${e.getMinutes().toString().padStart(2, "0")}`;
}
function Y(e) {
	if (e === null) return null;
	let [t, n] = e.split(":").map(Number), r = /* @__PURE__ */ new Date();
	return r.setHours(t), r.setMinutes(n), r;
}
var X = (0, S.memo)(U);
//#endregion
export { X as default };

//# sourceMappingURL=TimeInput-DuMfskY4-DHZrAOSh.js.map