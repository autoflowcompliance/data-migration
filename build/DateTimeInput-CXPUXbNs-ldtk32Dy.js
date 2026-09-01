import { Cn as e, Da as t, J as n, Ka as r, N as i, P as a, Pt as o, Ua as s, Un as c, Ur as l, dt as u, ii as d, ma as f, nr as p, q as m, sr as h, ti as g, ya as _, z as v } from "./index-Dl4ETd_L-D2oMd1k2.js";
import { n as y } from "./moment-C29_LcvN-Dw52XTOQ.js";
import { t as b } from "./WidgetLabel-CQfHGtry-udktvHE5.js";
import { t as x } from "./WidgetLabelHelpIcon-C6IRqJ_I-BBI6AbZ-.js";
import { n as S } from "./useBasicWidgetState-D3zHnRUK-Dsaz4YO6.js";
import { t as C } from "./ErrorOutline.esm-YgtldkCQ-yEmqiuMG.js";
import { i as w } from "./select-DyvsciAf-DTdJ1yfK.js";
import { i as T, n as E, t as D } from "./useIntlLocale-DdLGxiZO-BQljgqPP.js";
import { n as O, t as k } from "./styled-components-CZBaXqHz-DfCZphf1.js";
//#region ../react/build/DateTimeInput-CXPUXbNs.js
var A = /* @__PURE__ */ r(s(), 1), j = k(O), M = ({ theme: t, isInSidebar: r, step: a, minTime: s, maxTime: l, disabled: d, clearable: f, error: _, scrollbarGutterSize: v, windowHeight: y }) => {
	let b = Math.ceil(86400 / a), x = e(t.sizes.dropdownItemHeight), S = Math.min(e(t.sizes.maxDropdownHeight), y * .7), T = b * x > S;
	return {
		Popover: { props: {
			ignoreBoundary: r,
			placement: m.bottomLeft,
			popoverMargin: e(t.spacing.twoXS),
			overrides: { Body: { style: {
				...p(t),
				...h(t) && { borderWidth: t.spacing.none }
			} } }
		} },
		CalendarContainer: { style: {
			fontSize: t.fontSizes.sm,
			paddingRight: t.spacing.sm,
			paddingLeft: t.spacing.sm,
			paddingBottom: t.spacing.none,
			paddingTop: t.spacing.sm,
			borderWidth: t.spacing.none
		} },
		Week: { style: { fontSize: t.fontSizes.sm } },
		Day: { style: ({ $pseudoHighlighted: e, $pseudoSelected: n, $selected: r, $isHovered: i }) => ({
			fontSize: t.fontSizes.sm,
			lineHeight: t.lineHeights.base,
			"::before": { backgroundColor: r || n || e || i ? `${t.colors.darkenedBgMix15} !important` : t.colors.transparent },
			"::after": { borderColor: t.colors.transparent },
			...h(t) && i && n && !r ? { color: t.colors.secondaryBg } : {}
		}) },
		PrevButton: { style: () => ({
			display: "flex",
			alignItems: "center",
			justifyContent: "center",
			":active": { backgroundColor: t.colors.transparent },
			":focus": {
				backgroundColor: t.colors.transparent,
				outline: 0
			}
		}) },
		NextButton: { style: () => ({
			display: "flex",
			alignItems: "center",
			justifyContent: "center",
			":active": { backgroundColor: t.colors.transparent },
			":focus": {
				backgroundColor: t.colors.transparent,
				outline: 0
			}
		}) },
		Input: { props: {
			maskChar: null,
			endEnhancer: _ && /* @__PURE__ */ g.jsx(o, {
				content: /* @__PURE__ */ g.jsx(u, {
					source: _,
					allowHTML: !1
				}),
				placement: n.TOP_RIGHT,
				error: !0,
				children: /* @__PURE__ */ g.jsx(i, {
					content: C,
					size: "lg"
				})
			}),
			overrides: {
				EndEnhancer: { style: {
					color: _ ? t.colors.redTextColor : t.colors.grayTextColor,
					backgroundColor: t.colors.transparent
				} },
				Root: { style: ({ $isFocused: e }) => {
					let n = c(t.colors, e);
					return {
						borderLeftWidth: t.sizes.borderWidth,
						borderRightWidth: t.sizes.borderWidth,
						borderTopWidth: t.sizes.borderWidth,
						borderBottomWidth: t.sizes.borderWidth,
						paddingRight: t.spacing.twoXS,
						borderTopColor: n,
						borderRightColor: n,
						borderBottomColor: n,
						borderLeftColor: n,
						..._ && { backgroundColor: t.colors.redBackgroundColor }
					};
				} },
				ClearIcon: { props: { overrides: { Svg: { style: {
					color: t.colors.grayTextColor,
					padding: t.spacing.threeXS,
					height: t.sizes.clearIconSize,
					width: t.sizes.clearIconSize,
					":hover": { fill: t.colors.bodyText }
				} } } } },
				InputContainer: { style: { backgroundColor: "transparent" } },
				Input: {
					style: {
						fontWeight: t.fontWeights.normal,
						paddingRight: t.spacing.sm,
						paddingLeft: `calc(${t.spacing.sm} + ${t.sizes.tagMarginInsideBorder})`,
						paddingBottom: t.spacing.sm,
						paddingTop: t.spacing.sm,
						lineHeight: t.lineHeights.inputWidget,
						"::placeholder": { color: t.colors.fadedText60 },
						..._ && { color: t.colors.redTextColor }
					},
					props: { "data-testid": "stDateTimeInputField" }
				}
			}
		} },
		TimeSelectContainer: { style: {
			paddingTop: t.spacing.none,
			paddingBottom: t.spacing.none
		} },
		TimeSelectFormControl: {
			style: { marginBottom: t.spacing.none },
			props: { overrides: { Label: { component: () => null } } }
		},
		TimeSelect: { props: {
			step: a,
			format: "24",
			disabled: d,
			nullable: f,
			minTime: s,
			maxTime: l,
			overrides: { Select: { props: {
				disabled: d,
				overrides: {
					ControlContainer: { style: ({ $isFocused: e }) => {
						let n = c(t.colors, e);
						return {
							height: t.sizes.minElementHeight,
							borderLeftWidth: t.sizes.borderWidth,
							borderRightWidth: t.sizes.borderWidth,
							borderTopWidth: t.sizes.borderWidth,
							borderBottomWidth: t.sizes.borderWidth,
							borderTopColor: n,
							borderRightColor: n,
							borderBottomColor: n,
							borderLeftColor: n
						};
					} },
					IconsContainer: { style: () => ({ paddingRight: t.spacing.sm }) },
					ValueContainer: { style: () => ({
						lineHeight: t.lineHeights.inputWidget,
						paddingRight: t.spacing.sm,
						paddingLeft: `calc(${t.spacing.sm} + ${t.sizes.tagMarginInsideBorder})`,
						paddingBottom: t.spacing.sm,
						paddingTop: t.spacing.sm
					}) },
					SingleValue: {
						style: {
							fontWeight: t.fontWeights.normal,
							marginLeft: t.spacing.none
						},
						props: { "data-testid": "stDateTimeInputTimeDisplay" }
					},
					Dropdown: { style: () => ({
						paddingTop: t.spacing.none,
						paddingBottom: t.spacing.none,
						paddingLeft: t.spacing.none,
						paddingRight: t.spacing.none,
						boxShadow: "none",
						maxHeight: `min(${t.sizes.maxDropdownHeight}, 70vh)`,
						"--scrollbar-gutter-size": T ? `${v}px` : "0px"
					}) },
					DropdownContainer: { style: () => ({
						...p(t),
						overflow: "hidden"
					}) },
					DropdownListItem: { component: j },
					Popover: { props: {
						ignoreBoundary: r,
						popoverMargin: e(t.spacing.twoXS),
						overrides: { Body: { style: () => ({ overflow: "hidden" }) } }
					} },
					Placeholder: { style: () => ({
						color: t.colors.fadedText60,
						position: "absolute"
					}) },
					Input: { style: {
						position: "relative",
						zIndex: t.zIndices.priority
					} },
					SelectArrow: {
						component: w,
						props: { overrides: { Svg: { style: () => ({
							width: t.iconSizes.xl,
							height: t.iconSizes.xl
						}) } } }
					}
				}
			} } }
		} }
	};
}, N = "YYYY-MM-DDTHH:mm", P = (e, t) => {
	let n = e.getStringArrayValue(t);
	if (n !== void 0) return n.length > 0 ? n[0] : null;
}, F = (e) => e.default?.length ? e.default[0] : null, I = (e) => e.value?.length ? e.value[0] : null, L = (e) => {
	let t;
	if (t = Array.isArray(e) ? e.find((e) => e instanceof Date) : e, !t || Number.isNaN(t.getTime())) return null;
	let n = new Date(t.getTime());
	return n.setSeconds(0, 0), n;
}, R = [N, "YYYY/MM/DD, HH:mm"], z = (e) => {
	if (l(e) || e === "") return null;
	let t = y(e, R, !0);
	return t.isValid() ? L(t.toDate()) : null;
}, B = (e, t) => e.getFullYear() === t.getFullYear() && e.getMonth() === t.getMonth() && e.getDate() === t.getDate(), V = (e, t) => {
	let n = new Date(e.getTime());
	return n.setHours(t.getHours(), t.getMinutes(), 0, 0), n;
}, H = (e, t, n, r) => {
	let i = z(e.min), a = z(e.max), o = (i) => {
		t.setStringArrayValue(e, i ? [i] : [], { fromUi: n.fromUi }, r);
	};
	if (n.value) {
		let e = z(n.value);
		if (e) {
			i && e < i || a && e > a || o(n.value);
			return;
		}
	}
	o(n.value);
};
function U({ disabled: e, element: n, widgetMgr: r, fragmentId: i }) {
	let o = f(), s = (0, A.useContext)(a), c = _(), { innerHeight: l } = t(), u = (0, A.useRef)(null), p = n.queryParamKey ? {
		paramKey: n.queryParamKey,
		valueType: "string_array_value",
		clearable: n.default.length === 0
	} : void 0, m = () => z(P(r, n) ?? (n.setValue ? I(n) : F(n))), [h, C] = (0, A.useState)(m), [w, O] = (0, A.useState)(m), [k, j] = S({
		getStateFromWidgetMgr: P,
		getDefaultStateFromProto: F,
		getCurrStateFromProto: I,
		updateWidgetMgrState: H,
		element: n,
		widgetMgr: r,
		fragmentId: i,
		queryParamBinding: p,
		formClearBehavior: "resetValueAndRunCallback",
		onFormCleared: (0, A.useCallback)(() => {
			C(z(F(n)));
		}, [n])
	}), { locale: R } = (0, A.useContext)(v), U = D(R), W = n.step ? Number(n.step) : 900, G = (0, A.useMemo)(() => z(n.min), [n.min]), K = (0, A.useMemo)(() => z(n.max), [n.max]), q = (0, A.useMemo)(() => z(k), [k]);
	q !== w && (C(q), O(q));
	let J = G ?? void 0, Y = K ?? void 0, X = (0, A.useMemo)(() => {
		if (!(!h || !G)) return B(h, G) ? V(h, G) : void 0;
	}, [h, G]), Z = (0, A.useMemo)(() => {
		if (!(!h || !K)) return B(h, K) ? V(h, K) : void 0;
	}, [h, K]), ee = n.format.replaceAll(/[a-zA-Z]/g, "9"), Q = `${n.format.replaceAll("Y", "y").replaceAll("D", "d")}, HH:mm`, te = `${ee}, 99:99`, ne = `${n.format}, HH:MM`, $ = (n.default && n.default.length > 0 ? n.default[0] : "").length === 0 && !e, re = (0, A.useMemo)(() => h && (G && h < G || K && h > K) ? `**Error**: Date and time set outside allowed range. Please select a date and time between ${y(G).format(Q)} and ${y(K).format(Q)}.` : null, [
		h,
		G,
		K,
		Q
	]), ie = (0, A.useCallback)(({ date: e }) => {
		C(L(e)), u.current?.open?.();
	}, []), ae = (0, A.useCallback)(() => {
		let e = h ? y(h).format(N) : null;
		e !== k && j({
			value: e,
			fromUi: !0
		});
	}, [
		h,
		k,
		j
	]), oe = M({
		theme: o,
		isInSidebar: s,
		step: W,
		minTime: X,
		maxTime: Z,
		disabled: e,
		clearable: $,
		error: re,
		scrollbarGutterSize: c,
		windowHeight: l
	});
	return /* @__PURE__ */ g.jsxs("div", {
		className: "stDateTimeInput",
		"data-testid": "stDateTimeInput",
		children: [/* @__PURE__ */ g.jsx(b, {
			label: n.label,
			disabled: e,
			labelVisibility: d(n.labelVisibility?.value),
			children: n.help && /* @__PURE__ */ g.jsx(x, {
				content: n.help,
				label: n.label
			})
		}), /* @__PURE__ */ g.jsx(E, {
			ref: u,
			locale: U,
			density: T.high,
			value: h,
			onChange: ie,
			onClose: ae,
			minDate: J,
			maxDate: Y,
			disabled: e,
			timeSelectStart: !0,
			formatString: Q,
			mask: te,
			placeholder: ne,
			clearable: $,
			overrides: oe,
			"aria-label": n.label
		})]
	});
}
var W = (0, A.memo)(U);
//#endregion
export { W as default };

//# sourceMappingURL=DateTimeInput-CXPUXbNs-ldtk32Dy.js.map