import { En as e, Ka as t, Sa as n, Ua as r, oi as i, pa as a, ti as o, xa as s, zt as c } from "./index-Dl4ETd_L-D2oMd1k2.js";
//#region ../react/build/Video-B1N4EHQq.js
var l = /* @__PURE__ */ t(r(), 1), u = /* @__PURE__ */ e("iframe", { target: "evvcert1" })(({ theme: e }) => ({
	colorScheme: "normal",
	border: "none",
	padding: e.spacing.none,
	margin: e.spacing.none,
	width: "100%",
	aspectRatio: "16 / 9",
	borderRadius: e.radii.default,
	overflow: "hidden"
}), ""), d = /* @__PURE__ */ e("video", { target: "evvcert0" })(({ theme: e }) => ({
	display: "block",
	width: "100%",
	borderRadius: e.radii.default,
	overflow: "hidden"
}), ""), f = i.getLogger("Video");
function p({ element: e, endpoints: t, elementMgr: r }) {
	let i = (0, l.useRef)(null), { type: p, url: m, startTime: h, subtitles: g, endTime: _, loop: v, autoplay: y, muted: b } = e, x = s(m), S = n(g), C = a(x), w = (0, l.useMemo)(() => {
		if (!e.id) return !0;
		let t = r.getElementState(e.id, "preventAutoplay");
		return t || r.setElementState(e.id, "preventAutoplay", !0), t ?? !1;
	}, [e.id, r]), T = (0, l.useMemo)(() => JSON.stringify(S ? S.map((e) => t.buildMediaURL(`${e.url}`)) : []), [S, t]);
	return (0, l.useEffect)(() => {
		let e = JSON.parse(T);
		e.length !== 0 && e.forEach((e) => {
			t.checkSourceUrlResponse(e, "Video Subtitle");
		});
	}, [T, t]), (0, l.useEffect)(() => {
		i.current && (i.current.currentTime = h);
	}, [h]), (0, l.useEffect)(() => {
		let t = i.current, n = () => {
			t && (t.currentTime = e.startTime);
		};
		return t && t.addEventListener("loadedmetadata", n), () => {
			t && t.removeEventListener("loadedmetadata", n);
		};
	}, [e]), (0, l.useEffect)(() => {
		let e = i.current;
		if (!e) return;
		let t = !1, n = () => {
			_ > 0 && e.currentTime >= _ && (v ? (e.currentTime = h || 0, e.play()) : t || (t = !0, e.pause()));
		};
		return _ > 0 && e.addEventListener("timeupdate", n), () => {
			e && _ > 0 && e.removeEventListener("timeupdate", n);
		};
	}, [
		_,
		v,
		h
	]), (0, l.useEffect)(() => {
		let e = i.current;
		if (!e) return;
		let t = () => {
			v && (e.currentTime = h || 0, e.play());
		};
		return e.addEventListener("ended", t), () => {
			e && e.removeEventListener("ended", t);
		};
	}, [v, h]), p === c.Type.YOUTUBE_IFRAME ? /* @__PURE__ */ o.jsx(u, {
		className: "stVideo",
		"data-testid": "stVideo",
		title: x,
		src: ((e) => {
			let t = new URL(e);
			if (h && !isNaN(h) && t.searchParams.append("start", h.toString()), _ && !isNaN(_) && t.searchParams.append("end", _.toString()), v) {
				t.searchParams.append("loop", "1");
				let e = t.pathname.split("/").pop();
				e && t.searchParams.append("playlist", e);
			}
			return y && t.searchParams.append("autoplay", "1"), b && t.searchParams.append("mute", "1"), t.toString();
		})(x),
		allow: "autoplay; encrypted-media",
		allowFullScreen: !0
	}) : /* @__PURE__ */ o.jsx(d, {
		className: "stVideo",
		"data-testid": "stVideo",
		ref: i,
		controls: !0,
		muted: b,
		autoPlay: y && !w,
		src: t.buildMediaURL(x),
		crossOrigin: C,
		onError: (e) => {
			let n = e.currentTarget.src;
			f.error(`Client Error: Video source error - ${n}`), t.sendClientErrorToHost("Video", "Video source failed to load", "onerror triggered", n);
		},
		children: S?.map((e, n) => /* @__PURE__ */ o.jsx("track", {
			kind: "captions",
			src: t.buildMediaURL(`${e.url}`),
			label: `${e.label}`,
			default: n === 0,
			"data-testid": "stVideoSubtitle"
		}, n))
	});
}
var m = (0, l.memo)(p);
//#endregion
export { m as default };

//# sourceMappingURL=Video-B1N4EHQq-9J-BIqxv.js.map