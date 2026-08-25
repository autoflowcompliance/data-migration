import { C as e, En as t, Ha as n, I as r, Ka as i, Mn as a, Ua as o, Ur as s, at as c, i as l, ji as u, ma as d, oi as f, ot as p, p as m, r as h, ra as g, ti as _, ut as v, vi as y, wa as b } from "./index-Dl4ETd_L-D2oMd1k2.js";
import { i as x, r as S } from "./urls-hxAPaE-_-CaxBV_RZ.js";
import { t as C } from "./withCalculatedWidth-DwrWHMUR-BEQsmBif.js";
import { n as w, t as T } from "./IFrameUtil-BYTcNZ4E-B8B2FnkH.js";
//#region ../react/build/ComponentInstance-Dlz3boBV.js
var E = /* @__PURE__ */ i(o(), 1), D = /* @__PURE__ */ i(n(), 1), O = /* @__PURE__ */ ((e) => (e.COMPONENT_READY = "streamlit:componentReady", e.SET_COMPONENT_VALUE = "streamlit:setComponentValue", e.SET_FRAME_HEIGHT = "streamlit:setFrameHeight", e))(O || {}), k = /* @__PURE__ */ ((e) => (e.RENDER = "streamlit:render", e))(k || {}), A = 1, j = f.getLogger("componentUtils");
function M(e) {
	return (t, n) => {
		if (!e.current) return;
		let { isReady: r, element: i, widgetMgr: a, setComponentError: o, componentReadyCallback: s, frameHeightCallback: c, fragmentId: l } = e.current, u = r();
		switch (t) {
			case O.COMPONENT_READY: {
				let { apiVersion: e } = n;
				e === A ? s() : o(/* @__PURE__ */ Error(`Unrecognized component API version: '${e}'`));
				break;
			}
			case O.SET_COMPONENT_VALUE:
				u ? F(I(n, "value"), n.dataType, { fromUi: !0 }, i, a, l) : j.warn(`Got ${t} before ${O.COMPONENT_READY}!`);
				break;
			case O.SET_FRAME_HEIGHT:
				u ? c(I(n, "height")) : j.warn(`Got ${t} before ${O.COMPONENT_READY}!`);
				break;
			default: j.warn(`Unrecognized ComponentBackMsgType: ${t}`);
		}
	};
}
function N(e, t) {
	let n = JSON.parse(e), r = [];
	for (let e of t) {
		let { key: t } = e;
		switch (e.value?.toLowerCase()) {
			case "arrowdataframe":
				r.push({
					key: t,
					value: l.toObject(e.arrowDataframe)
				});
				break;
			case "bytes":
				n[t] = e.bytes;
				break;
			default: throw Error(`Unrecognized SpecialArg type: ${e.value}`);
		}
	}
	return [n, r];
}
function P(e, t, n, r, i) {
	if (!i) {
		j.warn("Can't send ForwardMsg; missing our iframe!");
		return;
	}
	if (s(i.contentWindow)) {
		j.warn("Can't send ForwardMsg; iframe has no contentWindow!");
		return;
	}
	i.contentWindow.postMessage({
		type: k.RENDER,
		args: e,
		dfs: t,
		disabled: n,
		theme: {
			...g(r),
			font: r.genericFonts.bodyFont
		}
	}, "*");
}
function F(e, t, n, r, i, a) {
	if (e === void 0) {
		j.warn("handleSetComponentValue: missing 'value' prop");
		return;
	}
	switch (t) {
		case "dataframe":
			i.setArrowValue(r, e, n, a);
			break;
		case "bytes":
			i.setBytesValue(r, e, n, a);
			break;
		default: i.setJsonValue(r, e, n, a);
	}
}
function I(e, t, n = void 0) {
	return Object.hasOwn(e, t) ? e[t] : n;
}
var L = /* @__PURE__ */ t("iframe", { target: "e1fjvnnc0" })(({ theme: e, componentReady: t }) => ({
	colorScheme: "normal",
	border: "none",
	padding: e.spacing.none,
	margin: e.spacing.none,
	display: t ? "initial" : "none"
}), ""), R = f.getLogger("ComponentInstance"), z = 6e4;
function B(e, t, n) {
	let r;
	r = y(n) && n !== "" ? n : t.getComponentURL(e, "index.html");
	let i = v.CUSTOM_COMPONENT_CLIENT_ID, a = new URL(window.location.href);
	return r = u.stringifyUrl({
		url: r,
		query: {
			streamlitUrl: a.origin + a.pathname,
			...i && { __streamlit_parent_client_id: i }
		}
	}), r;
}
function V(e, t) {
	let n;
	return n = t && t !== "" ? `Your app is having trouble loading the **${e}** component.
The app is attempting to load the component from **${t}**,
and hasn't received its \`Streamlit.setComponentReady()\` message.

If this is a development build, have you started the dev server?

For more troubleshooting help, please see the [Streamlit Component docs](${x}) or visit our [forums](${S}).` : `Your app is having trouble loading the **${e}** component.

If this is an installed component that works locally, the app may be having trouble accessing the component frontend assets due to network latency or proxy settings in your app deployment.

For more troubleshooting help, please see the [Streamlit Component docs](${x}) or visit our [forums](${S}).`, n;
}
function H(e, t, n, r) {
	if (!r) try {
		return N(e, t);
	} catch (e) {
		n(a(e));
	}
	return [{}, []];
}
function U(e, t) {
	return e === t || e.length === t.length && e.every((e, n) => {
		let r = t[n];
		return e.key === r.key && e.value === r.value;
	});
}
function W(t) {
	let n = d(), [i, a] = (0, E.useState)(), { disabled: o, element: l, widgetMgr: u, width: f, fragmentId: g, componentRegistry: v } = t, { componentName: y, jsonArgs: x, specialArgs: S, url: C } = l, [O, k] = H(x, S, a, i), A = (0, E.useMemo)(() => B(y, v, C), [
		y,
		v,
		C
	]), j = (0, E.useRef)({
		args: {},
		dataframeArgs: []
	}), N = U(j.current.dataframeArgs, k);
	j.current.args = O, j.current.dataframeArgs = k;
	let [F, I] = (0, E.useState)(), [W, G] = (0, E.useState)(() => {
		let e = O.height;
		return e === void 0 || isNaN(e) ? void 0 : e;
	}), K = (0, E.useRef)(!1), q = (0, E.useRef)(null), J = (0, E.useRef)(), { clear: Y } = b(() => R.warn(V(y, C)), z / 4), { clear: X } = b(() => {
		(0, D.flushSync)(() => {
			I(!0);
		});
	}, z);
	if ((0, E.useEffect)(() => {
		v.checkSourceUrlResponse(A, y);
	}, [
		A,
		y,
		v
	]), (0, E.useEffect)(() => {
		F && !K.current && (R.error(`Client Error: Custom Component ${y} timeout error`), v.sendTimeoutError(A, y));
	}, [
		F,
		A,
		y,
		v
	]), (0, E.useEffect)(() => {
		K.current && P(j.current.args, j.current.dataframeArgs, o, n, q.current ?? void 0);
	}, [
		o,
		W,
		N,
		x,
		n,
		f
	]), (0, E.useEffect)(() => {
		J.current = {
			isReady: () => K.current,
			element: l,
			widgetMgr: u,
			setComponentError: a,
			componentReadyCallback: () => {
				P(j.current.args, j.current.dataframeArgs, o, n, q.current ?? void 0), Y(), X(), K.current = !0, (0, D.flushSync)(() => {
					I(!1);
				});
			},
			frameHeightCallback: (e) => {
				if (e === void 0) {
					R.warn("handleSetFrameHeight: missing 'height' prop");
					return;
				}
				if (e !== W) {
					if (s(q.current)) {
						R.warn("handleSetFrameHeight: missing our iframeRef!");
						return;
					}
					q.current.height = e.toString(), (0, D.flushSync)(() => {
						G(e);
					});
				}
			},
			fragmentId: g
		};
	}, [
		y,
		o,
		l,
		W,
		N,
		F,
		x,
		n,
		u,
		X,
		Y,
		g
	]), (0, E.useEffect)(() => {
		let e = q.current?.contentWindow ?? void 0;
		if (e) return v.registerListener(e, M(J)), () => {
			e && v.deregisterListener(e);
		};
	}, [v, y]), i) return /* @__PURE__ */ _.jsx(e, {
		name: i.name,
		message: i.message
	});
	let Z = !K.current && !F && W !== 0 && /* @__PURE__ */ _.jsx(c, { element: p.create({
		height: W,
		style: p.SkeletonStyle.ELEMENT
	}) }), Q = !K.current && F ? /* @__PURE__ */ _.jsx(h, {
		body: V(y, C),
		kind: r.WARNING
	}) : null;
	return /* @__PURE__ */ _.jsxs(_.Fragment, { children: [
		Z,
		Q,
		/* @__PURE__ */ _.jsx(m, {
			IframeComponent: L,
			className: "stCustomComponentV1",
			"data-testid": "stCustomComponentV1",
			allow: w,
			ref: q,
			src: A,
			width: f,
			height: W ?? 0,
			scrolling: "no",
			sandbox: T,
			title: y,
			componentReady: K.current,
			tabIndex: l.tabIndex ?? void 0
		})
	] });
}
var G = C((0, E.memo)(W));
//#endregion
export { z as COMPONENT_READY_WARNING_TIME_MS, G as default };

//# sourceMappingURL=ComponentInstance-Dlz3boBV-CFds2N7Y.js.map