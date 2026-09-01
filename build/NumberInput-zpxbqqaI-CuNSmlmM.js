import { Cn as e, En as t, K as n, Ka as r, N as i, Pr as a, S as o, Ua as s, Ur as c, Wt as l, da as ee, ii as te, ma as u, oi as d, ti as f, vi as p, x as ne, zr as m } from "./index-Dl4ETd_L-D2oMd1k2.js";
import { t as h } from "./sprintfjs-pgmg3ABV-CZ4af2dB.js";
import { t as g } from "./WidgetLabel-CQfHGtry-udktvHE5.js";
import { t as re } from "./WidgetLabelHelpIcon-C6IRqJ_I-BBI6AbZ-.js";
import { n as ie } from "./useBasicWidgetState-D3zHnRUK-Dsaz4YO6.js";
import { t as ae } from "./InputInstructions-BQBBgzXB-ClQbP4Gu.js";
import { t as oe } from "./input-CClPhvPt-C_5WYNdx.js";
//#region ../react/build/NumberInput-zpxbqqaI.js
var _ = /* @__PURE__ */ r(s(), 1), v = /* @__PURE__ */ _.forwardRef(function(e, t) {
	return /* @__PURE__ */ _.createElement(o, l({
		iconAttrs: {
			fill: "currentColor",
			xmlns: "http://www.w3.org/2000/svg"
		},
		iconVerticalAlign: "middle",
		iconViewBox: "0 0 8 8"
	}, e, { ref: t }), /* @__PURE__ */ _.createElement("path", { d: "M0 3v2h8V3H0z" }));
});
v.displayName = "Minus";
var y = /* @__PURE__ */ _.forwardRef(function(e, t) {
	return /* @__PURE__ */ _.createElement(o, l({
		iconAttrs: {
			fill: "currentColor",
			xmlns: "http://www.w3.org/2000/svg"
		},
		iconVerticalAlign: "middle",
		iconViewBox: "0 0 8 8"
	}, e, { ref: t }), /* @__PURE__ */ _.createElement("path", { d: "M3 0v3H0v2h3v3h2V5h3V3H5V0H3z" }));
});
y.displayName = "Plus";
var b = /* @__PURE__ */ t("div", { target: "e116k4er3" })(({ theme: e }) => ({
	display: "flex",
	flexDirection: "row",
	flexWrap: "nowrap",
	alignItems: "center",
	height: e.sizes.minElementHeight,
	borderWidth: e.sizes.borderWidth,
	borderStyle: "solid",
	borderColor: e.colors.widgetBorderColor ?? e.colors.secondaryBg,
	transitionDuration: "200ms",
	transitionProperty: "border",
	transitionTimingFunction: "cubic-bezier(0.2, 0.8, 0.4, 1)",
	borderRadius: e.radii.default,
	overflow: "hidden",
	"&.focused": { borderColor: e.colors.primary },
	input: {
		MozAppearance: "textfield",
		"&::-webkit-inner-spin-button, &::-webkit-outer-spin-button": {
			WebkitAppearance: "none",
			margin: e.spacing.none
		}
	}
}), ""), se = /* @__PURE__ */ t("div", { target: "e116k4er2" })({
	name: "76z9jo",
	styles: "display:flex;flex-direction:row;align-self:stretch"
}), x = /* @__PURE__ */ t("button", { target: "e116k4er1" })(({ theme: e }) => ({
	margin: e.spacing.none,
	border: "none",
	height: e.sizes.full,
	display: "flex",
	alignItems: "center",
	width: e.sizes.numberInputControlsWidth,
	justifyContent: "center",
	color: e.colors.bodyText,
	transition: "color 300ms, backgroundColor 300ms",
	backgroundColor: e.colors.secondaryBg,
	"&:hover:enabled, &:focus:enabled": {
		color: e.colors.white,
		backgroundColor: e.colors.primary,
		transition: "none",
		outline: "none"
	},
	"&:active": {
		outline: "none",
		border: "none"
	},
	"&:disabled": {
		cursor: "not-allowed",
		color: e.colors.fadedText40
	}
}), ""), ce = /* @__PURE__ */ t("div", { target: "e116k4er0" })(({ theme: e, clearable: t }) => ({
	position: "absolute",
	marginRight: e.spacing.twoXS,
	left: 0,
	right: `calc(${e.sizes.numberInputControlsWidth} * 2 + ${t ? "1em" : "0em"})`
}), ""), S = d.getLogger("NumberInput");
function C(e) {
	return c(e) || e === "" ? void 0 : e;
}
var w = (e) => {
	let t = e.toString();
	if (t.includes("e-")) {
		let e = t.match(/(\d+(?:\.\d+)?)e-(\d+)/);
		return e ? (e[1]?.split(".")[1] || "").length + parseInt(e[2], 10) : 0;
	}
	return (t.split(".")[1] || "").length;
}, T = ({ value: e, format: t, step: r, dataType: i }) => {
	if (c(e)) return null;
	let a = C(t);
	if (c(a) && p(r) && i === n.DataType.FLOAT && r !== 0) {
		let e = w(r);
		e > 0 && (a = `%0.${e}f`);
	}
	if (c(a)) return e.toString();
	try {
		return h(a, e);
	} catch (t) {
		return S.warn(`Error in sprintf(${a}, ${e}): ${t}`), String(e);
	}
}, le = (e, t, n) => c(e) ? !1 : e - t >= n, ue = (e, t, n) => c(e) ? !1 : e + t <= n, E = (e, t, n) => {
	let r = w(t);
	if (r === 0) switch (n) {
		case "add": return e + t;
		case "subtract": return e - t;
	}
	let i = 10 ** r, a = Math.round(e * i), o = Math.round(t * i);
	switch (n) {
		case "add": return (a + o) / i;
		case "subtract": return (a - o) / i;
	}
}, D = ({ step: e, dataType: t }) => e || (t === n.DataType.INT ? 1 : .01);
function O(e, t) {
	return t.dataType === n.DataType.INT ? e.getIntValue(t) : e.getDoubleValue(t);
}
function de(e) {
	return e.default ?? null;
}
function fe(e) {
	return e.value ?? e.default ?? null;
}
function pe(e, t, r, i) {
	switch (e.dataType) {
		case n.DataType.INT:
			t.setIntValue(e, r.value, { fromUi: r.fromUi }, i);
			break;
		case n.DataType.FLOAT:
			t.setDoubleValue(e, r.value, { fromUi: r.fromUi }, i);
			break;
		default: throw Error("Invalid data type");
	}
}
var k = (0, _.memo)(({ disabled: t, element: r, widgetMgr: o, fragmentId: s }) => {
	let l = u(), { dataType: d, formId: h, default: S, format: C, icon: w, min: k, max: A } = r, { width: j, elementRef: me } = ee(), M = (0, _.useMemo)(() => D({
		step: r.step,
		dataType: r.dataType
	}), [r.step, r.dataType]), N = (0, _.useCallback)((e) => T({
		value: e,
		dataType: d,
		format: C,
		step: M
	}), [
		d,
		C,
		M
	]), [P, F] = (0, _.useState)(!1), [I, L] = (0, _.useState)(() => T({
		value: O(o, r) ?? S ?? null,
		dataType: d,
		format: C,
		step: M
	})), R = r.queryParamKey ? {
		paramKey: r.queryParamKey,
		valueType: "double_value",
		clearable: c(r.default)
	} : void 0, [z, B] = ie({
		getStateFromWidgetMgr: O,
		getDefaultStateFromProto: de,
		getCurrStateFromProto: fe,
		updateWidgetMgrState: pe,
		element: r,
		widgetMgr: o,
		fragmentId: s,
		formClearBehavior: "resetValueAndRunCallback",
		onFormCleared: (0, _.useCallback)(() => {
			let e = S ?? null;
			F(!1), L(N(e));
		}, [S, N]),
		queryParamBinding: R
	}), [V, H] = (0, _.useState)(!1), U = (0, _.useRef)(null), W = (0, _.useId)(), G = a({ formId: h }), he = G ? o.allowFormEnterToSubmit(h) : P, ge = V && j > e(l.breakpoints.hideWidgetDetails);
	(0, _.useEffect)(() => {
		P || L(N(z));
	}, [
		z,
		P,
		N
	]);
	let K = (0, _.useCallback)(({ value: e, fromUi: t }) => {
		if (p(e) && (k > e || e > A)) {
			U.current?.reportValidity();
			return;
		}
		let n = e ?? S ?? null;
		B({
			value: n,
			fromUi: t
		}), F(!1), L(N(n));
	}, [
		k,
		A,
		S,
		N,
		B
	]), _e = (0, _.useCallback)(() => {
		H(!0);
	}, []);
	(0, _.useEffect)(() => {
		let e = U.current;
		if (e) {
			let t = (e) => {
				e.preventDefault();
			};
			return e.addEventListener("wheel", t), () => {
				e.removeEventListener("wheel", t);
			};
		}
	}, []);
	let q = c(r.default) && !t, ve = (0, _.useCallback)((e) => {
		let { value: t } = e.target;
		t === "" ? (F(!0), L(null)) : (F(!0), L(t));
	}, []), J = (0, _.useMemo)(() => {
		if (I === null || I === "") return null;
		if (r.dataType === n.DataType.INT) {
			let e = parseInt(I, 10);
			return isNaN(e) ? null : e;
		}
		let e = parseFloat(I);
		return isNaN(e) ? null : e;
	}, [I, r.dataType]), Y = le(J, M, k), X = ue(J, M, A), ye = (0, _.useCallback)(() => {
		P && K({
			value: J,
			fromUi: !0
		}), H(!1);
	}, [
		P,
		J,
		K
	]), Z = (0, _.useCallback)(() => {
		X && K({
			value: E(J ?? k, M, "add"),
			fromUi: !0
		});
	}, [
		J,
		k,
		M,
		X,
		K
	]), Q = (0, _.useCallback)(() => {
		Y && K({
			value: E(J ?? A, M, "subtract"),
			fromUi: !0
		});
	}, [
		J,
		A,
		M,
		Y,
		K
	]), be = (0, _.useCallback)((e) => {
		let { key: t } = e;
		switch (t) {
			case "ArrowUp":
				e.preventDefault(), Z();
				break;
			case "ArrowDown":
				e.preventDefault(), Q();
				break;
		}
	}, [Z, Q]), xe = (0, _.useCallback)((e) => {
		e.key === "Enter" && (P && K({
			value: J,
			fromUi: !0
		}), o.allowFormEnterToSubmit(h) && o.submitForm(h, s));
	}, [
		P,
		J,
		K,
		o,
		h,
		s
	]), Se = e(l.iconSizes.lg) + 2 * e(l.spacing.twoXS), $ = e(l.breakpoints.hideNumberInputControls), Ce = w ? $ + Se : $;
	return /* @__PURE__ */ f.jsxs("div", {
		className: "stNumberInput",
		"data-testid": "stNumberInput",
		ref: me,
		children: [
			/* @__PURE__ */ f.jsx(g, {
				label: r.label,
				disabled: t,
				labelVisibility: te(r.labelVisibility?.value),
				htmlFor: W,
				children: r.help && /* @__PURE__ */ f.jsx(re, {
					content: r.help,
					label: r.label
				})
			}),
			/* @__PURE__ */ f.jsxs(b, {
				className: V ? "focused" : "",
				"data-testid": "stNumberInputContainer",
				children: [/* @__PURE__ */ f.jsx(oe, {
					type: "number",
					inputRef: U,
					value: I ?? "",
					placeholder: r.placeholder,
					onBlur: ye,
					onFocus: _e,
					onChange: ve,
					onKeyPress: xe,
					onKeyDown: be,
					clearable: q,
					clearOnEscape: q,
					disabled: t,
					"aria-label": r.label,
					startEnhancer: r.icon && /* @__PURE__ */ f.jsx(ne, {
						"data-testid": "stNumberInputIcon",
						iconValue: r.icon,
						size: "lg"
					}),
					id: W,
					overrides: {
						ClearIconContainer: { style: { padding: 0 } },
						ClearIcon: { props: { overrides: { Svg: { style: {
							color: l.colors.grayTextColor,
							padding: l.spacing.threeXS,
							height: l.sizes.clearIconSize,
							width: l.sizes.clearIconSize,
							":hover": { fill: l.colors.bodyText }
						} } } } },
						Input: {
							props: {
								"data-testid": "stNumberInputField",
								step: M,
								min: k,
								max: A,
								type: "number",
								inputMode: ""
							},
							style: {
								fontWeight: l.fontWeights.normal,
								lineHeight: l.lineHeights.inputWidget,
								paddingRight: l.spacing.sm,
								paddingLeft: l.spacing.md,
								paddingBottom: l.spacing.sm,
								paddingTop: l.spacing.sm,
								"::placeholder": { color: l.colors.fadedText60 }
							}
						},
						InputContainer: { style: () => ({
							borderTopRightRadius: 0,
							borderBottomRightRadius: 0
						}) },
						Root: { style: {
							borderTopRightRadius: 0,
							borderBottomRightRadius: 0,
							borderTopLeftRadius: 0,
							borderBottomLeftRadius: 0,
							borderLeftWidth: 0,
							borderRightWidth: 0,
							borderTopWidth: 0,
							borderBottomWidth: 0,
							paddingRight: 0,
							paddingLeft: w ? l.spacing.sm : 0
						} },
						StartEnhancer: { style: {
							paddingLeft: 0,
							paddingRight: 0,
							minWidth: l.iconSizes.lg,
							color: m(w) ? l.colors.fadedText60 : "inherit"
						} }
					}
				}), j > Ce && /* @__PURE__ */ f.jsxs(se, { children: [/* @__PURE__ */ f.jsx(x, {
					"data-testid": "stNumberInputStepDown",
					onClick: Q,
					disabled: !Y || t,
					tabIndex: -1,
					children: /* @__PURE__ */ f.jsx(i, {
						content: v,
						size: "xs",
						color: Y ? "inherit" : l.colors.fadedText40
					})
				}), /* @__PURE__ */ f.jsx(x, {
					"data-testid": "stNumberInputStepUp",
					onClick: Z,
					disabled: !X || t,
					tabIndex: -1,
					children: /* @__PURE__ */ f.jsx(i, {
						content: y,
						size: "xs",
						color: X ? "inherit" : l.colors.fadedText40
					})
				})] })]
			}),
			ge && /* @__PURE__ */ f.jsx(ce, {
				clearable: q,
				children: /* @__PURE__ */ f.jsx(ae, {
					dirty: P,
					value: I ?? "",
					inForm: G,
					allowEnterToSubmit: he
				})
			})
		]
	});
});
//#endregion
export { k as default };

//# sourceMappingURL=NumberInput-zpxbqqaI-CuNSmlmM.js.map