import { Cn as e, En as t, Ka as n, Pr as r, Ua as i, Un as a, da as o, ii as s, kt as c, ma as l, ti as u, x as d, zr as f } from "./index-Dl4ETd_L-D2oMd1k2.js";
import { t as p } from "./WidgetLabel-CQfHGtry-udktvHE5.js";
import { t as m } from "./WidgetLabelHelpIcon-C6IRqJ_I-BBI6AbZ-.js";
import { n as h } from "./useBasicWidgetState-D3zHnRUK-Dsaz4YO6.js";
import { t as g } from "./InputInstructions-BQBBgzXB-ClQbP4Gu.js";
import { t as _ } from "./input-CClPhvPt-C_5WYNdx.js";
import { n as v, r as y, t as b } from "./useUpdateUiValue-CsBMIrnj-CV6fKyop.js";
//#region ../react/build/TextInput-D1xd0P97.js
var x = /* @__PURE__ */ n(i(), 1), S = /* @__PURE__ */ t("div", { target: "e11y4ecf0" })({
	name: "bjn8wh",
	styles: "position:relative"
});
function C({ disabled: t, element: n, widgetMgr: i, fragmentId: c }) {
	let [C, k] = (0, x.useState)(() => w(i, n) ?? null), { width: A, elementRef: j } = o(), [M, N] = (0, x.useState)(!1), [P, F] = h({
		getStateFromWidgetMgr: w,
		getDefaultStateFromProto: T,
		getCurrStateFromProto: E,
		updateWidgetMgrState: D,
		element: n,
		widgetMgr: i,
		fragmentId: c,
		formClearBehavior: "resetValueAndRunCallback",
		onFormCleared: (0, x.useCallback)(() => {
			k(n.default ?? null), N(!0);
		}, [n.default]),
		queryParamBinding: n.queryParamKey ? {
			paramKey: n.queryParamKey,
			valueType: "string_value",
			clearable: !0
		} : void 0
	});
	v(P, C, k, M);
	let [I, L] = (0, x.useState)(!1), R = l(), z = (0, x.useId)(), { placeholder: B, formId: V, icon: H, maxChars: U } = n, W = (0, x.useCallback)(() => {
		N(!1), F({
			value: C,
			fromUi: !0
		});
	}, [C, F]), G = r({ formId: V }) ? i.allowFormEnterToSubmit(V) : M, K = I && A > e(R.breakpoints.hideWidgetDetails), q = (0, x.useCallback)(() => {
		M && W(), L(!1);
	}, [M, W]), J = (0, x.useCallback)(() => {
		L(!0);
	}, []), Y = b({
		formId: V,
		maxChars: U,
		setDirty: N,
		setUiValue: k,
		setValueWithSource: F
	}), X = y(V, W, M, i, c);
	return /* @__PURE__ */ u.jsxs(S, {
		className: "stTextInput",
		"data-testid": "stTextInput",
		ref: j,
		children: [
			/* @__PURE__ */ u.jsx(p, {
				label: n.label,
				disabled: t,
				labelVisibility: s(n.labelVisibility?.value),
				htmlFor: z,
				children: n.help && /* @__PURE__ */ u.jsx(m, {
					content: n.help,
					label: n.label
				})
			}),
			/* @__PURE__ */ u.jsx(_, {
				value: C ?? "",
				placeholder: B,
				onBlur: q,
				onFocus: J,
				onChange: Y,
				onKeyPress: X,
				"aria-label": n.label,
				disabled: t,
				id: z,
				type: O(n),
				autoComplete: n.autocomplete,
				startEnhancer: H && /* @__PURE__ */ u.jsx(d, {
					"data-testid": "stTextInputIcon",
					iconValue: H,
					size: "lg"
				}),
				overrides: {
					Input: { style: {
						fontWeight: R.fontWeights.normal,
						minWidth: 0,
						lineHeight: R.lineHeights.inputWidget,
						paddingRight: R.spacing.sm,
						paddingLeft: R.spacing.md,
						paddingBottom: R.spacing.sm,
						paddingTop: R.spacing.sm,
						"::placeholder": { color: R.colors.fadedText60 }
					} },
					Root: {
						props: { "data-testid": "stTextInputRootElement" },
						style: ({ $isFocused: e }) => {
							let t = a(R.colors, e);
							return {
								height: R.sizes.minElementHeight,
								borderLeftWidth: R.sizes.borderWidth,
								borderRightWidth: R.sizes.borderWidth,
								borderTopWidth: R.sizes.borderWidth,
								borderBottomWidth: R.sizes.borderWidth,
								borderTopColor: t,
								borderRightColor: t,
								borderBottomColor: t,
								borderLeftColor: t,
								paddingLeft: H ? R.spacing.sm : 0
							};
						}
					},
					StartEnhancer: { style: {
						paddingLeft: 0,
						paddingRight: 0,
						minWidth: R.iconSizes.lg,
						color: f(H) ? R.colors.fadedText60 : "inherit"
					} }
				}
			}),
			K && /* @__PURE__ */ u.jsx(g, {
				dirty: M,
				value: C ?? "",
				maxLength: U,
				inForm: r({ formId: V }),
				allowEnterToSubmit: G
			})
		]
	});
}
function w(e, t) {
	return e.getStringValue(t) ?? null;
}
function T(e) {
	return e.default ?? null;
}
function E(e) {
	return e.value ?? null;
}
function D(e, t, n, r) {
	t.setStringValue(e, n.value, { fromUi: n.fromUi }, r);
}
function O(e) {
	return e.type === c.Type.PASSWORD ? "password" : "text";
}
var k = (0, x.memo)(C);
//#endregion
export { k as default };

//# sourceMappingURL=TextInput-D1xd0P97-CcUc9Gq9.js.map