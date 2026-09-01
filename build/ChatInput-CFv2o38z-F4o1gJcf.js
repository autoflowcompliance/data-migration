import { $t as e, Ba as t, Cn as n, Da as r, E as i, En as a, J as o, Ka as s, Lt as c, N as l, Pt as u, S as d, Ua as f, Ur as p, Wt as m, da as ee, fn as te, ma as ne, n as h, oi as g, ti as _, x as re } from "./index-Dl4ETd_L-D2oMd1k2.js";
import { t as ie } from "./useWaveformController-rxqEhP00-DiSi28dC.js";
import { t as v } from "./UploadFileInfo-DdcsXhjv-C0F82PE-.js";
import { a as ae, c as oe, i as se, n as ce, o as y, p as b, r as x, s as le, t as ue } from "./utils-CotIDfd1-hvXXk-4A.js";
import { t as de } from "./InputInstructions-BQBBgzXB-ClQbP4Gu.js";
import { n as fe, t as pe } from "./useTextInputAutoExpand-D9pA1iXq-CBWLLIpD.js";
import { t as me } from "./inputUtils-DCYiajnz-DpM8zsby.js";
//#region ../react/build/ChatInput-CFv2o38z.js
var S = /* @__PURE__ */ s(f(), 1), C = /* @__PURE__ */ S.forwardRef(function(e, t) {
	return /* @__PURE__ */ S.createElement(d, m({
		iconAttrs: {
			fill: "currentColor",
			xmlns: "http://www.w3.org/2000/svg"
		},
		iconVerticalAlign: "middle",
		iconViewBox: "0 0 24 24"
	}, e, { ref: t }), /* @__PURE__ */ S.createElement("path", {
		fill: "none",
		d: "M0 0h24v24H0V0z"
	}), /* @__PURE__ */ S.createElement("path", { d: "M12 14c1.66 0 3-1.34 3-3V5c0-1.66-1.34-3-3-3S9 3.34 9 5v6c0 1.66 1.34 3 3 3zm-1-9c0-.55.45-1 1-1s1 .45 1 1v6c0 .55-.45 1-1 1s-1-.45-1-1V5zm6 6c0 2.76-2.24 5-5 5s-5-2.24-5-5H5c0 3.53 2.61 6.43 6 6.92V21h2v-3.08c3.39-.49 6-3.39 6-6.92h-2z" }));
});
C.displayName = "MicNone";
var w = /* @__PURE__ */ S.forwardRef(function(e, t) {
	return /* @__PURE__ */ S.createElement(d, m({
		iconAttrs: {
			fill: "currentColor",
			xmlns: "http://www.w3.org/2000/svg"
		},
		iconVerticalAlign: "middle",
		iconViewBox: "0 0 24 24"
	}, e, { ref: t }), /* @__PURE__ */ S.createElement("rect", {
		width: 24,
		height: 24,
		fill: "none"
	}), /* @__PURE__ */ S.createElement("path", { d: "M18 13h-5v5c0 .55-.45 1-1 1s-1-.45-1-1v-5H6c-.55 0-1-.45-1-1s.45-1 1-1h5V6c0-.55.45-1 1-1s1 .45 1 1v5h5c.55 0 1 .45 1 1s-.45 1-1 1z" }));
});
w.displayName = "Add";
var T = /* @__PURE__ */ S.forwardRef(function(e, t) {
	return /* @__PURE__ */ S.createElement(d, m({
		iconAttrs: {
			fill: "currentColor",
			xmlns: "http://www.w3.org/2000/svg"
		},
		iconVerticalAlign: "middle",
		iconViewBox: "0 0 24 24"
	}, e, { ref: t }), /* @__PURE__ */ S.createElement("path", {
		fill: "none",
		d: "M0 0h24v24H0V0z"
	}), /* @__PURE__ */ S.createElement("path", { d: "M13 19V7.83l4.88 4.88c.39.39 1.03.39 1.42 0a.996.996 0 000-1.41l-6.59-6.59a.996.996 0 00-1.41 0l-6.6 6.58a.996.996 0 101.41 1.41L11 7.83V19c0 .55.45 1 1 1s1-.45 1-1z" }));
});
T.displayName = "ArrowUpward";
var he = /* @__PURE__ */ S.forwardRef(function(e, t) {
	return /* @__PURE__ */ S.createElement(d, m({
		iconAttrs: {
			fill: "currentColor",
			xmlns: "http://www.w3.org/2000/svg"
		},
		iconVerticalAlign: "middle",
		iconViewBox: "0 0 24 24"
	}, e, { ref: t }), /* @__PURE__ */ S.createElement("path", {
		fill: "none",
		d: "M0 0h24v24H0V0z"
	}), /* @__PURE__ */ S.createElement("path", { d: "M18 6.7l-8.48 8.48-3.54-3.54a.996.996 0 10-1.41 1.41l4.24 4.24c.39.39 1.02.39 1.41 0l9.18-9.18a.999.999 0 00-.01-1.42c-.37-.38-1-.38-1.39.01z" }));
});
he.displayName = "Check";
var ge = /* @__PURE__ */ S.forwardRef(function(e, t) {
	return /* @__PURE__ */ S.createElement(d, m({
		iconAttrs: {
			fill: "currentColor",
			xmlns: "http://www.w3.org/2000/svg"
		},
		iconVerticalAlign: "middle",
		iconViewBox: "0 0 24 24"
	}, e, { ref: t }), /* @__PURE__ */ S.createElement("path", {
		fill: "none",
		d: "M0 0h24v24H0V0z"
	}), /* @__PURE__ */ S.createElement("path", { d: "M18.3 5.71a.996.996 0 00-1.41 0L12 10.59 7.11 5.7A.996.996 0 105.7 7.11L10.59 12 5.7 16.89a.996.996 0 101.41 1.41L12 13.41l4.89 4.89a.996.996 0 101.41-1.41L13.41 12l4.89-4.89c.38-.38.38-1.02 0-1.4z" }));
});
ge.displayName = "Close";
var _e = /* @__PURE__ */ S.forwardRef(function(e, t) {
	return /* @__PURE__ */ S.createElement(d, m({
		iconAttrs: {
			fill: "currentColor",
			xmlns: "http://www.w3.org/2000/svg"
		},
		iconVerticalAlign: "middle",
		iconViewBox: "0 0 24 24"
	}, e, { ref: t }), /* @__PURE__ */ S.createElement("rect", {
		width: 24,
		height: 24,
		fill: "none"
	}), /* @__PURE__ */ S.createElement("path", { d: "M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm0 11c-.55 0-1-.45-1-1V8c0-.55.45-1 1-1s1 .45 1 1v4c0 .55-.45 1-1 1zm0 4c-.55 0-1-.45-1-1s.45-1 1-1 1 .45 1 1-.45 1-1 1z" }));
});
_e.displayName = "ErrorOutline";
var E = g.getLogger("ChatInput"), ve = /* @__PURE__ */ a("div", { target: "e1d2x3se11" })(({ isStretchHeight: e }) => ({
	position: "relative",
	display: "flex",
	flexDirection: "column",
	...e && { height: "100%" }
}), ""), ye = /* @__PURE__ */ a("div", { target: "e1d2x3se10" })(({ theme: e, isStretchHeight: t }) => ({
	backgroundColor: e.colors.secondaryBg,
	border: `${e.sizes.borderWidth} solid`,
	borderColor: e.colors.widgetBorderColor ?? e.colors.transparent,
	position: "relative",
	display: "flex",
	flexDirection: "column",
	alignItems: "stretch",
	flex: 1,
	paddingTop: e.spacing.md,
	paddingBottom: e.spacing.md,
	paddingLeft: e.spacing.lg,
	paddingRight: e.spacing.lg,
	gap: e.spacing.sm,
	borderRadius: e.radii.default,
	boxSizing: "border-box",
	...t && { height: "100%" },
	":focus-within": { borderColor: e.colors.primary }
}), ""), be = /* @__PURE__ */ a("div", { target: "e1d2x3se9" })(({ theme: e }) => ({
	display: "flex",
	flexWrap: "wrap",
	gap: e.spacing.sm
}), ""), xe = /* @__PURE__ */ a("div", { target: "e1d2x3se8" })(({ theme: e, isStacked: t, hasExpandedHeight: n }) => ({
	display: "flex",
	flexDirection: n ? "column" : "row",
	alignItems: n ? "stretch" : "center",
	justifyContent: n ? "flex-start" : "space-between",
	width: "100%",
	gap: e.spacing.sm,
	flexWrap: !n && t ? "wrap" : "nowrap",
	...n && { flex: 1 }
}), ""), Se = /* @__PURE__ */ a("div", { target: "e1d2x3se7" })(({ isStacked: e, hasExpandedHeight: t }) => ({
	flex: e && !t ? "none" : 1,
	width: e || t ? "100%" : "auto",
	order: e && !t ? -1 : 0,
	display: "flex",
	alignItems: t ? "stretch" : "center",
	minWidth: 0
}), ""), Ce = /* @__PURE__ */ a("div", { target: "e1d2x3se6" })(({ theme: e, hasExpandedHeight: t }) => ({
	display: "flex",
	flexDirection: "row",
	flexShrink: 0,
	gap: e.spacing.sm,
	alignItems: "center",
	order: t ? 0 : -1
}), ""), we = /* @__PURE__ */ a("div", { target: "e1d2x3se5" })(({ theme: e }) => ({
	display: "flex",
	flexDirection: "row",
	gap: e.spacing.sm,
	alignItems: "center"
}), ""), Te = /* @__PURE__ */ a("div", { target: "e1d2x3se4" })(({ theme: e }) => ({
	display: "flex",
	flexDirection: "row",
	justifyContent: "space-between",
	alignItems: "center",
	width: "100%",
	gap: e.spacing.sm
}), ""), Ee = /* @__PURE__ */ a("div", { target: "e1d2x3se3" })(({ theme: e }) => ({
	color: e.colors.fadedText60,
	fontSize: e.fontSizes.twoSm,
	textAlign: "right",
	whiteSpace: "nowrap",
	pointerEvents: "auto",
	cursor: "text",
	"& .stChatInputInstructions": { position: "static" }
}), ""), D = /* @__PURE__ */ a("button", { target: "e1d2x3se2" })(({ theme: e, disabled: t, hasError: n, primary: r }) => r ? {
	border: "none",
	backgroundColor: t ? e.colors.darkenedBgMix15 : e.colors.primary,
	borderRadius: e.radii.button,
	display: "inline-flex",
	alignItems: "center",
	justifyContent: "center",
	lineHeight: e.lineHeights.none,
	margin: e.spacing.none,
	padding: e.spacing.xs,
	width: e.sizes.chatInputPrimaryButtonSize,
	height: e.sizes.chatInputPrimaryButtonSize,
	color: t ? e.colors.fadedText40 : e.colors.white,
	cursor: t ? "not-allowed" : "pointer",
	transition: "background-color 200ms ease",
	"&:focus": { outline: "none" },
	":focus": { outline: "none" },
	"&:focus-visible": { boxShadow: e.shadows.focusRing },
	"&:hover": { backgroundColor: t ? e.colors.darkenedBgMix15 : e.colors.primary }
} : {
	border: "none",
	backgroundColor: e.colors.transparent,
	borderRadius: e.radii.default,
	display: "inline-flex",
	alignItems: "center",
	justifyContent: "center",
	lineHeight: e.lineHeights.none,
	margin: e.spacing.none,
	padding: e.spacing.none,
	color: n ? e.colors.redTextColor : t ? e.colors.fadedText40 : e.colors.fadedText60,
	pointerEvents: "auto",
	"&:focus": { outline: "none" },
	":focus": { outline: "none" },
	"&:focus-visible": { boxShadow: e.shadows.focusRing },
	"&:hover": { color: n ? e.colors.redColor : e.colors.bodyText },
	"&:active": { color: e.colors.primary },
	"&:disabled, &:disabled:hover, &:disabled:active": {
		backgroundColor: e.colors.transparent,
		borderColor: e.colors.transparent,
		color: e.colors.fadedText40,
		cursor: "not-allowed"
	},
	"& svg": {
		width: e.iconSizes.lg,
		height: e.iconSizes.lg
	}
}, ""), De = /* @__PURE__ */ a("div", { target: "e1d2x3se1" })(({ isRecording: e }) => ({
	display: e ? "flex" : "none",
	flex: 1,
	alignItems: "center",
	minWidth: 0
}), ""), Oe = /* @__PURE__ */ a("div", { target: "e1d2x3se0" })(({ theme: e }) => ({
	position: "relative",
	width: "100%",
	height: e.sizes.chatInputPrimaryButtonSize,
	borderRadius: e.radii.default,
	overflow: "hidden",
	"& > div": {
		position: "absolute",
		inset: 0
	}
}), ""), O = (e, t) => t === h.Directory ? {
	...e,
	webkitdirectory: "",
	multiple: !0
} : e, ke = (e, t) => b(e, t) ? { isValid: !0 } : {
	isValid: !1,
	errorMessage: `${e.type || "This type of"} files are not allowed.`
}, k = (t) => {
	switch (t) {
		case h.None: return "a file";
		case h.Single: return "a file";
		case h.Multiple: return "files";
		case h.Directory: return "a directory";
		default: return e(t), "a file";
	}
}, Ae = /* @__PURE__ */ a("div", { target: "e3id6jz2" })(({ theme: e }) => ({
	backgroundColor: e.colors.transparent,
	position: "absolute",
	inset: 0,
	zIndex: e.zIndices.priority,
	borderRadius: e.radii.chatInput
}), ""), A = /* @__PURE__ */ a("div", { target: "e3id6jz1" })(({ theme: e }) => ({
	position: "absolute",
	inset: 0,
	border: `${e.sizes.borderWidth} solid`,
	borderColor: e.colors.primary,
	borderRadius: e.radii.chatInput,
	backgroundColor: e.colors.secondaryBg,
	color: e.colors.primary,
	display: "flex",
	alignItems: "center",
	justifyContent: "center",
	fontWeight: e.fontWeights.bold,
	pointerEvents: "none",
	zIndex: e.zIndices.priority
}), ""), j = /* @__PURE__ */ a("div", { target: "e3id6jz0" })(({ disabled: e }) => ({ pointerEvents: e ? "none" : "auto" }), ""), je = (0, S.memo)(({ onDrop: e, multiple: t, accept: n, maxSize: r, acceptFile: i, disabled: a, fileTypes: s }) => {
	let { getRootProps: c, getInputProps: d } = oe({
		onDrop: e,
		multiple: t,
		accept: n,
		maxSize: r,
		useFsAccessApi: !1
	}), f = O(d(), i), p = c({ tabIndex: -1 }), m = () => {
		let e = `Upload or drag and drop ${k(i)}`;
		return s && s.length > 0 ? `${e} (${y(s)})` : e;
	};
	return /* @__PURE__ */ _.jsxs(j, {
		"data-testid": "stChatInputFileUploadButton",
		disabled: a,
		...p,
		children: [/* @__PURE__ */ _.jsx("input", { ...f }), /* @__PURE__ */ _.jsx(u, {
			content: m(),
			placement: o.TOP,
			onMouseEnterDelay: 500,
			children: /* @__PURE__ */ _.jsx(D, {
				type: "button",
				disabled: a,
				"aria-label": `Upload ${k(i)}`,
				children: /* @__PURE__ */ _.jsx(l, {
					content: w,
					size: "xl",
					color: "inherit"
				})
			})
		})]
	});
}), Me = (0, S.memo)(({ getRootProps: e, getInputProps: t, acceptFile: n }) => {
	let r = O(t(), n);
	return /* @__PURE__ */ _.jsxs(_.Fragment, { children: [/* @__PURE__ */ _.jsx(Ae, {
		...e(),
		children: /* @__PURE__ */ _.jsx("input", { ...r })
	}), /* @__PURE__ */ _.jsx(A, { children: `Drag and drop ${k(n)} here` })] });
}), M = (e, t, n) => {
	let r = [], i = [];
	return e.forEach((e) => {
		if (e.size > n) {
			i.push({
				file: e,
				errors: [{
					code: x.FileTooLarge,
					message: `File is too large. Maximum size is ${n} bytes.`
				}]
			});
			return;
		}
		let a = ke(e, t.fileType);
		if (!a.isValid) {
			i.push({
				file: e,
				errors: [{
					code: x.FileInvalidType,
					message: a.errorMessage || "File type not allowed."
				}]
			});
			return;
		}
		r.push(e);
	}), {
		accepted: r,
		rejected: i
	};
}, Ne = ({ acceptMultipleFiles: e, maxFileSize: n, uploadClient: r, uploadFile: i, addFiles: a, getNextLocalFileId: o, deleteExistingFiles: s, onUploadComplete: c, element: l }) => (u, d) => {
	if (u.length > 0) {
		let { accepted: e, rejected: t } = M(u, l, n);
		u = e, d = [...d, ...t];
	}
	if (!e && u.length === 0 && d.length > 1) {
		let e = d.findIndex((e) => e.errors?.[0].code === x.TooManyFiles);
		e >= 0 && (u.push(d[e].file), d.splice(e, 1));
	}
	!e && u.length > 0 && s(), r.fetchFileURLs(u).then((e) => {
		t(e, u).forEach(([e, t]) => {
			i(e, t);
		});
	}).catch((e) => {
		a(u.map((t) => new v(t.name, t.size, o(), {
			type: "error",
			errorMessage: e
		}, t)));
	}), d.length > 0 && a(d.map((e) => se(e, o(), n))), c();
}, Pe = ({ getNextLocalFileId: e, addFiles: t, updateFile: n, uploadClient: r, element: i, onUploadProgress: a, onUploadComplete: o }) => (s, c) => {
	let l = c.webkitRelativePath || c.name, u = new AbortController(), d = new v(l, c.size, e(), {
		type: "uploading",
		abortController: u,
		progress: 1
	}, c);
	t([d]), r.uploadFile({
		formId: "",
		...i
	}, s.uploadUrl, c, (e) => a(e, d.id), u.signal).then(() => o(d.id, s)).catch((e) => {
		e instanceof DOMException && e.name === "AbortError" || n(d.id, d.setStatus({
			type: "error",
			errorMessage: e ? e.toString() : "Unknown error"
		}));
	});
};
function Fe(e, t, n, r, i) {
	return {
		Root: { style: {
			minHeight: r ?? e.sizes.chatInputTextareaMinHeight,
			outline: "none",
			borderLeftWidth: "0",
			borderRightWidth: "0",
			borderTopWidth: "0",
			borderBottomWidth: "0",
			borderTopLeftRadius: "0",
			borderTopRightRadius: "0",
			borderBottomRightRadius: "0",
			borderBottomLeftRadius: "0",
			...n
		} },
		Input: {
			props: { "data-testid": "stChatInputTextArea" },
			style: {
				fontWeight: e.fontWeights.normal,
				lineHeight: e.lineHeights.inputWidget,
				"::placeholder": { color: e.colors.fadedText60 },
				height: i ? "100%" : t.isExtended ? t.height : "auto",
				maxHeight: i ? "none" : t.maxHeight,
				overflowY: "auto",
				paddingLeft: e.spacing.none,
				paddingRight: e.spacing.none,
				paddingBottom: e.spacing.twoXS,
				paddingTop: e.spacing.twoXS,
				width: "100%"
			}
		}
	};
}
var Ie = (e, t, n) => n.map((n) => n.id === e ? t : n), Le = (e, t) => t.find((t) => t.id === e);
function N({ disabled: e, element: t, widgetMgr: a, fragmentId: s, uploadClient: d, heightConfig: f }) {
	let m = ne(), { placeholder: g, maxChars: v } = t, se = (0, S.useRef)(0), y = (0, S.useRef)(null), b = (0, S.useRef)(!1), x = (0, S.useRef)(null), w = (0, S.useRef)(null), { width: O, elementRef: ke } = ee(), { innerWidth: k, innerHeight: Ae } = r(), [A, j] = (0, S.useState)(t.default), [M, N] = (0, S.useState)([]), [P, Re] = (0, S.useState)(!1), [F, ze] = (0, S.useState)(!1), [I, L] = (0, S.useState)(null), [R, Be] = (0, S.useState)(!1), [Ve, He] = (0, S.useState)(0), z = t.acceptAudio ?? !1;
	(0, S.useEffect)(() => () => {
		w.current && w.current.abort();
	}, []);
	let Ue = (0, S.useRef)(!1), B = fe({
		textareaRef: y,
		dependencies: [g, R]
	}), { updateScrollHeight: We } = B;
	(0, S.useLayoutEffect)(() => {
		O > 0 && !Ue.current && (Ue.current = !0, We());
	}, [O, We]);
	let V = (0, S.useRef)(""), H = (0, S.useRef)(0), Ge = (0, S.useRef)(null), Ke = (0, S.useRef)(null), U = (0, S.useCallback)((e) => {
		let t = getComputedStyle(e);
		V.current = `${t.fontWeight} ${t.fontSize} ${t.fontFamily}`;
		let n = parseFloat(t.paddingLeft) || 0, r = parseFloat(t.paddingRight) || 0;
		H.current = e.clientWidth - n - r;
	}, []);
	(0, S.useLayoutEffect)(() => {
		let e = y.current;
		if (!e) return;
		U(e);
		let t = new ResizeObserver(() => U(e));
		return t.observe(e), () => t.disconnect();
	}, [U, R]), (0, S.useEffect)(() => {
		if (A === "") {
			Be(!1);
			return;
		}
		if (R) return;
		let e = y.current;
		if (!e || ((H.current <= 0 || !V.current) && U(e), H.current <= 0 || !V.current)) return;
		Ge.current || (Ge.current = document.createElement("canvas"), Ke.current = Ge.current.getContext("2d"));
		let t = Ke.current;
		t && (t.font = V.current, t.measureText(A).width > H.current - 10 && Be(!0));
	}, [
		A,
		R,
		U
	]);
	let W = (0, S.useMemo)(() => M.some((e) => e.status.type === "uploading") ? !1 : A !== "" || M.length > 0, [M, A]), G = te(t.acceptFile), K = ae(t.maxUploadSizeMb, le.Megabyte, le.Byte), qe = (0, S.useCallback)((e) => N((t) => [...t, ...e]), []), Je = (0, S.useCallback)((e) => {
		e.status.type === "uploading" && e.status.abortController.abort(), e.status.type === "uploaded" && e.status.fileUrls.deleteUrl && d.deleteFile(e.status.fileUrls.deleteUrl).catch((e) => {
			E.error("Failed to delete file from server:", e);
		});
	}, [d]), Ye = (0, S.useCallback)((e) => {
		N((t) => {
			let n = Le(e, t);
			if (p(n)) return t;
			Je(n);
			let r = t.filter((t) => t.id !== e);
			return r.length === 0 && He((e) => e + 1), r;
		});
	}, [Je]), Xe = (0, S.useRef)(null), Ze = (0, S.useCallback)((e) => {
		!e.file || e.status.type !== "error" || (N((t) => t.filter((t) => t.id !== e.id)), Xe.current && Xe.current([e.file], []));
	}, []), Qe = (0, S.useCallback)(() => new i({ uploadedFileInfo: M.filter((e) => e.status.type === "uploaded").map((e) => {
		let { name: t, size: n, status: r } = e, { fileId: i, fileUrls: a } = r;
		return new c({
			fileId: i,
			fileUrls: a,
			name: t,
			size: n
		});
	}) }), [M]), $e = () => se.current++, q = Ne({
		acceptMultipleFiles: G === h.Multiple || G === h.Directory,
		maxFileSize: K,
		uploadClient: d,
		uploadFile: Pe({
			getNextLocalFileId: $e,
			addFiles: qe,
			updateFile: (e, t) => {
				N((n) => Ie(e, t, n));
			},
			uploadClient: d,
			element: t,
			onUploadProgress: (e, t) => {
				N((n) => {
					let r = Le(t, n);
					if (p(r) || r.status.type !== "uploading") return n;
					let i = e.total ? Math.round(e.loaded * 100 / e.total) : 0;
					return r.status.progress === i ? n : Ie(t, r.setStatus({
						type: "uploading",
						abortController: r.status.abortController,
						progress: i
					}), n);
				});
			},
			onUploadComplete: (e, t) => {
				N((n) => {
					let r = Le(e, n);
					return p(r) || r.status.type !== "uploading" ? n : Ie(r.id, r.setStatus({
						type: "uploaded",
						fileId: t.fileId,
						fileUrls: t
					}), n);
				});
			}
		}),
		addFiles: qe,
		getNextLocalFileId: $e,
		deleteExistingFiles: () => M.forEach((e) => Ye(e.id)),
		onUploadComplete: () => {
			y.current && y.current.focus();
		},
		element: t
	});
	Xe.current = q;
	let { getRootProps: et, getInputProps: tt } = oe({
		onDrop: q,
		multiple: G === h.Multiple || G === h.Directory,
		accept: ce(t.fileType),
		maxSize: K,
		useFsAccessApi: !1
	}), J = (0, S.useCallback)((n) => {
		if (y.current && y.current.focus(), !W && !n || e) return;
		let r = {
			data: A,
			fileUploaderState: Qe(),
			audioFileInfo: n
		};
		a.setChatInputValue(t, r, { fromUi: !0 }, s), M.length > 0 && He((e) => e + 1), N([]), j(""), Be(!1), B.clearScrollHeight();
	}, [
		W,
		e,
		A,
		M.length,
		Qe,
		a,
		t,
		s,
		B
	]), nt = (0, S.useCallback)(async (e) => {
		let n = (/* @__PURE__ */ new Date()).toISOString().replace(/[:.]/g, "-"), r = new File([e], `audio-${n}.wav`, { type: "audio/wav" });
		try {
			ze(!0);
			let e = await d.fetchFileURLs([r]);
			if (e.length === 0) throw Error("Failed to get upload URL for audio file");
			let n = e[0];
			w.current = new AbortController(), await d.uploadFile({
				formId: "",
				...t
			}, n.uploadUrl, r, () => {}, w.current.signal), J(new c({
				fileId: n.fileId,
				fileUrls: n,
				name: r.name,
				size: r.size
			}));
		} catch (e) {
			E.error("Audio upload failed:", e), L("Recording failed"), y.current && y.current.focus();
		} finally {
			ze(!1);
		}
	}, [
		d,
		t,
		J
	]), rt = (0, S.useMemo)(() => ({
		onApprove: nt,
		onPermissionDenied: () => {
			let e = "Microphone access denied";
			L(e), E.error("Permission denied:", e);
		},
		onError: (e) => {
			L("Recording failed"), E.error("Recording error:", e);
		},
		onRecordStart: () => {
			L(null);
		}
	}), [nt]), Y = ie({
		containerRef: x,
		sampleRate: t.audioSampleRate ?? void 0,
		events: rt
	}), it = (0, S.useCallback)(() => {
		J();
	}, [J]), at = (e) => {
		let { metaKey: t, ctrlKey: n, shiftKey: r } = e;
		me(e) && !r && !n && !t && (e.preventDefault(), it());
	}, ot = (e) => {
		let { value: t } = e.target;
		v !== 0 && t.length > v || (j(t), We(), I && L(null));
	}, st = (0, S.useCallback)(async (t) => {
		t.preventDefault(), t.stopPropagation(), !(!z || e || Y.state === "recording") && await Y.start();
	}, [
		z,
		e,
		Y
	]), ct = (0, S.useCallback)(() => {
		Y.cancel(), y.current && y.current.focus();
	}, [Y]), lt = (0, S.useCallback)(async () => {
		let { blob: e } = await Y.stop();
		await Y.approve(e);
	}, [Y]), X = (0, S.useCallback)((e) => {
		st(e);
	}, [st]), ut = (0, S.useCallback)(() => {
		lt();
	}, [lt]), dt = (0, S.useCallback)(() => {
		y.current && y.current.focus();
	}, []);
	(0, S.useEffect)(() => {
		t.setValue && !b.current && (b.current = !0, j(t.value || ""));
	}, [t.setValue, t.value]), (0, S.useEffect)(() => {
		b.current = !1;
	}, [t]), (0, S.useEffect)(() => {
		let e = (e) => {
			e.preventDefault(), e.stopPropagation(), !P && e.dataTransfer?.types.includes("Files") && Re(!0);
		}, t = (e) => {
			e.preventDefault(), e.stopPropagation(), P && (e.clientX <= 0 && e.clientY <= 0 || e.clientX >= k && e.clientY >= Ae) && Re(!1);
		}, n = (e) => {
			e.preventDefault(), e.stopPropagation(), P && Re(!1);
		};
		return window.addEventListener("dragover", e), window.addEventListener("drop", n), window.addEventListener("dragleave", t), () => {
			window.removeEventListener("dragover", e), window.removeEventListener("drop", n), window.removeEventListener("dragleave", t);
		};
	}, [
		P,
		k,
		Ae
	]);
	let ft = G !== h.None && P, Z = Y.state === "recording", pt = !Z && O > n(m.breakpoints.hideWidgetDetails) && v > 0, mt = (0, S.useMemo)(() => {
		if (!(!f || f.useContent)) {
			if (f.useStretch) return "100%";
			if (f.pixelHeight && f.pixelHeight > 0) {
				let e = parseInt(m.sizes.borderWidth, 10) || 1, t = n(m.spacing.md) * 2 + e * 2;
				return `${Math.max(0, f.pixelHeight - t)}px`;
			}
		}
	}, [
		f,
		m.sizes.borderWidth,
		m.spacing.md
	]), Q = f?.useStretch ?? !1, ht = Q || (f?.pixelHeight ?? 0) > 0, $ = ht || B.isExtended;
	return /* @__PURE__ */ _.jsx(ve, {
		className: "stChatInput",
		"data-testid": "stChatInput",
		ref: ke,
		isStretchHeight: Q,
		children: /* @__PURE__ */ _.jsxs(ye, {
			isStretchHeight: Q,
			children: [
				ft && /* @__PURE__ */ _.jsx(Me, {
					getRootProps: et,
					getInputProps: tt,
					acceptFile: G
				}),
				G !== h.None && M.length > 0 && /* @__PURE__ */ _.jsx(be, { children: /* @__PURE__ */ _.jsx(ue, {
					items: [...M],
					onDelete: Ye,
					onRetry: Ze
				}) }),
				/* @__PURE__ */ _.jsxs(xe, {
					isStacked: R,
					hasExpandedHeight: $ && !Z,
					children: [!Z && /* @__PURE__ */ _.jsx(Se, {
						isStacked: R,
						hasExpandedHeight: $,
						children: /* @__PURE__ */ _.jsx(pe, {
							inputRef: y,
							value: A,
							placeholder: g,
							onChange: ot,
							onKeyDown: at,
							"aria-label": g,
							disabled: e,
							rows: 1,
							"aria-describedby": pt ? "stChatInputInstructions" : void 0,
							overrides: Fe(m, B, {
								width: "100%",
								...$ ? { flex: 1 } : {}
							}, mt, ht)
						})
					}), $ && !Z ? /* @__PURE__ */ _.jsxs(Te, { children: [/* @__PURE__ */ _.jsx(Ce, {
						hasExpandedHeight: !0,
						children: G !== h.None && /* @__PURE__ */ _.jsx(je, {
							onDrop: q,
							multiple: G === h.Multiple || G === h.Directory,
							accept: ce(t.fileType),
							maxSize: K,
							acceptFile: G,
							disabled: e,
							fileTypes: t.fileType
						}, Ve)
					}), /* @__PURE__ */ _.jsxs(we, { children: [
						pt && /* @__PURE__ */ _.jsx(Ee, {
							onClick: dt,
							id: "stChatInputInstructions",
							children: /* @__PURE__ */ _.jsx(de, {
								dirty: W,
								value: A,
								maxLength: v,
								type: "chat",
								inForm: !1,
								className: "stChatInputInstructions"
							})
						}),
						z && /* @__PURE__ */ _.jsx(_.Fragment, { children: I ? /* @__PURE__ */ _.jsx(u, {
							content: I,
							placement: o.TOP,
							error: !0,
							children: /* @__PURE__ */ _.jsx(D, {
								onClick: X,
								disabled: e || F,
								hasError: !0,
								"data-testid": "stChatInputMicButton",
								"aria-label": "Start recording",
								children: /* @__PURE__ */ _.jsx(l, {
									content: _e,
									size: "xl",
									color: "inherit"
								})
							})
						}) : /* @__PURE__ */ _.jsx(D, {
							onClick: X,
							disabled: e || F,
							"data-testid": "stChatInputMicButton",
							"aria-label": "Start recording",
							children: /* @__PURE__ */ _.jsx(l, {
								content: C,
								size: "xl",
								color: "inherit"
							})
						}) }),
						/* @__PURE__ */ _.jsx(D, {
							onClick: it,
							disabled: !W || e || F,
							"data-testid": "stChatInputSubmitButton",
							"aria-label": "Send message",
							primary: !0,
							children: /* @__PURE__ */ _.jsx(l, {
								content: T,
								size: "lg",
								color: "inherit"
							})
						})
					] })] }) : /* @__PURE__ */ _.jsxs(_.Fragment, { children: [
						/* @__PURE__ */ _.jsx(Ce, {
							hasExpandedHeight: !1,
							children: G !== h.None && !Z && /* @__PURE__ */ _.jsx(je, {
								onDrop: q,
								multiple: G === h.Multiple || G === h.Directory,
								accept: ce(t.fileType),
								maxSize: K,
								acceptFile: G,
								disabled: e,
								fileTypes: t.fileType
							}, Ve)
						}),
						/* @__PURE__ */ _.jsx(De, {
							isRecording: Z,
							children: /* @__PURE__ */ _.jsx(Oe, { ref: x })
						}),
						/* @__PURE__ */ _.jsx(we, { children: Z ? /* @__PURE__ */ _.jsxs(_.Fragment, { children: [/* @__PURE__ */ _.jsx(D, {
							onClick: ct,
							disabled: e,
							"data-testid": "stChatInputCancelButton",
							"aria-label": "Cancel recording",
							children: /* @__PURE__ */ _.jsx(l, {
								content: ge,
								size: "lg",
								color: "inherit"
							})
						}), /* @__PURE__ */ _.jsx(D, {
							onClick: ut,
							disabled: e || F,
							"data-testid": "stChatInputApproveButton",
							"aria-label": "Submit recording",
							children: F ? /* @__PURE__ */ _.jsx(re, {
								size: "lg",
								iconValue: "spinner"
							}) : /* @__PURE__ */ _.jsx(l, {
								content: he,
								size: "lg",
								color: "inherit"
							})
						})] }) : /* @__PURE__ */ _.jsxs(_.Fragment, { children: [
							pt && /* @__PURE__ */ _.jsx(Ee, {
								onClick: dt,
								id: "stChatInputInstructions",
								children: /* @__PURE__ */ _.jsx(de, {
									dirty: W,
									value: A,
									maxLength: v,
									type: "chat",
									inForm: !1,
									className: "stChatInputInstructions"
								})
							}),
							z && /* @__PURE__ */ _.jsx(_.Fragment, { children: I ? /* @__PURE__ */ _.jsx(u, {
								content: I,
								placement: o.TOP,
								error: !0,
								children: /* @__PURE__ */ _.jsx(D, {
									onClick: X,
									disabled: e || F,
									hasError: !0,
									"data-testid": "stChatInputMicButton",
									"aria-label": "Start recording",
									children: /* @__PURE__ */ _.jsx(l, {
										content: _e,
										size: "xl",
										color: "inherit"
									})
								})
							}) : /* @__PURE__ */ _.jsx(D, {
								onClick: X,
								disabled: e || F,
								"data-testid": "stChatInputMicButton",
								"aria-label": "Start recording",
								children: /* @__PURE__ */ _.jsx(l, {
									content: C,
									size: "xl",
									color: "inherit"
								})
							}) }),
							/* @__PURE__ */ _.jsx(D, {
								onClick: it,
								disabled: !W || e || F,
								"data-testid": "stChatInputSubmitButton",
								"aria-label": "Send message",
								primary: !0,
								children: /* @__PURE__ */ _.jsx(l, {
									content: T,
									size: "lg",
									color: "inherit"
								})
							})
						] }) })
					] })]
				})
			]
		})
	});
}
var P = (0, S.memo)(N);
//#endregion
export { P as default };

//# sourceMappingURL=ChatInput-CFv2o38z-F4o1gJcf.js.map