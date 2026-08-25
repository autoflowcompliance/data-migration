import { Cn as e, Ka as t, Ua as n, ln as r, ma as i } from "./index-Dl4ETd_L-D2oMd1k2.js";
//#region ../react/build/useWaveformController-rxqEhP00.js
var a = /* @__PURE__ */ t(n(), 1), o = class {
	constructor() {
		this.wavesurfer = null, this.currentBlobUrl = null, this.events = {}, this.isPlaying = !1;
	}
	initialize(e) {
		this.wavesurfer = e, this.setupEventListeners();
	}
	setupEventListeners() {
		this.wavesurfer && (this.teardownEventListeners(), this.handleTimeUpdate = (e) => {
			this.events.onTimeUpdate?.(e * 1e3);
		}, this.handlePause = () => {
			this.isPlaying = !1, this.events.onPause?.();
		}, this.handlePlay = () => {
			this.isPlaying = !0, this.events.onPlay?.();
		}, this.handleFinish = () => {
			this.isPlaying = !1, this.events.onFinish?.();
		}, this.handleReady = () => {
			this.events.onReady?.();
		}, this.handleError = (e) => {
			let t = e instanceof Error ? e : Error(String(e));
			this.events.onError?.(t);
		}, this.wavesurfer.on("timeupdate", this.handleTimeUpdate), this.wavesurfer.on("pause", this.handlePause), this.wavesurfer.on("play", this.handlePlay), this.wavesurfer.on("finish", this.handleFinish), this.wavesurfer.on("ready", this.handleReady), this.wavesurfer.on("error", this.handleError));
	}
	setEventHandlers(e) {
		this.events = e;
	}
	async load(e) {
		if (!this.wavesurfer) throw Error("WaveSurfer not initialized");
		this.cleanupPreviousUrl();
		let t, n = null;
		try {
			if (e instanceof Blob) n = URL.createObjectURL(e), t = n;
			else if (e instanceof ArrayBuffer) {
				let r = new Blob([e]);
				n = URL.createObjectURL(r), t = n;
			} else t = e;
			this.currentBlobUrl = n, await this.wavesurfer.load(t);
		} catch (e) {
			throw this.cleanupPreviousUrl(), e;
		}
	}
	async play() {
		if (!this.wavesurfer) throw Error("WaveSurfer not initialized");
		await this.wavesurfer.play();
	}
	pause() {
		this.wavesurfer && this.wavesurfer.pause();
	}
	getDuration() {
		return this.wavesurfer ? this.wavesurfer.getDuration() * 1e3 : 0;
	}
	getCurrentTime() {
		return this.wavesurfer ? this.wavesurfer.getCurrentTime() * 1e3 : 0;
	}
	getIsPlaying() {
		return this.isPlaying;
	}
	seekToStart() {
		this.wavesurfer && this.wavesurfer.seekTo(0);
	}
	cleanupPreviousUrl() {
		this.currentBlobUrl &&= (URL.revokeObjectURL(this.currentBlobUrl), null);
	}
	destroy() {
		this.pause(), this.cleanupPreviousUrl(), this.wavesurfer &&= (this.teardownEventListeners(), this.wavesurfer.empty(), null), this.events = {}, this.isPlaying = !1, this.handleTimeUpdate = void 0, this.handlePause = void 0, this.handlePlay = void 0, this.handleFinish = void 0, this.handleReady = void 0, this.handleError = void 0;
	}
	teardownEventListeners() {
		this.wavesurfer && (this.handleTimeUpdate &&= (this.wavesurfer.un("timeupdate", this.handleTimeUpdate), void 0), this.handlePause &&= (this.wavesurfer.un("pause", this.handlePause), void 0), this.handlePlay &&= (this.wavesurfer.un("play", this.handlePlay), void 0), this.handleFinish &&= (this.wavesurfer.un("finish", this.handleFinish), void 0), this.handleReady &&= (this.wavesurfer.un("ready", this.handleReady), void 0), this.handleError &&= (this.wavesurfer.un("error", this.handleError), void 0));
	}
};
function s(e) {
	return e.name === "NotAllowedError" || e.name === "PermissionDeniedError" || e.message?.toLowerCase().includes("permission denied");
}
var c = class {
	constructor(e = {}) {
		this.wavesurfer = null, this.recordPlugin = null, this.isRecording = !1, this.recordEndResolve = null, this.recordEndReject = null, this.events = {}, this.options = e;
	}
	initialize(e, t) {
		this.wavesurfer = e;
		try {
			let n = {
				renderRecordedAudio: !1,
				mimeType: "audio/webm"
			};
			this.recordPlugin = e.registerPlugin(t.create(n)), this.setupEventListeners();
		} catch (e) {
			let t = e instanceof Error ? e : Error(String(e));
			throw s(t) ? (this.events.onPermissionDenied?.(), /* @__PURE__ */ Error("Microphone permission denied")) : (this.events.onError?.(t), t);
		}
	}
	setupEventListeners() {
		this.recordPlugin && (this.recordPlugin.on("record-start", () => {
			this.isRecording = !0, this.events.onRecordStart?.();
		}), this.recordPlugin.on("record-end", (e) => {
			this.isRecording = !1, this.events.onRecordEnd?.(e), this.recordEndResolve && e && e.size > 0 ? (this.recordEndResolve(e), this.recordEndResolve = null, this.recordEndReject = null) : this.recordEndReject ? (this.recordEndReject(/* @__PURE__ */ Error("Invalid or empty recording")), this.recordEndResolve = null, this.recordEndReject = null) : (this.recordEndResolve = null, this.recordEndReject = null);
		}), this.recordPlugin.on("record-progress", (e) => {
			this.events.onRecordProgress?.(e);
		}));
	}
	setEventHandlers(e) {
		this.events = e;
	}
	async startRecording() {
		if (!this.recordPlugin) throw Error("Record plugin not initialized");
		if (this.isRecording) return;
		let e = typeof this.options.sampleRate == "number" ? this.options.sampleRate : void 0, t = {};
		e !== void 0 && (t.sampleRate = { ideal: e }), await this.startRecordingWithConstraints(t, e !== void 0);
	}
	async startRecordingWithConstraints(e, t) {
		if (!this.recordPlugin) throw Error("Record plugin not initialized");
		try {
			let t = Object.keys(e).length ? e : void 0;
			await this.recordPlugin.startRecording(t);
		} catch (e) {
			let n = e instanceof Error ? e : Error(String(e));
			if (s(n)) throw this.events.onPermissionDenied?.(), /* @__PURE__ */ Error("Microphone permission denied");
			if (t && (n.name === "OverconstrainedError" || n.name === "NotReadableError")) {
				this.options.sampleRate = void 0, await this.startRecordingWithConstraints({}, !1);
				return;
			}
			throw this.events.onError?.(n), n;
		}
	}
	async stopRecording() {
		if (!this.recordPlugin || !this.isRecording) throw Error("Not currently recording");
		try {
			return await new Promise((e, t) => {
				this.recordEndResolve = e, this.recordEndReject = t, this.recordPlugin?.stopRecording();
			});
		} catch (e) {
			let t = e instanceof Error ? e : Error(String(e));
			throw this.events.onError?.(t), t;
		}
	}
	cancelRecording() {
		this.recordPlugin && this.isRecording && (this.recordPlugin.stopRecording(), this.isRecording = !1, this.recordEndResolve = null, this.recordEndReject = null);
	}
	destroy() {
		this.cancelRecording(), this.recordPlugin &&= (this.recordPlugin.destroy(), null), this.wavesurfer = null, this.events = {};
	}
};
async function l(e, t = 16e3) {
	if (!e || e.size === 0) throw Error("Invalid or empty blob provided");
	if (!window.AudioContext) throw Error("AudioContext not supported in this browser");
	let n = new AudioContext();
	try {
		let r = await e.arrayBuffer(), i = await n.decodeAudioData(r), a = t ?? i.sampleRate;
		return d(await u(i, a), a);
	} finally {
		n.close();
	}
}
async function u(e, t) {
	let { duration: n, numberOfChannels: r, sampleRate: i } = e, a = Math.ceil(n * t);
	if (!window.OfflineAudioContext) throw Error("OfflineAudioContext not supported");
	let o = new OfflineAudioContext(1, a, t), s = o.createBufferSource();
	if (s.buffer = e, r > 1) {
		let e = o.createChannelSplitter(r), t = o.createChannelMerger(1);
		s.connect(e);
		for (let n = 0; n < r; n++) {
			let i = o.createGain();
			i.gain.value = 1 / r, e.connect(i, n), i.connect(t, 0, 0);
		}
		t.connect(o.destination);
	} else s.connect(o.destination);
	s.start(0);
	try {
		return await o.startRendering();
	} catch (e) {
		throw Error(`Failed to resample audio from ${i}Hz to ${t}Hz: ${e instanceof Error ? e.message : String(e)}`);
	}
}
function d(e, t) {
	let n = e.length, r = n * 2 + 44, i = new ArrayBuffer(r), a = new DataView(i), o = e.getChannelData(0), s = (e, t) => {
		for (let n = 0; n < t.length; n++) a.setUint8(e + n, t.charCodeAt(n));
	};
	s(0, "RIFF"), a.setUint32(4, r - 8, !0), s(8, "WAVE"), s(12, "fmt "), a.setUint32(16, 16, !0), a.setUint16(20, 1, !0), a.setUint16(22, 1, !0), a.setUint32(24, t, !0), a.setUint32(28, t * 2, !0), a.setUint16(32, 2, !0), a.setUint16(34, 16, !0), s(36, "data"), a.setUint32(40, n * 2, !0);
	let c = 44;
	for (let e = 0; e < n; e++) {
		let t = Math.max(-1, Math.min(1, o[e]));
		a.setInt16(c, t * 32767, !0), c += 2;
	}
	return new Blob([i], { type: "audio/wav" });
}
var f = 4, p = 4, m = 8, h = 0, g = 16e3;
function _({ containerRef: t, sampleRate: n, events: s, waveformPadding: u = 0 }) {
	let d = i(), [_, v] = (0, a.useState)("idle"), [y, b] = (0, a.useState)(null), [x, S] = (0, a.useState)(!1), C = (0, a.useRef)(null), w = (0, a.useRef)(null), T = (0, a.useRef)(null), E = (0, a.useRef)(s), D = (0, a.useRef)(!1), O = (0, a.useRef)(!1), k = (0, a.useRef)(/* @__PURE__ */ new Set()), A = (0, a.useRef)(!1), j = n === void 0 ? g : n, M = (0, a.useCallback)(() => {
		k.current.clear(), S(!1), w.current &&= (w.current.destroy(), null), T.current &&= (T.current.destroy(), null), C.current &&= (C.current.destroy(), null), D.current = !1, A.current = !1, v("idle"), b(null);
	}, []), N = (0, a.useCallback)(() => {
		let e = Array.from(k.current);
		k.current.clear(), e.forEach((e) => {
			e.resolve();
		});
	}, []), P = (0, a.useCallback)((e) => {
		S(!1);
		let t = Array.from(k.current);
		k.current.clear(), t.forEach((t) => {
			t.reject(e);
		});
	}, []), F = (0, a.useCallback)((e) => {
		e.setEventHandlers({
			onPlay: () => {
				S(!0), E.current.onPlaybackPlay?.();
			},
			onPause: () => {
				S(!1), E.current.onPlaybackPause?.();
			},
			onFinish: () => {
				S(!1), E.current.onPlaybackFinish?.();
			},
			onReady: () => {
				N();
			},
			onError: (e) => {
				S(!1), P(e), E.current.onError?.(e);
			}
		});
	}, [N, P]);
	(0, a.useEffect)(() => {
		E.current = s, T.current && F(T.current);
	}, [s, F]);
	let I = (0, a.useCallback)(async () => {
		if (!(D.current || O.current || !t.current)) {
			O.current = !0;
			try {
				let [n, r] = await Promise.all([import("./wavesurfer.esm-SpUmkfwo-BUVhZlGD.js"), import("./record-CvRL89xC-Djmz1rvI.js")]), i = n.default, a = r.default, s = i.create({
					container: t.current,
					waveColor: d.colors.primary,
					progressColor: d.colors.bodyText,
					height: u > 0 ? e(d.sizes.largestElementHeight) - 2 * u : "auto",
					barWidth: f,
					barGap: p,
					barRadius: m,
					cursorWidth: h,
					interact: !0
				});
				C.current = s, A.current = !1;
				let l = new c({ sampleRate: j });
				l.initialize(s, a), l.setEventHandlers({
					onRecordProgress: (e) => {
						E.current.onProgressMs?.(e);
					},
					onPermissionDenied: () => {
						E.current.onPermissionDenied(), v("idle");
					},
					onError: (e) => {
						E.current.onError(e), v("idle");
					}
				}), w.current = l;
				let g = new o();
				g.initialize(s), T.current = g, F(g), D.current = !0;
			} catch (e) {
				let t = e instanceof Error ? e : Error(String(e));
				E.current.onError?.(t);
			} finally {
				O.current = !1;
			}
		}
	}, [
		t,
		d,
		j,
		F,
		u
	]);
	(0, a.useEffect)(() => (I(), () => {
		M();
	}), [M, I]), (0, a.useEffect)(() => {
		let e = C.current;
		if (e) {
			if (_ === "recording") {
				e.setOptions({
					waveColor: d.colors.primary,
					progressColor: d.colors.primary
				});
				return;
			}
			if (A.current) {
				e.setOptions({
					interact: !0,
					waveColor: r(d.colors.fadedText40, d.colors.secondaryBg),
					progressColor: d.colors.bodyText
				});
				return;
			}
			e.setOptions({
				waveColor: d.colors.primary,
				progressColor: d.colors.bodyText
			});
		}
	}, [
		_,
		d.colors.bodyText,
		d.colors.fadedText40,
		d.colors.primary,
		d.colors.secondaryBg
	]);
	let L = (0, a.useCallback)(async () => {
		if (_ !== "recording") {
			if (D.current || await I(), !w.current) throw Error("Record backend not initialized");
			C.current && C.current.setOptions({
				waveColor: d.colors.primary,
				progressColor: d.colors.primary
			}), A.current = !1, await w.current.startRecording(), v("recording"), b(null), S(!1), E.current.onRecordStart?.();
		}
	}, [
		_,
		I,
		d.colors.primary
	]), R = (0, a.useCallback)(() => {
		T.current && C.current && (T.current.destroy(), T.current = new o(), T.current.initialize(C.current), k.current.clear(), S(!1), F(T.current)), A.current = !1;
	}, [F]), z = (0, a.useCallback)(() => {
		T.current?.seekToStart(), S(!1), A.current = !0, C.current && C.current.setOptions({
			interact: !0,
			waveColor: r(d.colors.fadedText40, d.colors.secondaryBg),
			progressColor: d.colors.bodyText
		});
	}, [
		d.colors.bodyText,
		d.colors.fadedText40,
		d.colors.secondaryBg
	]), B = (0, a.useCallback)(async () => {
		if (_ !== "recording") throw Error("Not currently recording");
		if (!w.current || !T.current) throw Error("Backends not initialized");
		try {
			let e = await w.current.stopRecording();
			b(e), await new Promise((t, n) => {
				if (!T.current) {
					n(/* @__PURE__ */ Error("Player not initialized"));
					return;
				}
				let r = {
					resolve: () => {
						k.current.delete(r), t();
					},
					reject: (e) => {
						k.current.delete(r), n(e);
					}
				};
				k.current.add(r), T.current.load(e).catch((e) => {
					k.current.delete(r), n(e instanceof Error ? e : Error(String(e)));
				});
			}), v("idle"), S(!1), z();
			let t = {
				blob: e,
				meta: {
					durationMs: T.current?.getDuration() ?? 0,
					sampleRate: typeof j == "number" ? j : null,
					mimeType: e.type || "audio/webm",
					size: e.size
				}
			};
			return E.current.onRecordReady?.(e), t;
		} catch (e) {
			let t = e instanceof Error ? e : Error(String(e));
			return S(!1), v("idle"), E.current.onError(t), {
				blob: new Blob(),
				meta: {
					durationMs: 0,
					sampleRate: null,
					mimeType: "audio/webm",
					size: 0
				}
			};
		}
	}, [
		_,
		z,
		j
	]), V = (0, a.useCallback)(async (e) => {
		let t = e ?? y;
		if (!t) {
			let e = /* @__PURE__ */ Error("No recorded audio to approve");
			E.current.onError(e);
			return;
		}
		try {
			let e = await l(t, j);
			await E.current.onApprove?.(e), b(null), v("idle");
		} catch (e) {
			let t = e instanceof Error ? e : Error(String(e));
			E.current.onError(t);
		}
	}, [y, j]), H = (0, a.useCallback)(() => {
		_ === "recording" && w.current?.cancelRecording(), R(), b(null), v("idle"), S(!1), A.current = !1, E.current.onCancel?.();
	}, [_, R]), U = (0, a.useMemo)(() => ({
		isPlaying: () => T.current?.getIsPlaying() ?? !1,
		play: async () => {
			if (!T.current) throw Error("Player not initialized");
			await T.current.play();
		},
		pause: () => {
			T.current?.pause();
		},
		load: async (e) => {
			if (D.current || await I(), !T.current) throw Error("Player not initialized");
			await T.current.load(e), z();
		},
		getCurrentTimeMs: () => T.current?.getCurrentTime() ?? 0,
		getDurationMs: () => T.current?.getDuration() ?? 0
	}), [z, I]), W = (0, a.useCallback)((e) => {
		E.current = e;
	}, []);
	return (0, a.useEffect)(() => () => {
		M();
	}, [M]), {
		state: _,
		isPlaybackPlaying: x,
		mountRef: t,
		start: L,
		stop: B,
		approve: V,
		cancel: H,
		destroy: M,
		playback: U,
		setEventHandlers: W
	};
}
//#endregion
export { _ as t };

//# sourceMappingURL=useWaveformController-rxqEhP00-DiSi28dC.js.map