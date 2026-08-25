import { Ba as e, Cn as t, E as n, Ea as r, En as i, J as a, Ka as o, Lt as s, Mn as c, Mt as l, N as u, Nt as d, S as f, Ua as p, Ur as ee, Wt as m, a as h, ii as te, k as ne, ma as re, o as g, ti as _, vi as v, x as y, z as b } from "./index-Dl4ETd_L-D2oMd1k2.js";
import { t as x } from "./createDownloadLinkElement-CnWgptKS-D3FE3dhN.js";
import { n as ie, t as ae } from "./FileDownload.esm-DA6EBJWo-Bi9VuX1R.js";
import { t as oe } from "./useWaveformController-rxqEhP00-DiSi28dC.js";
import { t as se } from "./WidgetLabel-CQfHGtry-udktvHE5.js";
import { t as ce } from "./WidgetLabelHelpIcon-C6IRqJ_I-BBI6AbZ-.js";
import { n as S } from "./urls-hxAPaE-_-CaxBV_RZ.js";
//#region ../react/build/AudioInput-Csthtpwn.js
var C = /* @__PURE__ */ o(p(), 1), w = /* @__PURE__ */ C.forwardRef(function(e, t) {
	return /* @__PURE__ */ C.createElement(f, m({
		iconAttrs: {
			fill: "currentColor",
			xmlns: "http://www.w3.org/2000/svg"
		},
		iconVerticalAlign: "middle",
		iconViewBox: "0 0 24 24"
	}, e, { ref: t }), /* @__PURE__ */ C.createElement("g", { fill: "none" }, /* @__PURE__ */ C.createElement("rect", {
		width: 24,
		height: 24
	}), /* @__PURE__ */ C.createElement("rect", {
		width: 24,
		height: 24
	}), /* @__PURE__ */ C.createElement("rect", {
		width: 24,
		height: 24
	})), /* @__PURE__ */ C.createElement("path", { d: "M12 14c1.66 0 3-1.34 3-3V5c0-1.66-1.34-3-3-3S9 3.34 9 5v6c0 1.66 1.34 3 3 3z" }), /* @__PURE__ */ C.createElement("path", { d: "M17 11c0 2.76-2.24 5-5 5s-5-2.24-5-5H5c0 3.53 2.61 6.43 6 6.92V21h2v-3.08c3.39-.49 6-3.39 6-6.92h-2z" }));
});
w.displayName = "Mic";
var T = /* @__PURE__ */ C.forwardRef(function(e, t) {
	return /* @__PURE__ */ C.createElement(f, m({
		iconAttrs: {
			fill: "currentColor",
			xmlns: "http://www.w3.org/2000/svg"
		},
		iconVerticalAlign: "middle",
		iconViewBox: "0 0 24 24"
	}, e, { ref: t }), /* @__PURE__ */ C.createElement("rect", {
		width: 24,
		height: 24,
		fill: "none"
	}), /* @__PURE__ */ C.createElement("path", { d: "M8 19c1.1 0 2-.9 2-2V7c0-1.1-.9-2-2-2s-2 .9-2 2v10c0 1.1.9 2 2 2zm6-12v10c0 1.1.9 2 2 2s2-.9 2-2V7c0-1.1-.9-2-2-2s-2 .9-2 2z" }));
});
T.displayName = "Pause";
var E = /* @__PURE__ */ C.forwardRef(function(e, t) {
	return /* @__PURE__ */ C.createElement(f, m({
		iconAttrs: {
			fill: "currentColor",
			xmlns: "http://www.w3.org/2000/svg"
		},
		iconVerticalAlign: "middle",
		iconViewBox: "0 0 24 24"
	}, e, { ref: t }), /* @__PURE__ */ C.createElement("rect", {
		width: 24,
		height: 24,
		fill: "none"
	}), /* @__PURE__ */ C.createElement("path", { d: "M8 6.82v10.36c0 .79.87 1.27 1.54.84l8.14-5.18a1 1 0 000-1.69L9.54 5.98A.998.998 0 008 6.82z" }));
});
E.displayName = "PlayArrow";
var D = /* @__PURE__ */ C.forwardRef(function(e, t) {
	return /* @__PURE__ */ C.createElement(f, m({
		iconAttrs: {
			fill: "currentColor",
			xmlns: "http://www.w3.org/2000/svg"
		},
		iconVerticalAlign: "middle",
		iconViewBox: "0 0 24 24"
	}, e, { ref: t }), /* @__PURE__ */ C.createElement("path", {
		fill: "none",
		d: "M0 0h24v24H0V0z"
	}), /* @__PURE__ */ C.createElement("path", { d: "M17.65 6.35a7.95 7.95 0 00-6.48-2.31c-3.67.37-6.69 3.35-7.1 7.02C3.52 15.91 7.27 20 12 20a7.98 7.98 0 007.21-4.56c.32-.67-.16-1.44-.9-1.44-.37 0-.72.2-.88.53a5.994 5.994 0 01-6.8 3.31c-2.22-.49-4.01-2.3-4.48-4.52A6.002 6.002 0 0112 6c1.66 0 3.14.69 4.22 1.78l-1.51 1.51c-.63.63-.19 1.71.7 1.71H19c.55 0 1-.45 1-1V6.41c0-.89-1.08-1.34-1.71-.71l-.64.65z" }));
});
D.displayName = "Refresh";
var O = /* @__PURE__ */ C.forwardRef(function(e, t) {
	return /* @__PURE__ */ C.createElement(f, m({
		iconAttrs: {
			fill: "currentColor",
			xmlns: "http://www.w3.org/2000/svg"
		},
		iconVerticalAlign: "middle",
		iconViewBox: "0 0 24 24"
	}, e, { ref: t }), /* @__PURE__ */ C.createElement("g", { fill: "none" }, /* @__PURE__ */ C.createElement("rect", {
		width: 24,
		height: 24
	}), /* @__PURE__ */ C.createElement("rect", {
		width: 24,
		height: 24
	})), /* @__PURE__ */ C.createElement("path", {
		fillRule: "evenodd",
		d: "M9 16h6c.55 0 1-.45 1-1V9c0-.55-.45-1-1-1H9c-.55 0-1 .45-1 1v6c0 .55.45 1 1 1zm3-14C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2z"
	}));
});
O.displayName = "StopCircle";
var le = (e, t) => {
	let { enforceDownloadInNewTab: n = !1 } = (0, C.useContext)(b);
	return (0, C.useCallback)(() => {
		if (!e) return;
		let r = x({
			enforceDownloadInNewTab: n,
			url: e,
			filename: t
		});
		r.style.display = "none", document.body.appendChild(r), r.click(), document.body.removeChild(r);
	}, [
		e,
		n,
		t
	]);
}, ue = async ({ files: t, uploadClient: r, widgetMgr: i, widgetInfo: a, fragmentId: o, signal: l }) => {
	let u = [];
	try {
		u = await r.fetchFileURLs(t);
	} catch (e) {
		return {
			successfulUploads: [],
			failedUploads: t.map((t) => ({
				file: t,
				error: c(e)
			}))
		};
	}
	let d = e(t, u), f = [], p = [];
	return await Promise.all(d.map(async ([e, t]) => {
		if (!e || !t?.uploadUrl || !t.fileId) {
			e && p.push({
				file: e,
				error: /* @__PURE__ */ Error("No upload URL found")
			});
			return;
		}
		try {
			await r.uploadFile({
				id: t.fileId,
				formId: a.formId || ""
			}, t.uploadUrl, e, void 0, l), f.push({
				fileUrl: t,
				file: e
			});
		} catch (t) {
			let n = c(t);
			p.push({
				file: e,
				error: n
			});
		}
	})), i.setFileUploaderStateValue(a, new n({ uploadedFileInfo: f.map(({ file: e, fileUrl: t }) => new s({
		fileId: t.fileId,
		fileUrls: t,
		name: e.webkitRelativePath || e.name,
		size: e.size
	})) }), { fromUi: !0 }, o), {
		successfulUploads: f,
		failedUploads: p
	};
}, de = /* @__PURE__ */ i("div", { target: "e12wn80j13" })(""), k = /* @__PURE__ */ i("div", { target: "e12wn80j12" })(({ theme: e, disabled: t }) => ({
	height: e.sizes.largestElementHeight,
	width: "100%",
	background: e.colors.secondaryBg,
	borderRadius: e.radii.default,
	marginBottom: e.spacing.twoXS,
	display: "flex",
	alignItems: "center",
	position: "relative",
	paddingLeft: e.spacing.xs,
	paddingRight: e.spacing.sm,
	border: e.colors.widgetBorderColor ? `${e.sizes.borderWidth} solid ${e.colors.widgetBorderColor}` : void 0,
	cursor: t ? "not-allowed" : "auto",
	overflow: "hidden"
}), ""), fe = /* @__PURE__ */ i("div", { target: "e12wn80j11" })({
	name: "82a6rk",
	styles: "flex:1"
}), pe = /* @__PURE__ */ i("div", { target: "e12wn80j10" })(({ show: e, theme: t }) => ({
	display: e ? "block" : "none",
	position: "relative",
	height: t.sizes.largestElementHeight,
	"& > div": {
		position: "absolute",
		top: 0,
		left: 0,
		width: "100%",
		height: "100%",
		display: "flex",
		alignItems: "center"
	}
}), ""), me = /* @__PURE__ */ i("span", { target: "e12wn80j9" })(({ theme: e, isPlayingOrRecording: t, disabled: n }) => ({
	margin: e.spacing.sm,
	fontFamily: e.fonts.monospace,
	color: n ? e.colors.fadedText40 : t ? e.colors.bodyText : e.colors.fadedText60,
	backgroundColor: e.colors.secondaryBg,
	fontSize: e.fontSizes.sm
}), ""), A = /* @__PURE__ */ i("div", { target: "e12wn80j8" })({
	name: "1kyw74z",
	styles: "width:100%;text-align:center;overflow:hidden"
}), j = /* @__PURE__ */ i("span", { target: "e12wn80j7" })(({ theme: e }) => ({ color: e.colors.bodyText }), ""), M = /* @__PURE__ */ i("a", { target: "e12wn80j6" })(({ theme: e }) => ({
	color: e.colors.link,
	textDecoration: e.linkUnderline ? "underline" : "none"
}), ""), N = /* @__PURE__ */ i("div", { target: "e12wn80j5" })(({ theme: e }) => ({
	flex: 1,
	height: e.sizes.largestElementHeight,
	display: "flex",
	justifyContent: "center",
	alignItems: "center"
}), ""), P = /* @__PURE__ */ i("div", { target: "e12wn80j4" })(({ theme: e }) => {
	let t = "0.625em";
	return {
		opacity: .2,
		width: "100%",
		height: t,
		backgroundSize: t,
		backgroundImage: `radial-gradient(${e.colors.fadedText10} 40%, transparent 40%)`,
		backgroundRepeat: "repeat"
	};
}, ""), F = /* @__PURE__ */ i("span", { target: "e12wn80j3" })(({ theme: e }) => ({
	"& > button": {
		color: e.colors.primary,
		padding: e.spacing.threeXS
	},
	"& > button:hover, & > button:focus": { color: e.colors.redColor }
}), ""), I = /* @__PURE__ */ i("span", { target: "e12wn80j2" })(({ theme: e }) => ({
	"& > button": {
		padding: e.spacing.threeXS,
		color: e.colors.fadedText60
	},
	"& > button:hover, & > button:focus": { color: e.colors.bodyText }
}), ""), L = /* @__PURE__ */ i("span", { target: "e12wn80j1" })(({ theme: e }) => ({
	"& > button": {
		padding: e.spacing.threeXS,
		color: e.colors.fadedText60
	},
	"& > button:hover, & > button:focus": { color: e.colors.bodyText }
}), ""), R = /* @__PURE__ */ i("div", { target: "e12wn80j0" })(({ theme: e }) => ({
	display: "flex",
	justifyContent: "center",
	alignItems: "center",
	flexGrow: 0,
	flexShrink: 1,
	padding: e.spacing.xs,
	gap: e.spacing.twoXS,
	marginRight: e.spacing.twoXS
}), ""), z = ({ onClick: e, disabled: t, ariaLabel: n, iconContent: r }) => /* @__PURE__ */ _.jsx(h, {
	kind: g.BORDERLESS_ICON,
	onClick: e,
	disabled: t,
	"aria-label": n,
	containerWidth: !0,
	"data-testid": "stAudioInputActionButton",
	children: /* @__PURE__ */ _.jsx(u, {
		content: r,
		size: "lg",
		color: "inherit"
	})
}), B = ({ disabled: e, stopRecording: t }) => /* @__PURE__ */ _.jsx(F, { children: /* @__PURE__ */ _.jsx(z, {
	onClick: t,
	disabled: e,
	ariaLabel: "Stop recording",
	iconContent: O
}) }), V = ({ disabled: e, isPlaying: t, onClickPlayPause: n }) => /* @__PURE__ */ _.jsx(L, { children: t ? /* @__PURE__ */ _.jsx(z, {
	onClick: n,
	disabled: e,
	ariaLabel: "Pause",
	iconContent: T
}) : /* @__PURE__ */ _.jsx(z, {
	onClick: n,
	disabled: e,
	ariaLabel: "Play",
	iconContent: E
}) }), H = ({ disabled: e, startRecording: t }) => /* @__PURE__ */ _.jsx(I, { children: /* @__PURE__ */ _.jsx(z, {
	onClick: t,
	disabled: e,
	ariaLabel: "Record",
	iconContent: w
}) }), U = ({ onClick: e }) => /* @__PURE__ */ _.jsx(L, { children: /* @__PURE__ */ _.jsx(z, {
	disabled: !1,
	onClick: e,
	ariaLabel: "Reset",
	iconContent: D
}) }), he = (0, C.memo)(({ disabled: e, isRecording: t, isPlaying: n, isUploading: r, isError: i, recordingUrlExists: a, startRecording: o, stopRecording: s, onClickPlayPause: c, onClear: l }) => i ? /* @__PURE__ */ _.jsx(R, { children: /* @__PURE__ */ _.jsx(U, { onClick: l }) }) : r ? /* @__PURE__ */ _.jsx(R, { children: /* @__PURE__ */ _.jsx(y, {
	size: "base",
	iconValue: "spinner"
}) }) : /* @__PURE__ */ _.jsxs(R, { children: [t ? /* @__PURE__ */ _.jsx(B, {
	disabled: e,
	stopRecording: s
}) : /* @__PURE__ */ _.jsx(H, {
	disabled: e,
	startRecording: o
}), a && /* @__PURE__ */ _.jsx(V, {
	disabled: e,
	isPlaying: n,
	onClickPlayPause: c
})] })), ge = (0, C.memo)(() => /* @__PURE__ */ _.jsx(A, { children: /* @__PURE__ */ _.jsx(j, { children: "An error has occurred, please try again." }) })), W = "00:00", G = (e) => {
	let t = Math.floor(e / 1e3), n = Math.floor(t / 60), r = Math.floor(n / 60), i = t % 60, a = n % 60, o = i.toString().padStart(2, "0"), s = a.toString().padStart(2, "0"), c = r.toString().padStart(2, "0");
	return n < 60 ? `${s}:${o}` : `${c}:${s}:${o}`;
}, _e = (0, C.memo)(() => /* @__PURE__ */ _.jsxs(A, { children: [
	/* @__PURE__ */ _.jsx(j, { children: "This app would like to use your microphone." }),
	" ",
	/* @__PURE__ */ _.jsx(M, {
		href: S,
		rel: "noopener noreferrer",
		target: "_blank",
		children: "Learn how to allow access."
	})
] })), ve = (0, C.memo)(() => /* @__PURE__ */ _.jsx(N, { children: /* @__PURE__ */ _.jsx(P, {}) })), K = (0, C.memo)(({ element: e, uploadClient: n, widgetMgr: i, fragmentId: o, disabled: s }) => {
	let c = re(), u = (0, C.useRef)(null), [f, p] = (0, C.useState)(!1), [m, h] = (0, C.useState)(!1), [g, y] = (0, C.useState)(!1), [b, x] = (0, C.useState)(W), [S, w] = r({
		widgetMgr: i,
		id: e.id,
		key: "deleteFileUrl",
		defaultValue: null
	}), [T, E] = r({
		widgetMgr: i,
		id: e.id,
		key: "recordingUrl",
		defaultValue: null
	}), [D, O] = r({
		widgetMgr: i,
		id: e.id,
		formId: e.formId,
		key: "recordingTime",
		defaultValue: W
	}), A = (0, C.useRef)(null), j = (0, C.useRef)(null), M = (0, C.useRef)(null), N = e.id, P = e.formId, F = (0, C.useCallback)(async (e) => {
		A.current && A.current.abort();
		let t = new AbortController();
		A.current = t;
		try {
			if (h(!0), v(P) && i.setFormsWithUploadsInProgress(/* @__PURE__ */ new Set([P])), t.signal.aborted) return;
			let r;
			try {
				r = URL.createObjectURL(e), j.current && j.current !== r && URL.revokeObjectURL(j.current), j.current = r;
			} catch {
				y(!0), h(!1), v(P) && i.setFormsWithUploadsInProgress(/* @__PURE__ */ new Set());
				return;
			}
			if (t.signal.aborted) {
				URL.revokeObjectURL(r), j.current = null;
				return;
			}
			E(r);
			let a = (/* @__PURE__ */ new Date()).toISOString().slice(0, 16).replace(/:/g, "-"), s = new File([e], `${a}_audio.wav`, { type: e.type });
			try {
				let { successfulUploads: e, failedUploads: r } = await ue({
					files: [s],
					uploadClient: n,
					widgetMgr: i,
					widgetInfo: {
						id: N,
						formId: P
					},
					fragmentId: o,
					signal: t.signal
				});
				if (t.signal.aborted) return;
				if (r.length > 0) {
					y(!0);
					return;
				}
				y(!1);
				let a = e[0];
				a?.fileUrl?.deleteUrl && w(a.fileUrl.deleteUrl);
			} catch {
				t.signal.aborted || y(!0);
			} finally {
				v(P) && i.setFormsWithUploadsInProgress(/* @__PURE__ */ new Set()), t.signal.aborted || h(!1);
			}
		} catch {
			t.signal.aborted || (y(!0), h(!1)), v(P) && i.setFormsWithUploadsInProgress(/* @__PURE__ */ new Set());
		}
	}, [
		n,
		i,
		N,
		P,
		o,
		w,
		E
	]), I = (0, C.useRef)(null), L = oe({
		containerRef: u,
		sampleRate: e.sampleRate ?? void 0,
		waveformPadding: t(c.spacing.twoXS),
		events: {
			onPermissionDenied: () => {
				p(!0);
			},
			onError: () => {
				y(!0);
			},
			onRecordStart: () => {
				O(W), x(W);
			},
			onRecordReady: () => {
				let e = G(I.current?.playback.getDurationMs() ?? 0);
				O(e), x(e);
			},
			onApprove: F,
			onCancel: () => {
				O(W), x(W);
			},
			onProgressMs: (e) => {
				O(G(e));
			},
			onPlaybackPause: () => {
				x(G(I.current?.playback.getCurrentTimeMs() ?? 0));
			},
			onPlaybackFinish: () => {
				x(G(I.current?.playback.getDurationMs() ?? 0));
			}
		}
	});
	I.current = L;
	let { state: R, isPlaybackPlaying: z, start: B, stop: V, approve: H, cancel: U, playback: { play: K, pause: q, load: J, getCurrentTimeMs: Y, getDurationMs: ye } } = L, X = (0, C.useCallback)(async ({ updateWidgetManager: t, deleteFile: r }) => {
		let a = T;
		if (a && j.current === a && (URL.revokeObjectURL(a), j.current = null), M.current &&= (cancelAnimationFrame(M.current), null), E(null), w(null), x(W), O(W), U(), t && i.setFileUploaderStateValue(e, {}, { fromUi: !0 }, o), r && S) try {
			await n.deleteFile(S);
		} catch {}
		v(a) && URL.revokeObjectURL(a);
	}, [
		S,
		T,
		n,
		U,
		e,
		i,
		o,
		O,
		w,
		E
	]);
	(0, C.useEffect)(() => {
		let e = () => {
			z && (x(G(Y())), M.current = requestAnimationFrame(e));
		};
		return z ? M.current = requestAnimationFrame(e) : M.current &&= (cancelAnimationFrame(M.current), null), () => {
			M.current &&= (cancelAnimationFrame(M.current), null);
		};
	}, [z, Y]), (0, C.useEffect)(() => {
		if (!T) return;
		let e = !1;
		return x(D), (async () => {
			try {
				if (await J(T), e) return;
				let t = ye();
				t > 0 && x(G(t));
			} catch {
				e || y(!0);
			}
		})(), () => {
			e = !0;
		};
	}, [
		T,
		D,
		J,
		ye
	]), (0, C.useEffect)(() => {
		if (ee(P)) return;
		let e = new ne();
		return e.manageFormClearListener(i, P, () => {
			X({
				updateWidgetManager: !0,
				deleteFile: !1
			});
		}), () => e.disconnect();
	}, [
		P,
		X,
		i
	]), (0, C.useEffect)(() => () => {
		A.current &&= (A.current.abort(), null), M.current &&= (cancelAnimationFrame(M.current), null), j.current &&= (URL.revokeObjectURL(j.current), null);
	}, []);
	let be = (0, C.useCallback)(async () => {
		try {
			if (z) {
				let e = Y();
				q(), x(G(e));
			} else R === "idle" && T && (Y() <= 100 && x(W), await K());
		} catch {
			y(!0);
		}
	}, [
		z,
		Y,
		q,
		K,
		T,
		R
	]), xe = (0, C.useCallback)(async () => {
		T && await X({
			updateWidgetManager: !1,
			deleteFile: !0
		});
		try {
			x(W), await B();
		} catch {}
	}, [
		X,
		T,
		B
	]), Se = (0, C.useCallback)(async () => {
		try {
			let { blob: e } = await V();
			await H(e);
		} catch {
			y(!0);
		}
	}, [H, V]), Z = le(T, "recording.wav"), Ce = (0, C.useCallback)(() => {
		xe();
	}, [xe]), we = (0, C.useCallback)(() => {
		Se();
	}, [Se]), Te = (0, C.useCallback)(() => {
		X({
			updateWidgetManager: !1,
			deleteFile: !0
		}), y(!1);
	}, [X]), Ee = (0, C.useCallback)(() => {
		Z();
	}, [Z]), De = (0, C.useCallback)(() => {
		X({
			updateWidgetManager: !0,
			deleteFile: !0
		});
	}, [X]), Q = R === "recording", Oe = z, ke = Q ? D : b, $ = R === "idle" && !f && !T, Ae = f || $ || g;
	return /* @__PURE__ */ _.jsxs(de, {
		className: "stAudioInput",
		"data-testid": "stAudioInput",
		children: [/* @__PURE__ */ _.jsx(se, {
			label: e.label,
			disabled: s,
			labelVisibility: te(e.labelVisibility?.value),
			children: e.help && /* @__PURE__ */ _.jsx(ce, {
				content: e.help,
				placement: a.TOP,
				label: e.label
			})
		}), /* @__PURE__ */ _.jsxs(k, {
			disabled: s,
			children: [
				/* @__PURE__ */ _.jsxs(l, {
					isFullScreen: !1,
					disableFullscreenMode: !0,
					target: k,
					children: [T && /* @__PURE__ */ _.jsx(d, {
						label: "Download as WAV",
						icon: ae,
						onClick: Ee
					}), S && /* @__PURE__ */ _.jsx(d, {
						label: "Clear recording",
						icon: ie,
						onClick: De
					})]
				}),
				/* @__PURE__ */ _.jsx(he, {
					isRecording: Q,
					isPlaying: Oe,
					isUploading: m,
					isError: g,
					recordingUrlExists: !!T,
					startRecording: Ce,
					stopRecording: we,
					onClickPlayPause: () => {
						be();
					},
					onClear: Te,
					disabled: s || f
				}),
				/* @__PURE__ */ _.jsxs(fe, { children: [
					g && /* @__PURE__ */ _.jsx(ge, {}),
					$ && /* @__PURE__ */ _.jsx(ve, {}),
					f && /* @__PURE__ */ _.jsx(_e, {}),
					/* @__PURE__ */ _.jsx(pe, {
						"data-testid": "stAudioInputWaveSurfer",
						ref: u,
						show: !Ae
					})
				] }),
				/* @__PURE__ */ _.jsx(me, {
					isPlayingOrRecording: Q || Oe,
					disabled: s,
					"data-testid": "stAudioInputWaveformTimeCode",
					children: ke
				})
			]
		})]
	});
});
//#endregion
export { K as default };

//# sourceMappingURL=AudioInput-Csthtpwn-DFB1rRpe.js.map