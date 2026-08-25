import { Ct as e, En as t, Ka as n, Mt as r, Sa as i, Ua as a, dt as o, oi as s, pa as c, ti as l, va as u } from "./index-Dl4ETd_L-D2oMd1k2.js";
import { n as d, t as f } from "./withFullScreenWrapper-tGGSjEWy-DoekoEMQ.js";
//#region ../react/build/ImageList-C_I_gGvM.js
var p = /* @__PURE__ */ n(a(), 1), m = /* @__PURE__ */ t("div", { target: "e115fcil3" })(({ theme: e, shouldStretch: t }) => ({
	display: "flex",
	flexDirection: "row",
	flexWrap: "wrap",
	rowGap: e.spacing.lg,
	maxWidth: "100%",
	width: t ? "100%" : "fit-content"
}), ""), h = /* @__PURE__ */ t("div", { target: "e115fcil2" })(({ theme: e, shouldStretch: t }) => ({
	display: "flex",
	flexDirection: "column",
	alignItems: "stretch",
	width: t ? "100%" : "auto",
	flexGrow: +!!t,
	">img": { borderRadius: e.radii.default }
}), ""), g = /* @__PURE__ */ t("div", { target: "e115fcil1" })(({ theme: e }) => ({
	textAlign: "center",
	marginTop: e.spacing.xs,
	wordWrap: "break-word",
	padding: e.spacing.threeXS
}), ""), _ = /* @__PURE__ */ t("a", { target: "e115fcil0" })(({ theme: e }) => ({
	display: "block",
	borderRadius: e.radii.default,
	overflow: "hidden",
	"&:hover": { opacity: .85 },
	"&:focus-visible": { boxShadow: e.shadows.focusRing }
}), ""), v = s.getLogger("ImageList");
function y(e, t) {
	if (e) {
		if (e.useStretch) return t;
		if (e.useContent) return;
		if (e.pixelWidth) return e.pixelWidth;
	}
}
var b = ({ itemKey: e, image: t, imgStyle: n, buildMediaURL: r, handleImageError: i, shouldStretch: a, link: s }) => {
	let u = c(t.url), d = /* @__PURE__ */ l.jsx("img", {
		style: n,
		src: r(t.url),
		alt: e,
		onError: i,
		crossOrigin: u
	});
	return /* @__PURE__ */ l.jsxs(h, {
		"data-testid": "stImageContainer",
		shouldStretch: a,
		children: [s ? /* @__PURE__ */ l.jsx(_, {
			href: s,
			target: "_blank",
			rel: "noreferrer",
			"aria-label": t.caption || s,
			"data-testid": "stImageLink",
			children: d
		}) : d, t.caption && /* @__PURE__ */ l.jsx(g, {
			"data-testid": "stImageCaption",
			style: n,
			children: /* @__PURE__ */ l.jsx(o, {
				source: t.caption,
				allowHTML: !1,
				isCaption: !0,
				isLabel: !0
			})
		})]
	});
};
function x({ element: t, endpoints: n, widthConfig: a, disableFullscreenMode: o }) {
	let s = i(t.imgs), { expanded: c, width: f, height: p, expand: h, collapse: g } = u(d), _ = f || 0, x = y(a, _), S = a?.useStretch ?? !1, C = {};
	p && c ? (C.maxHeight = p, C.objectFit = "contain", C.width = "100%") : (C.width = x ?? "100%", C.maxWidth = "100%");
	let w = (e) => {
		let t = e.currentTarget.src;
		v.error(`Client Error: Image source error - ${t}`), n.sendClientErrorToHost("Image", "Image source failed to load", "onerror triggered", t);
	};
	return /* @__PURE__ */ l.jsxs(e, {
		width: _,
		height: p,
		useContainerWidth: c,
		topCentered: !0,
		children: [/* @__PURE__ */ l.jsx(r, {
			target: e,
			isFullScreen: c,
			onExpand: h,
			onCollapse: g,
			disableFullscreenMode: o
		}), /* @__PURE__ */ l.jsx(m, {
			className: "stImage",
			"data-testid": "stImage",
			shouldStretch: S,
			children: s.map((e, r) => /* @__PURE__ */ l.jsx(b, {
				itemKey: r.toString(),
				image: e,
				imgStyle: C,
				buildMediaURL: (e) => n.buildMediaURL(e),
				handleImageError: w,
				shouldStretch: S,
				link: t.imgs.length === 1 ? t.link : void 0
			}, r))
		})]
	});
}
var S = (0, p.memo)(f(x));
//#endregion
export { S as default };

//# sourceMappingURL=ImageList-C_I_gGvM-B9E6ZaSX.js.map