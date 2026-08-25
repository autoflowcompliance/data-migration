import { Cn as e, En as t, Ka as n, Mi as r, Ot as i, St as a, Ua as o, Wr as s, dt as c, h as l, ti as u } from "./index-Dl4ETd_L-D2oMd1k2.js";
import { a as d, i as f, r as p } from "./pandasStylerUtils-lPQUevWP-DEF4qf3G.js";
//#region ../react/build/Table-Bc9x-fDk.js
var m = /* @__PURE__ */ n(o(), 1), h = /* @__PURE__ */ t("div", { target: "e1artoc06" })(({ theme: e }) => ({
	fontSize: e.fontSizes.md,
	fontFamily: e.genericFonts.bodyFont,
	lineHeight: e.lineHeights.small,
	captionSide: "bottom",
	height: "100%",
	width: "100%",
	maxWidth: "100%",
	overflow: "clip",
	display: "block"
}), ""), g = /* @__PURE__ */ t("div", { target: "e1artoc05" })(({ theme: e }) => ({
	fontFamily: e.genericFonts.bodyFont,
	fontSize: e.fontSizes.sm,
	paddingTop: e.spacing.sm,
	paddingBottom: 0,
	color: e.colors.fadedText60,
	textAlign: "left",
	wordWrap: "break-word",
	display: "inline-block"
}), ""), _ = /* @__PURE__ */ t("div", { target: "e1artoc04" })(({ theme: e, borderMode: t, hasScrollableHeight: n }) => ({
	border: t === i.BorderMode.ALL ? `${e.sizes.borderWidth} solid ${e.colors.dataframeBorderColor}` : "none",
	borderRadius: e.radii.default,
	overflow: "auto",
	width: "100%",
	maxWidth: "100%",
	height: n ? "100%" : void 0,
	position: "relative",
	display: "block"
}), ""), v = /* @__PURE__ */ t("table", { target: "e1artoc03" })(({ theme: e, useContentWidth: t, hasScrollableWidth: n }) => ({
	color: e.colors.bodyText,
	borderSpacing: 0,
	display: "inline-table",
	verticalAlign: "top",
	minWidth: t || n ? void 0 : "100%"
}), ""), y = (e, t = i.BorderMode.ALL, n = !1) => ({
	borderBottom: t === i.BorderMode.NONE ? "none" : `${e.sizes.borderWidth} solid ${e.colors.dataframeBorderColor}`,
	"tbody tr:last-child &": { borderBottom: t === i.BorderMode.ALL || t === i.BorderMode.HORIZONTAL ? "none" : void 0 },
	borderRight: t === i.BorderMode.ALL ? `${e.sizes.borderWidth} solid ${e.colors.dataframeBorderColor}` : "none",
	"&:last-child": {
		borderRight: t === i.BorderMode.ALL ? "none" : void 0,
		paddingRight: t === i.BorderMode.NONE ? "0" : e.spacing.xs
	},
	verticalAlign: "middle",
	padding: `${e.spacing.twoXS} ${e.spacing.xs}`,
	"&:not(:first-of-type)": { paddingLeft: t === i.BorderMode.NONE || t === i.BorderMode.HORIZONTAL ? e.spacing.lg : e.spacing.xs },
	"&:first-of-type": { paddingLeft: t === i.BorderMode.NONE ? "0" : e.spacing.xs },
	fontWeight: e.fontWeights.normal,
	...n ? {
		whiteSpace: "nowrap",
		maxWidth: e.sizes.tableColumnMaxWidth,
		overflow: "hidden",
		textOverflow: "ellipsis"
	} : {
		whiteSpace: "nowrap",
		[`${a}`]: {
			display: "inline-block",
			width: "fit-content",
			maxWidth: e.sizes.tableColumnMaxWidth,
			whiteSpace: "normal",
			overflowWrap: "normal",
			wordBreak: "normal",
			overflowY: "hidden",
			verticalAlign: "top",
			margin: 0
		},
		[`${a}:has(pre)`]: {
			display: "block",
			width: "100%",
			maxWidth: "none"
		},
		[`${a} p`]: {
			whiteSpace: "normal",
			overflowWrap: "normal",
			wordBreak: "normal",
			margin: 0
		}
	}
}), b = /* @__PURE__ */ t("td", { target: "e1artoc02" })(({ theme: e, borderMode: t, truncateContent: n }) => y(e, t, n), ""), x = {
	corner: 3,
	header: 2,
	index: 1
}, S = /* @__PURE__ */ t("th", { target: "e1artoc01" })(({ theme: e, borderMode: t, stickyType: n, stickyTopOffset: r, stickyLeftOffset: a, truncateContent: o }) => {
	let s = {
		...y(e, t, o),
		textAlign: "inherit",
		color: e.colors.fadedText60,
		"&:first-of-type": { paddingLeft: t === i.BorderMode.NONE ? "0" : e.spacing.sm },
		"&:not(:first-of-type)": { paddingLeft: t === i.BorderMode.NONE || t === i.BorderMode.HORIZONTAL ? e.spacing.lg : e.spacing.sm }
	};
	if (n) {
		let t = {
			position: "sticky",
			backgroundColor: e.colors.bgColor
		};
		return (n === "header" || n === "corner") && (t.top = r ?? 0), (n === "index" || n === "corner") && (t.left = a ?? 0), t.zIndex = x[n], {
			...s,
			...t
		};
	}
	return s;
}, ""), C = /* @__PURE__ */ t(b, { target: "e1artoc00" })(({ theme: e }) => ({
	color: e.colors.gray70,
	fontStyle: "italic",
	fontSize: e.fontSizes.md,
	textAlign: "center"
}), ""), w = "2rem";
function T(e, t) {
	return e * t;
}
function E(e, t) {
	if (e && t) return "corner";
	if (e) return "header";
	if (t) return "index";
}
function D(t) {
	let n = t.data, { cssId: i, cssStyles: a, caption: o } = n.styler ?? {}, { numHeaderRows: s, numDataRows: c, numColumns: l, numIndexColumns: d } = n.dimensions, f = r(c), p = t.element.borderMode, y = t.element.hideIndex ?? !1, b = t.element.hideHeader ?? !1, x = y ? 0 : d, S = y ? l - d : l, E = !!t.heightConfig?.pixelHeight, D = !!t.widthConfig?.pixelWidth, A = !!t.widthConfig?.useContent, j = E && !b, M = D && x === 1, N = D, P = (0, m.useMemo)(() => r(s).map((t) => T(t, e(w))), [s]), F = [0];
	return /* @__PURE__ */ u.jsxs(h, {
		className: "stTable",
		"data-testid": "stTable",
		children: [
			a && /* @__PURE__ */ u.jsx("style", { children: a }),
			/* @__PURE__ */ u.jsx(_, {
				borderMode: p,
				hasScrollableHeight: E,
				tabIndex: E || D ? 0 : void 0,
				role: E || D ? "region" : void 0,
				"aria-label": E || D ? "Scrollable table" : void 0,
				children: /* @__PURE__ */ u.jsxs(v, {
					id: i,
					"data-testid": "stTableStyledTable",
					useContentWidth: A,
					hasScrollableWidth: D,
					children: [s > 0 && !b && O(n, p, j, M, d, P, F, N, y), /* @__PURE__ */ u.jsx("tbody", { children: f.length === 0 ? /* @__PURE__ */ u.jsx("tr", { children: /* @__PURE__ */ u.jsx(C, {
						"data-testid": "stTableStyledEmptyTableCell",
						colSpan: S || 1,
						borderMode: p,
						truncateContent: N,
						children: "empty"
					}) }) : f.map((e) => k(n, e, l, p, M, d, F, N, y)) })]
				})
			}),
			o && /* @__PURE__ */ u.jsx(g, { children: o })
		]
	});
}
function O(e, t, n, r, a, o, l, d, f) {
	let m = t === i.BorderMode.NONE || t === i.BorderMode.HORIZONTAL;
	return /* @__PURE__ */ u.jsx("thead", { children: p(e).map((i, p) => /* @__PURE__ */ u.jsx("tr", { children: i.map((i, h) => {
		if (f && h < a) return null;
		let g = "inherit";
		if (m && e.dimensions.numDataRows > 0) {
			let { contentType: t } = e.getCell(0, h);
			g = s(t) ? "right" : "left";
		}
		let _ = h < a, v = n, y = r && _, b = v ? o[p] : void 0, x = y ? l[h] : void 0, C = E(v, y);
		return /* @__PURE__ */ u.jsx(S, {
			className: i.cssClass,
			scope: "col",
			borderMode: t,
			stickyType: C,
			stickyTopOffset: b,
			stickyLeftOffset: x,
			truncateContent: d,
			style: { textAlign: g },
			children: /* @__PURE__ */ u.jsx(c, {
				source: i.name || "\xA0",
				allowHTML: !1
			})
		}, h);
	}) }, p)) });
}
function k(e, t, n, i, a, o, s, c, l) {
	return /* @__PURE__ */ u.jsx("tr", { children: r(n).map((n) => l && n < o ? null : A(e, t, n, i, a, o, s, c)) }, t);
}
function A(e, t, n, r, i, a, o, p) {
	let { type: m, content: h, contentType: g } = e.getCell(t, n), _ = d(e, t, n), v = _?.displayContent || f(h, g), y = !1, x = { textAlign: s(g) ? "right" : "left" };
	switch (v?.endsWith("<span class=\"pd-t\"></span>") && (v = v.replace(/<span class="pd-t"><\/span>$/, ""), y = !0), m) {
		case l.INDEX: {
			let e = i && n < a ? "index" : void 0, t = e === "index" ? o[n] : void 0;
			return /* @__PURE__ */ u.jsxs(S, {
				scope: "row",
				id: _?.cssId,
				className: _?.cssClass,
				borderMode: r,
				stickyType: e,
				stickyLeftOffset: t,
				truncateContent: p,
				children: [y && /* @__PURE__ */ u.jsx("span", { className: "pd-t" }), /* @__PURE__ */ u.jsx(c, {
					source: v || "\xA0",
					allowHTML: !1
				})]
			}, n);
		}
		case l.DATA: return /* @__PURE__ */ u.jsxs(b, {
			id: _?.cssId,
			className: _?.cssClass,
			style: x,
			borderMode: r,
			truncateContent: p,
			children: [y && /* @__PURE__ */ u.jsx("span", { className: "pd-t" }), /* @__PURE__ */ u.jsx(c, {
				source: v || "\xA0",
				allowHTML: !1
			})]
		}, n);
		default: throw Error(`Cannot parse type "${m}".`);
	}
}
var j = (0, m.memo)(D);
//#endregion
export { D as Table, j as default };

//# sourceMappingURL=Table-Bc9x-fDk-DnJcb3Hg.js.map