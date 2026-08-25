import { Cn as e, En as t, Ka as n, Pr as r, R as i, Ua as a, Un as o, da as ee, ii as s, ma as c, ti as l } from "./index-Dl4ETd_L-D2oMd1k2.js";
import { t as u } from "./WidgetLabel-CQfHGtry-udktvHE5.js";
import { t as d } from "./WidgetLabelHelpIcon-C6IRqJ_I-BBI6AbZ-.js";
import { n as f } from "./useBasicWidgetState-D3zHnRUK-Dsaz4YO6.js";
import { t as p } from "./InputInstructions-BQBBgzXB-ClQbP4Gu.js";
import { n as m, t as h } from "./useTextInputAutoExpand-D9pA1iXq-CBWLLIpD.js";
import { n as g, r as _, t as v } from "./useUpdateUiValue-CsBMIrnj-CV6fKyop.js";
//#region ../react/build/TextArea-B1xQzjI6.js
var y = /* @__PURE__ */ n(a(), 1), b = (e, t) => {
	let n = "auto";
	if (e.heightConfig?.useStretch) n = "100%";
	else if (e.heightConfig?.pixelHeight && e.heightConfig.pixelHeight > 0) {
		let r = s(t.labelVisibility?.value) === i.Collapsed ? 2 : 30, a = e.heightConfig.pixelHeight - r;
		n = `${Math.max(0, a)}px`;
	}
	return n;
}, x = /* @__PURE__ */ t("div", { target: "ezh4s2r0" })({
	name: "kdbhus",
	styles: "height:100%;display:flex;flex-direction:column"
}), S = (e, t) => e.getStringValue(t) ?? null, C = (e) => e.default ?? null, w = (e) => e.value ?? null, T = (e, t, n, r) => {
	t.setStringValue(e, n.value, { fromUi: n.fromUi }, r);
}, E = (0, y.memo)(({ disabled: t, element: n, widgetMgr: i, fragmentId: a, outerElement: E }) => {
	let D = (0, y.useId)(), { width: O, elementRef: k } = ee(), [A, j] = (0, y.useState)(!1), [M, N] = (0, y.useState)(!1), P = E.heightConfig?.useContent ?? !1, F = E.heightConfig?.useStretch ?? !1, I = b(E, n), L = (0, y.useRef)(null), [R, z] = (0, y.useState)(() => S(i, n) ?? null), [B, V] = f({
		getStateFromWidgetMgr: S,
		getDefaultStateFromProto: C,
		getCurrStateFromProto: w,
		updateWidgetMgrState: T,
		element: n,
		widgetMgr: i,
		fragmentId: a,
		formClearBehavior: "resetValueAndRunCallback",
		onFormCleared: (0, y.useCallback)(() => {
			z(n.default ?? null), j(!0);
		}, [n]),
		queryParamBinding: n.queryParamKey ? {
			paramKey: n.queryParamKey,
			valueType: "string_value",
			clearable: !0
		} : void 0
	});
	g(B, R, z, A);
	let H = c(), U = (0, y.useRef)(!1), { height: W, maxHeight: G, updateScrollHeight: K } = m({
		textareaRef: L,
		dependencies: [n.placeholder, ...P ? [R] : [B]]
	});
	(0, y.useLayoutEffect)(() => {
		P && O > 0 && !U.current && (U.current = !0, K());
	}, [
		P,
		O,
		K
	]);
	let q = (0, y.useCallback)(() => {
		j(!1), V({
			value: R,
			fromUi: !0
		});
	}, [R, V]), J = (0, y.useCallback)(() => {
		A && q(), N(!1);
	}, [A, q]), Y = (0, y.useCallback)(() => {
		N(!0);
	}, []), X = (0, y.useCallback)(() => {
		P && K();
	}, [P, K]), Z = v({
		formId: n.formId,
		maxChars: n.maxChars,
		setDirty: j,
		setUiValue: z,
		setValueWithSource: V,
		additionalAction: X
	}), Q = _(n.formId, q, A, i, a, !0), { placeholder: te, formId: $ } = n, ne = r({ formId: $ }) ? i.allowFormEnterToSubmit($) : A, re = M && O > e(H.breakpoints.hideWidgetDetails);
	return /* @__PURE__ */ l.jsxs(x, {
		className: "stTextArea",
		"data-testid": "stTextArea",
		ref: k,
		children: [
			/* @__PURE__ */ l.jsx(u, {
				label: n.label,
				disabled: t,
				labelVisibility: s(n.labelVisibility?.value),
				htmlFor: D,
				children: n.help && /* @__PURE__ */ l.jsx(d, {
					content: n.help,
					label: n.label
				})
			}),
			/* @__PURE__ */ l.jsx(h, {
				inputRef: P ? L : void 0,
				value: R ?? "",
				placeholder: te,
				onBlur: J,
				onFocus: Y,
				onChange: Z,
				onKeyDown: Q,
				"aria-label": n.label,
				disabled: t,
				id: D,
				overrides: {
					Input: { style: {
						fontWeight: H.fontWeights.normal,
						lineHeight: H.lineHeights.inputWidget,
						height: P ? W : I,
						maxHeight: P ? G : "",
						minHeight: H.sizes.largestElementHeight,
						resize: F ? "none" : "vertical",
						paddingRight: H.spacing.md,
						paddingLeft: H.spacing.md,
						paddingBottom: H.spacing.md,
						paddingTop: H.spacing.md,
						"::placeholder": { color: H.colors.fadedText60 }
					} },
					Root: {
						props: { "data-testid": "stTextAreaRootElement" },
						style: ({ $isFocused: e }) => {
							let t = o(H.colors, e);
							return {
								borderLeftWidth: H.sizes.borderWidth,
								borderRightWidth: H.sizes.borderWidth,
								borderTopWidth: H.sizes.borderWidth,
								borderBottomWidth: H.sizes.borderWidth,
								borderTopColor: t,
								borderRightColor: t,
								borderBottomColor: t,
								borderLeftColor: t,
								flexGrow: 1
							};
						}
					}
				}
			}),
			re && /* @__PURE__ */ l.jsx(p, {
				dirty: A,
				value: R ?? "",
				maxLength: n.maxChars,
				type: "multiline",
				inForm: r({ formId: $ }),
				allowEnterToSubmit: ne
			})
		]
	});
});
//#endregion
export { E as default };

//# sourceMappingURL=TextArea-B1xQzjI6-CppXj4dW.js.map