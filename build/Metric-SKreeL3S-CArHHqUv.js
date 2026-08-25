import { Cn as e, En as t, J as n, Ka as r, N as i, R as a, S as o, U as s, Ua as c, Wt as l, da as u, dt as d, ii as f, j as p, la as m, ma as h, sr as g, ti as _ } from "./index-Dl4ETd_L-D2oMd1k2.js";
import { n as v, t as y } from "./formatNumber-B9NmJPl4-CfTaoV6j.js";
import { i as b, r as x, s as S, t as C } from "./embed-C21m9f7b-ByOdo_l6.js";
import { n as w } from "./styled-components-BDZ1Vzrp-C65H8d9R.js";
import { t as T } from "./WidgetLabelHelpIconInline-BTmzKeRa-CZ4j9Xyg.js";
//#region ../react/build/Metric-SKreeL3S.js
var E = /* @__PURE__ */ r(c(), 1), D = /* @__PURE__ */ E.forwardRef(function(e, t) {
	return /* @__PURE__ */ E.createElement(o, l({
		iconAttrs: {
			fill: "currentColor",
			xmlns: "http://www.w3.org/2000/svg"
		},
		iconVerticalAlign: "middle",
		iconViewBox: "0 0 24 24"
	}, e, { ref: t }), /* @__PURE__ */ E.createElement("path", {
		fill: "none",
		d: "M0 0h24v24H0V0z"
	}), /* @__PURE__ */ E.createElement("path", { d: "M20 12l-1.41-1.41L13 16.17V4h-2v12.17l-5.58-5.59L4 12l8 8 8-8z" }));
});
D.displayName = "ArrowDownward";
var O = /* @__PURE__ */ E.forwardRef(function(e, t) {
	return /* @__PURE__ */ E.createElement(o, l({
		iconAttrs: {
			fill: "currentColor",
			xmlns: "http://www.w3.org/2000/svg"
		},
		iconVerticalAlign: "middle",
		iconViewBox: "0 0 24 24"
	}, e, { ref: t }), /* @__PURE__ */ E.createElement("path", {
		fill: "none",
		d: "M0 0h24v24H0V0z"
	}), /* @__PURE__ */ E.createElement("path", { d: "M4 12l1.41 1.41L11 7.83V20h2V7.83l5.58 5.59L20 12l-8-8-8 8z" }));
});
O.displayName = "ArrowUpward";
function k(e, t) {
	switch (t) {
		case s.MetricColor.RED: return e.colors.redColor;
		case s.MetricColor.GREEN: return e.colors.greenColor;
		case s.MetricColor.ORANGE: return e.colors.orangeColor;
		case s.MetricColor.YELLOW: return e.colors.yellowColor;
		case s.MetricColor.BLUE: return e.colors.blueColor;
		case s.MetricColor.VIOLET: return e.colors.violetColor;
		case s.MetricColor.PRIMARY: return e.colors.primary;
		default: return e.colors.grayColor;
	}
}
function A(e, t) {
	let n = g(e);
	switch (t) {
		case s.MetricColor.RED: return e.colors.redBackgroundColor;
		case s.MetricColor.GREEN: return e.colors.greenBackgroundColor;
		case s.MetricColor.ORANGE: return e.colors.orangeBackgroundColor;
		case s.MetricColor.YELLOW: return e.colors.yellowBackgroundColor;
		case s.MetricColor.BLUE: return e.colors.blueBackgroundColor;
		case s.MetricColor.VIOLET: return e.colors.violetBackgroundColor;
		case s.MetricColor.PRIMARY: return m(e.colors.primary, n ? .9 : .7);
		default: return e.colors.grayBackgroundColor;
	}
}
function j(e, t) {
	switch (t) {
		case s.MetricColor.RED: return e.colors.redTextColor;
		case s.MetricColor.GREEN: return e.colors.greenTextColor;
		case s.MetricColor.ORANGE: return e.colors.orangeTextColor;
		case s.MetricColor.YELLOW: return e.colors.yellowTextColor;
		case s.MetricColor.BLUE: return e.colors.blueTextColor;
		case s.MetricColor.VIOLET: return e.colors.violetTextColor;
		case s.MetricColor.PRIMARY: return e.colors.primary;
		default: return e.colors.grayTextColor;
	}
}
var M = /* @__PURE__ */ t("div", { target: "e1i5pmia7" })(({ theme: e, showBorder: t }) => ({
	height: "100%",
	...t && {
		border: `${e.sizes.borderWidth} solid ${e.colors.borderColor}`,
		borderRadius: e.radii.default,
		overflow: "hidden"
	}
}), ""), N = /* @__PURE__ */ t("div", { target: "e1i5pmia6" })(({ theme: e, showBorder: t }) => ({ ...t && { padding: `calc(${e.spacing.lg} - ${e.sizes.borderWidth})` } }), ""), P = /* @__PURE__ */ t("div", { target: "e1i5pmia5" })(({ theme: e, showBorder: t }) => ({
	marginTop: t ? void 0 : e.spacing.lg,
	marginBottom: t ? e.spacing.twoXL : void 0
}), ""), F = /* @__PURE__ */ t(w, { target: "e1i5pmia4" })(({ visibility: e }) => ({
	marginBottom: 0,
	display: e === a.Collapsed ? "none" : "grid",
	gridTemplateColumns: e === a.Collapsed ? "initial" : "auto 1fr",
	visibility: e === a.Hidden ? "hidden" : "visible"
}), ""), I = /* @__PURE__ */ t("div", { target: "e1i5pmia3" })(({ theme: e }) => ({
	fontSize: e.fontSizes.metricValueFontSize,
	lineHeight: "normal",
	fontWeight: e.fontWeights.metricValueFontWeight,
	color: e.colors.bodyText,
	paddingBottom: e.spacing.twoXS
}), ""), L = /* @__PURE__ */ t("div", { target: "e1i5pmia2" })(({ theme: e, metricColor: t, showArrow: n }) => ({
	color: j(e, t),
	backgroundColor: A(e, t),
	fontSize: e.fontSizes.sm,
	lineHeight: "normal",
	display: "inline-flex",
	flexDirection: "row",
	alignItems: "center",
	fontWeight: e.fontWeights.normal,
	borderRadius: e.radii.full,
	maxWidth: "100%",
	flexShrink: 0,
	padding: `${e.spacing.threeXS} ${e.spacing.xs}`,
	...n && { paddingLeft: e.spacing.twoXS }
}), ""), R = /* @__PURE__ */ t("div", { target: "e1i5pmia1" })(({ theme: e }) => ({
	display: "flex",
	flexDirection: "row",
	alignItems: "center",
	gap: "0.5em",
	maxWidth: "100%",
	overflow: "hidden",
	paddingBottom: e.spacing.twoXS
}), ""), z = /* @__PURE__ */ t("div", { target: "e1i5pmia0" })({
	name: "1m7ehjk",
	styles: "overflow:hidden;flex-shrink:1;min-width:0"
}), B = 1e3;
function V(e, t) {
	try {
		return y(Number(e), t);
	} catch {
		return e;
	}
}
function H(t, n, r, i, a) {
	let o = `metric_chart_${Math.random().toString(36).slice(2, 10)}`, c = t.length === 1 ? [t[0], t[0]] : t, l = {
		$schema: "https://vega.github.io/schema/vega-lite/v5.json",
		width: Math.round(r),
		height: Math.round(e("3.5rem")),
		data: { values: c.map((e, t) => ({
			x: t,
			y: e
		})) },
		layer: [
			{
				name: `${o}_mark`,
				mark: {
					type: "line",
					...n === s.ChartType.LINE && {
						type: "line",
						strokeCap: "round",
						strokeWidth: i.sizes.metricStrokeWidth
					},
					...n === s.ChartType.BAR && {
						type: "bar",
						cornerRadius: parseFloat(i.radii.full)
					},
					...n === s.ChartType.AREA && {
						type: "area",
						color: A(i, a),
						opacity: 1,
						line: {
							color: k(i, a),
							opacity: 1,
							strokeWidth: i.sizes.metricStrokeWidth,
							strokeCap: "round"
						}
					}
				},
				encoding: {
					x: {
						field: "x",
						type: "quantitative",
						axis: null,
						scale: {
							zero: !1,
							nice: !1
						}
					},
					y: {
						field: "y",
						type: "quantitative",
						axis: null,
						scale: {
							zero: !1,
							nice: !1
						}
					}
				}
			},
			{
				name: `${o}_points`,
				mark: {
					type: "point",
					opacity: 0
				},
				encoding: {
					x: {
						field: "x",
						type: "quantitative",
						axis: null,
						scale: {
							zero: !1,
							nice: !1
						}
					},
					y: {
						field: "y",
						type: "quantitative",
						axis: null,
						scale: {
							zero: !1,
							nice: !1
						}
					}
				},
				params: [{
					name: `${o}_hover_selection`,
					select: {
						type: "point",
						encodings: ["x"],
						nearest: !0,
						on: t.length > B ? "mousemove{16}" : "mousemove",
						clear: "mouseleave"
					}
				}]
			},
			{
				name: `${o}_highlighted_points`,
				transform: [{ filter: {
					param: `${o}_hover_selection`,
					empty: !1
				} }],
				mark: {
					type: "point",
					filled: !0,
					size: 65,
					tooltip: !0
				},
				encoding: {
					x: {
						field: "x",
						type: "quantitative",
						axis: null,
						scale: {
							zero: !1,
							nice: !1
						}
					},
					y: {
						field: "y",
						type: "quantitative",
						axis: null,
						scale: {
							zero: !1,
							nice: !1
						}
					}
				}
			}
		],
		config: {
			view: { stroke: null },
			padding: {
				left: -3,
				right: -3,
				top: 2,
				bottom: 2
			},
			...n === s.ChartType.BAR && { padding: {
				left: 0,
				right: 0,
				top: 2,
				bottom: 2
			} },
			mark: {
				tooltip: { content: "encoding" },
				color: k(i, a)
			}
		}
	};
	return l.config = S(l.config, i), l;
}
function U({ element: e }) {
	let t = h(), r = (0, E.useRef)(null), { width: a, elementRef: o } = u(), { MetricDirection: c } = s, { body: l, label: m, delta: g, direction: y, color: S, labelVisibility: w, help: k, showBorder: A, chartData: j, chartType: B, format: U, deltaDescription: W } = e, G = U && v(l) ? V(l, U) : l, K = U && g && v(g) ? V(g, U) : g, q = null;
	switch (y) {
		case c.DOWN:
			q = D;
			break;
		case c.UP:
			q = O;
			break;
		case c.NONE: break;
	}
	let J = g !== "", Y = (0, E.useId)();
	return (0, E.useEffect)(() => {
		if (j && j.length > 0 && r.current && a > 0) {
			let e = H(j, B, a, t, S);
			b(r.current, e, {
				actions: !1,
				renderer: "svg",
				ast: !0,
				expr: C,
				tooltip: {
					theme: "custom",
					formatTooltip: (e) => `${e.y}`
				}
			});
		}
	}, [
		j,
		S,
		t,
		a,
		B,
		r
	]), /* @__PURE__ */ _.jsxs(M, {
		className: "stMetric",
		"data-testid": "stMetric",
		showBorder: A,
		children: [/* @__PURE__ */ _.jsxs(N, {
			showBorder: A,
			children: [
				/* @__PURE__ */ _.jsxs(F, {
					"data-testid": "stMetricLabel",
					visibility: f(w?.value),
					children: [/* @__PURE__ */ _.jsx(d, {
						source: m,
						allowHTML: !1,
						isLabel: !0,
						truncate: !0
					}), k && /* @__PURE__ */ _.jsx(T, {
						content: k,
						placement: n.TOP_RIGHT,
						label: m
					})]
				}),
				/* @__PURE__ */ _.jsx(I, {
					"data-testid": "stMetricValue",
					children: /* @__PURE__ */ _.jsx(d, {
						source: G,
						allowHTML: !1,
						isLabel: !0,
						inheritFont: !0,
						truncate: !0
					})
				}),
				(J || W) && /* @__PURE__ */ _.jsxs(R, { children: [J && /* @__PURE__ */ _.jsxs(L, {
					"data-testid": "stMetricDelta",
					metricColor: S,
					showArrow: q !== null,
					"aria-describedby": W ? Y : void 0,
					children: [q && /* @__PURE__ */ _.jsx(i, {
						testid: q === O ? "stMetricDeltaIcon-Up" : "stMetricDeltaIcon-Down",
						content: q,
						size: "md",
						margin: "0 threeXS 0 0"
					}), /* @__PURE__ */ _.jsx(d, {
						source: K,
						allowHTML: !1,
						isLabel: !0,
						inheritFont: !0,
						truncate: !0
					})]
				}), W && /* @__PURE__ */ _.jsx(z, {
					"data-testid": "stMetricDeltaDescription",
					id: Y,
					title: W,
					children: /* @__PURE__ */ _.jsx(d, {
						source: W,
						allowHTML: !1,
						isLabel: !0,
						isCaption: !0,
						truncate: !0
					})
				})] })
			]
		}), j && j.length > 0 && /* @__PURE__ */ _.jsxs("div", {
			ref: o,
			children: [/* @__PURE__ */ _.jsx(p, { styles: x }), /* @__PURE__ */ _.jsx(P, {
				ref: r,
				"data-testid": "stMetricChart",
				showBorder: A
			})]
		})]
	});
}
var W = (0, E.memo)(U);
//#endregion
export { W as default, H as getMetricChartSpec };

//# sourceMappingURL=Metric-SKreeL3S-CArHHqUv.js.map