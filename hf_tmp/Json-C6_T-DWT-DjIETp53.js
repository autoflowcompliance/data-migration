import { C as e, En as t, Ka as n, Mn as r, Ua as i, X as a, fa as o, ma as s, q as c, sr as l, t as u, ti as d, x as f } from "./index-Dl4ETd_L-D2oMd1k2.js";
import { t as p } from "./index-CVld_lKx-BpaiPOLH.js";
import { t as m } from "./reactJsonViewCompat-BZlB_0r4-BAr45JB0.js";
//#region ../react/build/Json-C6_T-DWT.js
var h = /* @__PURE__ */ n(i(), 1), g = /* @__PURE__ */ t("div", { target: "e1xfr5s3" })(({ theme: e }) => ({
	overflowY: "auto",
	position: "relative",
	".react-json-view .copy-icon svg": {
		fontSize: "1em !important",
		marginRight: `${e.spacing.threeXS} !important`,
		verticalAlign: "middle !important"
	}
}), ""), _ = /* @__PURE__ */ t("div", { target: "e1xfr5s2" })(({ theme: e }) => ({
	display: "flex",
	alignItems: "center",
	gap: e.spacing.sm,
	padding: e.spacing.sm,
	paddingLeft: e.spacing.md,
	fontFamily: e.genericFonts.codeFont,
	fontSize: e.fontSizes.twoSm,
	color: e.colors.bodyText,
	maxWidth: "90vw",
	wordBreak: "break-all"
}), ""), v = /* @__PURE__ */ t("button", { target: "e1xfr5s1" })(({ theme: e }) => ({
	display: "flex",
	alignItems: "center",
	justifyContent: "center",
	padding: e.spacing.threeXS,
	backgroundColor: "transparent",
	border: "none",
	borderRadius: e.radii.sm,
	cursor: "pointer",
	color: e.colors.fadedText60,
	transition: "color 0.15s ease, background-color 0.15s ease",
	"&:hover": {
		backgroundColor: e.colors.darkenedBgMix15,
		color: e.colors.bodyText
	},
	"&:active": { backgroundColor: e.colors.darkenedBgMix25 },
	"&:focus": { outline: "none" },
	"&:focus-visible": { boxShadow: e.shadows.focusRing }
}), ""), y = /* @__PURE__ */ t("div", { target: "e1xfr5s0" })(({ top: e, left: t }) => ({
	position: "fixed",
	top: e,
	left: t
}), "");
function b({ top: e, left: t, path: n, clearTooltip: r }) {
	let [i, p] = (0, h.useState)(!0), m = s(), { colors: g, radii: b } = m, { isCopied: x, copyToClipboard: S, label: C } = o(), w = (0, h.useCallback)(() => {
		p(!1), r();
	}, [r]), T = (0, h.useCallback)(() => {
		S(n);
	}, [S, n]);
	return /* @__PURE__ */ d.jsx(a, {
		content: /* @__PURE__ */ d.jsxs(_, {
			"data-testid": "stJsonPathTooltip",
			children: [/* @__PURE__ */ d.jsx("code", { children: n }), /* @__PURE__ */ d.jsx(v, {
				onClick: T,
				title: C,
				"aria-label": C,
				autoFocus: !0,
				children: /* @__PURE__ */ d.jsx(f, {
					size: "sm",
					iconValue: x ? ":material/check:" : ":material/content_copy:"
				})
			})]
		}),
		placement: c.top,
		accessibilityType: u.tooltip,
		showArrow: !1,
		popoverMargin: 15,
		onClickOutside: w,
		onEsc: w,
		overrides: {
			Body: { style: {
				borderTopLeftRadius: b.default,
				borderTopRightRadius: b.default,
				borderBottomLeftRadius: b.default,
				borderBottomRightRadius: b.default,
				paddingTop: "0 !important",
				paddingBottom: "0 !important",
				paddingLeft: "0 !important",
				paddingRight: "0 !important",
				backgroundColor: "transparent"
			} },
			Inner: { style: {
				backgroundColor: l(m) ? g.bgColor : g.secondaryBg,
				color: g.bodyText,
				borderTopLeftRadius: b.default,
				borderTopRightRadius: b.default,
				borderBottomLeftRadius: b.default,
				borderBottomRightRadius: b.default,
				paddingTop: "0 !important",
				paddingBottom: "0 !important",
				paddingLeft: "0 !important",
				paddingRight: "0 !important"
			} }
		},
		isOpen: i,
		children: /* @__PURE__ */ d.jsx(y, {
			"data-testid": "stJsonPathTooltipTarget",
			top: e,
			left: t
		})
	});
}
var x = (0, h.memo)(b);
function S(e) {
	return e.length === 0 ? "$" : e.reduce((e, t, n) => t === null ? e : /^\d+$/.test(t) ? `${e}[${t}]` : t === "" || /[^a-zA-Z0-9_$]/.test(t) || /^\d/.test(t) ? `${e}["${t.replace(/\\/g, "\\\\").replace(/"/g, "\\\"")}"]` : n === 0 || e === "" ? t : `${e}.${t}`, "");
}
function C() {
	let [e, t] = (0, h.useState)(null), n = (0, h.useRef)({
		x: 0,
		y: 0
	});
	return (0, h.useEffect)(() => {
		let e = (e) => {
			n.current = {
				x: e.clientX,
				y: e.clientY
			};
		};
		return document.addEventListener("mousedown", e), () => document.removeEventListener("mousedown", e);
	}, []), {
		tooltip: e,
		handleSelect: (0, h.useCallback)((e) => {
			let { x: r, y: i } = n.current;
			t({
				path: S([...e.namespace, e.name]),
				x: r,
				y: i
			});
		}, []),
		clearTooltip: (0, h.useCallback)(() => {
			t(null);
		}, [])
	};
}
function w({ element: t }) {
	let n = s(), { tooltip: i, handleSelect: a, clearTooltip: c } = C(), { copyToClipboard: u } = o(), f = (0, h.useCallback)((e) => {
		u(JSON.stringify(e.src));
	}, [u]), _;
	try {
		_ = JSON.parse(t.body);
	} catch (n) {
		let i = r(n);
		try {
			_ = p.parse(t.body);
		} catch {
			let n = parseInt(i.message.replace(/[^0-9]/g, ""), 10);
			return i.message += `
${t.body.substring(0, n + 1)} ← here`, /* @__PURE__ */ d.jsx(e, {
				name: "Json Parse Error",
				message: i.message
			});
		}
	}
	let v = l(n) ? "rjv-default" : "monokai";
	return /* @__PURE__ */ d.jsxs(g, {
		className: "stJson",
		"data-testid": "stJson",
		children: [/* @__PURE__ */ d.jsx(m, {
			src: _,
			collapsed: t.maxExpandDepth ?? !t.expanded,
			displayDataTypes: !1,
			displayObjectSize: !1,
			name: !1,
			theme: v,
			enableClipboard: f,
			onSelect: a,
			showComma: !1,
			style: {
				fontFamily: n.genericFonts.codeFont,
				fontSize: n.fontSizes.codeFontSize,
				fontWeight: n.fontWeights.code,
				backgroundColor: n.colors.bgColor,
				whiteSpace: "pre-wrap"
			}
		}), i && /* @__PURE__ */ d.jsx(x, {
			top: i.y,
			left: i.x,
			path: i.path,
			clearTooltip: c
		})]
	});
}
var T = (0, h.memo)(w);
//#endregion
export { T as default };

//# sourceMappingURL=Json-C6_T-DWT-DjIETp53.js.map