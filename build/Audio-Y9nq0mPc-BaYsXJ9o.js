import { En as e, Ka as t, Ua as n, oi as r, pa as i, ti as a, xa as o } from "./index-Dl4ETd_L-D2oMd1k2.js";
//#region ../react/build/Audio-Y9nq0mPc.js
var s = /* @__PURE__ */ t(n(), 1), c = /* @__PURE__ */ e("div", { target: "exyuj7n1" })(() => ({ lineHeight: 0 }), ""), l = /* @__PURE__ */ e("audio", { target: "exyuj7n0" })(({ theme: e }) => ({
	width: "100%",
	height: e.sizes.minElementHeight,
	margin: 0,
	padding: 0
}), ""), u = r.getLogger("Audio");
function d({ element: e, endpoints: t, elementMgr: n }) {
	let r = (0, s.useRef)(null), { startTime: d, endTime: f, loop: p, autoplay: m } = e, h = (0, s.useMemo)(() => {
		if (!e.id) return !0;
		let t = n.getElementState(e.id, "preventAutoplay");
		return t || n.setElementState(e.id, "preventAutoplay", !0), t ?? !1;
	}, [e.id, n]);
	(0, s.useEffect)(() => {
		r.current && (r.current.currentTime = d);
	}, [d]), (0, s.useEffect)(() => {
		let t = r.current, n = () => {
			t && (t.currentTime = e.startTime);
		};
		return t && t.addEventListener("loadedmetadata", n), () => {
			t && t.removeEventListener("loadedmetadata", n);
		};
	}, [e]), (0, s.useEffect)(() => {
		let e = r.current;
		if (!e) return;
		let t = !1, n = () => {
			f > 0 && e.currentTime >= f && (p ? (e.currentTime = d || 0, e.play()) : t || (t = !0, e.pause()));
		};
		return f > 0 && e.addEventListener("timeupdate", n), () => {
			e && f > 0 && e.removeEventListener("timeupdate", n);
		};
	}, [
		f,
		p,
		d
	]), (0, s.useEffect)(() => {
		let e = r.current;
		if (!e) return;
		let t = () => {
			p && (e.currentTime = d || 0, e.play());
		};
		return e.addEventListener("ended", t), () => {
			e && e.removeEventListener("ended", t);
		};
	}, [p, d]);
	let g = o(e.url), _ = i(g), v = t.buildMediaURL(g);
	return /* @__PURE__ */ a.jsx(c, { children: /* @__PURE__ */ a.jsx(l, {
		className: "stAudio",
		"data-testid": "stAudio",
		ref: r,
		controls: !0,
		autoPlay: m && !h,
		src: v,
		onError: (e) => {
			let n = e.currentTarget.src;
			u.error(`Client Error: Audio source error - ${n}`), t.sendClientErrorToHost("Audio", "Audio source failed to load", "onerror triggered", n);
		},
		crossOrigin: _
	}) });
}
var f = (0, s.memo)(d);
//#endregion
export { f as default };

//# sourceMappingURL=Audio-Y9nq0mPc-BaYsXJ9o.js.map