import { En as e, Ka as t, Ua as n, dt as r, pn as i, ti as a, x as o } from "./index-Dl4ETd_L-D2oMd1k2.js";
//#region ../react/build/Spinner-B3_-SaXN.js
var s = /* @__PURE__ */ t(n(), 1), c = /* @__PURE__ */ e("div", { target: "e1se5lgy3" })(({ theme: e, cache: t }) => ({ ...t ? {
	paddingBottom: e.spacing.lg,
	background: `linear-gradient(to bottom, ${e.colors.bgColor} 0%, ${e.colors.bgColor} 80%, transparent 100%)`
} : null }), ""), l = /* @__PURE__ */ e("div", { target: "e1se5lgy2" })(({ theme: e }) => ({
	display: "flex",
	alignItems: "center",
	width: "100%",
	gap: e.spacing.sm
}), ""), u = /* @__PURE__ */ e("div", { target: "e1se5lgy1" })(({ theme: e }) => ({
	display: "flex",
	gap: e.spacing.sm,
	alignItems: "baseline"
}), ""), d = /* @__PURE__ */ e("span", { target: "e1se5lgy0" })(({ theme: e }) => ({
	opacity: .6,
	fontSize: e.fontSizes.sm,
	lineHeight: e.lineHeights.none,
	whiteSpace: "nowrap"
}), ""), f = (e) => {
	let t = Math.floor(e / 3600), n = Math.floor(e % 3600 / 60), r = e % 60;
	return t === 0 && n === 0 ? `(${r.toFixed(1)} seconds)` : t === 0 ? `(${`${n} minute${n === 1 ? "" : "s"}`}${r === 0 ? "" : `, ${r.toFixed(1)} seconds`})` : `(${`${t} hour${t === 1 ? "" : "s"}`}${n === 0 ? "" : `, ${n} minute${n === 1 ? "" : "s"}`}${r === 0 ? "" : `, ${r.toFixed(1)} seconds`})`;
};
function p({ element: e }) {
	let { cache: t, showTime: n } = e, [p, m] = (0, s.useState)(0), h = (0, s.useRef)(null);
	return (0, s.useEffect)(() => {
		if (!n) return;
		h.current = Date.now();
		let e = () => {
			h.current !== null && m((Date.now() - h.current) / 1e3);
		};
		e();
		let t = setInterval(e, 100);
		return () => clearInterval(t);
	}, [n]), /* @__PURE__ */ a.jsx(c, {
		className: i({
			stSpinner: !0,
			stCacheSpinner: t
		}),
		"data-testid": "stSpinner",
		cache: t,
		children: /* @__PURE__ */ a.jsxs(l, { children: [/* @__PURE__ */ a.jsx(o, {
			size: "lg",
			iconValue: "spinner"
		}), /* @__PURE__ */ a.jsxs(u, { children: [/* @__PURE__ */ a.jsx(r, {
			source: e.text,
			allowHTML: !1
		}), n && /* @__PURE__ */ a.jsx(d, { children: f(p) })] })] })
	});
}
var m = (0, s.memo)(p);
//#endregion
export { m as default };

//# sourceMappingURL=Spinner-B3_-SaXN-C-zFM0mD.js.map