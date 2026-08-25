import { En as e, Gi as t, Ka as n, Ua as r, ti as i, w as a, x as o } from "./index-Dl4ETd_L-D2oMd1k2.js";
import { n as s } from "./useBasicWidgetState-D3zHnRUK-Dsaz4YO6.js";
//#region ../react/build/Feedback-BcHw2pQG.js
var c = /* @__PURE__ */ n(r(), 1), l = /* @__PURE__ */ e("div", { target: "e1b8h3j92" })(({ containerWidth: e }) => ({
	width: e ? "100%" : "auto",
	minWidth: "fit-content"
}), ""), u = /* @__PURE__ */ e("div", { target: "e1b8h3j91" })(({ theme: e }) => ({
	display: "flex",
	flexWrap: "nowrap",
	gap: e.spacing.threeXS,
	minWidth: "fit-content"
}), ""), d = /* @__PURE__ */ e("button", { target: "e1b8h3j90" })(({ theme: e, isSelected: t }) => ({
	display: "inline-flex",
	alignItems: "center",
	justifyContent: "center",
	padding: e.spacing.threeXS,
	margin: e.spacing.none,
	backgroundColor: e.colors.transparent,
	color: t ? e.colors.bodyText : e.colors.fadedText60,
	border: "none",
	borderRadius: e.radii.button,
	cursor: "pointer",
	userSelect: "none",
	minHeight: "unset",
	flex: "0 0 fit-content",
	"&:focus": {
		boxShadow: "none",
		outline: "none"
	},
	"&:focus-visible": { boxShadow: e.shadows.focusRing },
	"&:hover:not(:disabled)": { color: e.colors.bodyText },
	"&:disabled": {
		color: t ? e.colors.fadedText40 : e.colors.fadedText10,
		cursor: "not-allowed",
		img: { opacity: .4 }
	}
}), ""), f = [":material/thumb_up:", ":material/thumb_down:"], p = [
	":material/sentiment_sad:",
	":material/sentiment_dissatisfied:",
	":material/sentiment_neutral:",
	":material/sentiment_satisfied:",
	":material/sentiment_very_satisfied:"
], m = ":material/star:", h = ":material/star_filled:", g = 5;
function _(e) {
	switch (e) {
		case a.FeedbackType.FACES: return p.map((e, t) => ({
			icon: e,
			selectedIcon: e,
			value: t
		}));
		case a.FeedbackType.STARS: return Array.from({ length: g }, (e, t) => ({
			icon: m,
			selectedIcon: h,
			value: t
		}));
		default: return [{
			icon: f[0],
			selectedIcon: f[0],
			value: 1
		}, {
			icon: f[1],
			selectedIcon: f[1],
			value: 0
		}];
	}
}
function v(e, t) {
	switch (t) {
		case a.FeedbackType.THUMBS: return e === 1 ? "Thumbs up" : "Thumbs down";
		case a.FeedbackType.FACES: return [
			"Very dissatisfied",
			"Dissatisfied",
			"Neutral",
			"Satisfied",
			"Very satisfied"
		][e] ?? `Rating ${e + 1}`;
		case a.FeedbackType.STARS: return `${e + 1} out of ${g} stars`;
		default: return `Rating ${e + 1}`;
	}
}
function y(e, t, n) {
	return t === null ? !1 : n === a.FeedbackType.STARS ? e <= t : e === t;
}
function b(e, t) {
	let n = e.getStringValue(t);
	if (n !== void 0) return n === "" ? null : parseInt(n, 10);
}
function x(e) {
	return e.default ?? null;
}
function S(e) {
	return e.value ?? null;
}
function C(e, t, n, r) {
	let i = n.value === null ? "" : String(n.value);
	t.setStringValue(e, i, { fromUi: n.fromUi }, r);
}
function w(e) {
	let { disabled: n, element: r, fragmentId: a, widgetMgr: f, widthConfig: p } = e, { type: m } = r, [h, g] = s({
		getStateFromWidgetMgr: b,
		getDefaultStateFromProto: x,
		getCurrStateFromProto: S,
		updateWidgetMgrState: C,
		element: r,
		widgetMgr: f,
		fragmentId: a,
		formClearBehavior: "resetValueOnly"
	}), w = r.value ?? h, T = t(p), E = (0, c.useMemo)(() => _(m), [m]), D = (0, c.useRef)([]), O = (0, c.useCallback)((e) => {
		g({
			value: w === e ? null : e,
			fromUi: !0
		});
	}, [w, g]), k = (0, c.useCallback)((e, t) => {
		let n;
		switch (e.key) {
			case "ArrowLeft":
			case "ArrowUp":
				e.preventDefault(), n = t > 0 ? t - 1 : E.length - 1;
				break;
			case "ArrowRight":
			case "ArrowDown":
				e.preventDefault(), n = t < E.length - 1 ? t + 1 : 0;
				break;
			case " ":
			case "Enter":
				e.preventDefault(), O(E[t].value);
				return;
			default: return;
		}
		D.current[n]?.focus();
	}, [E, O]);
	return /* @__PURE__ */ i.jsx(l, {
		className: "stFeedback",
		"data-testid": "stFeedback",
		containerWidth: T,
		children: /* @__PURE__ */ i.jsx(u, {
			role: "radiogroup",
			"aria-label": "Feedback rating",
			children: E.map((e, t) => {
				let r = y(e.value, w, m), a = r ? e.selectedIcon : e.icon;
				return /* @__PURE__ */ i.jsx(d, {
					ref: (e) => {
						D.current[t] = e;
					},
					type: "button",
					role: "radio",
					"aria-checked": w === e.value,
					"aria-label": v(e.value, m),
					tabIndex: w === e.value || w === null && t === 0 ? 0 : -1,
					disabled: n,
					isSelected: r,
					onClick: () => O(e.value),
					onKeyDown: (e) => k(e, t),
					"data-testid": r ? "stFeedbackButtonActive" : "stFeedbackButton",
					children: /* @__PURE__ */ i.jsx(o, {
						iconValue: a,
						size: "lg"
					})
				}, e.value);
			})
		})
	});
}
var T = (0, c.memo)(w);
//#endregion
export { T as default };

//# sourceMappingURL=Feedback-BcHw2pQG-WYt6SpuG.js.map