import { Bt as e, Da as t, En as n, Ka as r, Ua as i, da as a, ma as o, ti as s, ur as c } from "./index-Dl4ETd_L-D2oMd1k2.js";
//#region ../react/build/withFullScreenWrapper-tGGSjEWy.js
var l = /* @__PURE__ */ r(i(), 1), u = (0, l.createContext)(null);
u.displayName = "ElementFullscreenContext";
var d = /* @__PURE__ */ n("div", { target: "elp1w7k0" })(({ theme: e, isExpanded: t }) => ({
	width: "100%",
	height: "100%",
	...t ? {
		position: "fixed",
		top: 0,
		left: 0,
		bottom: 0,
		right: 0,
		background: e.colors.bgColor,
		zIndex: e.zIndices.fullscreenWrapper,
		padding: e.spacing.md,
		paddingTop: e.sizes.fullScreenHeaderHeight,
		overflow: "auto",
		display: "flex",
		alignItems: "center",
		justifyContent: "center"
	} : {}
}), ""), f = () => {
	let { setFullScreen: n } = (0, l.useContext)(e), [r, i] = (0, l.useState)(!1), { fullHeight: a, fullWidth: o } = t(), s = (0, l.useCallback)((e) => {
		i(e), n(e);
	}, [n]), c = (0, l.useCallback)(() => {
		document.body.style.overflow = "hidden", s(!0);
	}, [s]), u = (0, l.useCallback)(() => {
		document.body.style.overflow = "unset", s(!1);
	}, [s]), d = (0, l.useCallback)((e) => {
		e.keyCode === 27 && r && u();
	}, [u, r]);
	return (0, l.useEffect)(() => (document.addEventListener("keydown", d, !1), () => {
		document.removeEventListener("keydown", d, !1);
	}), [d]), (0, l.useMemo)(() => ({
		expanded: r,
		zoomIn: c,
		zoomOut: u,
		fullHeight: a,
		fullWidth: o
	}), [
		r,
		c,
		u,
		a,
		o
	]);
}, p = ({ children: e }) => {
	let t = o(), { expanded: n, fullHeight: r, fullWidth: i, zoomIn: c, zoomOut: p } = f(), { width: m, elementRef: h } = a(), g = (0, l.useMemo)(() => ({
		width: n ? i : m,
		height: n ? r : void 0,
		expanded: n,
		expand: c,
		collapse: p
	}), [
		n,
		r,
		i,
		m,
		c,
		p
	]);
	return /* @__PURE__ */ s.jsx(u.Provider, {
		value: g,
		children: /* @__PURE__ */ s.jsx(d, {
			ref: h,
			isExpanded: n,
			"data-testid": "stFullScreenFrame",
			theme: t,
			children: e
		})
	});
};
function m(e) {
	let t = (t) => /* @__PURE__ */ s.jsx(p, { children: /* @__PURE__ */ s.jsx(e, { ...t }) });
	return t.displayName = `withFullScreenWrapper(${e.displayName || e.name})`, c(t, e);
}
//#endregion
export { u as n, m as t };

//# sourceMappingURL=withFullScreenWrapper-tGGSjEWy-DoekoEMQ.js.map