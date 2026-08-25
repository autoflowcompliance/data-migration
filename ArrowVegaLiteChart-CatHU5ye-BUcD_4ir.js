import { Bi as e, Ct as t, Gi as n, Hr as r, Ka as i, Mt as a, Nt as o, S as s, Tr as c, Ua as l, Ur as u, Wi as d, Wr as f, Wt as p, da as m, g as h, ga as g, h as _, j as v, kn as y, kr as b, ma as x, oi as S, or as C, qi as w, ti as T, va as E, vi as D, wr as O } from "./index-Dl4ETd_L-D2oMd1k2.js";
import { n as k, t as A } from "./withFullScreenWrapper-tGGSjEWy-DoekoEMQ.js";
import { D as j } from "./DataFrame-ZHi5iyDV-BYXp5O6Z.js";
import { a as M, i as N, n as P, o as F, r as ee, s as I, t as L } from "./embed-C21m9f7b-ByOdo_l6.js";
import { t as te } from "./TableChart.esm-DqSB-klz-Bw-e4jrG.js";
//#region ../react/build/ArrowVegaLiteChart-CatHU5ye.js
var R = /* @__PURE__ */ i(l(), 1), z = /* @__PURE__ */ R.forwardRef(function(e, t) {
	return /* @__PURE__ */ R.createElement(s, p({
		iconAttrs: {
			fill: "currentColor",
			xmlns: "http://www.w3.org/2000/svg"
		},
		iconVerticalAlign: "middle",
		iconViewBox: "0 0 24 24"
	}, e, { ref: t }), /* @__PURE__ */ R.createElement("path", {
		fill: "none",
		d: "M0 0h24v24H0V0z"
	}), /* @__PURE__ */ R.createElement("path", { d: "M19 3H5c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h14c1.1 0 2-.9 2-2V5c0-1.1-.9-2-2-2zm0 16H5V5h14v14zM7 10h2v7H7zm4-3h2v10h-2zm4 6h2v4h-2z" }));
});
z.displayName = "InsertChart";
var ne = ({ data: e, height: t, width: n, customToolbarActions: r }) => /* @__PURE__ */ T.jsx(j, {
	element: new h({
		editingMode: h.EditingMode.READ_ONLY,
		disabled: !0,
		arrowData: null,
		id: "",
		columns: "",
		formId: "",
		columnOrder: [],
		selectionMode: []
	}),
	data: e,
	widgetMgr: void 0,
	disabled: !0,
	fragmentId: void 0,
	disableFullscreenMode: !0,
	customToolbarActions: r,
	widthConfig: n ?? new w.WidthConfig({ useStretch: !0 }),
	heightConfig: t ? new w.HeightConfig({ pixelHeight: t }) : void 0
});
function B(e, t) {
	if (V(e, t), Array.isArray(e.layer)) for (let n of e.layer) n && typeof n == "object" && B(n, t);
	for (let n of [
		"vconcat",
		"hconcat",
		"concat"
	]) if (Array.isArray(e[n])) for (let r of e[n]) r && typeof r == "object" && B(r, t);
	("facet" in e || "repeat" in e) && e.spec && typeof e.spec == "object" && B(e.spec, t);
}
function V(t, n) {
	let i = t.encoding;
	if (!i) return;
	let a = i.color;
	if (!a) return;
	"value" in a && r(a.value) && (a.value = e(a.value, n));
	let o = a.scale;
	o && Array.isArray(o.range) && (o.range = o.range.map((t) => r(t) ? e(t, n) : t));
}
var H = 20;
function U(e) {
	"params" in e && "encoding" in e && e.params.forEach((t) => {
		"select" in t && (typeof t.select == "string" && ["interval", "point"].includes(t.select) && (t.select = { type: t.select }), !(typeof t.select != "object" || t.select === null || !("type" in t.select)) && t.select.type === "point" && !("encodings" in t.select) && u(t.select.encodings) && (t.select.encodings = Object.keys(e.encoding)));
	});
}
var W = (e, t, n, r, i, a, o, s) => {
	let c = JSON.parse(e);
	if (typeof c.height == "number" && c.height <= 0 && delete c.height, typeof c.width == "number" && c.width <= 0 && delete c.width, r === "streamlit" ? c.config = I(c.config, a) : c.usermeta?.embedOptions?.theme === "streamlit" ? (c.config = I(c.config, a), c.usermeta.embedOptions.theme = void 0) : c.config = F(c.config, a), c.title && (typeof c.title == "string" && (c.title = { text: c.title }), c.title.limit = c.title.limit ?? Math.max(o - 40, 0)), n && s && s > 0 && (c.height = s), t && o && o > 0 && (c.width = o, "vconcat" in c && c.vconcat.forEach((e) => {
		typeof e != "object" || !e || "hconcat" in e || "vconcat" in e || "concat" in e || "facet" in e || "repeat" in e || (e.width = o);
	})), c.padding ||= {}, u(c.padding.bottom) && (c.padding.bottom = H), c.datasets) throw Error("Datasets should not be passed as part of the spec");
	return i.length > 0 && U(c), B(c, a), c;
}, G = (e, t, n, r, i) => {
	let a = x(), { id: o, formId: s, spec: c, data: l, datasets: u, vegaLiteTheme: d, selectionMode: f } = e, p = (0, R.useMemo)(() => f, [JSON.stringify(f)]);
	return {
		id: o,
		formId: s,
		vegaLiteTheme: d,
		spec: (0, R.useMemo)(() => W(c, r, i, d, p, a, t, n), [
			c,
			r,
			i,
			d,
			p,
			a,
			t,
			n
		]),
		selectionMode: p,
		data: l,
		datasets: u,
		useContainerWidth: r
	};
}, K = { DATAFRAME_INDEX: "(index)" };
function q(e) {
	return !e || e.dimensions.numDataRows === 0 ? null : X(e);
}
function J(e) {
	let t = Y(e);
	if (u(t)) return null;
	let n = {};
	for (let [e, r] of Object.entries(t)) n[e] = X(r);
	return n;
}
function Y(e) {
	if (e?.length === 0) return null;
	let t = {};
	return e.forEach((e) => {
		if (!e) return;
		let n = e.hasName ? e.name : null;
		t[n] = e.data;
	}), t;
}
function X(e, t = 0) {
	if (e.dimensions.numDataRows === 0) return [];
	let n = [], { numDataRows: r, numDataColumns: i, numIndexColumns: a } = e.dimensions, o = e.columnTypes[0] ?? void 0, s = o?.type === _.INDEX && (f(o) || c(o) || O(o));
	for (let o = t; o < r; o++) {
		let t = {};
		if (s) {
			let { content: n } = e.getCell(o, 0);
			t[K.DATAFRAME_INDEX] = typeof n == "bigint" ? Number(n) : n;
		}
		for (let n = 0; n < i; n++) {
			let r = n + a, { content: i, contentType: s } = e.getCell(o, r);
			if ((i instanceof Date || typeof i == "number" && Number.isFinite(i)) && (c(s) || O(s)) && !C(s)) {
				let n = new Date(i).getTimezoneOffset() * 60 * 1e3;
				t[e.columnNames[0][r]] = i.valueOf() + n;
			} else t[e.columnNames[0][r]] = typeof i == "bigint" ? Number(i) : i;
		}
		n.push(t);
	}
	return n;
}
var re = 150, ie = S.getLogger("useVegaLiteSelections"), ae = (e, t, n) => {
	let { id: r, formId: i, selectionMode: a } = e;
	return {
		maybeConfigureSelections: (0, R.useCallback)((e) => {
			a.forEach((o) => {
				e.addSignalListener(o, y(re, (o, s) => {
					let c = e.getState({
						data: (e, t) => a.some((t) => `${t}_store` === e),
						recurse: !1
					});
					D(c) && t.setElementState(r, "viewState", c);
					let l = s;
					"vlPoint" in s && "or" in s.vlPoint && (l = s.vlPoint.or);
					let u = {
						id: r,
						formId: i
					}, d = JSON.parse(t.getStringValue(u) || "{}"), f = { selection: {
						...d?.selection,
						[o]: l || {}
					} };
					b(d, f) || t.setStringValue(u, JSON.stringify(f), { fromUi: !0 }, n);
				}));
			});
			let o = t.getElementState(r, "viewState");
			if (D(o)) try {
				return e.setState(o);
			} catch (e) {
				ie.warn("Failed to restore view state", e);
			}
			return e;
		}, [
			r,
			a,
			t,
			i,
			n
		]),
		onFormCleared: (0, R.useCallback)(() => {
			let e = { selection: {} };
			a.forEach((t) => {
				e.selection[t] = {};
			});
			let o = {
				id: r,
				formId: i
			}, s = t.getStringValue(o);
			b(s ? JSON.parse(s) : e, e) || t.setStringValue(o, JSON.stringify(e), { fromUi: !0 }, n);
		}, [
			r,
			i,
			n,
			a,
			t
		])
	};
}, Z = "source", oe = S.getLogger("useVegaEmbed");
function se(e, t, n) {
	let r = (0, R.useRef)(null), i = (0, R.useRef)(null), a = (0, R.useRef)(Z), o = (0, R.useRef)(null), s = (0, R.useRef)([]), c = (0, R.useRef)(null), l = (0, R.useRef)([]), [u, d] = (0, R.useState)(!1), { maybeConfigureSelections: f, onFormCleared: p } = ae(e, t, n);
	g({
		widgetMgr: t,
		element: e,
		onFormCleared: p
	});
	let { data: m, datasets: h } = e;
	(0, R.useEffect)(() => {
		c.current = m, l.current = h, r.current === null && (o.current = m, s.current = h);
	}, [m, h]);
	let _ = (0, R.useCallback)(() => {
		i.current && i.current(), i.current = null, r.current = null;
	}, []), v = (0, R.useCallback)(async (e, t) => {
		if (e.current === null) throw Error("Element missing.");
		d(!0);
		try {
			_();
			let n = {
				ast: !0,
				expr: L,
				tooltip: { disableDefaultStyle: !0 },
				defaultStyle: !1,
				forceActionsMenu: !0
			}, { vgSpec: u, view: d, finalize: p } = await N(e.current, t, n);
			r.current = f(d), i.current = p;
			let m = J(l.current), h = m ? Object.keys(m) : [];
			if (h.length === 1) {
				let [e] = h;
				a.current = e;
			} else h.length === 0 && u.data && (a.current = Z);
			let g = q(c.current);
			if (g && r.current.insert(a.current, g), m) for (let [e, t] of Object.entries(m)) r.current.insert(e, t);
			return await r.current.runAsync(), await r.current.resize().runAsync(), o.current = c.current, s.current = l.current, r.current;
		} finally {
			d(!1);
		}
	}, [_, f]), y = (0, R.useCallback)((e, t, n, r) => {
		if (!r || r.dimensions.numDataRows === 0) {
			try {
				e.remove(t, P);
			} catch {}
			return;
		}
		if (!n || n.dimensions.numDataRows === 0) {
			e.insert(t, X(r));
			return;
		}
		r.hash !== n.hash && (e.data(t, X(r)), oe.info(`Had to clear the ${t} dataset before inserting data through Vega view.`));
	}, []);
	return {
		createView: v,
		updateView: (0, R.useCallback)(async (e, t) => {
			if (r.current === null || u) return null;
			let n = o.current, i = s.current;
			(n || e) && y(r.current, a.current, n, e);
			let c = Y(i) ?? {}, l = Y(t) ?? {};
			for (let [e, t] of Object.entries(l)) {
				let n = e || a.current, i = c[n];
				y(r.current, n, i, t);
			}
			for (let e of Object.keys(c)) !Object.hasOwn(l, e) && e !== a.current && y(r.current, e, null, null);
			return await r.current?.resize().runAsync(), o.current = e, s.current = t, r.current;
		}, [y, u]),
		finalizeView: _
	};
}
function Q(e) {
	try {
		let t = typeof e == "string" ? JSON.parse(e) : e;
		return !!(t.facet || t.encoding?.row || t.encoding?.column || t.encoding?.facet);
	} catch {
		return !1;
	}
}
function $(e) {
	try {
		let t = typeof e == "string" ? JSON.parse(e) : e;
		return !("vconcat" in t) || !Array.isArray(t.vconcat) ? !1 : t.vconcat.some((e) => typeof e == "object" && !!e && ("hconcat" in e || "vconcat" in e || "concat" in e || "layer" in e || "facet" in e || "repeat" in e));
	} catch {
		return !1;
	}
}
var ce = (0, R.memo)(A(({ disableFullscreenMode: e, element: r, fragmentId: i, widgetMgr: s, widthConfig: c, heightConfig: l }) => {
	let [u, f] = (0, R.useState)(!1), [p, h] = (0, R.useState)(!1), { expanded: g, height: _, width: y, expand: b, collapse: x } = E(k), { width: S, height: C, elementRef: w } = m([u]), D = n(c) || r.useContainerWidth, O = d(l), A = Q(r.spec), j = $(r.spec), N = G(r, A ? y ?? 0 : S, (g ? _ : C) ?? 0, g && !j ? !0 : D, g ? !0 : O), { createView: P, updateView: F, finalizeView: I } = se(N, s, i), { data: L, datasets: B, spec: V } = N;
	if ((0, R.useLayoutEffect)(() => (w.current !== null && P(w, V), I), [
		P,
		I,
		V,
		y,
		_,
		u,
		w
	]), (0, R.useEffect)(() => {
		F(L, B);
	}, [L, B]), (0, R.useEffect)(() => {
		L || B?.[0]?.data ? h(!0) : h(!1);
	}, [L, B]), u) {
		let e = _ ?? (C > 0 ? C : void 0);
		return /* @__PURE__ */ T.jsx(ne, {
			data: L ?? B[0]?.data,
			height: e,
			width: c ?? void 0,
			customToolbarActions: [/* @__PURE__ */ T.jsx(o, {
				label: "Show chart",
				icon: z,
				onClick: () => {
					f(!1);
				}
			}, "show-chart")]
		});
	}
	return /* @__PURE__ */ T.jsxs(t, {
		height: O ? g ? _ : "100%" : _,
		useContainerWidth: g ? !0 : D,
		children: [
			/* @__PURE__ */ T.jsx(a, {
				target: t,
				isFullScreen: g,
				onExpand: b,
				onCollapse: x,
				disableFullscreenMode: e,
				children: p && /* @__PURE__ */ T.jsx(o, {
					label: "Show data",
					icon: te,
					onClick: () => {
						f(!0);
					}
				})
			}),
			/* @__PURE__ */ T.jsx(v, { styles: ee }),
			/* @__PURE__ */ T.jsx(M, {
				"data-testid": "stVegaLiteChart",
				className: "stVegaLiteChart",
				useContainerWidth: D,
				useContainerHeight: O,
				ref: w
			})
		]
	});
}));
//#endregion
export { ce as default, $ as hasNestedComposition, Q as isFacetChart };

//# sourceMappingURL=ArrowVegaLiteChart-CatHU5ye-BUcD_4ir.js.map