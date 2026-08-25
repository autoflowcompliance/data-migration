import { En as e, I as t, Ka as n, Ua as r, dt as i, ma as a, r as o, sa as s, sr as c, ti as l, vi as u, x as d } from "./index-Dl4ETd_L-D2oMd1k2.js";
//#region ../react/build/Toast-CJKq1jpo.js
var f = /* @__PURE__ */ n(r(), 1), p = /* @__PURE__ */ e("button", { target: "elibz2u2" })(({ theme: e }) => ({
	fontSize: e.fontSizes.sm,
	lineHeight: e.lineHeights.base,
	color: e.colors.fadedText60,
	backgroundColor: e.colors.transparent,
	fontFamily: "inherit",
	margin: e.spacing.none,
	border: "none",
	boxShadow: "none",
	padding: e.spacing.none,
	"&:hover, &:active, &:focus": {
		border: "none",
		outline: "none",
		boxShadow: "none"
	},
	"&:hover": { color: e.colors.primary }
}), ""), m = /* @__PURE__ */ e("div", { target: "elibz2u1" })(({ theme: e }) => ({
	display: "flex",
	flexDirection: "row",
	gap: e.spacing.lg,
	"> span": { marginTop: e.spacing.twoXS }
}), ""), h = /* @__PURE__ */ e("div", { target: "elibz2u0" })(({ theme: e }) => ({
	display: "flex",
	flexDirection: "column",
	gap: e.spacing.sm,
	alignItems: "start",
	justifyContent: "center",
	overflow: "hidden",
	minHeight: "100%",
	fontSize: e.fontSizes.sm,
	lineHeight: e.lineHeights.base,
	div: { display: "inline-flex" }
}), "");
function g(e) {
	let t = c(e);
	return {
		Body: {
			props: {
				"data-testid": "stToast",
				className: "stToast"
			},
			style: {
				display: "flex",
				flexDirection: "row",
				gap: e.spacing.md,
				width: e.sizes.toastWidth,
				marginTop: e.spacing.sm,
				borderTopLeftRadius: e.radii.default,
				borderTopRightRadius: e.radii.default,
				borderBottomLeftRadius: e.radii.default,
				borderBottomRightRadius: e.radii.default,
				paddingTop: e.spacing.lg,
				paddingBottom: e.spacing.lg,
				paddingLeft: e.spacing.twoXL,
				paddingRight: e.spacing.twoXL,
				backgroundColor: e.colors.bgColor,
				filter: t ? "brightness(0.98)" : "brightness(1.2)",
				color: e.colors.bodyText,
				boxShadow: e.shadows.popover
			}
		},
		CloseIcon: { style: {
			color: e.colors.fadedText40,
			width: e.fontSizes.lg,
			height: e.fontSizes.lg,
			marginRight: `calc(-1 * ${e.spacing.lg} / 2)`,
			":hover": { color: e.colors.bodyText }
		} }
	};
}
function _(e) {
	if (e.length > 104) {
		let t = e.replace(/^(.{104}[^\s]*).*/, "$1");
		return t.length > 104 && (t = t.substring(0, 104).split(" ").slice(0, -1).join(" ")), t.trim();
	}
	return e;
}
function v({ element: e }) {
	let { body: n, icon: r, duration: c } = e, v = a(), y = _(n), b = n !== y, [x, S] = (0, f.useState)(!b), [C, w] = (0, f.useState)(0), T = (0, f.useCallback)(() => {
		S(!x);
	}, [x]), E = (0, f.useMemo)(() => g(v), [v]), D = (0, f.useMemo)(() => /* @__PURE__ */ l.jsxs(m, {
		expanded: x,
		children: [r && /* @__PURE__ */ l.jsx(d, {
			iconValue: r,
			size: "xl",
			testid: "stToastDynamicIcon"
		}), /* @__PURE__ */ l.jsxs(h, { children: [/* @__PURE__ */ l.jsx(i, {
			source: x ? n : y,
			allowHTML: !1,
			isToast: !0
		}), b && /* @__PURE__ */ l.jsx(p, {
			"data-testid": "stToastViewButton",
			onClick: T,
			children: x ? "view less" : "view more"
		})] })]
	}), [
		b,
		x,
		n,
		r,
		y,
		T
	]);
	(0, f.useEffect)(() => {
		if (v.inSidebar) return;
		let e = u(c) ? c === 0 ? 0 : c * 1e3 : 4e3, t = s.info(D, {
			overrides: { ...E },
			autoHideDuration: e
		});
		return w(t), () => {
			s.update(t, { overrides: { Body: { style: { display: "none" } } } }), s.clear(t);
		};
	}, []), (0, f.useEffect)(() => {
		s.update(C, {
			children: D,
			overrides: { ...E }
		});
	}, [
		C,
		D,
		E
	]);
	let O = /* @__PURE__ */ l.jsx(o, {
		kind: t.ERROR,
		body: "Streamlit API Error: `st.toast` cannot be called directly on the sidebar with `st.sidebar.toast`.\n        See our `st.toast` API [docs](https://docs.streamlit.io/develop/api-reference/status/st.toast) for more information."
	});
	return /* @__PURE__ */ l.jsx(l.Fragment, { children: v.inSidebar && O });
}
var y = (0, f.memo)(v);
//#endregion
export { y as default, _ as shortenMessage };

//# sourceMappingURL=Toast-CJKq1jpo-BewEEd69.js.map