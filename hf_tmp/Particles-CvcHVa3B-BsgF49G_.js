import { En as e, Ha as t, Ka as n, Mi as r, Ua as i, Z as a, ti as o, z as s } from "./index-Dl4ETd_L-D2oMd1k2.js";
//#region ../react/build/Particles-CvcHVa3B.js
var c = /* @__PURE__ */ n(i(), 1), l = /* @__PURE__ */ n(t(), 1), u = ({ children: e }) => {
	let t = (0, c.useContext)(a)?.();
	return t ? (0, l.createPortal)(e, t) : /* @__PURE__ */ o.jsx(o.Fragment, { children: e });
}, d = /* @__PURE__ */ e("div", { target: "ecnfqzf0" })({
	name: "my9yfq",
	styles: "@media print{display:none;}"
}), f = (0, c.memo)(({ className: e, scriptRunId: t, numParticles: n, numParticleTypes: i, ParticleComponent: a }) => {
	let { resourceCrossOriginMode: l } = (0, c.useContext)(s), u = (0, c.useMemo)(() => r(n).map(() => Math.floor(Math.random() * i)), [n, i]);
	return /* @__PURE__ */ o.jsx(d, {
		className: e,
		"data-testid": e,
		children: u.map((e, n) => /* @__PURE__ */ o.jsx(a, {
			particleType: e,
			resourceCrossOriginMode: l
		}, t + n))
	});
});
//#endregion
export { u as n, f as t };

//# sourceMappingURL=Particles-CvcHVa3B-BsgF49G_.js.map