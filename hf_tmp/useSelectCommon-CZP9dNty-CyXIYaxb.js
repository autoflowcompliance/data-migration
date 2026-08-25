import { Cn as e, Da as t, En as n, Gt as r, J as i, Ka as a, Lr as o, Pt as s, Qt as c, Tt as l, Ua as u, Ur as d, Vr as f, Wt as p, Zr as m, _r as h, _t as g, an as _, cn as v, en as y, fr as b, ir as x, ma as S, nn as C, qi as w, qr as T, rn as E, ti as D, tn as O, vr as k, ya as ee } from "./index-Dl4ETd_L-D2oMd1k2.js";
import { t as A } from "./assertThisInitialized-C1dAyb4j-jFURGdZo.js";
import { i as j, r as M } from "./stateful-menu-CW-YE2l8-DNHb-gL3.js";
import { n as N } from "./select-DyvsciAf-DTdJ1yfK.js";
import { t as P } from "./styled-components-Cxzc3DcQ-DbuOYdSx.js";
//#region ../react/build/useSelectCommon-CZP9dNty.js
var F = /* @__PURE__ */ a(u(), 1);
function I(e, t) {
	var n = -1, r = k(e) ? Array(e.length) : [];
	return y(e, function(e, i, a) {
		r[++n] = t(e, i, a);
	}), r;
}
function L(e, t) {
	var n = e.length;
	for (e.sort(t); n--;) e[n] = e[n].value;
	return e;
}
function R(e, t) {
	if (e !== t) {
		var n = e !== void 0, r = e === null, i = e === e, a = m(e), o = t !== void 0, s = t === null, c = t === t, l = m(t);
		if (!s && !l && !a && e > t || a && o && c && !s && !l || r && o && c || !n && c || !i) return 1;
		if (!r && !a && !l && e < t || l && n && i && !r && !a || s && n && i || !o && i || !c) return -1;
	}
	return 0;
}
function te(e, t, n) {
	for (var r = -1, i = e.criteria, a = t.criteria, o = i.length, s = n.length; ++r < o;) {
		var c = R(i[r], a[r]);
		if (c) return r >= s ? c : c * (n[r] == "desc" ? -1 : 1);
	}
	return e.index - t.index;
}
function ne(e, t, n) {
	t = t.length ? c(t, function(e) {
		return h(e) ? function(t) {
			return C(t, e.length === 1 ? e[0] : e);
		} : e;
	}) : [b];
	var r = -1;
	return t = c(t, v(E)), L(I(e, function(e, n, i) {
		return {
			criteria: c(t, function(t) {
				return t(e);
			}),
			index: ++r,
			value: e
		};
	}), function(e, t) {
		return te(e, t, n);
	});
}
var re = _(function(e, t) {
	if (e == null) return [];
	var n = t.length;
	return n > 1 && o(e, t[0], t[1]) ? t = [] : n > 2 && o(t[0], t[1], t[2]) && (t = [t[0]]), ne(e, O(t), []);
}), z = Number.isNaN || function(e) {
	return typeof e == "number" && e !== e;
};
function ie(e, t) {
	return !!(e === t || z(e) && z(t));
}
function ae(e, t) {
	if (e.length !== t.length) return !1;
	for (var n = 0; n < e.length; n++) if (!ie(e[n], t[n])) return !1;
	return !0;
}
function B(e, t) {
	t === void 0 && (t = ae);
	var n, r = [], i, a = !1;
	function o() {
		var o = [...arguments];
		return a && n === this && t(o, r) || (i = e.apply(this, o), a = !0, n = this, r = o), i;
	}
	return o;
}
var V = typeof performance == "object" && typeof performance.now == "function" ? function() {
	return performance.now();
} : function() {
	return Date.now();
};
function H(e) {
	cancelAnimationFrame(e.id);
}
function U(e, t) {
	var n = V();
	function r() {
		V() - n >= t ? e.call(null) : i.id = requestAnimationFrame(r);
	}
	var i = { id: requestAnimationFrame(r) };
	return i;
}
var W = -1;
function G(e) {
	if (e === void 0 && (e = !1), W === -1 || e) {
		var t = document.createElement("div"), n = t.style;
		n.width = "50px", n.height = "50px", n.overflow = "scroll", document.body.appendChild(t), W = t.offsetWidth - t.clientWidth, document.body.removeChild(t);
	}
	return W;
}
var K = null;
function q(e) {
	if (e === void 0 && (e = !1), K === null || e) {
		var t = document.createElement("div"), n = t.style;
		n.width = "50px", n.height = "50px", n.overflow = "scroll", n.direction = "rtl";
		var r = document.createElement("div"), i = r.style;
		return i.width = "100px", i.height = "100px", t.appendChild(r), document.body.appendChild(t), t.scrollLeft > 0 ? K = "positive-descending" : (t.scrollLeft = 1, K = t.scrollLeft === 0 ? "negative" : "positive-ascending"), document.body.removeChild(t), K;
	}
	return K;
}
var J = 150, oe = function(e, t) {
	return e;
};
function se(e) {
	var t, n = e.getItemOffset, i = e.getEstimatedTotalSize, a = e.getItemSize, o = e.getOffsetForIndexAndAlignment, s = e.getStartIndexForOffset, c = e.getStopIndexForStartIndex, l = e.initInstanceProps, u = e.shouldResetStyleCacheOnItemSizeChange, d = e.validateProps;
	return t = /* @__PURE__ */ function(e) {
		r(t, e);
		function t(t) {
			var r;
			return r = e.call(this, t) || this, r._instanceProps = l(r.props, A(r)), r._outerRef = void 0, r._resetIsScrollingTimeoutId = null, r.state = {
				instance: A(r),
				isScrolling: !1,
				scrollDirection: "forward",
				scrollOffset: typeof r.props.initialScrollOffset == "number" ? r.props.initialScrollOffset : 0,
				scrollUpdateWasRequested: !1
			}, r._callOnItemsRendered = void 0, r._callOnItemsRendered = B(function(e, t, n, i) {
				return r.props.onItemsRendered({
					overscanStartIndex: e,
					overscanStopIndex: t,
					visibleStartIndex: n,
					visibleStopIndex: i
				});
			}), r._callOnScroll = void 0, r._callOnScroll = B(function(e, t, n) {
				return r.props.onScroll({
					scrollDirection: e,
					scrollOffset: t,
					scrollUpdateWasRequested: n
				});
			}), r._getItemStyle = void 0, r._getItemStyle = function(e) {
				var t = r.props, i = t.direction, o = t.itemSize, s = t.layout, c = r._getItemStyleCache(u && o, u && s, u && i), l;
				if (c.hasOwnProperty(e)) l = c[e];
				else {
					var d = n(r.props, e, r._instanceProps), f = a(r.props, e, r._instanceProps), p = i === "horizontal" || s === "horizontal", m = i === "rtl", h = p ? d : 0;
					c[e] = l = {
						position: "absolute",
						left: m ? void 0 : h,
						right: m ? h : void 0,
						top: p ? 0 : d,
						height: p ? "100%" : f,
						width: p ? f : "100%"
					};
				}
				return l;
			}, r._getItemStyleCache = void 0, r._getItemStyleCache = B(function(e, t, n) {
				return {};
			}), r._onScrollHorizontal = function(e) {
				var t = e.currentTarget, n = t.clientWidth, i = t.scrollLeft, a = t.scrollWidth;
				r.setState(function(e) {
					if (e.scrollOffset === i) return null;
					var t = r.props.direction, o = i;
					if (t === "rtl") switch (q()) {
						case "negative":
							o = -i;
							break;
						case "positive-descending":
							o = a - n - i;
							break;
					}
					return o = Math.max(0, Math.min(o, a - n)), {
						isScrolling: !0,
						scrollDirection: e.scrollOffset < o ? "forward" : "backward",
						scrollOffset: o,
						scrollUpdateWasRequested: !1
					};
				}, r._resetIsScrollingDebounced);
			}, r._onScrollVertical = function(e) {
				var t = e.currentTarget, n = t.clientHeight, i = t.scrollHeight, a = t.scrollTop;
				r.setState(function(e) {
					if (e.scrollOffset === a) return null;
					var t = Math.max(0, Math.min(a, i - n));
					return {
						isScrolling: !0,
						scrollDirection: e.scrollOffset < t ? "forward" : "backward",
						scrollOffset: t,
						scrollUpdateWasRequested: !1
					};
				}, r._resetIsScrollingDebounced);
			}, r._outerRefSetter = function(e) {
				var t = r.props.outerRef;
				r._outerRef = e, typeof t == "function" ? t(e) : typeof t == "object" && t && t.hasOwnProperty("current") && (t.current = e);
			}, r._resetIsScrollingDebounced = function() {
				r._resetIsScrollingTimeoutId !== null && H(r._resetIsScrollingTimeoutId), r._resetIsScrollingTimeoutId = U(r._resetIsScrolling, J);
			}, r._resetIsScrolling = function() {
				r._resetIsScrollingTimeoutId = null, r.setState({ isScrolling: !1 }, function() {
					r._getItemStyleCache(-1, null);
				});
			}, r;
		}
		t.getDerivedStateFromProps = function(e, t) {
			return ce(e, t), d(e), null;
		};
		var f = t.prototype;
		return f.scrollTo = function(e) {
			e = Math.max(0, e), this.setState(function(t) {
				return t.scrollOffset === e ? null : {
					scrollDirection: t.scrollOffset < e ? "forward" : "backward",
					scrollOffset: e,
					scrollUpdateWasRequested: !0
				};
			}, this._resetIsScrollingDebounced);
		}, f.scrollToItem = function(e, t) {
			t === void 0 && (t = "auto");
			var n = this.props, r = n.itemCount, i = n.layout, a = this.state.scrollOffset;
			e = Math.max(0, Math.min(e, r - 1));
			var s = 0;
			if (this._outerRef) {
				var c = this._outerRef;
				s = i === "vertical" ? c.scrollWidth > c.clientWidth ? G() : 0 : c.scrollHeight > c.clientHeight ? G() : 0;
			}
			this.scrollTo(o(this.props, e, t, a, this._instanceProps, s));
		}, f.componentDidMount = function() {
			var e = this.props, t = e.direction, n = e.initialScrollOffset, r = e.layout;
			if (typeof n == "number" && this._outerRef != null) {
				var i = this._outerRef;
				t === "horizontal" || r === "horizontal" ? i.scrollLeft = n : i.scrollTop = n;
			}
			this._callPropsCallbacks();
		}, f.componentDidUpdate = function() {
			var e = this.props, t = e.direction, n = e.layout, r = this.state, i = r.scrollOffset;
			if (r.scrollUpdateWasRequested && this._outerRef != null) {
				var a = this._outerRef;
				if (t === "horizontal" || n === "horizontal") if (t === "rtl") switch (q()) {
					case "negative":
						a.scrollLeft = -i;
						break;
					case "positive-ascending":
						a.scrollLeft = i;
						break;
					default:
						var o = a.clientWidth;
						a.scrollLeft = a.scrollWidth - o - i;
						break;
				}
				else a.scrollLeft = i;
				else a.scrollTop = i;
			}
			this._callPropsCallbacks();
		}, f.componentWillUnmount = function() {
			this._resetIsScrollingTimeoutId !== null && H(this._resetIsScrollingTimeoutId);
		}, f.render = function() {
			var e = this.props, t = e.children, n = e.className, r = e.direction, a = e.height, o = e.innerRef, s = e.innerElementType, c = e.innerTagName, l = e.itemCount, u = e.itemData, d = e.itemKey, f = d === void 0 ? oe : d, m = e.layout, h = e.outerElementType, g = e.outerTagName, _ = e.style, v = e.useIsScrolling, y = e.width, b = this.state.isScrolling, x = r === "horizontal" || m === "horizontal", S = x ? this._onScrollHorizontal : this._onScrollVertical, C = this._getRangeToRender(), w = C[0], T = C[1], E = [];
			if (l > 0) for (var D = w; D <= T; D++) E.push((0, F.createElement)(t, {
				data: u,
				key: f(D, u),
				index: D,
				isScrolling: v ? b : void 0,
				style: this._getItemStyle(D)
			}));
			var O = i(this.props, this._instanceProps);
			return (0, F.createElement)(h || g || "div", {
				className: n,
				onScroll: S,
				ref: this._outerRefSetter,
				style: p({
					position: "relative",
					height: a,
					width: y,
					overflow: "auto",
					WebkitOverflowScrolling: "touch",
					willChange: "transform",
					direction: r
				}, _)
			}, (0, F.createElement)(s || c || "div", {
				children: E,
				ref: o,
				style: {
					height: x ? "100%" : O,
					pointerEvents: b ? "none" : void 0,
					width: x ? O : "100%"
				}
			}));
		}, f._callPropsCallbacks = function() {
			if (typeof this.props.onItemsRendered == "function" && this.props.itemCount > 0) {
				var e = this._getRangeToRender(), t = e[0], n = e[1], r = e[2], i = e[3];
				this._callOnItemsRendered(t, n, r, i);
			}
			if (typeof this.props.onScroll == "function") {
				var a = this.state, o = a.scrollDirection, s = a.scrollOffset, c = a.scrollUpdateWasRequested;
				this._callOnScroll(o, s, c);
			}
		}, f._getRangeToRender = function() {
			var e = this.props, t = e.itemCount, n = e.overscanCount, r = this.state, i = r.isScrolling, a = r.scrollDirection, o = r.scrollOffset;
			if (t === 0) return [
				0,
				0,
				0,
				0
			];
			var l = s(this.props, o, this._instanceProps), u = c(this.props, l, o, this._instanceProps), d = !i || a === "backward" ? Math.max(1, n) : 1, f = !i || a === "forward" ? Math.max(1, n) : 1;
			return [
				Math.max(0, l - d),
				Math.max(0, Math.min(t - 1, u + f)),
				l,
				u
			];
		}, t;
	}(F.PureComponent), t.defaultProps = {
		direction: "ltr",
		itemData: void 0,
		layout: "vertical",
		overscanCount: 2,
		useIsScrolling: !1
	}, t;
}
var ce = function(e, t) {
	e.children, e.direction, e.height, e.layout, e.innerTagName, e.outerTagName, e.width, t.instance;
}, le = /* @__PURE__ */ se({
	getItemOffset: function(e, t) {
		return t * e.itemSize;
	},
	getItemSize: function(e, t) {
		return e.itemSize;
	},
	getEstimatedTotalSize: function(e) {
		var t = e.itemCount;
		return e.itemSize * t;
	},
	getOffsetForIndexAndAlignment: function(e, t, n, r, i, a) {
		var o = e.direction, s = e.height, c = e.itemCount, l = e.itemSize, u = e.layout, d = e.width, f = o === "horizontal" || u === "horizontal" ? d : s, p = Math.max(0, c * l - f), m = Math.min(p, t * l), h = Math.max(0, t * l - f + l + a);
		switch (n === "smart" && (n = r >= h - f && r <= m + f ? "auto" : "center"), n) {
			case "start": return m;
			case "end": return h;
			case "center":
				var g = Math.round(h + (m - h) / 2);
				return g < Math.ceil(f / 2) ? 0 : g > p + Math.floor(f / 2) ? p : g;
			default: return r >= h && r <= m ? r : r < h ? h : m;
		}
	},
	getStartIndexForOffset: function(e, t) {
		var n = e.itemCount, r = e.itemSize;
		return Math.max(0, Math.min(n - 1, Math.floor(t / r)));
	},
	getStopIndexForStartIndex: function(e, t, n) {
		var r = e.direction, i = e.height, a = e.itemCount, o = e.itemSize, s = e.layout, c = e.width, l = r === "horizontal" || s === "horizontal", u = t * o, d = Math.ceil(((l ? c : i) + n - u) / o);
		return Math.max(0, Math.min(a - 1, t + d - 1));
	},
	initInstanceProps: function(e) {},
	shouldResetStyleCacheOnItemSizeChange: !0,
	validateProps: function(e) {
		e.itemSize;
	}
});
function ue({ content: e, placement: t, children: n, inline: r, style: i }) {
	let a = (0, F.useRef)(null), [o, c] = (0, F.useState)(!1);
	return (0, F.useEffect)(() => {
		let e = a?.current ? a.current.offsetWidth < a.current.scrollWidth : !1;
		e !== o && c(e);
	}, [n, o]), /* @__PURE__ */ D.jsx(s, {
		content: o ? e : "",
		placement: t,
		inline: r,
		children: /* @__PURE__ */ D.jsx(l, { children: /* @__PURE__ */ D.jsx(g, {
			ref: a,
			style: i,
			children: n
		}) })
	});
}
function Y(e) {
	return `max(0px, calc(${e.sizes.tagMarginInsideBorder} - var(--scrollbar-gutter-size, 0px)))`;
}
var de = /* @__PURE__ */ n(N, {
	shouldForwardProp: (e) => T(e) && e !== "$isSelectAll" && e !== "$isCreatable",
	target: "e1811lun0"
})(({ theme: e, $isSelectAll: t, $isCreatable: n }) => {
	let r = {
		content: "\"\"",
		position: "absolute",
		left: e.sizes.tagMarginInsideBorder,
		right: Y(e),
		height: e.sizes.borderWidth,
		backgroundColor: e.colors.fadedText10
	};
	return {
		position: "relative",
		display: "flex",
		alignItems: "center",
		margin: e.spacing.none,
		height: e.sizes.dropdownItemHeight,
		paddingTop: e.spacing.none,
		paddingBottom: e.spacing.none,
		paddingLeft: e.sizes.tagMarginInsideBorder,
		paddingRight: Y(e),
		background: "transparent",
		fontWeight: e.fontWeights.normal,
		[`@media (max-width: ${e.breakpoints.md})`]: {
			minHeight: e.sizes.dropdownItemHeight,
			height: "auto !important"
		},
		"&::before": n ? {
			...r,
			top: 0,
			transform: "translateY(-50%)"
		} : void 0,
		"&::after": t ? {
			...r,
			bottom: 0,
			transform: "translateY(50%)"
		} : void 0
	};
}, ""), fe = "__SELECT_ALL__", pe = "__SELECT_MATCHES__";
function me(e) {
	let { data: t, index: n, style: r } = e, { item: a, overrides: o, $isHighlighted: s, ...c } = t[n].props, l = a.isCreatable ? `Add: ${a.label}` : a.label, u = a.id === "__SELECT_ALL__" || a.id === "__SELECT_MATCHES__";
	return /* @__PURE__ */ D.jsx(de, {
		style: r,
		$isSelectAll: u,
		$isCreatable: a.isCreatable,
		...c,
		children: /* @__PURE__ */ D.jsx(P, {
			$isHighlighted: s,
			children: /* @__PURE__ */ D.jsx(ue, {
				content: l,
				placement: i.AUTO,
				children: l
			})
		})
	}, a.value);
}
var X = (0, F.forwardRef)((n, r) => {
	let i = S(), a = ee(), { innerHeight: o } = t(), s = F.Children.toArray(n.children);
	if (!s[0]?.props.item) {
		let e = s[0] ? s[0].props : {};
		return /* @__PURE__ */ D.jsx(j, {
			$style: {
				height: i.sizes.emptyDropdownHeight,
				paddingLeft: i.spacing.none,
				paddingRight: i.spacing.none,
				paddingTop: i.spacing.none,
				paddingBottom: i.spacing.none,
				display: "flex",
				alignItems: "center",
				justifyContent: "center",
				boxShadow: "none",
				overflow: "hidden"
			},
			ref: r,
			"data-testid": "stSelectboxVirtualDropdownEmpty",
			children: /* @__PURE__ */ D.jsx(M, {
				$style: {
					paddingLeft: i.spacing.none,
					paddingRight: i.spacing.none,
					paddingTop: i.spacing.none,
					paddingBottom: i.spacing.none,
					color: i.colors.fadedText60
				},
				...e
			})
		});
	}
	let c = Math.min(e(i.sizes.maxDropdownHeight), o * .7), l = s.length * e(i.sizes.dropdownItemHeight), u = Math.min(c, l), d = l > c ? a : 0, f = e(i.sizes.dropdownItemHeight), p = s.findIndex((e) => e.props.$isHighlighted), m = p > 0 ? Math.max(0, p * f - u / 2 + f / 2) : 0;
	return /* @__PURE__ */ D.jsx(j, {
		ref: r,
		$style: {
			paddingTop: i.spacing.none,
			paddingBottom: i.spacing.none,
			paddingLeft: i.spacing.none,
			paddingRight: i.spacing.none,
			boxShadow: "none"
		},
		"data-testid": "stSelectboxVirtualDropdown",
		children: /* @__PURE__ */ D.jsx(le, {
			width: "100%",
			height: u,
			itemCount: s.length,
			itemData: s,
			itemKey: (e, t) => {
				let { id: n, value: r } = t[e].props.item;
				return n ?? r;
			},
			itemSize: f,
			initialScrollOffset: m,
			style: { "--scrollbar-gutter-size": `${d}px` },
			children: me
		})
	});
});
X.displayName = "VirtualDropdown";
var Z = -Infinity, he = Infinity, ge = -.005, _e = -.005, ve = -.01, ye = 1, be = .9, xe = .8, Q = .7, Se = .6;
function Ce(e) {
	return e.toLowerCase() === e;
}
function we(e) {
	return e.toUpperCase() === e;
}
function Te(e) {
	let t = e.length, n = Array(t), r = "/";
	for (let i = 0; i < t; i++) {
		let t = e[i];
		r === "/" ? n[i] = be : r === "-" || r === "_" || r === " " ? n[i] = xe : r === "." ? n[i] = Se : Ce(r) && we(t) ? n[i] = Q : n[i] = 0, r = t;
	}
	return n;
}
function Ee(e, t, n, r, i = !1) {
	let a = e.length, o = t.length, s = i ? e : e.toLowerCase(), c = i ? t : t.toLowerCase(), l = Te(t);
	for (let e = 0; e < a; e++) {
		n[e] = Array(o), r[e] = Array(o);
		let t = Z, i = e === a - 1 ? _e : ve;
		for (let a = 0; a < o; a++) if (s[e] === c[a]) {
			let o = Z;
			e ? a && (o = Math.max(r[e - 1][a - 1] + l[a], n[e - 1][a - 1] + ye)) : o = a * ge + l[a], n[e][a] = o, r[e][a] = t = Math.max(o, t + i);
		} else n[e][a] = Z, r[e][a] = t += i;
	}
}
function De(e, t, n = !1) {
	let r = e.length, i = t.length;
	if (!r || !i) return Z;
	if (e === t || !n && i === r) return he;
	if (i > 1024) return Z;
	let a = Array(r), o = Array(r);
	return Ee(e, t, a, o, n), o[r - 1][i - 1];
}
function Oe(e, t) {
	e = e.toLowerCase(), t = t.toLowerCase();
	let n = e.length;
	for (let r = 0, i = 0; r < n; r += 1) if (i = t.indexOf(e[r], i) + 1, i === 0) return !1;
	return !0;
}
var $ = (e) => e.toLowerCase();
function ke(e) {
	return e ?? w.SelectWidgetFilterMode.FILTER_MODE_FUZZY;
}
function Ae(e, t) {
	return t ? re(e.filter((e) => Oe(t, e.label)), (e) => -De(t, e.label)) : e;
}
function je(e, t, n) {
	if (!t || n === w.SelectWidgetFilterMode.FILTER_MODE_NONE) return e;
	if (n === w.SelectWidgetFilterMode.FILTER_MODE_FUZZY) return Ae(e, t);
	let r = $(t);
	return n === w.SelectWidgetFilterMode.FILTER_MODE_CONTAINS ? e.filter((e) => $(e.label).includes(r)) : n === w.SelectWidgetFilterMode.FILTER_MODE_PREFIX ? e.filter((e) => $(e.label).startsWith(r)) : e;
}
function Me(e) {
	let { options: t, isMulti: n, acceptNewOptions: r, filterMode: i, placeholderInput: a } = e, o = ke(i), s = (0, F.useMemo)(() => t.map((e, t) => ({
		label: e,
		value: e,
		id: `${e}_${t}`
	})), [t]), { placeholder: c, shouldDisable: l } = (0, F.useMemo)(() => x(a, t, r, n), [
		r,
		n,
		t,
		a
	]), u = t.length > 10;
	return {
		selectOptions: s,
		placeholder: c,
		disabled: l,
		inputReadOnly: o === w.SelectWidgetFilterMode.FILTER_MODE_NONE || f() && !u && !r ? "readonly" : null,
		valueToUiSingle: (0, F.useMemo)(() => (e) => d(e) ? [] : [{
			label: e,
			value: e
		}], []),
		valuesToUiMulti: (0, F.useMemo)(() => (e) => e.map((e) => ({
			label: e,
			value: e
		})), []),
		createFilterOptions: (0, F.useMemo)(() => (e) => (t, n) => je(Array.isArray(e) ? t.filter((t) => !e.includes(t.value)) : t, n, o), [o])
	};
}
//#endregion
export { fe as i, pe as n, X as r, Me as t };

//# sourceMappingURL=useSelectCommon-CZP9dNty-CyXIYaxb.js.map