import { $i as e, Ka as t, Ua as n, fi as r, lr as i, ma as a, ti as o, tr as s, za as c } from "./index-Dl4ETd_L-D2oMd1k2.js";
//#region ../react/build/ProgressBar-DhIwITyC.js
var l = /* @__PURE__ */ t(n(), 1), u = {
	small: "small",
	medium: "medium",
	large: "large"
}, d;
function f() {
	return f = Object.assign ? Object.assign.bind() : function(e) {
		for (var t = 1; t < arguments.length; t++) {
			var n = arguments[t];
			for (var r in n) Object.prototype.hasOwnProperty.call(n, r) && (e[r] = n[r]);
		}
		return e;
	}, f.apply(this, arguments);
}
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
function g(e) {
	var t;
	return (t = {}, h(t, u.small, "2px"), h(t, u.medium, "4px"), h(t, u.large, "8px"), t)[e];
}
var _ = e("div", function(e) {
	return { width: "100%" };
});
_.displayName = "StyledRoot", _.displayName = "StyledRoot";
var v = e("div", function(e) {
	var t = e.$theme.sizing;
	return {
		display: "flex",
		marginLeft: t.scale500,
		marginRight: t.scale500,
		marginTop: t.scale500,
		marginBottom: t.scale500
	};
});
v.displayName = "StyledBarContainer", v.displayName = "StyledBarContainer";
var y = e("div", function(e) {
	var t = e.$theme, n = e.$size, r = e.$steps, a = t.colors, o = t.sizing, s = t.borders.useRoundedCorners ? o.scale0 : 0;
	return m({
		borderTopLeftRadius: s,
		borderTopRightRadius: s,
		borderBottomRightRadius: s,
		borderBottomLeftRadius: s,
		backgroundColor: i(a.progressbarTrackFill, "0.16"),
		height: g(n),
		flex: 1,
		overflow: "hidden"
	}, r < 2 ? {} : {
		marginLeft: o.scale300,
		":first-child": { marginLeft: "0" }
	});
});
y.displayName = "StyledBar", y.displayName = "StyledBar";
var b = e("div", function(e) {
	var t = e.$theme, n = e.$value, r = e.$successValue, i = e.$steps, a = e.$index, o = e.$maxValue, s = e.$minValue, c = s === void 0 ? 0 : s, l = o || r, u = t.colors, d = t.sizing, f = t.borders, p = `${100 - (n - c) * 100 / (l - c)}%`, h = {
		default: "default",
		awaits: "awaits",
		inProgress: "inProgress",
		completed: "completed"
	}, g = h.default;
	if (i > 1) {
		var _ = (l - c) / i, v = (n - c) / (l - c) * 100, y = Math.floor(v / _);
		g = a < y ? h.completed : a === y ? h.inProgress : h.awaits;
	}
	var b = f.useRoundedCorners ? d.scale0 : 0, x = { transform: `translateX(-${p})` }, S = g === h.inProgress ? {
		animationDuration: "2.1s",
		animationIterationCount: "infinite",
		animationTimingFunction: t.animation.linearCurve,
		animationName: {
			"0%": {
				transform: "translateX(-102%)",
				opacity: 1
			},
			"50%": {
				transform: "translateX(0%)",
				opacity: 1
			},
			"100%": {
				transform: "translateX(0%)",
				opacity: 0
			}
		}
	} : g === h.completed ? { transform: "translateX(0%)" } : { transform: "translateX(-102%)" };
	return m({
		borderTopLeftRadius: b,
		borderTopRightRadius: b,
		borderBottomRightRadius: b,
		borderBottomLeftRadius: b,
		backgroundColor: u.accent,
		height: "100%",
		width: "100%",
		transform: "translateX(-102%)",
		transition: "transform 0.5s"
	}, i > 1 ? S : x);
});
b.displayName = "StyledBarProgress", b.displayName = "StyledBarProgress";
var x = e("div", function(e) {
	var t = e.$theme, n = e.$isLeft, r = n === void 0 ? !1 : n, i = e.$size, a = i === void 0 ? u.medium : i, o = t.colors, s = t.sizing, c = t.borders.useRoundedCorners ? s.scale0 : 0, l = g(a), d = {
		display: "inline-block",
		flex: 1,
		marginLeft: "auto",
		marginRight: "auto",
		transitionProperty: "background-position",
		animationDuration: "1.5s",
		animationIterationCount: "infinite",
		animationTimingFunction: t.animation.linearCurve,
		backgroundSize: "300% auto",
		backgroundRepeat: "no-repeat",
		backgroundPositionX: r ? "-50%" : "150%",
		backgroundImage: `linear-gradient(${r ? "90" : "270"}deg, transparent 0%, ${o.accent} 25%, ${o.accent} 75%, transparent 100%)`,
		animationName: r ? {
			"0%": { backgroundPositionX: "-50%" },
			"33%": { backgroundPositionX: "50%" },
			"66%": { backgroundPositionX: "50%" },
			"100%": { backgroundPositionX: "150%" }
		} : {
			"0%": { backgroundPositionX: "150%" },
			"33%": { backgroundPositionX: "50%" },
			"66%": { backgroundPositionX: "50%" },
			"100%": { backgroundPositionX: "-50%" }
		}
	};
	return m(m({}, r ? {
		borderTopLeftRadius: c,
		borderBottomLeftRadius: c
	} : {
		borderTopRightRadius: c,
		borderBottomRightRadius: c
	}), {}, { height: l }, d);
});
x.displayName = "StyledInfiniteBar", x.displayName = "StyledInfiniteBar";
var S = e("div", function(e) {
	return m(m({ textAlign: "center" }, e.$theme.typography.font150), {}, { color: e.$theme.colors.contentTertiary });
});
S.displayName = "StyledLabel", S.displayName = "StyledLabel";
var C = (d = {}, h(d, u.large, {
	d: "M47.5 4H71.5529C82.2933 4 91 12.9543 91 24C91 35.0457 82.2933 44 71.5529 44H23.4471C12.7067 44 4 35.0457 4 24C4 12.9543 12.7067 4 23.4471 4H47.5195",
	width: 95,
	height: 48,
	strokeWidth: 8,
	typography: "LabelLarge"
}), h(d, u.medium, {
	d: "M39 2H60.5833C69.0977 2 76 9.16344 76 18C76 26.8366 69.0977 34 60.5833 34H17.4167C8.90228 34 2 26.8366 2 18C2 9.16344 8.90228 2 17.4167 2H39.0195",
	width: 78,
	height: 36,
	strokeWidth: 4,
	typography: "LabelMedium"
}), h(d, u.small, {
	d: "M32 1H51.6271C57.9082 1 63 6.37258 63 13C63 19.6274 57.9082 25 51.6271 25H12.3729C6.09181 25 1 19.6274 1 13C1 6.37258 6.09181 1 12.3729 1H32.0195",
	width: 64,
	height: 26,
	strokeWidth: 2,
	typography: "LabelSmall"
}), d), w = e("div", function(e) {
	var t = e.$size, n = e.$inline;
	return {
		width: C[t].width + "px",
		height: C[t].height + "px",
		position: "relative",
		display: n ? "inline-flex" : "flex",
		alignItems: "center",
		justifyContent: "center"
	};
});
w.displayName = "StyledProgressBarRoundedRoot", w.displayName = "StyledProgressBarRoundedRoot";
var T = e("svg", function(e) {
	var t = e.$size;
	return {
		width: C[t].width + "px",
		height: C[t].height + "px",
		position: "absolute",
		fill: "none"
	};
});
T.displayName = "_StyledProgressBarRoundedSvg", T.displayName = "_StyledProgressBarRoundedSvg", c(T, function(e) {
	return function(t) {
		return /* @__PURE__ */ l.createElement(e, f({
			viewBox: `0 0 ${C[t.$size].width} ${C[t.$size].height}`,
			xmlns: "http://www.w3.org/2000/svg"
		}, t));
	};
});
var E = e("path", function(e) {
	var t = e.$theme, n = e.$size;
	return {
		stroke: t.colors.backgroundTertiary,
		strokeWidth: C[n].strokeWidth + "px"
	};
});
E.displayName = "_StyledProgressBarRoundedTrackBackground", E.displayName = "_StyledProgressBarRoundedTrackBackground", c(E, function(e) {
	return function(t) {
		return /* @__PURE__ */ l.createElement(e, f({ d: C[t.$size].d }, t));
	};
});
var D = e("path", function(e) {
	var t = e.$theme, n = e.$size, r = e.$visible, i = e.$pathLength, a = e.$pathProgress;
	return {
		visibility: r ? "visible" : "hidden",
		stroke: t.colors.borderAccent,
		strokeWidth: C[n].strokeWidth + "px",
		strokeDasharray: i,
		strokeDashoffset: i * (1 - a) + ""
	};
});
D.displayName = "_StyledProgressBarRoundedTrackForeground", D.displayName = "_StyledProgressBarRoundedTrackForeground", c(D, function(e) {
	return function(t) {
		return /* @__PURE__ */ l.createElement(e, f({ d: C[t.$size].d }, t));
	};
});
var O = e("div", function(e) {
	var t = e.$theme, n = e.$size;
	return m({ color: t.colors.contentPrimary }, t.typography[C[n].typography]);
});
O.displayName = "StyledProgressBarRoundedText", O.displayName = "StyledProgressBarRoundedText";
function k(e) {
	"@babel/helpers - typeof";
	return k = typeof Symbol == "function" && typeof Symbol.iterator == "symbol" ? function(e) {
		return typeof e;
	} : function(e) {
		return e && typeof Symbol == "function" && e.constructor === Symbol && e !== Symbol.prototype ? "symbol" : typeof e;
	}, k(e);
}
var A = [
	"overrides",
	"getProgressLabel",
	"value",
	"size",
	"steps",
	"successValue",
	"minValue",
	"maxValue",
	"showLabel",
	"infinite",
	"errorMessage",
	"forwardedRef"
];
function j() {
	return j = Object.assign ? Object.assign.bind() : function(e) {
		for (var t = 1; t < arguments.length; t++) {
			var n = arguments[t];
			for (var r in n) Object.prototype.hasOwnProperty.call(n, r) && (e[r] = n[r]);
		}
		return e;
	}, j.apply(this, arguments);
}
function M(e, t) {
	return L(e) || I(e, t) || P(e, t) || N();
}
function N() {
	throw TypeError("Invalid attempt to destructure non-iterable instance.\nIn order to be iterable, non-array objects must have a [Symbol.iterator]() method.");
}
function P(e, t) {
	if (e) {
		if (typeof e == "string") return F(e, t);
		var n = Object.prototype.toString.call(e).slice(8, -1);
		if (n === "Object" && e.constructor && (n = e.constructor.name), n === "Map" || n === "Set") return Array.from(e);
		if (n === "Arguments" || /^(?:Ui|I)nt(?:8|16|32)(?:Clamped)?Array$/.test(n)) return F(e, t);
	}
}
function F(e, t) {
	(t == null || t > e.length) && (t = e.length);
	for (var n = 0, r = Array(t); n < t; n++) r[n] = e[n];
	return r;
}
function I(e, t) {
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
function L(e) {
	if (Array.isArray(e)) return e;
}
function R(e, t) {
	if (e == null) return {};
	var n = z(e, t), r, i;
	if (Object.getOwnPropertySymbols) {
		var a = Object.getOwnPropertySymbols(e);
		for (i = 0; i < a.length; i++) r = a[i], !(t.indexOf(r) >= 0) && Object.prototype.propertyIsEnumerable.call(e, r) && (n[r] = e[r]);
	}
	return n;
}
function z(e, t) {
	if (e == null) return {};
	var n = {}, r = Object.keys(e), i, a;
	for (a = 0; a < r.length; a++) i = r[a], !(t.indexOf(i) >= 0) && (n[i] = e[i]);
	return n;
}
function B(e, t) {
	if (!(e instanceof t)) throw TypeError("Cannot call a class as a function");
}
function V(e, t) {
	for (var n = 0; n < t.length; n++) {
		var r = t[n];
		r.enumerable = r.enumerable || !1, r.configurable = !0, "value" in r && (r.writable = !0), Object.defineProperty(e, r.key, r);
	}
}
function H(e, t, n) {
	return t && V(e.prototype, t), Object.defineProperty(e, "prototype", { writable: !1 }), e;
}
function U(e, t) {
	if (typeof t != "function" && t !== null) throw TypeError("Super expression must either be null or a function");
	e.prototype = Object.create(t && t.prototype, { constructor: {
		value: e,
		writable: !0,
		configurable: !0
	} }), Object.defineProperty(e, "prototype", { writable: !1 }), t && W(e, t);
}
function W(e, t) {
	return W = Object.setPrototypeOf ? Object.setPrototypeOf.bind() : function(e, t) {
		return e.__proto__ = t, e;
	}, W(e, t);
}
function G(e) {
	var t = J();
	return function() {
		var n = Y(e), r;
		if (t) {
			var i = Y(this).constructor;
			r = Reflect.construct(n, arguments, i);
		} else r = n.apply(this, arguments);
		return K(this, r);
	};
}
function K(e, t) {
	if (t && (k(t) === "object" || typeof t == "function")) return t;
	if (t !== void 0) throw TypeError("Derived constructors may only return object or undefined");
	return q(e);
}
function q(e) {
	if (e === void 0) throw ReferenceError("this hasn't been initialised - super() hasn't been called");
	return e;
}
function J() {
	if (typeof Reflect > "u" || !Reflect.construct || Reflect.construct.sham) return !1;
	if (typeof Proxy == "function") return !0;
	try {
		return Boolean.prototype.valueOf.call(Reflect.construct(Boolean, [], function() {})), !0;
	} catch {
		return !1;
	}
}
function Y(e) {
	return Y = Object.setPrototypeOf ? Object.getPrototypeOf.bind() : function(e) {
		return e.__proto__ || Object.getPrototypeOf(e);
	}, Y(e);
}
function X(e, t, n) {
	return t in e ? Object.defineProperty(e, t, {
		value: n,
		enumerable: !0,
		configurable: !0,
		writable: !0
	}) : e[t] = n, e;
}
var Z = /* @__PURE__ */ function(e) {
	U(n, e);
	var t = G(n);
	function n() {
		return B(this, n), t.apply(this, arguments);
	}
	return H(n, [{
		key: "componentDidMount",
		value: function() {}
	}, {
		key: "render",
		value: function() {
			var e = this.props, t = e.overrides, n = t === void 0 ? {} : t, r = e.getProgressLabel, i = e.value, a = e.size, o = e.steps, c = e.successValue, u = e.minValue, d = e.maxValue, f = e.showLabel, p = e.infinite, m = e.errorMessage, h = e.forwardedRef, g = R(e, A), C = this.props["aria-label"] || this.props.ariaLabel, w = d === 100 ? c : d, T = M(s(n.Root, _), 2), E = T[0], D = T[1], O = M(s(n.BarContainer, v), 2), k = O[0], N = O[1], P = M(s(n.Bar, y), 2), F = P[0], I = P[1], L = M(s(n.BarProgress, b), 2), z = L[0], B = L[1], V = M(s(n.Label, S), 2), H = V[0], U = V[1], W = M(s(n.InfiniteBar, x), 2), G = W[0], K = W[1], q = {
				$infinite: p,
				$size: a,
				$steps: o,
				$successValue: w,
				$minValue: u,
				$maxValue: w,
				$value: i
			};
			function J() {
				for (var e = [], t = 0; t < o; t++) e.push(/* @__PURE__ */ l.createElement(F, j({ key: t }, q, I), /* @__PURE__ */ l.createElement(z, j({ $index: t }, q, B))));
				return e;
			}
			return /* @__PURE__ */ l.createElement(E, j({
				ref: h,
				"data-baseweb": "progress-bar",
				role: "progressbar",
				"aria-label": C || r(i, w, u),
				"aria-valuenow": p ? null : i,
				"aria-valuemin": p ? null : u,
				"aria-valuemax": p ? null : w,
				"aria-invalid": m ? !0 : null,
				"aria-errormessage": m
			}, g, q, D), /* @__PURE__ */ l.createElement(k, j({}, q, N), p ? /* @__PURE__ */ l.createElement(l.Fragment, null, /* @__PURE__ */ l.createElement(G, j({
				$isLeft: !0,
				$size: q.$size
			}, K)), /* @__PURE__ */ l.createElement(G, j({ $size: q.$size }, K))) : J()), f && /* @__PURE__ */ l.createElement(H, j({}, q, U), r(i, w, u)));
		}
	}]), n;
}(l.Component);
X(Z, "defaultProps", {
	getProgressLabel: function(e, t, n) {
		return `${Math.round((e - n) / (t - n) * 100)}% Loaded`;
	},
	infinite: !1,
	overrides: {},
	showLabel: !1,
	size: u.medium,
	steps: 1,
	successValue: 100,
	minValue: 0,
	maxValue: 100,
	value: 0
});
var Q = /* @__PURE__ */ l.forwardRef(function(e, t) {
	return /* @__PURE__ */ l.createElement(Z, j({ forwardedRef: t }, e));
});
Q.displayName = "ProgressBar";
var $ = /* @__PURE__ */ ((e) => (e.EXTRASMALL = "xs", e.SMALL = "sm", e))($ || {});
function ee({ value: e, size: t = "sm", overrides: n }) {
	let i = a(), s = {
		xs: i.spacing.twoXS,
		sm: i.spacing.sm,
		md: i.spacing.lg,
		lg: i.spacing.xl,
		xl: i.spacing.twoXL
	}, c = {
		BarContainer: { style: {
			marginTop: i.spacing.none,
			marginBottom: i.spacing.none,
			marginRight: i.spacing.none,
			marginLeft: i.spacing.none
		} },
		Bar: { style: ({ $theme: e }) => ({
			marginTop: i.spacing.none,
			marginBottom: i.spacing.none,
			marginRight: i.spacing.none,
			marginLeft: i.spacing.none,
			height: s[t],
			backgroundColor: e.colors.progressbarTrackFill,
			borderTopLeftRadius: i.spacing.twoXS,
			borderTopRightRadius: i.spacing.twoXS,
			borderBottomLeftRadius: i.spacing.twoXS,
			borderBottomRightRadius: i.spacing.twoXS
		}) },
		BarProgress: { style: () => ({
			backgroundColor: i.colors.secondary,
			borderTopLeftRadius: i.spacing.twoXS,
			borderTopRightRadius: i.spacing.twoXS,
			borderBottomLeftRadius: i.spacing.twoXS,
			borderBottomRightRadius: i.spacing.twoXS
		}) }
	};
	return /* @__PURE__ */ o.jsx(Q, {
		value: e,
		overrides: r(c, n)
	});
}
//#endregion
export { ee as n, $ as t };

//# sourceMappingURL=ProgressBar-DhIwITyC-Bx_UJI5A.js.map