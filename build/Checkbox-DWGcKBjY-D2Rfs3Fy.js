import { J as e, Ka as t, Ua as n, d as r, dt as i, gt as a, ii as o, ma as s, mt as c, sr as l, ti as u } from "./index-Dl4ETd_L-D2oMd1k2.js";
import { n as d, r as f, t as p } from "./checkbox-BlFkpHIT-CZhSzhvC.js";
import { t as m } from "./WidgetLabelHelpIconInline-BTmzKeRa-CZ4j9Xyg.js";
import { n as h } from "./useBasicWidgetState-D3zHnRUK-Dsaz4YO6.js";
//#region ../react/build/Checkbox-DWGcKBjY.js
var g = /* @__PURE__ */ t(n(), 1);
function _({ element: t, disabled: n, widgetMgr: _, fragmentId: S }) {
	let [C, w] = h({
		getStateFromWidgetMgr: v,
		getDefaultStateFromProto: y,
		getCurrStateFromProto: b,
		updateWidgetMgrState: x,
		element: t,
		widgetMgr: _,
		fragmentId: S,
		formClearBehavior: "resetValueOnly",
		queryParamBinding: t.queryParamKey ? {
			paramKey: t.queryParamKey,
			valueType: "bool_value",
			clearable: !1
		} : void 0
	}), T = (0, g.useCallback)((e) => {
		w({
			value: e.target.checked,
			fromUi: !0
		});
	}, [w]), E = s(), { colors: D, spacing: O, sizes: k } = E, A = l(E), j = n ? D.fadedText40 : D.bodyText;
	return /* @__PURE__ */ u.jsx(c, {
		className: "row-widget stCheckbox",
		"data-testid": "stCheckbox",
		children: /* @__PURE__ */ u.jsx(d, {
			checked: C,
			disabled: n,
			onChange: T,
			"aria-label": t.label,
			checkmarkType: t.type === r.StyleType.TOGGLE ? p.toggle : p.default,
			labelPlacement: f.right,
			overrides: {
				Root: { style: ({ $isFocusVisible: e }) => ({
					marginBottom: O.none,
					marginTop: O.none,
					backgroundColor: e ? D.darkenedBgMix25 : "",
					display: "flex",
					alignItems: "start"
				}) },
				Toggle: { style: ({ $checked: e }) => {
					let t = A ? D.bgColor : D.bodyText;
					return n && (t = A ? D.gray70 : D.gray90), {
						width: `calc(${k.checkbox} - ${E.spacing.twoXS})`,
						height: `calc(${k.checkbox} - ${E.spacing.twoXS})`,
						transform: e ? `translateX(${k.checkbox})` : "",
						backgroundColor: t,
						boxShadow: ""
					};
				} },
				ToggleTrack: { style: ({ $checked: e, $isHovered: t }) => {
					let r = D.borderColor;
					return t && !n && (r = D.darkenedBgMix15), e && !n && (r = D.primary), {
						marginRight: 0,
						marginLeft: 0,
						marginBottom: 0,
						marginTop: E.spacing.twoXS,
						paddingLeft: E.spacing.threeXS,
						paddingRight: E.spacing.threeXS,
						width: `calc(2 * ${k.checkbox})`,
						minWidth: `calc(2 * ${k.checkbox})`,
						height: k.checkbox,
						minHeight: k.checkbox,
						borderBottomLeftRadius: E.radii.full,
						borderTopLeftRadius: E.radii.full,
						borderBottomRightRadius: E.radii.full,
						borderTopRightRadius: E.radii.full,
						backgroundColor: r
					};
				} },
				Checkmark: { style: ({ $isFocusVisible: e, $checked: t }) => {
					let r = t && !n ? D.primary : D.borderColor;
					return {
						outline: 0,
						width: k.checkbox,
						height: k.checkbox,
						marginTop: E.spacing.twoXS,
						marginLeft: 0,
						marginBottom: 0,
						boxShadow: e && t ? E.shadows.focusRing : "",
						borderLeftWidth: k.borderWidth,
						borderRightWidth: k.borderWidth,
						borderTopWidth: k.borderWidth,
						borderBottomWidth: k.borderWidth,
						borderLeftColor: r,
						borderRightColor: r,
						borderTopColor: r,
						borderBottomColor: r
					};
				} },
				Label: { style: {
					lineHeight: E.lineHeights.small,
					paddingLeft: E.spacing.sm,
					position: "relative",
					color: j
				} }
			},
			children: /* @__PURE__ */ u.jsxs(a, {
				visibility: o(t.labelVisibility?.value),
				"data-testid": "stWidgetLabel",
				children: [/* @__PURE__ */ u.jsx(i, {
					source: t.label,
					allowHTML: !1,
					isLabel: !0,
					largerLabel: !0
				}), t.help && /* @__PURE__ */ u.jsx(m, {
					content: t.help,
					placement: e.TOP_RIGHT,
					label: t.label
				})]
			})
		})
	});
}
function v(e, t) {
	return e.getBoolValue(t);
}
function y(e) {
	return e.default ?? !1;
}
function b(e) {
	return e.value ?? !1;
}
function x(e, t, n, r) {
	t.setBoolValue(e, n.value, { fromUi: n.fromUi }, r);
}
var S = (0, g.memo)(_);
//#endregion
export { S as default };

//# sourceMappingURL=Checkbox-DWGcKBjY-D2Rfs3Fy.js.map