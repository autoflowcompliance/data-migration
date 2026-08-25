import { $i as e, B as t, Gi as n, J as r, Ka as i, L as a, Ua as o, a as s, b as c, ii as l, ma as u, o as d, pt as f, s as p, ti as m, tr as h, u as g } from "./index-Dl4ETd_L-D2oMd1k2.js";
import { t as _ } from "./WidgetLabel-CQfHGtry-udktvHE5.js";
import { t as v } from "./WidgetLabelHelpIconInline-BTmzKeRa-CZ4j9Xyg.js";
import { n as y } from "./useBasicWidgetState-D3zHnRUK-Dsaz4YO6.js";
//#region ../react/build/ButtonGroup-tARGP97W.js
var b = /* @__PURE__ */ i(o(), 1), x = { secondary: "secondary" }, S = { default: "default" }, C = { default: "default" }, w = Object.freeze({
	radio: "radio",
	checkbox: "checkbox"
}), T = e("div", function(e) {
	var t = e.$shape, n = e.$length, r = e.$theme, i = n === 1 ? void 0 : t === S.default ? "-0.5px" : `-${r.sizing.scale100}`;
	return {
		display: "flex",
		marginLeft: i,
		marginRight: i
	};
});
T.displayName = "StyledRoot", T.displayName = "StyledRoot";
function E(e) {
	"@babel/helpers - typeof";
	return E = typeof Symbol == "function" && typeof Symbol.iterator == "symbol" ? function(e) {
		return typeof e;
	} : function(e) {
		return e && typeof Symbol == "function" && e.constructor === Symbol && e !== Symbol.prototype ? "symbol" : typeof e;
	}, E(e);
}
function D() {
	return D = Object.assign ? Object.assign.bind() : function(e) {
		for (var t = 1; t < arguments.length; t++) {
			var n = arguments[t];
			for (var r in n) Object.prototype.hasOwnProperty.call(n, r) && (e[r] = n[r]);
		}
		return e;
	}, D.apply(this, arguments);
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
			W(e, t, n[t]);
		}) : Object.getOwnPropertyDescriptors ? Object.defineProperties(e, Object.getOwnPropertyDescriptors(n)) : O(Object(n)).forEach(function(t) {
			Object.defineProperty(e, t, Object.getOwnPropertyDescriptor(n, t));
		});
	}
	return e;
}
function A(e, t) {
	return P(e) || ee(e, t) || M(e, t) || j();
}
function j() {
	throw TypeError("Invalid attempt to destructure non-iterable instance.\nIn order to be iterable, non-array objects must have a [Symbol.iterator]() method.");
}
function M(e, t) {
	if (e) {
		if (typeof e == "string") return N(e, t);
		var n = Object.prototype.toString.call(e).slice(8, -1);
		if (n === "Object" && e.constructor && (n = e.constructor.name), n === "Map" || n === "Set") return Array.from(e);
		if (n === "Arguments" || /^(?:Ui|I)nt(?:8|16|32)(?:Clamped)?Array$/.test(n)) return N(e, t);
	}
}
function N(e, t) {
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
function P(e) {
	if (Array.isArray(e)) return e;
}
function F(e, t) {
	if (!(e instanceof t)) throw TypeError("Cannot call a class as a function");
}
function I(e, t) {
	for (var n = 0; n < t.length; n++) {
		var r = t[n];
		r.enumerable = r.enumerable || !1, r.configurable = !0, "value" in r && (r.writable = !0), Object.defineProperty(e, r.key, r);
	}
}
function L(e, t, n) {
	return t && I(e.prototype, t), Object.defineProperty(e, "prototype", { writable: !1 }), e;
}
function R(e, t) {
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
function te(e) {
	var t = H();
	return function() {
		var n = U(e), r;
		if (t) {
			var i = U(this).constructor;
			r = Reflect.construct(n, arguments, i);
		} else r = n.apply(this, arguments);
		return B(this, r);
	};
}
function B(e, t) {
	if (t && (E(t) === "object" || typeof t == "function")) return t;
	if (t !== void 0) throw TypeError("Derived constructors may only return object or undefined");
	return V(e);
}
function V(e) {
	if (e === void 0) throw ReferenceError("this hasn't been initialised - super() hasn't been called");
	return e;
}
function H() {
	if (typeof Reflect > "u" || !Reflect.construct || Reflect.construct.sham) return !1;
	if (typeof Proxy == "function") return !0;
	try {
		return Boolean.prototype.valueOf.call(Reflect.construct(Boolean, [], function() {})), !0;
	} catch {
		return !1;
	}
}
function U(e) {
	return U = Object.setPrototypeOf ? Object.getPrototypeOf.bind() : function(e) {
		return e.__proto__ || Object.getPrototypeOf(e);
	}, U(e);
}
function W(e, t, n) {
	return t in e ? Object.defineProperty(e, t, {
		value: n,
		enumerable: !0,
		configurable: !0,
		writable: !0
	}) : e[t] = n, e;
}
function G(e, t) {
	return !Array.isArray(e) && typeof e != "number" ? !1 : Array.isArray(e) ? e.includes(t) : e === t;
}
var K = /* @__PURE__ */ function(e) {
	R(r, e);
	var n = te(r);
	function r() {
		var e;
		F(this, r);
		var t = [...arguments];
		return e = n.call.apply(n, [this].concat(t)), W(V(e), "childRefs", {}), e;
	}
	return L(r, [{
		key: "render",
		value: function() {
			var e = this, n = this.props, r = n.overrides, i = r === void 0 ? {} : r, a = n.mode, o = a === void 0 ? w.checkbox : a, s = n.children, c = n.selected, l = n.disabled, u = n.onClick, d = n.kind, f = n.shape, p = n.size, m = A(h(i.Root, T), 2), g = m[0], _ = m[1], v = this.props["aria-label"] || this.props.ariaLabel, y = o === w.radio, x = b.Children.count(s);
			return /* @__PURE__ */ b.createElement(t.Consumer, null, function(t) {
				return /* @__PURE__ */ b.createElement(g, D({
					"aria-label": v || t.buttongroup.ariaLabel,
					"data-baseweb": "button-group",
					role: y ? "radiogroup" : "group",
					$shape: f,
					$length: s.length
				}, _), b.Children.map(s, function(t, n) {
					if (!/* @__PURE__ */ b.isValidElement(t)) return null;
					var r = t.props.isSelected ? t.props.isSelected : G(c, n);
					return y && (e.childRefs[n] = /* @__PURE__ */ b.createRef()), /* @__PURE__ */ b.cloneElement(t, {
						disabled: l || t.props.disabled,
						isSelected: r,
						ref: y ? e.childRefs[n] : void 0,
						tabIndex: !y || r || y && (!c || c === -1) && n === 0 ? 0 : -1,
						onKeyDown: function(t) {
							if (y) {
								var n = Number(c) ? Number(c) : 0;
								if (t.key === "ArrowUp" || t.key === "ArrowLeft") {
									t.preventDefault && t.preventDefault();
									var r = n - 1 < 0 ? x - 1 : n - 1;
									u && u(t, r), e.childRefs[r].current && e.childRefs[r].current.focus();
								}
								if (t.key === "ArrowDown" || t.key === "ArrowRight") {
									t.preventDefault && t.preventDefault();
									var i = n + 1 > x - 1 ? 0 : n + 1;
									u && u(t, i), e.childRefs[i].current && e.childRefs[i].current.focus();
								}
							}
						},
						kind: d,
						onClick: function(e) {
							l || (t.props.onClick && t.props.onClick(e), u && u(e, n));
						},
						shape: f,
						size: p,
						overrides: k({ BaseButton: {
							style: function(e) {
								var t = e.$theme;
								return s.length === 1 ? {} : f === S.default ? {
									marginLeft: "0.5px",
									marginRight: "0.5px"
								} : {
									marginLeft: t.sizing.scale100,
									marginRight: t.sizing.scale100
								};
							},
							props: {
								"aria-checked": r,
								role: y ? "radio" : "checkbox"
							}
						} }, t.props.overrides)
					});
				}));
			});
		}
	}]), r;
}(b.Component);
W(K, "defaultProps", {
	disabled: !1,
	onClick: function() {},
	shape: S.default,
	size: C.default,
	kind: x.secondary
});
function q(e) {
	let t = e.contentIcon, n = e.content ?? "";
	return t ? `${t} ${n}`.trim() : n;
}
function J(e, t) {
	for (let n = e.length - 1; n >= 0; n--) if (q(e[n]) === t) return n;
	return -1;
}
function Y(e, t) {
	let n = [];
	for (let r of t) {
		let t = J(e, r);
		t >= 0 && n.push(t);
	}
	return n;
}
function X(e, t) {
	return t.includes(e) ? t.filter((t) => t !== e) : [...t, e];
}
function Z(e, t, n, r) {
	return e === g.ClickMode.MULTI_SELECT ? X(t, n) : r && n.includes(t) ? n : n.includes(t) ? [] : [t];
}
function ne(e) {
	switch (e) {
		case g.ClickMode.SINGLE_SELECT: return w.radio;
		case g.ClickMode.MULTI_SELECT: return w.checkbox;
		default: return;
	}
}
function re(e) {
	return e.length === 0 ? -1 : e[0];
}
function ie(e, t) {
	return e.getStringArrayValue(t);
}
function ae(e) {
	return (e.default ?? []).map((t) => {
		let n = e.options[t];
		return n ? q(n) : "";
	}).filter((e) => e !== "");
}
function oe(e) {
	return e.rawValues ?? [];
}
function se(e, t, n, r) {
	t.setStringArrayValue(e, n.value, { fromUi: n.fromUi }, r);
}
function Q(e, t, n) {
	let r = n === g.Style.PILLS ? d.PILLS : d.SEGMENTED_CONTROL;
	return {
		element: /* @__PURE__ */ m.jsx(c, {
			icon: t,
			label: e,
			iconSize: "base",
			useSmallerFont: !0
		}),
		kind: r,
		size: p.MEDIUM
	};
}
function ce(e, t) {
	return e && (t = `${t}Active`), t;
}
function le(e, t, n) {
	let r = {
		flexWrap: "wrap",
		maxWidth: n ? "100%" : "fit-content",
		margin: "0 0"
	}, i = n ? "100%" : "auto";
	switch (e) {
		case g.Style.PILLS: return {
			...r,
			columnGap: t.twoXS,
			rowGap: t.twoXS,
			width: i
		};
		case g.Style.SEGMENTED_CONTROL: return {
			...r,
			columnGap: t.none,
			rowGap: t.twoXS,
			width: i
		};
		default: return r;
	}
}
function $(e, t, n, r, i) {
	let a = n.includes(t);
	return (0, b.forwardRef)(function(t, n) {
		let { element: o, kind: c, size: l } = Q(e.content ?? "", e.contentIcon ?? void 0, r), u = ce(a, c);
		return /* @__PURE__ */ m.jsx(s, {
			...t,
			size: l,
			kind: u,
			containerWidth: i,
			children: o
		});
	});
}
function ue(e) {
	let { disabled: t, element: i, fragmentId: o, widgetMgr: s, widthConfig: c } = e, { clickMode: d, options: p, style: h, label: x, labelVisibility: S, help: C, required: w } = i, T = u(), [E, D] = y({
		getStateFromWidgetMgr: ie,
		getDefaultStateFromProto: ae,
		getCurrStateFromProto: oe,
		updateWidgetMgrState: se,
		element: i,
		widgetMgr: s,
		fragmentId: o,
		formClearBehavior: "resetValueOnly",
		queryParamBinding: i.queryParamKey ? {
			paramKey: i.queryParamKey,
			valueType: "string_array_value",
			clearable: !0,
			urlFormat: "repeated"
		} : void 0
	}), O = (0, b.useMemo)(() => Y(p, E), [p, E]), k = n(c), A = (0, b.useCallback)((e, t) => {
		let n = Z(d, q(p[t]), E, w);
		n !== E && D({
			value: n,
			fromUi: !0
		});
	}, [
		d,
		p,
		E,
		w,
		D
	]), j = ne(d), M = (0, b.useMemo)(() => p.map((e, t) => {
		let n = $(e, t, O, h, k);
		return /* @__PURE__ */ m.jsx(n, {}, `${e.content}-${t}`);
	}), [
		p,
		h,
		O,
		k
	]);
	return /* @__PURE__ */ m.jsxs(f, {
		className: "stButtonGroup",
		"data-testid": "stButtonGroup",
		containerWidth: k,
		children: [/* @__PURE__ */ m.jsx(_, {
			label: x,
			disabled: t,
			labelVisibility: l(S?.value ?? a.LabelVisibilityOptions.COLLAPSED),
			children: C && /* @__PURE__ */ m.jsx(v, {
				content: C,
				placement: r.TOP,
				label: x
			})
		}), /* @__PURE__ */ m.jsx(K, {
			disabled: t,
			mode: j,
			onClick: A,
			selected: d === g.ClickMode.MULTI_SELECT ? O : re(O),
			overrides: { Root: {
				props: { "aria-required": w || void 0 },
				style: (0, b.useCallback)(() => le(h, T.spacing, k), [
					h,
					T.spacing,
					k
				])
			} },
			children: M
		})]
	});
}
var de = (0, b.memo)(ue);
//#endregion
export { de as default, Q as getContentElement };

//# sourceMappingURL=ButtonGroup-tARGP97W-xDx3FYwM.js.map