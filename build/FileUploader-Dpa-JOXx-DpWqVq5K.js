import { Ba as e, Cn as t, E as n, En as r, Ha as i, Ka as a, Lt as o, Ua as s, Ur as c, a as l, b as u, da as d, ga as f, ii as p, kr as m, o as h, s as g, ti as _ } from "./index-Dl4ETd_L-D2oMd1k2.js";
import { t as v } from "./WidgetLabel-CQfHGtry-udktvHE5.js";
import { t as ee } from "./WidgetLabelHelpIcon-C6IRqJ_I-BBI6AbZ-.js";
import { t as y } from "./UploadFileInfo-DdcsXhjv-C0F82PE-.js";
import { a as b, d as x, f as S, h as C, i as w, l as T, m as E, n as D, o as O, p as te, s as k, t as A, u as j } from "./utils-CotIDfd1-hvXXk-4A.js";
//#region ../react/build/FileUploader-Dpa-JOXx.js
var M = /* @__PURE__ */ a(s(), 1), N = /* @__PURE__ */ a(i(), 1), P = /* @__PURE__ */ r("section", { target: "e1b2p2ww8" })(({ isDisabled: e, isDragActive: t, theme: n }) => ({
	position: "relative",
	display: "flex",
	gap: n.spacing.lg,
	alignItems: "flex-start",
	padding: n.spacing.md,
	backgroundColor: n.colors.secondaryBg,
	borderRadius: n.radii.default,
	border: n.colors.widgetBorderColor ? `${n.sizes.borderWidth} solid ${n.colors.widgetBorderColor}` : void 0,
	height: "auto",
	minHeight: n.sizes.largestElementHeight,
	":focus": { outline: "none" },
	":focus-visible": { boxShadow: n.shadows.focusRingOutline },
	cursor: e ? "not-allowed" : "pointer",
	...t && { boxShadow: `inset 0 0 0 2px ${n.colors.primary}` }
}), ""), F = /* @__PURE__ */ r("div", { target: "e1b2p2ww7" })(({ theme: e }) => ({
	position: "absolute",
	top: e.spacing.threeXS,
	right: e.spacing.threeXS,
	bottom: e.spacing.threeXS,
	left: e.spacing.threeXS,
	display: "flex",
	alignItems: "center",
	justifyContent: "center",
	backgroundColor: e.colors.secondaryBg,
	borderRadius: e.radii.default,
	zIndex: e.zIndices.priority
}), ""), I = /* @__PURE__ */ r("span", { target: "e1b2p2ww6" })(({ theme: e }) => ({
	color: e.colors.primary,
	fontSize: e.fontSizes.sm,
	fontWeight: e.fontWeights.extrabold
}), ""), L = /* @__PURE__ */ r("div", { target: "e1b2p2ww5" })({
	name: "1xfl00o",
	styles: "display:flex;align-items:center;justify-content:flex-start;text-align:left;align-self:center;min-width:0;flex:1"
}), R = /* @__PURE__ */ r("span", { target: "e1b2p2ww4" })(({ theme: e, disabled: t }) => ({
	fontSize: e.fontSizes.sm,
	color: t ? e.colors.fadedText40 : e.colors.fadedText60,
	display: "block",
	overflow: "hidden",
	textOverflow: "ellipsis",
	whiteSpace: "nowrap"
}), ""), z = /* @__PURE__ */ r("div", { target: "e1b2p2ww3" })({
	name: "1s8jot1",
	styles: "display:flex;flex-direction:column;min-width:0;max-width:100%"
}), B = /* @__PURE__ */ r("span", { target: "e1b2p2ww2" })({
	name: "1bmnxg7",
	styles: "white-space:nowrap"
}), V = /* @__PURE__ */ r("div", { target: "e1b2p2ww1" })(({ theme: e }) => ({ lineHeight: e.lineHeights.tight }), ""), H = 2.5, U = .5;
function W(e) {
	let t = Math.floor(e), n = e - t;
	return `${t * H + Math.max(0, t - 1) * U + (n > 0 ? U + n * H : 0)}rem`;
}
var G = () => ({ [S]: {
	maxHeight: W(2.25),
	overflowY: "auto"
} }), K = (e) => ({
	[P]: {
		flexDirection: "column",
		alignItems: "stretch",
		height: "fit-content",
		gap: e.spacing.md
	},
	[L]: { alignSelf: "stretch" },
	[S]: {
		flexDirection: "column",
		flexWrap: "nowrap",
		alignItems: "flex-start",
		maxHeight: "none",
		overflowY: "visible",
		gap: e.spacing.sm
	},
	[E]: {
		display: "flex",
		flexDirection: "column",
		flexWrap: "nowrap",
		alignItems: "flex-start",
		gap: e.spacing.sm,
		maxHeight: W(5.25),
		overflowY: "auto",
		width: e.sizes.full
	},
	[T]: { width: e.sizes.full },
	[j]: { width: e.sizes.full }
}), q = /* @__PURE__ */ r("div", { target: "e1b2p2ww0" })(({ theme: e, width: n }) => ({
	...G(),
	...n < t("23rem") ? K(e) : {}
}), ""), J = (0, M.memo)(({ acceptedTypes: e, maxSizeBytes: t, disabled: n }) => /* @__PURE__ */ _.jsx(L, {
	"data-testid": "stFileUploaderDropzoneInstructions",
	children: /* @__PURE__ */ _.jsx(z, { children: /* @__PURE__ */ _.jsxs(R, {
		disabled: n,
		children: [`${x(t, k.Byte, 0)} per file`, e.length ? ` • ${O(e)}` : null]
	}) })
})), Y = (0, M.memo)(({ onDrop: e, multiple: t, acceptedTypes: n, maxSizeBytes: r, disabled: i, label: a, acceptDirectory: o = !1, uploadedFiles: s, hasFiles: c = !1 }) => /* @__PURE__ */ _.jsx(C, {
	onDrop: e,
	multiple: t,
	accept: D(n),
	maxSize: r,
	disabled: i,
	useFsAccessApi: !1,
	children: ({ getRootProps: e, getInputProps: d, isDragActive: f }) => {
		let p = d({ multiple: t || !!o });
		return /* @__PURE__ */ _.jsxs(P, {
			...e(),
			"data-testid": "stFileUploaderDropzone",
			isDisabled: i,
			isDragActive: f,
			"aria-label": a,
			"aria-disabled": i,
			children: [
				/* @__PURE__ */ _.jsx("input", {
					"data-testid": "stFileUploaderDropzoneInput",
					...p,
					...o && { webkitdirectory: "" }
				}),
				f && /* @__PURE__ */ _.jsx(F, { children: /* @__PURE__ */ _.jsx(I, { children: o ? "Drag and drop directories here" : t ? "Drag and drop files here" : "Drag and drop a file here" }) }),
				c && s ? s : /* @__PURE__ */ _.jsxs(_.Fragment, { children: [/* @__PURE__ */ _.jsx(B, { children: /* @__PURE__ */ _.jsx(l, {
					kind: h.SECONDARY,
					disabled: i,
					size: g.MEDIUM,
					children: /* @__PURE__ */ _.jsx(u, {
						icon: ":material/upload:",
						label: o ? "Upload directories" : "Upload"
					})
				}) }), /* @__PURE__ */ _.jsx(J, {
					acceptedTypes: n,
					maxSizeBytes: r,
					disabled: i
				})] })
			]
		});
	}
})), X = (0, M.memo)(({ items: e, onDelete: t, disabled: n, trailingContent: r }) => /* @__PURE__ */ _.jsx(V, { children: /* @__PURE__ */ _.jsx(A, {
	items: e,
	onDelete: t,
	disabled: n,
	trailingContent: r
}) })), Z = (e, t) => {
	let n = t.getFileUploaderStateValue(e);
	if (c(n)) return {
		files: [],
		nextLocalId: 1
	};
	let { uploadedFileInfo: r } = n;
	if (c(r) || r.length === 0) return {
		files: [],
		nextLocalId: 1
	};
	let i = 1;
	return {
		files: r.map((e) => {
			let t = e.name, n = e.size, r = e.fileId, a = e.fileUrls, o = new y(t, n, i, {
				type: "uploaded",
				fileId: r,
				fileUrls: a
			});
			return i += 1, o;
		}),
		nextLocalId: i
	};
}, Q = (e) => new n({ uploadedFileInfo: e.filter((e) => e.status.type === "uploaded").map((e) => {
	let { name: t, size: n, status: r } = e, { fileId: i, fileUrls: a } = r;
	return new o({
		fileId: i,
		fileUrls: a,
		name: t,
		size: n
	});
}) }), $ = (0, M.memo)(({ disabled: t, element: n, widgetMgr: r, uploadClient: i, fragmentId: a }) => {
	let { width: o, elementRef: s } = d(), { files: x, nextLocalId: S } = (0, M.useMemo)(() => Z(n, r), [n, r]), C = (0, M.useRef)(S), [T, E] = (0, M.useState)(() => x), D = (0, M.useRef)(T);
	(0, M.useEffect)(() => {
		D.current = T;
	}, [T]);
	let [O, A] = (0, M.useState)(!1), j = (0, M.useCallback)(() => {
		let e = C.current;
		return C.current += 1, e;
	}, []), P = (0, M.useMemo)(() => {
		let e = n.maxUploadSizeMb;
		return b(e, k.Megabyte, k.Byte);
	}, [n.maxUploadSizeMb]), F = (0, M.useCallback)((e) => {
		(0, N.flushSync)(() => {
			E((t) => {
				let n = typeof e == "function" ? e(t) : e;
				return D.current = n, n;
			});
		});
	}, []), I = (0, M.useCallback)((e) => {
		(0, N.flushSync)(() => {
			A(e);
		});
	}, [A]), L = (0, M.useCallback)((e) => {
		F((t) => [...t, e]);
	}, [F]), R = (0, M.useCallback)((e) => {
		e.length !== 0 && F((t) => [...t, ...e]);
	}, [F]), z = (0, M.useCallback)((e) => {
		F((t) => t.filter((t) => t.id !== e));
	}, [F]), B = (0, M.useCallback)((e, t) => {
		F((n) => n.map((n) => n.id === e ? t : n));
	}, [F]), V = (0, M.useCallback)((e) => D.current.find((t) => t.id === e), []), H = T.some((e) => e.status.type === "uploading") || O ? "updating" : "ready";
	(0, M.useEffect)(() => {
		r.getFileUploaderStateValue(n) === void 0 && r.setFileUploaderStateValue(n, Q(D.current), { fromUi: !1 }, a);
	}, [
		r,
		n,
		a
	]), (0, M.useEffect)(() => {
		if (H !== "ready") return;
		let e = Q(T);
		m(e, r.getFileUploaderStateValue(n)) || r.setFileUploaderStateValue(n, e, { fromUi: !0 }, a);
	}, [
		H,
		T,
		r,
		n,
		a
	]), f({
		element: n,
		widgetMgr: r,
		onFormCleared: (0, M.useCallback)(() => {
			F(() => []);
			let e = Q([]);
			r.setFileUploaderStateValue(n, e, { fromUi: !0 }, a);
		}, [
			n,
			a,
			F,
			r
		])
	});
	let U = n.type, W = (0, M.useCallback)((e) => {
		let t = [], n = [];
		return e.forEach((e) => {
			te(e, U) ? t.push(e) : n.push({
				file: e,
				errors: [{
					code: "file-invalid-type",
					message: `${e.type} files are not allowed.`
				}]
			});
		}), {
			accepted: t,
			rejected: n
		};
	}, [U]), G = (0, M.useCallback)((e, t) => {
		let n = V(e);
		c(n) || n.status.type !== "uploading" || B(n.id, n.setStatus({
			type: "uploaded",
			fileId: t.fileId,
			fileUrls: t
		}));
	}, [V, B]), K = (0, M.useCallback)((e, t) => {
		let r = new AbortController(), a = new y(t.webkitRelativePath || t.name, t.size, j(), {
			type: "uploading",
			abortController: r,
			progress: 0
		});
		L(a), i.uploadFile(n, e.uploadUrl, t, void 0, r.signal).then(() => G(a.id, e)).catch((e) => {
			e instanceof DOMException && e.name === "AbortError" || B(a.id, a.setStatus({
				type: "error",
				errorMessage: e ? e.toString() : "Unknown error"
			}));
		});
	}, [
		L,
		n,
		j,
		G,
		B,
		i
	]), J = (0, M.useCallback)((e) => {
		if (t) return;
		let n = V(e);
		c(n) || (n.status.type === "uploading" && n.status.abortController.abort(), n.status.type === "uploaded" && n.status.fileUrls.deleteUrl && i.deleteFile(n.status.fileUrls.deleteUrl), z(e));
	}, [
		t,
		V,
		z,
		i
	]), $ = (0, M.useCallback)((t, r) => {
		let { multipleFiles: a } = n, o = !!n.acceptDirectory, s = [...t], c = [...r];
		if (o && s.length > 0) {
			let { accepted: e, rejected: t } = W(s);
			s = e, c = [...c, ...t];
		}
		if (!a && s.length === 0 && c.length > 1) {
			let e = c.findIndex((e) => e.errors.length === 1 && e.errors[0].code === "too-many-files");
			e >= 0 && (s.push(c[e].file), c.splice(e, 1));
		}
		i.fetchFileURLs(s).then((t) => {
			if (!a && s.length > 0) {
				let e = D.current.find((e) => e.status.type !== "error");
				if (e) {
					I(!0);
					try {
						J(e.id);
					} finally {
						I(!1);
					}
				}
			}
			e(t, s).forEach(([e, t]) => {
				K(e, t);
			});
		}).catch((e) => {
			R(s.map((t) => new y(t.name, t.size, j(), {
				type: "error",
				errorMessage: e
			})));
		}), c.length > 0 && R(c.map((e) => w(e, j(), P)));
	}, [
		R,
		J,
		n,
		W,
		P,
		j,
		i,
		K,
		I
	]);
	return /* @__PURE__ */ _.jsxs(q, {
		className: "stFileUploader",
		"data-testid": "stFileUploader",
		width: o,
		ref: s,
		children: [/* @__PURE__ */ _.jsx(v, {
			label: n.label,
			disabled: t,
			labelVisibility: p(n.labelVisibility?.value),
			children: n.help && /* @__PURE__ */ _.jsx(ee, {
				content: n.help,
				label: n.label
			})
		}), /* @__PURE__ */ _.jsx(Y, {
			onDrop: $,
			multiple: n.multipleFiles,
			acceptedTypes: U,
			maxSizeBytes: P,
			label: n.label,
			disabled: t,
			acceptDirectory: !!n.acceptDirectory,
			hasFiles: T.length > 0,
			uploadedFiles: T.length > 0 ? /* @__PURE__ */ _.jsx(X, {
				items: T,
				onDelete: J,
				disabled: t,
				trailingContent: /* @__PURE__ */ _.jsx(l, {
					kind: h.BORDERLESS_ICON,
					disabled: t,
					size: g.XSMALL,
					"aria-label": "Add files",
					children: /* @__PURE__ */ _.jsx(u, { icon: ":material/add:" })
				})
			}) : null
		})]
	});
});
//#endregion
export { $ as default };

//# sourceMappingURL=FileUploader-Dpa-JOXx-DpWqVq5K.js.map