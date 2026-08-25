import { En as e, J as t, Ka as n, Ua as r, W as i, c as a, dt as o, ma as s, ti as c, x as l } from "./index-Dl4ETd_L-D2oMd1k2.js";
import { t as u } from "./iconPosition-Cpqwt3HE-C-jUvRPi.js";
//#region ../react/build/PageLink-CS25U8sD.js
var d = /* @__PURE__ */ n(r(), 1), f = /* @__PURE__ */ e("div", { target: "e11k5jya2" })({
	name: "b6wrti",
	styles: "display:flex;flex-direction:column;width:100%"
}), p = /* @__PURE__ */ e("a", { target: "e11k5jya1" })(({ disabled: e, isCurrentPage: t, theme: n }) => ({
	textDecoration: "none",
	width: "100%",
	display: "flex",
	flexDirection: "row",
	alignItems: "center",
	justifyContent: "flex-start",
	gap: n.spacing.sm,
	borderRadius: n.radii.default,
	paddingLeft: n.spacing.sm,
	paddingRight: n.spacing.sm,
	marginTop: n.spacing.threeXS,
	marginBottom: n.spacing.threeXS,
	lineHeight: n.lineHeights.menuItem,
	backgroundColor: t ? n.colors.darkenedBgMix15 : "transparent",
	"&:hover": { backgroundColor: t ? n.colors.darkenedBgMix25 : n.colors.darkenedBgMix15 },
	"&:active,&:visited,&:hover": { textDecoration: "none" },
	"&:focus": { outline: "none" },
	"&:focus-visible": { backgroundColor: n.colors.darkenedBgMix15 },
	"@media print": { paddingLeft: n.spacing.none },
	...e ? {
		borderColor: n.colors.borderColor,
		backgroundColor: n.colors.transparent,
		color: n.colors.fadedText40,
		cursor: "not-allowed",
		"&:hover": {
			color: n.colors.fadedText40,
			backgroundColor: n.colors.transparent
		}
	} : {}
}), ""), m = /* @__PURE__ */ e("span", { target: "e11k5jya0" })(({ disabled: e, theme: t }) => ({
	color: t.colors.bodyText,
	overflow: "hidden",
	whiteSpace: "nowrap",
	textOverflow: "ellipsis",
	display: "table-cell",
	...e ? {
		borderColor: t.colors.borderColor,
		backgroundColor: t.colors.transparent,
		color: t.colors.fadedText40,
		cursor: "not-allowed"
	} : {}
}), "");
function h(e) {
	let t = e.page;
	if (e.queryString) if (e.external) try {
		let n = new URL(e.page);
		new URLSearchParams(e.queryString).forEach((e, t) => n.searchParams.append(t, e)), t = n.toString();
	} catch {
		let [n, r] = t.split("#");
		t = n + (n.includes("?") ? "&" : "?") + e.queryString + (r ? "#" + r : "");
	}
	else t += (t.includes("?") ? "&" : "?") + e.queryString;
	return t;
}
function g(e) {
	let { onPageChange: n, currentPageScriptHash: r } = (0, d.useContext)(i), { colors: g } = s(), { disabled: _, element: v } = e, y = r === v.pageScriptHash, b = (e) => {
		v.external ? _ && e.preventDefault() : (e.preventDefault(), _ || n(v.pageScriptHash, v.queryString));
	}, x = u(v.iconPosition), S = h(v);
	return /* @__PURE__ */ c.jsx("div", {
		className: "stPageLink",
		"data-testid": "stPageLink",
		children: /* @__PURE__ */ c.jsx(a, {
			help: v.help,
			placement: t.TOP_RIGHT,
			containerWidth: !0,
			children: /* @__PURE__ */ c.jsx(f, { children: /* @__PURE__ */ c.jsxs(p, {
				"data-testid": "stPageLink-NavLink",
				disabled: _,
				isCurrentPage: y,
				href: S,
				target: v.external ? "_blank" : "",
				rel: "noreferrer",
				onClick: b,
				children: [
					v.icon && x === "left" && /* @__PURE__ */ c.jsx(l, {
						size: "lg",
						color: _ ? g.fadedText40 : g.bodyText,
						iconValue: v.icon
					}),
					/* @__PURE__ */ c.jsx(m, {
						disabled: _,
						children: /* @__PURE__ */ c.jsx(o, {
							source: v.label,
							allowHTML: !1,
							isLabel: !0,
							boldLabel: y,
							largerLabel: !0,
							disableLinks: !0
						})
					}),
					v.icon && x === "right" && /* @__PURE__ */ c.jsx(l, {
						size: "lg",
						color: _ ? g.fadedText40 : g.bodyText,
						iconValue: v.icon
					})
				]
			}) })
		})
	});
}
var _ = (0, d.memo)(g);
//#endregion
export { h as buildHref, _ as default };

//# sourceMappingURL=PageLink-CS25U8sD-CcnJbuVq.js.map