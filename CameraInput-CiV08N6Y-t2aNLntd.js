import { E as e, En as t, Ha as n, J as r, Ka as i, Kn as a, Lt as o, N as s, Pt as c, S as l, Ua as u, Ur as d, Vr as f, Wt as p, a as m, da as h, ga as g, ii as ee, kn as _, kr as te, ma as v, na as y, o as b, oi as x, ti as S, wa as ne } from "./index-Dl4ETd_L-D2oMd1k2.js";
import { t as re } from "./WidgetLabel-CQfHGtry-udktvHE5.js";
import { t as ie } from "./WidgetLabelHelpIcon-C6IRqJ_I-BBI6AbZ-.js";
import { t as C } from "./urls-hxAPaE-_-CaxBV_RZ.js";
import { t as w } from "./UploadFileInfo-DdcsXhjv-C0F82PE-.js";
import { n as T, t as E } from "./ProgressBar-DhIwITyC-Bx_UJI5A.js";
//#region ../react/build/CameraInput-CiV08N6Y.js
var D = /* @__PURE__ */ i(u(), 1), ae = /* @__PURE__ */ i(n(), 1), O = /* @__PURE__ */ D.forwardRef(function(e, t) {
	return /* @__PURE__ */ D.createElement(l, p({
		iconAttrs: {
			fill: "currentColor",
			xmlns: "http://www.w3.org/2000/svg"
		},
		iconVerticalAlign: "middle",
		iconViewBox: "0 0 24 24"
	}, e, { ref: t }), /* @__PURE__ */ D.createElement("rect", {
		width: 24,
		height: 24,
		fill: "none"
	}), /* @__PURE__ */ D.createElement("path", { d: "M20 5h-3.17l-1.24-1.35A1.99 1.99 0 0014.12 3H9.88c-.56 0-1.1.24-1.48.65L7.17 5H4c-1.1 0-2 .9-2 2v12c0 1.1.9 2 2 2h16c1.1 0 2-.9 2-2V7c0-1.1-.9-2-2-2zm-1.35 8.35l-2.79 2.79c-.32.32-.86.1-.86-.35v-1.75H9v1.75c0 .45-.54.67-.85.35l-2.79-2.79c-.2-.2-.2-.51 0-.71l2.79-2.79a.5.5 0 01.85.36v1.83h6v-1.83c0-.45.54-.67.85-.35l2.79 2.79c.2.19.2.51.01.7z" }));
});
O.displayName = "SwitchCamera";
var k = /* @__PURE__ */ D.forwardRef(function(e, t) {
	return /* @__PURE__ */ D.createElement(l, p({
		iconAttrs: {
			fill: "currentColor",
			xmlns: "http://www.w3.org/2000/svg"
		},
		iconVerticalAlign: "middle",
		iconViewBox: "0 0 8 8"
	}, e, { ref: t }), /* @__PURE__ */ D.createElement("path", { d: "M.5 1c-.28 0-.5.23-.5.5v4c0 .28.23.5.5.5h5c.28 0 .5-.22.5-.5V4l1 1h1V2H7L6 3V1.5c0-.28-.22-.5-.5-.5h-5z" }));
});
k.displayName = "Video";
var A = /* @__PURE__ */ D.forwardRef(function(e, t) {
	return /* @__PURE__ */ D.createElement(l, p({
		iconAttrs: {
			fill: "currentColor",
			xmlns: "http://www.w3.org/2000/svg"
		},
		iconVerticalAlign: "middle",
		iconViewBox: "0 0 8 8"
	}, e, { ref: t }), /* @__PURE__ */ D.createElement("path", { d: "M1.41 0L0 1.41l.72.72L2.5 3.94.72 5.72 0 6.41l1.41 1.44.72-.72 1.81-1.81 1.78 1.81.69.72 1.44-1.44-.72-.69-1.81-1.78 1.81-1.81.72-.72L6.41 0l-.69.72L3.94 2.5 2.13.72 1.41 0z" }));
});
A.displayName = "X";
function j(e, t) {
	switch (e) {
		case "xsmall": return {
			padding: `${t.spacing.twoXS} ${t.spacing.sm}`,
			fontSize: t.fontSizes.sm
		};
		case "small": return { padding: `${t.spacing.twoXS} ${t.spacing.md}` };
		case "large": return { padding: `${t.spacing.md} ${t.spacing.md}` };
		default: return { padding: `${t.spacing.xs} ${t.spacing.md}` };
	}
}
var M = /* @__PURE__ */ t("div", { target: "etz5kuj8" })({
	name: "b6gpc",
	styles: "position:relative;overflow:hidden;width:100%;object-fit:contain"
}), N = /* @__PURE__ */ t("div", { target: "etz5kuj7" })(({ theme: e, width: t }) => ({
	backgroundColor: e.colors.secondaryBg,
	borderRadius: `${e.radii.default} ${e.radii.default} 0 0`,
	width: "100%",
	height: t * 9 / 16,
	display: "flex",
	flexDirection: "column",
	justifyContent: "center",
	alignItems: "center"
}), ""), P = /* @__PURE__ */ t("p", { target: "etz5kuj6" })(({ theme: e }) => ({
	marginTop: e.spacing.sm,
	textAlign: "center"
}), ""), oe = /* @__PURE__ */ t("img", { target: "etz5kuj5" })(({ theme: e, opacity: t }) => ({
	borderRadius: `${e.radii.default} ${e.radii.default} 0 0`,
	objectFit: "contain",
	opacity: t
}), ""), se = /* @__PURE__ */ t("a", { target: "etz5kuj4" })(({ theme: e }) => ({
	color: e.colors.link,
	textDecoration: e.linkUnderline ? "underline" : "none",
	display: "block"
}), ""), ce = /* @__PURE__ */ t("span", { target: "etz5kuj3" })({
	name: "s5xdrg",
	styles: "display:flex;align-items:center"
}), F = /* @__PURE__ */ t("div", { target: "etz5kuj2" })(({ theme: e }) => ({
	position: "absolute",
	top: e.spacing.lg,
	right: e.spacing.lg,
	zIndex: e.zIndices.priority,
	color: e.colors.fadedText40,
	mixBlendMode: "difference",
	opacity: .6
}), ""), I = /* @__PURE__ */ t("div", { target: "etz5kuj1" })({
	name: "1yoks5w",
	styles: "height:fit-content;width:100%;position:absolute;bottom:0"
}), L = /* @__PURE__ */ t("button", { target: "etz5kuj0" })(({ theme: e }) => ({
	position: "relative",
	display: "inline-flex",
	flexDirection: "column",
	alignItems: "center",
	justifyContent: "center",
	backgroundColor: e.colors.lightenedBg05,
	border: `${e.sizes.borderWidth} solid ${e.colors.borderColor}`,
	borderRadius: `0 0 ${e.radii.default} ${e.radii.default}`,
	"&:hover": {
		borderColor: e.colors.primary,
		color: e.colors.primary
	},
	"&:active": {
		color: e.colors.white,
		borderColor: e.colors.primary,
		backgroundColor: e.colors.primary
	},
	"&:focus:not(:active)": {
		borderColor: e.colors.primary,
		color: e.colors.primary
	},
	"&:disabled, &:disabled:hover, &:disabled:active": {
		color: e.colors.fadedText40,
		borderColor: e.colors.borderColor,
		backgroundColor: e.colors.lightenedBg05,
		cursor: "not-allowed"
	},
	fontWeight: e.fontWeights.normal,
	padding: `${e.spacing.xs} ${e.spacing.md}`,
	margin: e.spacing.none,
	lineHeight: e.lineHeights.base,
	color: "inherit",
	width: "100%",
	userSelect: "none",
	"&:focus": { outline: "none" },
	"&:focus-visible": { boxShadow: e.shadows.focusRing },
	...j("medium", e)
}), "");
function R({ disabled: e, onClick: t, children: n, progress: r }) {
	return /* @__PURE__ */ S.jsxs(L, {
		disabled: e || !1,
		onClick: t || (() => {}),
		progress: r || null,
		"data-testid": "stCameraInputButton",
		children: [n, r ? /* @__PURE__ */ S.jsx(I, { children: /* @__PURE__ */ S.jsx(T, {
			value: r,
			size: E.EXTRASMALL,
			overrides: {
				Bar: { style: {
					borderTopLeftRadius: 0,
					borderTopRightRadius: 0
				} },
				BarProgress: { style: {
					borderTopLeftRadius: 0,
					borderTopRightRadius: 0
				} },
				BarContainer: { style: {
					borderTopLeftRadius: 0,
					borderTopRightRadius: 0
				} }
			}
		}) }) : null]
	});
}
var z = (0, D.memo)(R), B = /* @__PURE__ */ ((e) => (e.USER = "user", e.ENVIRONMENT = "environment", e))(B || {}), V = (0, D.memo)(({ switchFacingMode: e }) => /* @__PURE__ */ S.jsx(F, {
	"data-testid": "stCameraInputSwitchButton",
	children: /* @__PURE__ */ S.jsx(c, {
		content: "Switch camera",
		placement: r.TOP_RIGHT,
		children: /* @__PURE__ */ S.jsx(m, {
			kind: b.MINIMAL,
			onClick: e,
			children: /* @__PURE__ */ S.jsx(s, {
				content: O,
				size: "twoXL",
				color: y.white
			})
		})
	})
})), H = { exports: {} }, U = H.exports, W;
function G() {
	return W || (W = 1, function(e, t) {
		(function(t, n) {
			e.exports = n(D.default);
		})(U, function(e) {
			return function(e) {
				var t = {};
				function n(r) {
					if (t[r]) return t[r].exports;
					var i = t[r] = {
						i: r,
						l: !1,
						exports: {}
					};
					return e[r].call(i.exports, i, i.exports, n), i.l = !0, i.exports;
				}
				return n.m = e, n.c = t, n.d = function(e, t, r) {
					n.o(e, t) || Object.defineProperty(e, t, {
						enumerable: !0,
						get: r
					});
				}, n.r = function(e) {
					typeof Symbol < "u" && Symbol.toStringTag && Object.defineProperty(e, Symbol.toStringTag, { value: "Module" }), Object.defineProperty(e, "__esModule", { value: !0 });
				}, n.t = function(e, t) {
					if (t & 1 && (e = n(e)), t & 8 || t & 4 && typeof e == "object" && e && e.__esModule) return e;
					var r = /* @__PURE__ */ Object.create(null);
					if (n.r(r), Object.defineProperty(r, "default", {
						enumerable: !0,
						value: e
					}), t & 2 && typeof e != "string") for (var i in e) n.d(r, i, function(t) {
						return e[t];
					}.bind(null, i));
					return r;
				}, n.n = function(e) {
					var t = e && e.__esModule ? (function() {
						return e.default;
					}) : (function() {
						return e;
					});
					return n.d(t, "a", t), t;
				}, n.o = function(e, t) {
					return Object.prototype.hasOwnProperty.call(e, t);
				}, n.p = "", n(n.s = "./src/react-webcam.tsx");
			}({
				"./src/react-webcam.tsx": (function(e, t, n) {
					n.r(t);
					var r = n("react"), i = /* @__PURE__ */ function() {
						var e = function(t, n) {
							return e = Object.setPrototypeOf || { __proto__: [] } instanceof Array && function(e, t) {
								e.__proto__ = t;
							} || function(e, t) {
								for (var n in t) t.hasOwnProperty(n) && (e[n] = t[n]);
							}, e(t, n);
						};
						return function(t, n) {
							e(t, n);
							function r() {
								this.constructor = t;
							}
							t.prototype = n === null ? Object.create(n) : (r.prototype = n.prototype, new r());
						};
					}(), a = function() {
						return a = Object.assign || function(e) {
							for (var t, n = 1, r = arguments.length; n < r; n++) for (var i in t = arguments[n], t) Object.prototype.hasOwnProperty.call(t, i) && (e[i] = t[i]);
							return e;
						}, a.apply(this, arguments);
					}, o = function(e, t) {
						var n = {};
						for (var r in e) Object.prototype.hasOwnProperty.call(e, r) && t.indexOf(r) < 0 && (n[r] = e[r]);
						if (e != null && typeof Object.getOwnPropertySymbols == "function") for (var i = 0, r = Object.getOwnPropertySymbols(e); i < r.length; i++) t.indexOf(r[i]) < 0 && Object.prototype.propertyIsEnumerable.call(e, r[i]) && (n[r[i]] = e[r[i]]);
						return n;
					};
					(function() {
						typeof window > "u" || (navigator.mediaDevices === void 0 && (navigator.mediaDevices = {}), navigator.mediaDevices.getUserMedia === void 0 && (navigator.mediaDevices.getUserMedia = function(e) {
							var t = navigator.getUserMedia || navigator.webkitGetUserMedia || navigator.mozGetUserMedia || navigator.msGetUserMedia;
							return t ? new Promise(function(n, r) {
								t.call(navigator, e, n, r);
							}) : Promise.reject(/* @__PURE__ */ Error("getUserMedia is not implemented in this browser"));
						}));
					})();
					function s() {
						return !!(navigator.mediaDevices && navigator.mediaDevices.getUserMedia);
					}
					t.default = function(e) {
						i(t, e);
						function t(t) {
							var n = e.call(this, t) || this;
							return n.canvas = null, n.ctx = null, n.requestUserMediaId = 0, n.unmounted = !1, n.state = { hasUserMedia: !1 }, n;
						}
						return t.prototype.componentDidMount = function() {
							var e = this, t = e.state, n = e.props;
							if (this.unmounted = !1, !s()) {
								n.onUserMediaError("getUserMedia not supported");
								return;
							}
							t.hasUserMedia || this.requestUserMedia(), n.children && typeof n.children != "function" && console.warn("children must be a function");
						}, t.prototype.componentDidUpdate = function(e) {
							var t = this.props;
							if (!s()) {
								t.onUserMediaError("getUserMedia not supported");
								return;
							}
							var n = JSON.stringify(e.audioConstraints) !== JSON.stringify(t.audioConstraints), r = JSON.stringify(e.videoConstraints) !== JSON.stringify(t.videoConstraints), i = e.minScreenshotWidth !== t.minScreenshotWidth, a = e.minScreenshotHeight !== t.minScreenshotHeight;
							(r || i || a) && (this.canvas = null, this.ctx = null), (n || r) && (this.stopAndCleanup(), this.requestUserMedia());
						}, t.prototype.componentWillUnmount = function() {
							this.unmounted = !0, this.stopAndCleanup();
						}, t.stopMediaStream = function(e) {
							e && (e.getVideoTracks && e.getAudioTracks ? (e.getVideoTracks().map(function(t) {
								e.removeTrack(t), t.stop();
							}), e.getAudioTracks().map(function(t) {
								e.removeTrack(t), t.stop();
							})) : e.stop());
						}, t.prototype.stopAndCleanup = function() {
							var e = this.state;
							e.hasUserMedia && (t.stopMediaStream(this.stream), e.src && window.URL.revokeObjectURL(e.src));
						}, t.prototype.getScreenshot = function(e) {
							var t = this, n = t.state, r = t.props;
							if (!n.hasUserMedia) return null;
							var i = this.getCanvas(e);
							return i && i.toDataURL(r.screenshotFormat, r.screenshotQuality);
						}, t.prototype.getCanvas = function(e) {
							var t = this, n = t.state, r = t.props;
							if (!this.video || !n.hasUserMedia || !this.video.videoHeight) return null;
							if (!this.ctx) {
								var i = this.video.videoWidth, a = this.video.videoHeight;
								if (!this.props.forceScreenshotSourceSize) {
									var o = i / a;
									i = r.minScreenshotWidth || this.video.clientWidth, a = i / o, r.minScreenshotHeight && a < r.minScreenshotHeight && (a = r.minScreenshotHeight, i = a * o);
								}
								this.canvas = document.createElement("canvas"), this.canvas.width = e?.width || i, this.canvas.height = e?.height || a, this.ctx = this.canvas.getContext("2d");
							}
							var s = this, c = s.ctx, l = s.canvas;
							return c && l && (l.width = e?.width || l.width, l.height = e?.height || l.height, r.mirrored && (c.translate(l.width, 0), c.scale(-1, 1)), c.imageSmoothingEnabled = r.imageSmoothing, c.drawImage(this.video, 0, 0, e?.width || l.width, e?.height || l.height), r.mirrored && (c.scale(-1, 1), c.translate(-l.width, 0))), l;
						}, t.prototype.requestUserMedia = function() {
							var e = this, n = this.props, r = function(r, i) {
								var a = { video: typeof i < "u" ? i : !0 };
								n.audio && (a.audio = typeof r < "u" ? r : !0), e.requestUserMediaId++;
								var o = e.requestUserMediaId;
								navigator.mediaDevices.getUserMedia(a).then(function(n) {
									e.unmounted || o !== e.requestUserMediaId ? t.stopMediaStream(n) : e.handleUserMedia(null, n);
								}).catch(function(t) {
									e.handleUserMedia(t);
								});
							};
							if ("mediaDevices" in navigator) r(n.audioConstraints, n.videoConstraints);
							else {
								var i = function(e) {
									return { optional: [{ sourceId: e }] };
								}, a = function(e) {
									var t = e.deviceId;
									return typeof t == "string" ? t : Array.isArray(t) && t.length > 0 ? t[0] : typeof t == "object" && t.ideal ? t.ideal : null;
								};
								MediaStreamTrack.getSources(function(e) {
									var t = null, o = null;
									e.forEach(function(e) {
										e.kind === "audio" ? t = e.id : e.kind === "video" && (o = e.id);
									});
									var s = a(n.audioConstraints);
									s && (t = s);
									var c = a(n.videoConstraints);
									c && (o = c), r(i(t), i(o));
								});
							}
						}, t.prototype.handleUserMedia = function(e, t) {
							var n = this.props;
							if (e || !t) {
								this.setState({ hasUserMedia: !1 }), n.onUserMediaError(e);
								return;
							}
							this.stream = t;
							try {
								this.video && (this.video.srcObject = t), this.setState({ hasUserMedia: !0 });
							} catch {
								this.setState({
									hasUserMedia: !0,
									src: window.URL.createObjectURL(t)
								});
							}
							n.onUserMedia(t);
						}, t.prototype.render = function() {
							var e = this, t = this, n = t.state, i = t.props, s = i.audio;
							i.forceScreenshotSourceSize;
							var c = i.disablePictureInPicture;
							i.onUserMedia, i.onUserMediaError, i.screenshotFormat, i.screenshotQuality, i.minScreenshotWidth, i.minScreenshotHeight, i.audioConstraints, i.videoConstraints, i.imageSmoothing;
							var l = i.mirrored, u = i.style, d = u === void 0 ? {} : u, f = i.children, p = o(i, [
								"audio",
								"forceScreenshotSourceSize",
								"disablePictureInPicture",
								"onUserMedia",
								"onUserMediaError",
								"screenshotFormat",
								"screenshotQuality",
								"minScreenshotWidth",
								"minScreenshotHeight",
								"audioConstraints",
								"videoConstraints",
								"imageSmoothing",
								"mirrored",
								"style",
								"children"
							]), m = l ? a(a({}, d), { transform: (d.transform || "") + " scaleX(-1)" }) : d, h = { getScreenshot: this.getScreenshot.bind(this) };
							return r.createElement(r.Fragment, null, r.createElement("video", a({
								autoPlay: !0,
								disablePictureInPicture: c,
								src: n.src,
								muted: !s,
								playsInline: !0,
								ref: function(t) {
									e.video = t;
								},
								style: m
							}, p)), f && f(h));
						}, t.defaultProps = {
							audio: !1,
							disablePictureInPicture: !1,
							forceScreenshotSourceSize: !1,
							imageSmoothing: !0,
							mirrored: !1,
							onUserMedia: function() {},
							onUserMediaError: function() {},
							screenshotFormat: "image/webp",
							screenshotQuality: .92
						}, t;
					}(r.Component);
				}),
				react: (function(t, n) {
					t.exports = e;
				})
			}).default;
		});
	}(H)), H.exports;
}
var K = /* @__PURE__ */ a(G()), q = ({ width: e }) => /* @__PURE__ */ S.jsxs(N, {
	width: e,
	children: [/* @__PURE__ */ S.jsx(s, {
		size: "threeXL",
		color: y.gray60,
		content: k
	}), /* @__PURE__ */ S.jsxs(P, { children: ["This app would like to use your camera.", /* @__PURE__ */ S.jsx(se, {
		href: C,
		rel: "noopener noreferrer",
		target: "_blank",
		children: "Learn how to allow access."
	})] })]
}), le = (0, D.memo)(({ handleCapture: e, width: t, disabled: n, clearPhotoInProgress: r, setClearPhotoInProgress: i, facingMode: a, setFacingMode: o, testOverride: s }) => {
	let [c, l] = (0, D.useState)(s || "pending"), u = (0, D.useRef)(null), [d, p] = (0, D.useState)(t), m = (0, D.useCallback)(_(1e3, p), []);
	(0, D.useEffect)(() => {
		m(t);
	}, [t, m]);
	function h() {
		u.current !== null && e(u.current.getScreenshot());
	}
	let g = v();
	return /* @__PURE__ */ S.jsxs(M, {
		"data-testid": "stCameraInputWebcamComponent",
		children: [
			c !== "success" && !n && !r ? /* @__PURE__ */ S.jsx(q, { width: d }) : f() && /* @__PURE__ */ S.jsx(V, { switchFacingMode: o }),
			/* @__PURE__ */ S.jsx(N, {
				"data-testid": "stCameraInputWebcamStyledBox",
				hidden: c !== "success" && !n && !r,
				width: d,
				children: !n && /* @__PURE__ */ S.jsx(K, {
					audio: !1,
					ref: u,
					screenshotFormat: "image/jpeg",
					screenshotQuality: 1,
					width: d,
					height: d * 9 / 16,
					style: { borderRadius: `${g.radii.default} ${g.radii.default} 0 0` },
					onUserMediaError: () => {
						l("error");
					},
					onUserMedia: () => {
						l("success"), i(!1);
					},
					videoConstraints: {
						width: { ideal: d },
						facingMode: a
					}
				})
			}),
			/* @__PURE__ */ S.jsx(z, {
				onClick: h,
				disabled: c !== "success" || n || r,
				children: "Take Photo"
			})
		]
	});
}), J = "RESTORED_FROM_WIDGET", ue = 150, de = x.getLogger("CameraInput"), Y = (t) => new e({ uploadedFileInfo: t.filter((e) => e.status.type === "uploaded").map((e) => {
	let { name: t, size: n, status: r } = e, { fileId: i, fileUrls: a } = r;
	return new o({
		fileId: i,
		fileUrls: a,
		name: t,
		size: n
	});
}) }), fe = (e, t) => {
	let n = t.getFileUploaderStateValue(e);
	if (d(n)) return {
		files: [],
		nextLocalId: 1,
		imgSrc: null
	};
	let { uploadedFileInfo: r } = n;
	if (d(r) || r.length === 0) return {
		files: [],
		nextLocalId: 1,
		imgSrc: null
	};
	let i = 1, a = r.map((e) => {
		let t = e.name, n = e.size, r = e.fileId, a = e.fileUrls, o = new w(t, n, i, {
			type: "uploaded",
			fileId: r,
			fileUrls: a
		});
		return i += 1, o;
	});
	return {
		files: a,
		nextLocalId: i,
		imgSrc: a.length > 0 ? J : null
	};
};
function pe(e, t) {
	return fetch(e).then((e) => e.arrayBuffer()).then((e) => new File([e], t, { type: "image/jpeg" }));
}
var X = (0, D.memo)(({ element: e, widgetMgr: t, uploadClient: n, disabled: r, fragmentId: i, testOverride: a }) => {
	let { width: o, elementRef: c } = h(), l = (0, D.useRef)(null);
	l.current === null && (l.current = fe(e, t));
	let { files: u, nextLocalId: f, imgSrc: p } = l.current, m = (0, D.useRef)(f), [_, v] = (0, D.useState)(() => u), y = (0, D.useRef)(_);
	(0, D.useLayoutEffect)(() => {
		y.current = _;
	}, [_]);
	let [b, x] = (0, D.useState)(() => p), [C, T] = (0, D.useState)(!1), [E, O] = (0, D.useState)(!0), [k, j] = (0, D.useState)(!1), [P, se] = (0, D.useState)(B.USER), F = (0, D.useRef)([]), I = (0, D.useRef)(null), L = (0, D.useCallback)(() => {
		F.current.length !== 0 && (F.current.forEach((e) => e()), F.current = []);
	}, []), { clear: R, restart: V } = ne(() => {
		L();
	}, ue, { autoStart: !1 }), H = (0, D.useCallback)(() => new Promise((e) => {
		F.current.push(e), V();
	}), [V]);
	(0, D.useEffect)(() => () => {
		R(), L(), I.current = null;
	}, [R, L]);
	let U = (0, D.useCallback)(() => {
		let e = m.current;
		return m.current += 1, e;
	}, []), W = (0, D.useMemo)(() => _.some((e) => e.status.type === "uploading") ? "updating" : "ready", [_]), G = (0, D.useMemo)(() => {
		if (_.length > 0 && _[_.length - 1].status.type === "uploading") return _[_.length - 1].status.progress;
	}, [_]), K = (0, D.useCallback)(() => {
		se((e) => e === B.USER ? B.ENVIRONMENT : B.USER);
	}, []), q = (0, D.useCallback)((e) => y.current.find((t) => t.id === e), []), X = (0, D.useCallback)((e) => {
		(0, ae.flushSync)(() => {
			v((t) => [...t, e]);
		});
	}, []), Z = (0, D.useCallback)((e) => {
		v((t) => t.filter((t) => t.id !== e));
	}, []), Q = (0, D.useCallback)((e, t) => {
		v((n) => n.map((n) => n.id === e ? t : n));
	}, []), $ = (0, D.useCallback)((e, t) => {
		T(!1);
		let n = q(e);
		d(n) || n.status.type !== "uploading" || Q(n.id, n.setStatus({
			type: "uploaded",
			fileId: t.fileId,
			fileUrls: t
		}));
	}, [q, Q]), me = (0, D.useCallback)((e, t) => {
		let n = q(t);
		if (d(n) || n.status.type !== "uploading") return;
		let r = e.total ? Math.round(e.loaded * 100 / e.total) : 0;
		n.status.progress !== r && Q(t, n.setStatus({
			type: "uploading",
			abortController: n.status.abortController,
			progress: r
		}));
	}, [q, Q]), he = (0, D.useCallback)((t, r) => {
		let i = new AbortController(), a = new w(r.name, r.size, U(), {
			type: "uploading",
			abortController: i,
			progress: 1
		});
		X(a), n.uploadFile(e, t.uploadUrl, r, (e) => me(e, a.id), i.signal).then(() => $(a.id, t)).catch((e) => {
			e instanceof DOMException && e.name === "AbortError" || Q(a.id, a.setStatus({
				type: "error",
				errorMessage: e ? e.toString() : "Unknown error"
			}));
		});
	}, [
		X,
		e,
		U,
		$,
		me,
		Q,
		n
	]), ge = (0, D.useCallback)((e) => {
		let t = q(e);
		d(t) || (t.status.type === "uploading" && t.status.abortController.abort(), t.status.type === "uploaded" && t.status.fileUrls.deleteUrl && n.deleteFile(t.status.fileUrls.deleteUrl), Z(e));
	}, [
		q,
		Z,
		n
	]), _e = (0, D.useCallback)((e) => {
		if (e === null) return Promise.resolve();
		if (I.current) return I.current;
		x(e), T(!0), O(!1);
		let t = pe(e, `camera-input-${(/* @__PURE__ */ new Date()).toISOString().replace(/:/g, "_")}.jpg`).then((e) => n.fetchFileURLs([e]).then((t) => ({
			file: e,
			fileUrls: t[0]
		}))).then(({ file: e, fileUrls: t }) => he(t, e)).then(H).then(() => {
			O(!0);
		}).catch((e) => {
			de.error(e);
		}).finally(() => {
			I.current = null;
		});
		return I.current = t, t;
	}, [
		n,
		he,
		H
	]), ve = (0, D.useCallback)((e) => {
		_e(e);
	}, [_e]), ye = (0, D.useCallback)(() => {
		_.length !== 0 && (_.forEach((e) => ge(e.id)), x(null), j(!0));
	}, [_, ge]);
	return (0, D.useEffect)(() => {
		t.getFileUploaderStateValue(e) === void 0 && t.setFileUploaderStateValue(e, Y(_), { fromUi: !1 }, i);
	}, []), (0, D.useEffect)(() => {
		if (W !== "ready") return;
		let n = Y(_);
		te(n, t.getFileUploaderStateValue(e)) || t.setFileUploaderStateValue(e, n, { fromUi: !0 }, i);
	}, [
		W,
		_,
		t,
		e,
		i
	]), g({
		element: e,
		widgetMgr: t,
		onFormCleared: (0, D.useCallback)(() => {
			v([]), x(null);
			let n = Y([]);
			t.setFileUploaderStateValue(e, n, { fromUi: !0 }, i);
		}, [
			e,
			i,
			t
		])
	}), /* @__PURE__ */ S.jsxs(M, {
		className: "stCameraInput",
		"data-testid": "stCameraInput",
		ref: c,
		children: [/* @__PURE__ */ S.jsx(re, {
			label: e.label,
			disabled: r,
			labelVisibility: ee(e.labelVisibility?.value),
			children: e.help && /* @__PURE__ */ S.jsx(ie, {
				content: e.help,
				label: e.label
			})
		}), b ? /* @__PURE__ */ S.jsxs(S.Fragment, { children: [/* @__PURE__ */ S.jsx(N, {
			width: o,
			children: b !== J && /* @__PURE__ */ S.jsx(oe, {
				src: b,
				alt: "Snapshot",
				opacity: C || !E ? "50%" : "100%",
				width: o,
				height: o * 9 / 16
			})
		}), /* @__PURE__ */ S.jsx(z, {
			onClick: ye,
			progress: G,
			disabled: !!G || r,
			children: G ? "Uploading..." : /* @__PURE__ */ S.jsxs(ce, { children: [/* @__PURE__ */ S.jsx(s, {
				content: A,
				margin: "0 xs 0 0",
				size: "sm"
			}), " Clear photo"] })
		})] }) : /* @__PURE__ */ S.jsx(le, {
			handleCapture: ve,
			width: o,
			disabled: r,
			clearPhotoInProgress: k,
			setClearPhotoInProgress: j,
			facingMode: P,
			setFacingMode: K,
			testOverride: a
		})]
	});
});
//#endregion
export { X as default };

//# sourceMappingURL=CameraInput-CiV08N6Y-t2aNLntd.js.map