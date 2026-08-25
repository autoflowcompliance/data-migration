import { Cn as e, Ka as t, P as n, Ua as r, Un as i, Ur as a, ha as o, ii as s, ma as c, nr as l, ti as u } from "./index-Dl4ETd_L-D2oMd1k2.js";
import { t as d } from "./WidgetLabel-CQfHGtry-udktvHE5.js";
import { t as f } from "./WidgetLabelHelpIcon-C6IRqJ_I-BBI6AbZ-.js";
import { n as p } from "./useBasicWidgetState-D3zHnRUK-Dsaz4YO6.js";
import { i as m, r as h } from "./select-DyvsciAf-DTdJ1yfK.js";
import { r as g, t as _ } from "./useSelectCommon-CZP9dNty-CyXIYaxb.js";
//#region ../react/build/Selectbox-3CDAXdnY.js
var v = /* @__PURE__ */ t(r(), 1), y = (0, v.memo)(({ disabled: t, value: r, onChange: a, options: s, label: p, labelVisibility: y, help: b, placeholder: x, clearable: S, acceptNewOptions: C, filterMode: w }) => {
	let T = c(), E = (0, v.useContext)(n), [D, O] = (0, v.useState)(r), k = (0, v.useRef)(D);
	o(() => {
		O(r), k.current = null;
	}, [r]);
	let A = (0, v.useCallback)((e) => {
		if (e.type === "remove") {
			k.current = e.option?.value, O(null);
			return;
		}
		if (k.current = null, e.type === "clear") {
			O(null), a(null);
			return;
		}
		let [t] = e.value;
		O(t.value), a(t.value);
	}, [a]), j = (0, v.useCallback)(() => {
		k.current !== null && O(k.current);
	}, []), { placeholder: M, disabled: N, selectOptions: P, inputReadOnly: F, valueToUiSingle: I, createFilterOptions: L } = _({
		options: s,
		isMulti: !1,
		acceptNewOptions: C,
		filterMode: w,
		placeholderInput: x
	}), R = t || N, z = (0, v.useMemo)(() => L(), [L]), B = I(D);
	return /* @__PURE__ */ u.jsxs("div", {
		className: "stSelectbox",
		"data-testid": "stSelectbox",
		children: [/* @__PURE__ */ u.jsx(d, {
			label: p,
			labelVisibility: y,
			disabled: R,
			children: b && /* @__PURE__ */ u.jsx(f, {
				content: b,
				label: p
			})
		}), /* @__PURE__ */ u.jsx(h, {
			creatable: C,
			disabled: R,
			labelKey: "label",
			"aria-label": p || "",
			onChange: A,
			onBlur: j,
			options: P,
			filterOptions: z,
			clearable: S || !1,
			escapeClearsValue: S || !1,
			value: B,
			valueKey: "value",
			placeholder: M,
			ignoreCase: !1,
			overrides: {
				Root: { style: () => ({
					lineHeight: T.lineHeights.inputWidget,
					fontWeight: T.fontWeights.normal
				}) },
				Dropdown: {
					component: g,
					style: {
						boxShadow: "none",
						overflow: "hidden"
					}
				},
				ClearIcon: { props: { overrides: { Svg: { style: {
					color: T.colors.grayTextColor,
					padding: T.spacing.threeXS,
					height: T.sizes.clearIconSize,
					width: T.sizes.clearIconSize,
					":hover": { fill: T.colors.bodyText }
				} } } } },
				ControlContainer: { style: ({ $isFocused: e }) => {
					let t = i(T.colors, e);
					return {
						height: T.sizes.minElementHeight,
						borderLeftWidth: T.sizes.borderWidth,
						borderRightWidth: T.sizes.borderWidth,
						borderTopWidth: T.sizes.borderWidth,
						borderBottomWidth: T.sizes.borderWidth,
						borderTopColor: t,
						borderRightColor: t,
						borderBottomColor: t,
						borderLeftColor: t
					};
				} },
				IconsContainer: { style: () => ({ paddingRight: T.spacing.sm }) },
				ValueContainer: { style: () => ({
					flexGrow: 1,
					paddingRight: T.spacing.sm,
					paddingLeft: T.spacing.sm,
					paddingBottom: T.spacing.sm,
					paddingTop: T.spacing.sm,
					marginLeft: T.sizes.tagMarginInsideBorder
				}) },
				Placeholder: { style: () => ({
					color: R ? T.colors.fadedText40 : T.colors.fadedText60,
					position: "absolute",
					pointerEvents: "none"
				}) },
				InputContainer: { style: () => ({
					marginLeft: T.spacing.none,
					position: "relative",
					minWidth: T.spacing.threeXS,
					flexGrow: 0
				}) },
				Input: {
					props: { readOnly: F },
					style: () => ({
						lineHeight: T.lineHeights.inputWidget,
						color: T.colors.bodyText,
						caretColor: T.colors.bodyText
					})
				},
				DropdownContainer: { style: () => ({
					...l(T),
					maxHeight: `min(${T.sizes.maxDropdownHeight}, 70vh)`,
					overflow: "hidden"
				}) },
				Popover: { props: {
					ignoreBoundary: E,
					popoverMargin: e(T.spacing.twoXS),
					overrides: { Body: { style: () => ({ overflow: "hidden" }) } }
				} },
				SingleValue: { style: () => ({ marginLeft: T.spacing.none }) },
				SelectArrow: {
					component: m,
					props: {
						style: { ...R && { cursor: "not-allowed" } },
						overrides: { Svg: { style: () => ({
							width: T.iconSizes.xl,
							height: T.iconSizes.xl
						}) } }
					}
				}
			}
		})]
	});
}), b = (e, t) => e.getStringValue(t), x = (e) => e.options.length === 0 || a(e.default) ? null : e.options[e.default], S = (e) => e.rawValue ?? null, C = (e, t, n, r) => {
	t.setStringValue(e, n.value, { fromUi: n.fromUi }, r);
}, w = (0, v.memo)(({ disabled: e, element: t, widgetMgr: n, fragmentId: r }) => {
	let { options: i, help: o, label: c, labelVisibility: l, placeholder: d, acceptNewOptions: f, filterMode: m } = t, [h, g] = p({
		getStateFromWidgetMgr: b,
		getDefaultStateFromProto: x,
		getCurrStateFromProto: S,
		updateWidgetMgrState: C,
		element: t,
		widgetMgr: n,
		fragmentId: r,
		formClearBehavior: "resetValueOnly",
		queryParamBinding: t.queryParamKey ? {
			paramKey: t.queryParamKey,
			valueType: "string_value",
			clearable: a(t.default)
		} : void 0
	}), _ = (0, v.useCallback)((e) => {
		g({
			value: e,
			fromUi: !0
		});
	}, [g]), w = a(t.default) && !e;
	return /* @__PURE__ */ u.jsx(y, {
		label: c,
		labelVisibility: s(l?.value),
		options: i,
		disabled: e,
		onChange: _,
		value: h,
		help: o,
		placeholder: d,
		clearable: w,
		acceptNewOptions: f ?? !1,
		filterMode: m
	});
});
//#endregion
export { w as default };

//# sourceMappingURL=Selectbox-3CDAXdnY-v2urKxiG.js.map