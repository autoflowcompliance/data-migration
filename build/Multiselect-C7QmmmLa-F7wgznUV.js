import { Cn as e, En as t, Ka as n, P as r, Ua as i, Un as a, an as o, ii as s, it as c, ma as l, nr as u, ti as d, un as f, yr as p } from "./index-Dl4ETd_L-D2oMd1k2.js";
import { t as m } from "./_baseIndexOf-OsCSwRmV-C7GT7Z0T.js";
import { t as h } from "./WidgetLabel-CQfHGtry-udktvHE5.js";
import { t as g } from "./WidgetLabelHelpIcon-C6IRqJ_I-BBI6AbZ-.js";
import { n as _ } from "./useBasicWidgetState-D3zHnRUK-Dsaz4YO6.js";
import { a as v, i as y, r as b, t as x } from "./select-DyvsciAf-DTdJ1yfK.js";
import { i as S, n as C, r as w, t as T } from "./useSelectCommon-CZP9dNty-CyXIYaxb.js";
//#region ../react/build/Multiselect-C7QmmmLa.js
var E = /* @__PURE__ */ n(i(), 1);
function D(e, t) {
	return !!(e != null && e.length) && m(e, t, 0) > -1;
}
var O = 200;
function k(e, t, n, r) {
	var i = -1, a = D, o = !0, s = e.length, l = [], u = t.length;
	if (!s) return l;
	t.length >= O && (a = f, o = !1, t = new c(t));
	e: for (; ++i < s;) {
		var d = e[i], p = d;
		if (d = d === 0 ? 0 : d, o && p === p) {
			for (var m = u; m--;) if (t[m] === p) continue e;
			l.push(d);
		} else a(t, p, r) || l.push(d);
	}
	return l;
}
var A = o(function(e, t) {
	return p(e) ? k(e, t) : [];
}), j = /* @__PURE__ */ t("div", { target: "e6zijwc0" })(({ theme: e }) => ({ "span[aria-disabled='true']": { background: e.colors.fadedText05 } }), ""), M = (e, t) => e.getStringArrayValue(t), N = (e) => e.default.map((t) => e.options[t]) ?? null, P = (e) => e.rawValues ?? null, F = (e, t, n, r) => {
	t.setStringArrayValue(e, n.value, { fromUi: n.fromUi }, r);
}, I = (0, E.memo)((t) => {
	let { element: n, widgetMgr: i, fragmentId: o } = t, c = l(), f = (0, E.useContext)(r), p = (0, E.useRef)(null), m = (0, E.useRef)(0), D = n.queryParamKey ? {
		paramKey: n.queryParamKey,
		valueType: "string_array_value",
		clearable: !0,
		urlFormat: "repeated"
	} : void 0, O = (0, E.useRef)([]), [k, I] = _({
		getStateFromWidgetMgr: M,
		getDefaultStateFromProto: N,
		getCurrStateFromProto: P,
		updateWidgetMgrState: F,
		element: n,
		widgetMgr: i,
		fragmentId: o,
		formClearBehavior: "resetValueOnly",
		queryParamBinding: D
	}), L = n.maxSelections > 0 && k.length >= n.maxSelections, R = (0, E.useMemo)(() => {
		if (n.maxSelections === 0) return "No results";
		if (k.length === n.maxSelections) {
			let e = n.maxSelections === 1 ? "option" : "options";
			return `You can only select up to ${n.maxSelections} ${e}. Remove an option first.`;
		}
		return "No results";
	}, [n.maxSelections, k.length]), z = (0, E.useCallback)((e) => {
		switch (e.type) {
			case "remove": return A(k, e.option?.value);
			case "clear": return [];
			case "select":
				if (e.option?.value === "__SELECT_ALL__") {
					let e = n.options.filter((e) => !k.includes(e));
					if (n.maxSelections > 0) {
						let t = n.maxSelections - k.length;
						return [...k, ...e.slice(0, t)];
					}
					return [...k, ...e];
				}
				if (e.option?.value === "__SELECT_MATCHES__") {
					let e = O.current;
					if (n.maxSelections > 0) {
						let t = n.maxSelections - k.length;
						return [...k, ...e.slice(0, t)];
					}
					return [...k, ...e];
				}
				return k.concat([e.option?.value]);
			default: throw Error(`State transition is unknown: ${e.type}`);
		}
	}, [
		k,
		n.maxSelections,
		n.options
	]), B = (0, E.useCallback)((e) => {
		n.maxSelections && e.type === "select" && k.length >= n.maxSelections || I({
			value: z(e),
			fromUi: !0
		});
	}, [
		n.maxSelections,
		z,
		I,
		k.length
	]), { options: V } = n, { placeholder: H, disabled: U, selectOptions: W, inputReadOnly: G, valuesToUiMulti: K, createFilterOptions: q } = T({
		options: V,
		isMulti: !0,
		acceptNewOptions: n.acceptNewOptions ?? !1,
		filterMode: n.filterMode,
		placeholderInput: n.placeholder
	}), J = (0, E.useCallback)((e, t) => {
		if (L) return [];
		let n = q(k)(e, t);
		return n.length > 1 ? t.trim() ? (O.current = n.map((e) => e.value), [{
			label: `Select ${n.length} matches`,
			value: C,
			id: C
		}, ...n]) : [{
			label: "Select all",
			value: S,
			id: S
		}, ...n] : n;
	}, [
		q,
		L,
		k
	]), Y = t.disabled || U, X = (0, E.useMemo)(() => K(k), [K, k]), Z = (0, E.useMemo)(() => `calc(4.5 * ${`calc(${c.sizes.elementHighlightHeight} + ${c.sizes.tagMarginInsideBorder})`} + ${c.sizes.tagMarginInsideBorder} + 2 * ${c.sizes.borderWidth})`, [
		c.sizes.elementHighlightHeight,
		c.sizes.tagMarginInsideBorder,
		c.sizes.borderWidth
	]);
	(0, E.useLayoutEffect)(() => {
		p.current && (p.current.scrollTop = m.current);
	});
	let Q = (0, E.useCallback)((e) => {
		m.current = e.currentTarget.scrollTop;
	}, []), $ = (0, E.useMemo)(() => function(e) {
		return /* @__PURE__ */ d.jsx(x, {
			...e,
			ref: p,
			onScroll: Q
		});
	}, [Q]);
	return /* @__PURE__ */ d.jsxs("div", {
		className: "stMultiSelect",
		"data-testid": "stMultiSelect",
		children: [/* @__PURE__ */ d.jsx(h, {
			label: n.label,
			disabled: Y,
			labelVisibility: s(n.labelVisibility?.value),
			children: n.help && /* @__PURE__ */ d.jsx(g, {
				content: n.help,
				label: n.label
			})
		}), /* @__PURE__ */ d.jsx(j, { children: /* @__PURE__ */ d.jsx(b, {
			creatable: n.acceptNewOptions ?? !1,
			options: W,
			labelKey: "label",
			valueKey: "value",
			"aria-label": n.label,
			placeholder: H,
			type: v.select,
			multi: !0,
			onChange: B,
			value: X,
			disabled: Y,
			size: "compact",
			noResultsMsg: R,
			filterOptions: J,
			closeOnSelect: !1,
			ignoreCase: !1,
			overrides: {
				DropdownContainer: { style: () => ({
					...u(c),
					maxHeight: `min(${c.sizes.maxDropdownHeight}, 70vh)`,
					overflow: "hidden"
				}) },
				Popover: { props: {
					ignoreBoundary: f,
					popoverMargin: e(c.spacing.twoXS),
					overrides: { Body: { style: () => ({ overflow: "hidden" }) } }
				} },
				SelectArrow: {
					component: y,
					props: {
						style: { cursor: "pointer" },
						overrides: { Svg: { style: () => ({
							width: c.iconSizes.xl,
							height: c.iconSizes.xl
						}) } }
					}
				},
				IconsContainer: { style: () => ({ paddingRight: c.spacing.sm }) },
				ControlContainer: { style: ({ $isFocused: e }) => {
					let t = a(c.colors, e);
					return {
						maxHeight: Z,
						minHeight: c.sizes.minElementHeight,
						borderLeftWidth: c.sizes.borderWidth,
						borderRightWidth: c.sizes.borderWidth,
						borderTopWidth: c.sizes.borderWidth,
						borderBottomWidth: c.sizes.borderWidth,
						borderTopColor: t,
						borderRightColor: t,
						borderBottomColor: t,
						borderLeftColor: t
					};
				} },
				Placeholder: { style: () => ({
					flex: "inherit",
					color: Y ? c.colors.fadedText40 : c.colors.fadedText60,
					position: "absolute",
					top: "50%",
					transform: "translateY(-50%)",
					paddingLeft: c.spacing.sm,
					pointerEvents: "none"
				}) },
				ValueContainer: {
					component: $,
					style: () => ({
						overflowY: "auto",
						paddingLeft: c.sizes.tagMarginInsideBorder,
						paddingTop: c.sizes.tagMarginInsideBorder,
						paddingBottom: c.spacing.none,
						paddingRight: c.spacing.none
					})
				},
				ClearIcon: { props: { overrides: { Svg: { style: {
					color: c.colors.grayTextColor,
					padding: c.spacing.threeXS,
					height: c.sizes.clearIconSize,
					width: c.sizes.clearIconSize,
					cursor: "pointer",
					":hover": { fill: c.colors.bodyText }
				} } } } },
				SearchIcon: { style: { color: c.colors.grayTextColor } },
				Tag: { props: { overrides: {
					Root: { style: {
						fontWeight: c.fontWeights.normal,
						borderTopLeftRadius: c.radii.md2,
						borderTopRightRadius: c.radii.md2,
						borderBottomRightRadius: c.radii.md2,
						borderBottomLeftRadius: c.radii.md2,
						fontSize: c.fontSizes.md,
						paddingLeft: c.spacing.sm,
						marginTop: c.spacing.none,
						marginLeft: c.spacing.none,
						marginRight: c.spacing.twoXS,
						marginBottom: c.sizes.tagMarginInsideBorder,
						height: c.sizes.elementHighlightHeight,
						maxWidth: `calc(100% - ${c.spacing.lg})`,
						cursor: "default !important",
						pointerEvents: "none"
					} },
					Text: { style: { pointerEvents: "auto" } },
					Action: { style: {
						paddingLeft: c.spacing.none,
						pointerEvents: "auto"
					} },
					ActionIcon: { props: { overrides: { Svg: { style: {
						width: "0.625em",
						height: "0.625em"
					} } } } }
				} } },
				MultiValue: { props: { overrides: { Root: { style: { fontSize: c.fontSizes.sm } } } } },
				InputContainer: { style: ({ $isFocused: e }) => ({
					height: c.sizes.elementHighlightHeight,
					alignSelf: "flex-start",
					marginLeft: c.spacing.none,
					marginTop: c.spacing.none,
					marginBottom: c.sizes.tagMarginInsideBorder,
					position: e ? "relative" : "absolute",
					width: "fit-content",
					flexGrow: 0,
					display: "flex"
				}) },
				Input: {
					props: { readOnly: G },
					style: () => ({
						color: c.colors.bodyText,
						caretColor: c.colors.bodyText,
						paddingLeft: c.spacing.sm,
						fieldSizing: "content"
					})
				},
				Dropdown: { component: w }
			}
		}) })]
	});
});
//#endregion
export { I as default };

//# sourceMappingURL=Multiselect-C7QmmmLa-F7wgznUV.js.map