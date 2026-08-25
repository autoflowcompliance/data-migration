import { $i as e, B as t, Ka as n, Ln as r, Rn as i, Ta as a, Ua as o, X as s, fi as c, jr as l, tr as u, za as d } from "./index-Dl4ETd_L-D2oMd1k2.js";
//#region ../react/build/stateful-menu-CW-YE2l8.js
var f = /* @__PURE__ */ n(o(), 1), p = {
	click: "click",
	moveUp: "moveUp",
	moveDown: "moveDown",
	mouseEnter: "mouseEnter",
	focus: "focus",
	reset: "reset",
	character: "character",
	enter: "enter"
}, m = {
	ArrowUp: "ArrowUp",
	ArrowDown: "ArrowDown",
	ArrowLeft: "ArrowLeft",
	ArrowRight: "ArrowRight",
	Enter: "Enter",
	Home: "Home",
	End: "End"
}, h = {
	default: "default",
	compact: "compact"
}, g = ["item"];
function _(e, t) {
	if (e == null) return {};
	var n = v(e, t), r, i;
	if (Object.getOwnPropertySymbols) {
		var a = Object.getOwnPropertySymbols(e);
		for (i = 0; i < a.length; i++) r = a[i], !(t.indexOf(r) >= 0) && Object.prototype.propertyIsEnumerable.call(e, r) && (n[r] = e[r]);
	}
	return n;
}
function v(e, t) {
	if (e == null) return {};
	var n = {}, r = Object.keys(e), i, a;
	for (a = 0; a < r.length; a++) i = r[a], !(t.indexOf(i) >= 0) && (n[i] = e[i]);
	return n;
}
function y(e, t) {
	var n = Object.keys(e);
	if (Object.getOwnPropertySymbols) {
		var r = Object.getOwnPropertySymbols(e);
		t && (r = r.filter(function(t) {
			return Object.getOwnPropertyDescriptor(e, t).enumerable;
		})), n.push.apply(n, r);
	}
	return n;
}
function b(e) {
	for (var t = 1; t < arguments.length; t++) {
		var n = arguments[t] == null ? {} : arguments[t];
		t % 2 ? y(Object(n), !0).forEach(function(t) {
			x(e, t, n[t]);
		}) : Object.getOwnPropertyDescriptors ? Object.defineProperties(e, Object.getOwnPropertyDescriptors(n)) : y(Object(n)).forEach(function(t) {
			Object.defineProperty(e, t, Object.getOwnPropertyDescriptor(n, t));
		});
	}
	return e;
}
function x(e, t, n) {
	return t in e ? Object.defineProperty(e, t, {
		value: n,
		enumerable: !0,
		configurable: !0,
		writable: !0
	}) : e[t] = n, e;
}
var S = e("ul", function(e) {
	var t = e.$theme, n = e.$isFocusVisible;
	return {
		backgroundColor: t.colors.menuFill,
		position: "relative",
		marginTop: 0,
		marginBottom: 0,
		marginLeft: 0,
		marginRight: 0,
		paddingTop: t.sizing.scale300,
		paddingBottom: t.sizing.scale300,
		paddingLeft: 0,
		paddingRight: 0,
		borderTopLeftRadius: t.borders.popoverBorderRadius,
		borderTopRightRadius: t.borders.popoverBorderRadius,
		borderBottomRightRadius: t.borders.popoverBorderRadius,
		borderBottomLeftRadius: t.borders.popoverBorderRadius,
		boxShadow: t.lighting.shadow600,
		overflow: "auto",
		":focus": { outline: n ? `3px solid ${t.colors.accent}` : "none" }
	};
});
S.displayName = "StyledList", S.displayName = "StyledList";
function C(e) {
	return e.$disabled ? e.$theme.colors.menuFontDisabled : e.$isHighlighted && e.$isFocused ? e.$theme.colors.menuFontHighlighted : e.$isHighlighted && !e.$isFocused ? e.$theme.colors.menuFontSelected : e.$theme.colors.menuFontDefault;
}
function w(e) {
	return e.$disabled ? "transparent" : e.$isHighlighted ? e.$theme.colors.menuFillHover : "transparent";
}
var T = e("li", function(e) {
	var t = e.$theme, n = e.$size;
	return b(b({}, n === h.compact ? t.typography.font100 : t.typography.font200), {}, {
		position: "relative",
		display: "block",
		color: t.colors.menuFontDisabled,
		textAlign: "center",
		cursor: "not-allowed",
		backgroundColor: "transparent",
		marginBottom: 0,
		paddingTop: t.sizing.scale800,
		paddingBottom: t.sizing.scale800,
		paddingRight: t.sizing.scale800,
		paddingLeft: t.sizing.scale800
	});
});
T.displayName = "StyledEmptyState", T.displayName = "StyledEmptyState";
var E = e("li", function(e) {
	var t = e.$theme.sizing.scale300, n = e.$theme.sizing.scale200;
	return b(b({}, e.$theme.typography.font250), {}, {
		color: e.$theme.colors.contentPrimary,
		paddingTop: n,
		paddingBottom: n,
		paddingRight: t,
		paddingLeft: t
	});
});
E.displayName = "StyledOptgroupHeader", E.displayName = "StyledOptgroupHeader";
var D = e("a", function(e) {
	return {
		display: "block",
		color: C(e)
	};
});
D.displayName = "StyledListItemAnchor", D.displayName = "StyledListItemAnchor";
var O = e("li", function(e) {
	var t = e.$disabled, n = e.$theme, r = e.$size;
	return b(b({}, r === h.compact ? n.typography.font100 : n.typography.font200), {}, {
		boxSizing: "border-box",
		position: "relative",
		display: "block",
		color: C(e),
		cursor: t ? "not-allowed" : "pointer",
		backgroundColor: w(e),
		transitionProperty: "color, background-color",
		transitionDuration: n.animation.timing200,
		transitionTimingFunction: n.animation.easeOutCurve,
		marginBottom: 0,
		paddingTop: r === h.compact ? n.sizing.scale100 : n.sizing.scale300,
		paddingBottom: r === h.compact ? n.sizing.scale100 : n.sizing.scale300,
		paddingRight: r === h.compact ? n.sizing.scale900 : n.sizing.scale600,
		paddingLeft: r === h.compact ? n.sizing.scale900 : n.sizing.scale600,
		":focus": { outline: "none" }
	});
});
O.displayName = "StyledListItemElement", O.displayName = "StyledListItemElement";
var k = d(O, function(e) {
	return (function(t) {
		t.item;
		var n = _(t, g);
		return /* @__PURE__ */ f.createElement(e, n);
	});
}), A = e("li", function(e) {
	var t = e.$theme;
	return {
		position: "relative",
		display: "flex",
		alignItems: "center",
		cursor: "pointer",
		paddingTop: t.sizing.scale300,
		paddingBottom: t.sizing.scale300,
		paddingRight: t.sizing.scale800,
		paddingLeft: t.sizing.scale800,
		transitionProperty: "color, background-color",
		transitionDuration: t.animation.timing200,
		transitionTimingFunction: t.animation.easeOutCurve,
		":hover": { backgroundColor: t.colors.menuFillHover }
	};
});
A.displayName = "StyledListItemProfile", A.displayName = "StyledListItemProfile";
var j = e("div", {
	width: "60px",
	height: "60px",
	display: "flex",
	justifyContent: "center",
	alignItems: "center"
});
j.displayName = "StyledProfileImgContainer", j.displayName = "StyledProfileImgContainer";
var M = e("img", {
	width: "100%",
	height: "100%",
	borderTopLeftRadius: "50%",
	borderTopRightRadius: "50%",
	borderBottomRightRadius: "50%",
	borderBottomLeftRadius: "50%"
});
M.displayName = "StyledProfileImg", M.displayName = "StyledProfileImg";
var N = e("div", function(e) {
	var t = e.$theme, n = t.direction, r = t.sizing;
	return b({
		alignSelf: n === "rtl" ? "flex-end" : "flex-start",
		display: "flex",
		flexDirection: "column"
	}, n === "rtl" ? { marginRight: r.scale600 } : { marginLeft: r.scale600 });
});
N.displayName = "StyledProfileLabelsContainer", N.displayName = "StyledProfileLabelsContainer";
var P = e("h6", function(e) {
	var t = e.$theme;
	return b(b({}, t.typography.font350), {}, {
		color: t.colors.contentPrimary,
		marginTop: 0,
		marginBottom: 0,
		marginLeft: 0,
		marginRight: 0
	});
});
P.displayName = "StyledProfileTitle", P.displayName = "StyledProfileTitle";
var ee = e("p", function(e) {
	var t = e.$theme;
	return b(b({}, t.typography.font200), {}, {
		color: t.colors.contentPrimary,
		marginTop: 0,
		marginBottom: 0,
		marginLeft: 0,
		marginRight: 0
	});
});
ee.displayName = "StyledProfileSubtitle", ee.displayName = "StyledProfileSubtitle";
var F = e("p", function(e) {
	var t = e.$theme;
	return b(b({}, t.typography.font100), {}, {
		color: t.colors.contentPrimary,
		marginTop: 0,
		marginBottom: 0,
		marginLeft: 0,
		marginRight: 0
	});
});
F.displayName = "StyledProfileBody", F.displayName = "StyledProfileBody";
var te = e("li", function(e) {
	var t = e.$theme;
	return {
		color: t.colors.contentPrimary,
		borderBottomWidth: t.borders.border300.borderWidth,
		borderBottomStyle: t.borders.border300.borderStyle,
		borderBottomColor: t.borders.border300.borderColor,
		marginTop: t.sizing.scale100,
		marginBottom: t.sizing.scale100,
		marginLeft: t.sizing.scale500,
		marginRight: t.sizing.scale500,
		listStyle: "none",
		height: 0
	};
});
te.displayName = "StyledMenuDivider", F.displayName = "StyledMenuDivider";
var I = /* @__PURE__ */ f.createContext({
	addMenuToNesting: function() {},
	removeMenuFromNesting: function() {},
	getParentMenu: function() {},
	getChildMenu: function() {},
	nestedMenuHoverIndex: -1,
	isNestedMenuVisible: function() {
		return !1;
	},
	mountRef: { current: null }
});
function L() {
	return L = Object.assign ? Object.assign.bind() : function(e) {
		for (var t = 1; t < arguments.length; t++) {
			var n = arguments[t];
			for (var r in n) Object.prototype.hasOwnProperty.call(n, r) && (e[r] = n[r]);
		}
		return e;
	}, L.apply(this, arguments);
}
function ne(e, t) {
	return oe(e) || ae(e, t) || re(e, t) || R();
}
function R() {
	throw TypeError("Invalid attempt to destructure non-iterable instance.\nIn order to be iterable, non-array objects must have a [Symbol.iterator]() method.");
}
function re(e, t) {
	if (e) {
		if (typeof e == "string") return ie(e, t);
		var n = Object.prototype.toString.call(e).slice(8, -1);
		if (n === "Object" && e.constructor && (n = e.constructor.name), n === "Map" || n === "Set") return Array.from(e);
		if (n === "Arguments" || /^(?:Ui|I)nt(?:8|16|32)(?:Clamped)?Array$/.test(n)) return ie(e, t);
	}
}
function ie(e, t) {
	(t == null || t > e.length) && (t = e.length);
	for (var n = 0, r = Array(t); n < t; n++) r[n] = e[n];
	return r;
}
function ae(e, t) {
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
function oe(e) {
	if (Array.isArray(e)) return e;
}
var se = function(e) {
	if (!e.getChildMenu) return e.children;
	var t = e.getChildMenu(e.item);
	if (!t) return e.children;
	var n = e.overrides, r = ne(u((n === void 0 ? {} : n).ChildMenuPopover, s), 2), i = r[0], a = r[1];
	return /* @__PURE__ */ f.createElement(I.Consumer, null, function(n) {
		return /* @__PURE__ */ f.createElement(i, L({
			focusLock: !1,
			autoFocus: !1,
			isOpen: e.isOpen,
			renderAll: e.renderAll,
			content: t,
			ignoreBoundary: !0,
			mountNode: n.mountRef.current ? n.mountRef.current : void 0,
			onClick: e.onClick,
			onMouseEnterDelay: 30,
			onMouseLeaveDelay: 30,
			onEsc: e.resetParentMenu,
			placement: "rightTop"
		}, a, { overrides: c({ Body: { props: { onKeyDown: function(e) {
			e.keyCode === 9 && e.preventDefault();
		} } } }, a.overrides) }), e.children);
	});
}, z = [
	"getChildMenu",
	"getItemLabel",
	"item",
	"onClick",
	"onMouseEnter",
	"overrides",
	"renderHrefAsAnchor",
	"resetMenu",
	"size",
	"$isHighlighted",
	"renderAll"
];
function B(e, t) {
	var n = Object.keys(e);
	if (Object.getOwnPropertySymbols) {
		var r = Object.getOwnPropertySymbols(e);
		t && (r = r.filter(function(t) {
			return Object.getOwnPropertyDescriptor(e, t).enumerable;
		})), n.push.apply(n, r);
	}
	return n;
}
function ce(e) {
	for (var t = 1; t < arguments.length; t++) {
		var n = arguments[t] == null ? {} : arguments[t];
		t % 2 ? B(Object(n), !0).forEach(function(t) {
			le(e, t, n[t]);
		}) : Object.getOwnPropertyDescriptors ? Object.defineProperties(e, Object.getOwnPropertyDescriptors(n)) : B(Object(n)).forEach(function(t) {
			Object.defineProperty(e, t, Object.getOwnPropertyDescriptor(n, t));
		});
	}
	return e;
}
function le(e, t, n) {
	return t in e ? Object.defineProperty(e, t, {
		value: n,
		enumerable: !0,
		configurable: !0,
		writable: !0
	}) : e[t] = n, e;
}
function V() {
	return V = Object.assign ? Object.assign.bind() : function(e) {
		for (var t = 1; t < arguments.length; t++) {
			var n = arguments[t];
			for (var r in n) Object.prototype.hasOwnProperty.call(n, r) && (e[r] = n[r]);
		}
		return e;
	}, V.apply(this, arguments);
}
function ue(e, t) {
	return he(e) || me(e, t) || fe(e, t) || de();
}
function de() {
	throw TypeError("Invalid attempt to destructure non-iterable instance.\nIn order to be iterable, non-array objects must have a [Symbol.iterator]() method.");
}
function fe(e, t) {
	if (e) {
		if (typeof e == "string") return pe(e, t);
		var n = Object.prototype.toString.call(e).slice(8, -1);
		if (n === "Object" && e.constructor && (n = e.constructor.name), n === "Map" || n === "Set") return Array.from(e);
		if (n === "Arguments" || /^(?:Ui|I)nt(?:8|16|32)(?:Clamped)?Array$/.test(n)) return pe(e, t);
	}
}
function pe(e, t) {
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
	if (e == null) return {};
	var n = _e(e, t), r, i;
	if (Object.getOwnPropertySymbols) {
		var a = Object.getOwnPropertySymbols(e);
		for (i = 0; i < a.length; i++) r = a[i], !(t.indexOf(r) >= 0) && Object.prototype.propertyIsEnumerable.call(e, r) && (n[r] = e[r]);
	}
	return n;
}
function _e(e, t) {
	if (e == null) return {};
	var n = {}, r = Object.keys(e), i, a;
	for (a = 0; a < r.length; a++) i = r[a], !(t.indexOf(i) >= 0) && (n[i] = e[i]);
	return n;
}
function ve(e, n) {
	var r = e.getChildMenu, i = e.getItemLabel, a = i === void 0 ? function(e) {
		return e ? e.label : "";
	} : i, o = e.item, s = e.onClick, c = s === void 0 ? function() {} : s, l = e.onMouseEnter, d = l === void 0 ? function() {} : l, p = e.overrides, m = p === void 0 ? {} : p, g = e.renderHrefAsAnchor, _ = g === void 0 ? !0 : g, v = e.resetMenu, y = v === void 0 ? function() {} : v, b = e.size, x = b === void 0 ? h.default : b, S = e.$isHighlighted, C = e.renderAll, w = ge(e, z), T = ue(u(m.ListItem, k), 2), E = T[0], O = T[1], A = ue(u(m.ListItemAnchor, D), 2), j = A[0], M = A[1], N = function(e) {
		return e.href && _ ? /* @__PURE__ */ f.createElement(j, V({
			$item: e,
			href: e.href
		}, M), a(e)) : /* @__PURE__ */ f.createElement(f.Fragment, null, a(e));
	};
	return /* @__PURE__ */ f.createElement(t.Consumer, null, function(e) {
		return /* @__PURE__ */ f.createElement(se, {
			getChildMenu: r,
			isOpen: !!S,
			item: o,
			resetParentMenu: y,
			renderAll: C,
			onClick: c,
			overrides: m
		}, /* @__PURE__ */ f.createElement(E, V({
			ref: n,
			"aria-label": r && r(o) ? e.menu.parentMenuItemAriaLabel : null,
			item: o,
			onClick: c,
			onMouseEnter: d,
			$size: x,
			$isHighlighted: S
		}, w, O), N(ce({ isHighlighted: S }, o))));
	});
}
function ye(e, t) {
	if (!e || !t) return !1;
	for (var n in e) if (e[n] !== t[n]) return !1;
	return !0;
}
function be(e, t) {
	return e.$isHighlighted === t.$isHighlighted && e.$isFocused === t.$isFocused && ye(e.item, t.item) && ye(e.overrides, t.overrides) && e.size === t.size && e.getItemLabel === t.getItemLabel && e.getChildMenu === t.getChildMenu && e.resetMenu === t.resetMenu;
}
var xe = /* @__PURE__ */ f.forwardRef(ve);
xe.displayName = "OptionList";
var Se = /* @__PURE__ */ f.memo(xe, be), Ce = [
	"disabled",
	"isFocused",
	"isHighlighted",
	"resetMenu"
];
function we(e, t) {
	if (e == null) return {};
	var n = Te(e, t), r, i;
	if (Object.getOwnPropertySymbols) {
		var a = Object.getOwnPropertySymbols(e);
		for (i = 0; i < a.length; i++) r = a[i], !(t.indexOf(r) >= 0) && Object.prototype.propertyIsEnumerable.call(e, r) && (n[r] = e[r]);
	}
	return n;
}
function Te(e, t) {
	if (e == null) return {};
	var n = {}, r = Object.keys(e), i, a;
	for (a = 0; a < r.length; a++) i = r[a], !(t.indexOf(i) >= 0) && (n[i] = e[i]);
	return n;
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
function U(e, t) {
	return Ae(e) || ke(e, t) || De(e, t) || Ee();
}
function Ee() {
	throw TypeError("Invalid attempt to destructure non-iterable instance.\nIn order to be iterable, non-array objects must have a [Symbol.iterator]() method.");
}
function De(e, t) {
	if (e) {
		if (typeof e == "string") return Oe(e, t);
		var n = Object.prototype.toString.call(e).slice(8, -1);
		if (n === "Object" && e.constructor && (n = e.constructor.name), n === "Map" || n === "Set") return Array.from(e);
		if (n === "Arguments" || /^(?:Ui|I)nt(?:8|16|32)(?:Clamped)?Array$/.test(n)) return Oe(e, t);
	}
}
function Oe(e, t) {
	(t == null || t > e.length) && (t = e.length);
	for (var n = 0, r = Array(t); n < t; n++) r[n] = e[n];
	return r;
}
function ke(e, t) {
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
function Ae(e) {
	if (Array.isArray(e)) return e;
}
function je(e) {
	var n = e.overrides, a = n === void 0 ? {} : n, o = e["aria-label"], s = o === void 0 ? "Menu" : o, c = e.rootRef, d = c === void 0 ? /* @__PURE__ */ f.createRef() : c, p = e.focusMenu, m = p === void 0 ? function() {} : p, h = e.unfocusMenu, g = h === void 0 ? function() {} : h, _ = e.handleMouseLeave, v = _ === void 0 ? function() {} : _, y = e.handleKeyDown, b = y === void 0 ? function(e) {} : y, x = e.renderAll, C = x === void 0 ? !1 : x, w = U(f.useState(!1), 2), D = w[0], O = w[1], k = function(e) {
		l(e) && O(!0);
	}, A = function(e) {
		D !== !1 && O(!1);
	}, j = U(u(a.List, S), 2), M = j[0], N = j[1], P = U(u(a.Option, Se), 2), ee = P[0], F = P[1], I = U(u(a.EmptyState, T), 2), L = I[0], ne = I[1], R = U(u(a.OptgroupHeader, E), 2), re = R[0], ie = R[1], ae = U(u(a.MenuDivider, te), 2), oe = ae[0], se = ae[1], z = Array.isArray(e.items) ? { __ungrouped: e.items } : e.items, B = Object.keys(z), ce = U(B.reduce(function(t, n) {
		var r = U(t, 2), i = r[0], a = r[1];
		n !== "__ungrouped" && i.push(/* @__PURE__ */ f.createElement(re, H({ key: n }, ie), n));
		var o = z[n].map(function(t, n) {
			a += 1;
			var r = e.getRequiredItemProps, i = r === void 0 ? function(e, t) {
				return {};
			} : r;
			if (t.divider === !0) return /* @__PURE__ */ f.createElement(oe, se);
			var o = i(t, a), s = o.disabled, c = o.isFocused, l = o.isHighlighted, u = o.resetMenu, d = u === void 0 ? function() {} : u, p = we(o, Ce);
			return /* @__PURE__ */ f.createElement(ee, H({
				renderAll: C,
				key: a,
				item: t,
				overrides: e.overrides,
				resetMenu: d,
				role: "option",
				$disabled: s,
				$isFocused: c,
				$isHighlighted: l,
				"aria-disabled": s,
				"aria-selected": l && c
			}, p, F));
		});
		return [i.concat(o), a];
	}, [[], -1]), 1)[0], le = B.every(function(e) {
		return !z[e].length;
	});
	return /* @__PURE__ */ f.createElement(t.Consumer, null, function(t) {
		return /* @__PURE__ */ f.createElement(M, H({
			"aria-activedescendant": e.activedescendantId || null,
			role: "listbox",
			"aria-label": s,
			ref: d,
			onMouseEnter: m,
			onMouseLeave: v,
			onMouseOver: m,
			onFocus: i({ onFocus: m }, k),
			onBlur: r({ onBlur: g }, A),
			onKeyDown: function(t) {
				e.isFocused && b(t);
			},
			tabIndex: 0,
			"data-baseweb": "menu",
			$isFocusVisible: D
		}, N), le ? /* @__PURE__ */ f.createElement(L, H({
			"aria-live": "polite",
			"aria-atomic": !0
		}, ne), e.noResultsMsg || t.menu.noResultsMsg) : ce);
	});
}
function W(e, t, n, r) {
	var i = arguments.length > 4 && arguments[4] !== void 0 ? arguments[4] : "auto";
	if (e) {
		var a = e.getBoundingClientRect(), o = t.getBoundingClientRect();
		a.bottom > o.bottom ? r ? t.scrollTop = t.scrollHeight - o.height : t.scrollTop = e.offsetTop + a.height - (i === "center" ? Math.round((o.height + a.height) / 2) : o.height) : a.top < o.top && (n ? t.scrollTop = 0 : t.scrollTop = e.offsetTop - (i === "center" ? Math.round((o.height - a.height) / 2) : 0));
	}
}
function G(e) {
	"@babel/helpers - typeof";
	return G = typeof Symbol == "function" && typeof Symbol.iterator == "symbol" ? function(e) {
		return typeof e;
	} : function(e) {
		return e && typeof Symbol == "function" && e.constructor === Symbol && e !== Symbol.prototype ? "symbol" : typeof e;
	}, G(e);
}
var Me = ["disabled"], Ne = [
	"initialState",
	"stateReducer",
	"children",
	"onItemSelect",
	"addMenuToNesting",
	"removeMenuFromNesting",
	"getParentMenu",
	"getChildMenu",
	"forceHighlight"
];
function K() {
	return K = Object.assign ? Object.assign.bind() : function(e) {
		for (var t = 1; t < arguments.length; t++) {
			var n = arguments[t];
			for (var r in n) Object.prototype.hasOwnProperty.call(n, r) && (e[r] = n[r]);
		}
		return e;
	}, K.apply(this, arguments);
}
function Pe(e, t) {
	if (e == null) return {};
	var n = Fe(e, t), r, i;
	if (Object.getOwnPropertySymbols) {
		var a = Object.getOwnPropertySymbols(e);
		for (i = 0; i < a.length; i++) r = a[i], !(t.indexOf(r) >= 0) && Object.prototype.propertyIsEnumerable.call(e, r) && (n[r] = e[r]);
	}
	return n;
}
function Fe(e, t) {
	if (e == null) return {};
	var n = {}, r = Object.keys(e), i, a;
	for (a = 0; a < r.length; a++) i = r[a], !(t.indexOf(i) >= 0) && (n[i] = e[i]);
	return n;
}
function Ie(e, t) {
	var n = Object.keys(e);
	if (Object.getOwnPropertySymbols) {
		var r = Object.getOwnPropertySymbols(e);
		t && (r = r.filter(function(t) {
			return Object.getOwnPropertyDescriptor(e, t).enumerable;
		})), n.push.apply(n, r);
	}
	return n;
}
function q(e) {
	for (var t = 1; t < arguments.length; t++) {
		var n = arguments[t] == null ? {} : arguments[t];
		t % 2 ? Ie(Object(n), !0).forEach(function(t) {
			Z(e, t, n[t]);
		}) : Object.getOwnPropertyDescriptors ? Object.defineProperties(e, Object.getOwnPropertyDescriptors(n)) : Ie(Object(n)).forEach(function(t) {
			Object.defineProperty(e, t, Object.getOwnPropertyDescriptor(n, t));
		});
	}
	return e;
}
function Le(e, t) {
	if (!(e instanceof t)) throw TypeError("Cannot call a class as a function");
}
function Re(e, t) {
	for (var n = 0; n < t.length; n++) {
		var r = t[n];
		r.enumerable = r.enumerable || !1, r.configurable = !0, "value" in r && (r.writable = !0), Object.defineProperty(e, r.key, r);
	}
}
function ze(e, t, n) {
	return t && Re(e.prototype, t), Object.defineProperty(e, "prototype", { writable: !1 }), e;
}
function Be(e, t) {
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
function Ve(e) {
	var t = Ue();
	return function() {
		var n = X(e), r;
		if (t) {
			var i = X(this).constructor;
			r = Reflect.construct(n, arguments, i);
		} else r = n.apply(this, arguments);
		return He(this, r);
	};
}
function He(e, t) {
	if (t && (G(t) === "object" || typeof t == "function")) return t;
	if (t !== void 0) throw TypeError("Derived constructors may only return object or undefined");
	return Y(e);
}
function Y(e) {
	if (e === void 0) throw ReferenceError("this hasn't been initialised - super() hasn't been called");
	return e;
}
function Ue() {
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
var We = {
	initialState: {
		highlightedIndex: -1,
		isFocused: !1
	},
	typeAhead: !0,
	keyboardControlNode: { current: null },
	stateReducer: function(e, t) {
		return t;
	},
	onItemSelect: function() {},
	getRequiredItemProps: function() {
		return {};
	},
	children: function() {
		return null;
	},
	addMenuToNesting: function() {},
	removeMenuFromNesting: function() {},
	getParentMenu: function() {},
	getChildMenu: function() {},
	nestedMenuHoverIndex: -1,
	isNestedMenuVisible: function() {
		return !1;
	},
	forceHighlight: !1
}, Ge = /* @__PURE__ */ function(e) {
	Be(n, e);
	var t = Ve(n);
	function n() {
		var e;
		Le(this, n);
		var r = [...arguments];
		return e = t.call.apply(t, [this].concat(r)), Z(Y(e), "state", q(q({}, e.constructor.defaultProps.initialState), e.props.initialState)), Z(Y(e), "rootRef", /* @__PURE__ */ f.createRef()), Z(Y(e), "keyboardControlNode", e.props.keyboardControlNode.current), Z(Y(e), "refList", []), Z(Y(e), "optionIds", []), Z(Y(e), "typeAheadChars", ""), Z(Y(e), "typeAheadTimeOut", null), Z(Y(e), "onKeyDown", function(t) {
			switch (t.key) {
				case m.ArrowUp:
				case m.ArrowDown:
				case m.ArrowLeft:
				case m.ArrowRight:
				case m.Home:
				case m.End:
					e.handleArrowKey(t);
					break;
				case m.Enter:
					if (t.keyCode === 229) break;
					e.handleEnterKey(t);
					break;
				default:
					e.props.typeAhead && (clearTimeout(e.typeAheadTimeOut), e.handleAlphaDown(t));
					break;
			}
		}), Z(Y(e), "handleAlphaDown", function(t) {
			var n = e.props.rootRef ? e.props.rootRef : e.rootRef, r = e.state.highlightedIndex;
			e.typeAheadChars += t.key, e.typeAheadTimeOut = setTimeout(function() {
				e.typeAheadChars = "";
			}, 500);
			var i = r, a = e.getItems();
			if (!(a.length === 0 || !("label" in a[0]))) {
				for (var o = !0, s = 0; s < a.length; s++) {
					var c = a[s].label;
					if (c && c.toUpperCase && c.toUpperCase().indexOf(e.typeAheadChars.toUpperCase()) === 0) {
						i = s, o = !1;
						break;
					}
				}
				if (o) for (var l = 0; l < a.length; l++) {
					var u = a[l].label;
					if (u && u.toUpperCase && u.toUpperCase().indexOf(e.typeAheadChars.toUpperCase()) > 0) {
						i = l;
						break;
					}
				}
				e.internalSetState(p.character, { highlightedIndex: i }), e.refList[i] && W(e.refList[i].current, n.current, i === 0, i === a.length - 1);
			}
		}), Z(Y(e), "handleArrowKey", function(t) {
			var n = e.props.rootRef ? e.props.rootRef : e.rootRef, r = e.state.highlightedIndex, i = r;
			if (t.key === m.ArrowUp) t.preventDefault(), i = Math.max(0, r - 1), e.internalSetState(p.moveUp, { highlightedIndex: i });
			else if (t.key === m.ArrowDown) t.preventDefault(), i = Math.min(r + 1, e.getItems().length - 1), e.internalSetState(p.moveDown, { highlightedIndex: i });
			else if (t.key === m.Home) t.preventDefault(), i = 0, e.internalSetState(p.moveUp, { highlightedIndex: i });
			else if (t.key === m.End) t.preventDefault(), i = e.getItems().length - 1, e.internalSetState(p.moveDown, { highlightedIndex: i });
			else if (t.key === m.ArrowLeft) {
				if (e.props.getParentMenu) {
					var a = e.props.getParentMenu(n);
					a && a.current && a.current.focus();
				}
			} else if (t.key === m.ArrowRight && e.props.getChildMenu) {
				var o = e.props.getChildMenu(n);
				o && o.current && o.current.focus();
			}
			e.refList[i] && W(e.refList[i].current, n.current, i === 0, i === e.getItems().length - 1);
		}), Z(Y(e), "handleEnterKey", function(t) {
			var n = e.props.onItemSelect, r = e.state.highlightedIndex, i = e.getItems();
			i[r] && n && !i[r].disabled && (t.preventDefault(), n({
				item: i[r],
				event: t
			}));
		}), Z(Y(e), "handleItemClick", function(t, n, r) {
			e.props.onItemSelect && !n.disabled && (e.props.onItemSelect({
				item: n,
				event: r
			}), e.internalSetState(p.click, {
				highlightedIndex: t,
				activedescendantId: e.optionIds[t]
			}));
		}), Z(Y(e), "handleMouseEnter", function(t) {
			e.internalSetState(p.mouseEnter, {
				highlightedIndex: t,
				activedescendantId: e.optionIds[t]
			});
		}), Z(Y(e), "handleMouseLeave", function(e) {}), Z(Y(e), "getRequiredItemProps", function(t, n) {
			var r = e.refList[n];
			r || (r = /* @__PURE__ */ f.createRef(), e.refList[n] = r, e.optionIds[n] = e.props.uidSeed(n));
			var i = e.props.getRequiredItemProps(t, n), a = i.disabled, o = Pe(i, Me), s = typeof a == "boolean" ? a : !!t.disabled;
			return q(q({
				id: o.id || e.optionIds[n],
				disabled: s,
				ref: r,
				isFocused: e.state.isFocused,
				isHighlighted: e.state.highlightedIndex === n,
				resetMenu: e.resetMenu
			}, s ? {} : {
				onClick: e.handleItemClick.bind(Y(e), n, t),
				onMouseEnter: e.handleMouseEnter.bind(Y(e), n)
			}), o);
		}), Z(Y(e), "focusMenu", function(t) {
			var n = e.props.rootRef ? e.props.rootRef : e.rootRef;
			!e.state.isFocused && n.current && n.current.contains(t.target) && (e.state.highlightedIndex < 0 ? e.internalSetState(p.focus, {
				isFocused: !0,
				highlightedIndex: 0
			}) : e.internalSetState(p.focus, { isFocused: !0 }), n.current.focus());
		}), Z(Y(e), "unfocusMenu", function() {
			e.internalSetState(p.focus, { isFocused: !1 });
		}), Z(Y(e), "resetMenu", function() {
			e.internalSetState(p.reset, {
				isFocused: !1,
				highlightedIndex: -1,
				activedescendantId: null
			});
		}), e;
	}
	return ze(n, [
		{
			key: "getItems",
			value: function() {
				var e = this;
				return Array.isArray(this.props.items) ? this.props.items : Object.keys(this.props.items).reduce(function(t, n) {
					return t.concat(e.props.items[n]);
				}, []);
			}
		},
		{
			key: "componentDidMount",
			value: function() {
				var e = this.props.rootRef ? this.props.rootRef : this.rootRef;
				typeof document < "u" && (e.current && this.state.highlightedIndex > -1 && this.refList[this.state.highlightedIndex] && W(this.refList[this.state.highlightedIndex].current, e.current, this.state.highlightedIndex === 0, this.state.highlightedIndex === this.getItems().length - 1, "center"), this.state.isFocused && this.keyboardControlNode && this.keyboardControlNode.addEventListener("keydown", this.onKeyDown)), this.props.addMenuToNesting && this.props.addMenuToNesting(e);
			}
		},
		{
			key: "componentWillUnmount",
			value: function() {
				var e = this.props.rootRef ? this.props.rootRef : this.rootRef;
				typeof document < "u" && this.keyboardControlNode && this.keyboardControlNode.removeEventListener("keydown", this.onKeyDown), this.props.removeMenuFromNesting && this.props.removeMenuFromNesting(e);
			}
		},
		{
			key: "componentDidUpdate",
			value: function(e, t) {
				typeof document < "u" && (!t.isFocused && this.state.isFocused ? this.keyboardControlNode && this.keyboardControlNode.addEventListener("keydown", this.onKeyDown) : t.isFocused && !this.state.isFocused && this.keyboardControlNode && this.keyboardControlNode.removeEventListener("keydown", this.onKeyDown));
				var n = this.getItems().length;
				this.props.forceHighlight && this.state.highlightedIndex === -1 && n > 0 && this.internalSetState(p.enter, { highlightedIndex: 0 }), n === 0 && this.state.highlightedIndex !== -1 ? this.internalSetState(p.enter, { highlightedIndex: -1 }) : this.state.highlightedIndex >= n && this.internalSetState(p.enter, { highlightedIndex: 0 }), this.props.isNestedMenuVisible && this.props.nestedMenuHoverIndex !== e.nestedMenuHoverIndex && !this.props.isNestedMenuVisible(this.rootRef) && !this.props.forceHighlight && this.setState({ highlightedIndex: -1 });
			}
		},
		{
			key: "internalSetState",
			value: function(e, t) {
				var n = this.props.stateReducer;
				this.props.onActiveDescendantChange && typeof t.highlightedIndex == "number" && this.state.highlightedIndex !== t.highlightedIndex && this.props.onActiveDescendantChange(this.optionIds[t.highlightedIndex]), this.setState(n(e, t, this.state));
			}
		},
		{
			key: "render",
			value: function() {
				var e = this, t = this.props;
				t.initialState, t.stateReducer, t.children, t.onItemSelect, t.addMenuToNesting, t.removeMenuFromNesting, t.getParentMenu, t.getChildMenu, t.forceHighlight;
				var n = Pe(t, Ne);
				return this.props.children(q(q({}, n), {}, {
					rootRef: this.props.rootRef ? this.props.rootRef : this.rootRef,
					activedescendantId: this.optionIds[this.state.highlightedIndex],
					getRequiredItemProps: function(t, n) {
						return e.getRequiredItemProps(t, n);
					},
					handleMouseLeave: this.handleMouseLeave,
					highlightedIndex: this.state.highlightedIndex,
					isFocused: this.state.isFocused,
					handleKeyDown: this.props.keyboardControlNode.current ? function(e) {} : this.onKeyDown,
					focusMenu: this.focusMenu,
					unfocusMenu: this.unfocusMenu
				}));
			}
		}
	]), n;
}(f.Component);
Z(Ge, "defaultProps", We);
var Ke = function(e) {
	return /* @__PURE__ */ f.createElement(Ge, K({ uidSeed: a() }, e));
};
Ke.defaultProps = We;
function qe(e) {
	"@babel/helpers - typeof";
	return qe = typeof Symbol == "function" && typeof Symbol.iterator == "symbol" ? function(e) {
		return typeof e;
	} : function(e) {
		return e && typeof Symbol == "function" && e.constructor === Symbol && e !== Symbol.prototype ? "symbol" : typeof e;
	}, qe(e);
}
var Je = ["overrides"];
function Q() {
	return Q = Object.assign ? Object.assign.bind() : function(e) {
		for (var t = 1; t < arguments.length; t++) {
			var n = arguments[t];
			for (var r in n) Object.prototype.hasOwnProperty.call(n, r) && (e[r] = n[r]);
		}
		return e;
	}, Q.apply(this, arguments);
}
function Ye(e, t) {
	if (e == null) return {};
	var n = Xe(e, t), r, i;
	if (Object.getOwnPropertySymbols) {
		var a = Object.getOwnPropertySymbols(e);
		for (i = 0; i < a.length; i++) r = a[i], !(t.indexOf(r) >= 0) && Object.prototype.propertyIsEnumerable.call(e, r) && (n[r] = e[r]);
	}
	return n;
}
function Xe(e, t) {
	if (e == null) return {};
	var n = {}, r = Object.keys(e), i, a;
	for (a = 0; a < r.length; a++) i = r[a], !(t.indexOf(i) >= 0) && (n[i] = e[i]);
	return n;
}
function Ze(e, t) {
	if (!(e instanceof t)) throw TypeError("Cannot call a class as a function");
}
function Qe(e, t) {
	for (var n = 0; n < t.length; n++) {
		var r = t[n];
		r.enumerable = r.enumerable || !1, r.configurable = !0, "value" in r && (r.writable = !0), Object.defineProperty(e, r.key, r);
	}
}
function $e(e, t, n) {
	return t && Qe(e.prototype, t), Object.defineProperty(e, "prototype", { writable: !1 }), e;
}
function et(e, t) {
	if (typeof t != "function" && t !== null) throw TypeError("Super expression must either be null or a function");
	e.prototype = Object.create(t && t.prototype, { constructor: {
		value: e,
		writable: !0,
		configurable: !0
	} }), Object.defineProperty(e, "prototype", { writable: !1 }), t && tt(e, t);
}
function tt(e, t) {
	return tt = Object.setPrototypeOf ? Object.setPrototypeOf.bind() : function(e, t) {
		return e.__proto__ = t, e;
	}, tt(e, t);
}
function nt(e) {
	var t = at();
	return function() {
		var n = $(e), r;
		if (t) {
			var i = $(this).constructor;
			r = Reflect.construct(n, arguments, i);
		} else r = n.apply(this, arguments);
		return rt(this, r);
	};
}
function rt(e, t) {
	if (t && (qe(t) === "object" || typeof t == "function")) return t;
	if (t !== void 0) throw TypeError("Derived constructors may only return object or undefined");
	return it(e);
}
function it(e) {
	if (e === void 0) throw ReferenceError("this hasn't been initialised - super() hasn't been called");
	return e;
}
function at() {
	if (typeof Reflect > "u" || !Reflect.construct || Reflect.construct.sham) return !1;
	if (typeof Proxy == "function") return !0;
	try {
		return Boolean.prototype.valueOf.call(Reflect.construct(Boolean, [], function() {})), !0;
	} catch {
		return !1;
	}
}
function $(e) {
	return $ = Object.setPrototypeOf ? Object.getPrototypeOf.bind() : function(e) {
		return e.__proto__ || Object.getPrototypeOf(e);
	}, $(e);
}
var ot = /* @__PURE__ */ function(e) {
	et(n, e);
	var t = nt(n);
	function n() {
		return Ze(this, n), t.apply(this, arguments);
	}
	return $e(n, [{
		key: "render",
		value: function() {
			var e = this.props, t = e.overrides, n = Ye(e, Je);
			return /* @__PURE__ */ f.createElement(I.Consumer, null, function(e) {
				return /* @__PURE__ */ f.createElement(Ke, Q({}, e, n), function(e) {
					return /* @__PURE__ */ f.createElement(je, Q({}, e, { overrides: t }));
				});
			});
		}
	}]), n;
}(f.PureComponent);
//#endregion
export { S as i, ot as n, T as r, k as t };

//# sourceMappingURL=stateful-menu-CW-YE2l8-DNHb-gL3.js.map