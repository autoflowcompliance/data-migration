import { Dn as e, En as t, Ka as n, Ua as r, _a as i, b as a, c as o, l as s, o as c, s as l, ti as u } from "./index-Dl4ETd_L-D2oMd1k2.js";
import { t as d } from "./iconPosition-Cpqwt3HE-C-jUvRPi.js";
//#region ../react/build/LinkButton-6uqUWhGF.js
var f = /* @__PURE__ */ n(r(), 1);
function p(e, t) {
	switch (e) {
		case l.XSMALL: return {
			padding: `${t.spacing.twoXS} ${t.spacing.sm}`,
			fontSize: t.fontSizes.sm
		};
		case l.SMALL: return { padding: `${t.spacing.twoXS} ${t.spacing.md}` };
		case l.LARGE: return { padding: `${t.spacing.md} ${t.spacing.md}` };
		default: return { padding: `${t.spacing.xs} ${t.spacing.md}` };
	}
}
var m = /* @__PURE__ */ t("a", { target: "e16zdaao3" })(({ containerWidth: e, size: t, theme: n }) => ({
	display: "inline-flex",
	alignItems: "center",
	justifyContent: "center",
	fontWeight: n.fontWeights.normal,
	padding: `${n.spacing.xs} ${n.spacing.md}`,
	borderRadius: n.radii.button,
	minHeight: n.sizes.minElementHeight,
	margin: 0,
	lineHeight: n.lineHeights.base,
	color: n.colors.primary,
	textDecoration: "none",
	width: e ? "100%" : "auto",
	userSelect: "none",
	"&:visited": { color: n.colors.primary },
	"&:focus": { outline: "none" },
	"&:focus-visible": { boxShadow: n.shadows.focusRing },
	"&:hover": { textDecoration: "none" },
	"&:active": { textDecoration: "none" },
	...p(t, n)
}), ""), h = /* @__PURE__ */ t(m, { target: "e16zdaao2" })(({ theme: t }) => ({
	backgroundColor: t.colors.primary,
	color: t.colors.white,
	border: `${t.sizes.borderWidth} solid ${t.colors.primary}`,
	"&:hover, &:focus-visible": {
		backgroundColor: e(t.colors.primary, .15),
		borderColor: e(t.colors.primary, .15)
	},
	"&:active": {
		backgroundColor: t.colors.primary,
		borderColor: e(t.colors.primary, .15)
	},
	"&:visited:not(:active)": { color: t.colors.white },
	"&[disabled], &[disabled]:hover, &[disabled]:active, &[disabled]:visited": {
		borderColor: t.colors.borderColor,
		backgroundColor: t.colors.transparent,
		color: t.colors.fadedText40,
		cursor: "not-allowed"
	}
}), ""), g = /* @__PURE__ */ t(m, { target: "e16zdaao1" })(({ theme: e }) => ({
	backgroundColor: e.colors.lightenedBg05,
	color: e.colors.bodyText,
	border: `${e.sizes.borderWidth} solid ${e.colors.borderColor}`,
	"&:visited": { color: e.colors.bodyText },
	"&:hover, &:focus-visible": { backgroundColor: e.colors.darkenedBgMix15 },
	"&:active": { backgroundColor: e.colors.darkenedBgMix25 },
	"&[disabled], &[disabled]:hover, &[disabled]:active": {
		borderColor: e.colors.borderColor,
		backgroundColor: e.colors.transparent,
		color: e.colors.fadedText40,
		cursor: "not-allowed"
	}
}), ""), _ = /* @__PURE__ */ t(m, { target: "e16zdaao0" })(({ theme: t }) => ({
	padding: t.spacing.none,
	backgroundColor: t.colors.transparent,
	color: t.colors.bodyText,
	border: "none",
	"&:visited": { color: t.colors.bodyText },
	"&:hover, &:focus-visible": { color: t.colors.primary },
	"&:hover:not([disabled]), &:focus-visible:not([disabled])": { "span.stMarkdownColoredText": { color: "inherit !important" } },
	"&:active": { color: e(t.colors.primary, .25) },
	"&[disabled], &[disabled]:hover, &[disabled]:active": {
		backgroundColor: t.colors.transparent,
		color: t.colors.fadedText40,
		cursor: "not-allowed"
	}
}), ""), v = (0, f.forwardRef)(function({ kind: e, size: t, disabled: n, children: r, autoFocus: i, href: a, rel: o, target: s, onClick: d }, f) {
	let p = h;
	return e === c.SECONDARY ? p = g : e === c.TERTIARY && (p = _), /* @__PURE__ */ u.jsx(p, {
		ref: f,
		kind: e,
		size: t || l.MEDIUM,
		containerWidth: !0,
		disabled: n || !1,
		autoFocus: i || !1,
		href: a,
		target: s,
		rel: o,
		onClick: d,
		tabIndex: n ? -1 : 0,
		"data-testid": `stBaseLinkButton-${e}`,
		children: r
	});
});
v.displayName = "BaseLinkButton";
var y = (0, f.memo)(v);
function b(e) {
	let { element: t, widgetMgr: n, fragmentId: r } = e, p = t.shortcut || void 0, m = c.SECONDARY;
	t.type === "primary" ? m = c.PRIMARY : t.type === "tertiary" && (m = c.TERTIARY);
	let h = (0, f.useRef)(null), g = (0, f.useCallback)(() => {
		t.disabled || h.current?.click();
	}, [t.disabled]), _ = (0, f.useCallback)((e) => {
		if (t.disabled) {
			e.preventDefault();
			return;
		}
		!t.ignoreRerun && t.id && n.setTriggerValue(t, { fromUi: !0 }, r);
	}, [
		t,
		r,
		n
	]);
	return i({
		shortcut: p,
		disabled: t.disabled,
		onActivate: g
	}), /* @__PURE__ */ u.jsx(s, {
		className: "stLinkButton",
		"data-testid": "stLinkButton",
		children: /* @__PURE__ */ u.jsx(o, {
			help: t.help,
			containerWidth: !0,
			children: /* @__PURE__ */ u.jsx(y, {
				ref: h,
				kind: m,
				size: l.SMALL,
				disabled: t.disabled,
				onClick: _,
				href: t.url,
				target: "_blank",
				rel: "noreferrer",
				"aria-disabled": t.disabled,
				children: /* @__PURE__ */ u.jsx(a, {
					icon: t.icon,
					iconPosition: d(t.iconPosition),
					label: t.label,
					shortcut: p
				})
			})
		})
	});
}
var x = (0, f.memo)(b);
//#endregion
export { x as default };

//# sourceMappingURL=LinkButton-6uqUWhGF-BSAGSZDP.js.map