import { Br as e, Cn as t, En as n, Et as r, Ka as i, Nn as a, P as o, Ua as s, X as c, a as l, b as u, c as d, dt as f, l as p, ma as m, nr as h, o as g, q as _, s as v, ti as y, x as b } from "./index-Dl4ETd_L-D2oMd1k2.js";
import { n as x } from "./stateful-menu-CW-YE2l8-DNHb-gL3.js";
import { t as S } from "./styled-components-Cxzc3DcQ-DbuOYdSx.js";
//#region ../react/build/MenuButton-Bmt95URR.js
var C = /* @__PURE__ */ i(s(), 1), w = /* @__PURE__ */ n("div", { target: "e1glrse04" })(({ theme: e, $hideChevron: t }) => ({
	display: "flex",
	alignItems: "center",
	gap: e.spacing.threeXS,
	marginRight: t ? 0 : `calc(-${e.iconSizes.lg} * 0.25)`
}), ""), T = /* @__PURE__ */ n("div", { target: "e1glrse03" })(({ theme: e }) => ({
	display: "inline-flex",
	marginTop: e.spacing.threeXS
}), ""), E = /* @__PURE__ */ n("div", { target: "e1glrse02" })(({ theme: e }) => ({
	display: "flex",
	alignItems: "center",
	gap: e.spacing.sm,
	whiteSpace: "nowrap"
}), ""), D = /* @__PURE__ */ n("span", { target: "e1glrse01" })(({ theme: e }) => ({
	display: "inline-flex",
	alignItems: "center",
	justifyContent: "center",
	flexShrink: 0,
	width: e.iconSizes.md,
	color: e.colors.bodyText
}), ""), O = /* @__PURE__ */ n("li", { target: "e1glrse00" })(({ theme: e }) => ({
	display: "flex",
	alignItems: "center",
	marginTop: e.spacing.twoXS,
	marginBottom: e.spacing.twoXS,
	padding: 0,
	background: "transparent",
	cursor: "pointer",
	listStyle: "none",
	minWidth: e.sizes.minMenuWidth
}), ""), k = {
	primary: g.PRIMARY,
	secondary: g.SECONDARY,
	tertiary: g.TERTIARY
}, A = (0, C.memo)(function({ item: e, $isHighlighted: t, onClick: n, onMouseEnter: r, onKeyDown: i, $disabled: o, $isFocused: s, $size: c, resetMenu: l, renderAll: u, ...d }) {
	let { icon: p, text: m } = a(e.label);
	return /* @__PURE__ */ y.jsx(O, {
		...d,
		role: "menuitem",
		onClick: n,
		onMouseEnter: r,
		onKeyDown: i,
		children: /* @__PURE__ */ y.jsx(S, {
			$isHighlighted: t,
			children: /* @__PURE__ */ y.jsxs(E, { children: [p && /* @__PURE__ */ y.jsx(D, {
				"aria-hidden": "true",
				children: /* @__PURE__ */ y.jsx(b, {
					iconValue: p,
					size: "md"
				})
			}), /* @__PURE__ */ y.jsx(f, {
				source: m,
				allowHTML: !1,
				isLabel: !0,
				largerLabel: !1,
				disableLinks: !0
			})] })
		})
	});
});
function j(n) {
	let { disabled: i, element: a, widgetMgr: s, fragmentId: f } = n, [S, E] = (0, C.useState)(!1), D = (0, C.useContext)(o), O = m(), j = k[a.type] ?? g.SECONDARY, M = (0, C.useMemo)(() => a.options.map((e) => ({
		label: e,
		value: e
	})), [a.options]), N = i || a.disabled || a.options.length === 0, P = e(a.icon, a.label), F = (0, C.useCallback)((e) => {
		E(!1), !N && s.setStringTriggerValue(a, e.item.value, { fromUi: !0 }, f);
	}, [
		N,
		a,
		s,
		f
	]);
	return /* @__PURE__ */ y.jsx(p, {
		className: "stMenuButton",
		"data-testid": "stMenuButton",
		children: /* @__PURE__ */ y.jsx(c, {
			triggerType: r.click,
			placement: _.bottomLeft,
			isOpen: S,
			onClickOutside: () => E(!1),
			onEsc: () => E(!1),
			ignoreBoundary: D,
			popoverMargin: t(O.spacing.twoXS),
			renderAll: !0,
			content: () => /* @__PURE__ */ y.jsx(x, {
				items: M,
				onItemSelect: F,
				overrides: {
					List: {
						props: { role: "menu" },
						style: {
							backgroundColor: O.colors.bgColor,
							paddingTop: O.spacing.threeXS,
							paddingBottom: O.spacing.threeXS,
							paddingLeft: O.spacing.xs,
							paddingRight: O.spacing.xs,
							boxShadow: "none",
							outline: "none"
						}
					},
					Option: { component: A }
				}
			}),
			overrides: { Body: {
				props: { "data-testid": "stMenuButtonBody" },
				style: () => ({
					...h(O),
					borderTopLeftRadius: O.radii.xl,
					borderTopRightRadius: O.radii.xl,
					borderBottomRightRadius: O.radii.xl,
					borderBottomLeftRadius: O.radii.xl,
					marginRight: O.spacing.lg,
					marginBottom: O.spacing.lg,
					maxHeight: "70vh",
					overflow: "auto"
				})
			} },
			children: /* @__PURE__ */ y.jsx("div", { children: /* @__PURE__ */ y.jsx(d, {
				help: a.help,
				containerWidth: !0,
				children: /* @__PURE__ */ y.jsx(l, {
					"data-testid": "stMenuButtonButton",
					kind: j,
					size: v.SMALL,
					disabled: N,
					containerWidth: !0,
					onClick: () => E(!S),
					"aria-haspopup": "menu",
					"aria-expanded": S,
					children: /* @__PURE__ */ y.jsxs(w, {
						$hideChevron: P,
						children: [/* @__PURE__ */ y.jsx(u, {
							icon: a.icon,
							label: a.label
						}), !P && /* @__PURE__ */ y.jsx(T, {
							"aria-hidden": "true",
							children: /* @__PURE__ */ y.jsx(b, {
								iconValue: S ? ":material/expand_less:" : ":material/expand_more:",
								size: "lg"
							})
						})]
					})
				})
			}) })
		})
	});
}
var M = (0, C.memo)(j);
//#endregion
export { M as default };

//# sourceMappingURL=MenuButton-Bmt95URR-TkDwQh8T.js.map