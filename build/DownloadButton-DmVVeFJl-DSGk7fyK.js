import { Ka as e, Ua as t, _a as n, a as r, b as i, ba as a, c as o, o as s, s as c, ti as l, vt as u, wa as d, y as f, z as p } from "./index-Dl4ETd_L-D2oMd1k2.js";
import { t as m } from "./createDownloadLinkElement-CnWgptKS-D3FE3dhN.js";
import { t as h } from "./iconPosition-Cpqwt3HE-C-jUvRPi.js";
//#region ../react/build/DownloadButton-DmVVeFJl.js
var g = /* @__PURE__ */ e(t(), 1), _ = /%([0-9A-Fa-f]{2})/g, v = /[^\x20-\x7e\xa0-\xff]/g, y = /\\([\u0000-\u007f])/g, b = /;[\x09\x20]*([!#$%&'*+.0-9A-Z^_`a-z|~-]+)[\x09\x20]*=[\x09\x20]*("(?:[\x20!\x23-\x5b\x5d-\x7e\x80-\xff]|\\[\x20-\x7e])*"|[!#$%&'*+.0-9A-Z^_`a-z|~-]+)[\x09\x20]*/g, x = /^([A-Za-z0-9!#$%&+\-^_`{}~]+)'(?:[A-Za-z]{2,3}(?:-[A-Za-z]{3}){0,3}|[A-Za-z]{4,8}|)'((?:%[0-9A-Fa-f]{2}|[A-Za-z0-9!#$&+.^_`|~-])+)$/, S = /^([!#$%&'*+.0-9A-Z^_`a-z|~-]+)[\x09\x20]*(?:$|;)/, C = (e) => String(e).replace(v, "?"), w = class {
	constructor(e, t) {
		this.type = e, this.parameters = t;
	}
}, T = (e, t) => String.fromCharCode(Number.parseInt(t, 16));
function E(e) {
	let t = x.exec(e);
	if (!t) throw TypeError("invalid extended field value");
	let n = t[1].toLowerCase(), r = t[2], i;
	switch (n) {
		case "iso-8859-1":
			i = C(r.replace(_, T));
			break;
		case "utf-8":
			try {
				i = decodeURIComponent(r);
			} catch {
				throw TypeError("invalid encoded utf-8");
			}
			break;
		default: throw TypeError("unsupported charset in extended field");
	}
	return i;
}
function D(e) {
	let t = S.exec(e);
	if (!t) throw TypeError("invalid type format");
	let n = t[0].length, r = t[1].toLowerCase(), i, a = [], o = {}, s;
	for (n = b.lastIndex = t[0].slice(-1) === ";" ? n - 1 : n; t = b.exec(e);) {
		if (t.index !== n) throw TypeError("invalid parameter format");
		if (n += t[0].length, i = t[1].toLowerCase(), s = t[2], a.indexOf(i) !== -1) throw TypeError("invalid duplicate parameter");
		if (a.push(i), i.indexOf("*") + 1 === i.length) {
			i = i.slice(0, -1), s = E(s), o[i] = s;
			continue;
		}
		typeof o[i] != "string" && (s[0] === "\"" && (s = s.slice(1, s.length - 1).replace(y, "$1")), o[i] = s);
	}
	if (n !== -1 && n !== e.length) throw TypeError("invalid parameter format");
	return new w(r, o);
}
function O(e) {
	let t = D(e);
	if (t.type !== "attachment") return;
	let n = t.parameters.filename;
	if (typeof n == "string") return n;
}
function k(e, t) {
	return e.sendHttpRequest({
		method: "GET",
		path: `${t}?title=${encodeURIComponent(document.title)}`,
		headers: {},
		body: ""
	}).then(({ statusCode: e, headers: t, body: n }) => {
		if (e !== 200) return;
		let r = t.get("Content-Disposition"), i = (r && O(r)) ?? "", a = t.get("Content-Type"), o = new Blob([n], a ? { type: a } : void 0), s = URL.createObjectURL(o), c = document.createElement("a");
		c.setAttribute("href", s), c.setAttribute("target", "_blank"), c.setAttribute("download", i), c.click(), URL.revokeObjectURL(s), c.remove();
	});
}
function A() {
	let e = a();
	return (0, g.useCallback)((t) => k(e, t), [e]);
}
function j(e) {
	let { disabled: t, element: a, widgetMgr: _, endpoints: v, fragmentId: y } = e, { help: b, label: x, icon: S, ignoreRerun: C, type: w, url: T, deferredFileId: E } = a, D = a.shortcut ? a.shortcut : void 0, [O, k] = (0, g.useState)(!1), [j, M] = (0, g.useState)(null), { enforceDownloadInNewTab: N = !1 } = (0, g.useContext)(p), { requestDeferredFile: P } = (0, g.useContext)(f), F = s.SECONDARY;
	w === "primary" ? F = s.PRIMARY : w === "tertiary" && (F = s.TERTIARY);
	let I = (0, g.useMemo)(() => v.buildDownloadUrl(T), [v, T]);
	(0, g.useEffect)(() => {
		E?.length || v.checkSourceUrlResponse(I, "Download Button");
	}, [
		I,
		v,
		E
	]);
	let L = (0, g.useCallback)(async () => {
		if (!P || !E) {
			M("Deferred download not properly configured");
			return;
		}
		k(!0), M(null);
		try {
			let e = await P(E);
			if (e.errorMsg) {
				M(e.errorMsg), k(!1);
				return;
			}
			let t = v.buildDownloadUrl(e.url);
			v.checkSourceUrlResponse(t, "Download Button"), m({
				filename: "",
				url: t,
				enforceDownloadInNewTab: N
			}).click();
		} catch (e) {
			M(e instanceof Error ? e.message : "Download failed");
		} finally {
			k(!1);
		}
	}, [
		P,
		E,
		v,
		N
	]), R = A(), z = (0, g.useCallback)(() => {
		if (!t) {
			if (C || _.setTriggerValue(a, { fromUi: !0 }, y), a.url.startsWith("/media")) {
				R(a.url);
				return;
			}
			E?.length ? L() : m({
				filename: "",
				url: I,
				enforceDownloadInNewTab: N
			}).click();
		}
	}, [
		t,
		C,
		_,
		a,
		y,
		E,
		L,
		I,
		N,
		R
	]);
	n({
		shortcut: D,
		disabled: t,
		onActivate: z
	});
	let { clear: B, restart: V } = d(() => {
		M(null);
	}, 5e3, { autoStart: !1 });
	return (0, g.useEffect)(() => {
		j ? V() : B();
	}, [
		B,
		j,
		V
	]), /* @__PURE__ */ l.jsxs("div", {
		className: "stDownloadButton",
		"data-testid": "stDownloadButton",
		children: [/* @__PURE__ */ l.jsx(o, {
			help: b,
			containerWidth: !0,
			children: /* @__PURE__ */ l.jsx(r, {
				kind: F,
				size: c.SMALL,
				disabled: t || O,
				onClick: z,
				containerWidth: !0,
				children: /* @__PURE__ */ l.jsx(i, {
					icon: O ? "spinner" : S,
					iconPosition: h(a.iconPosition),
					label: x,
					shortcut: D
				})
			})
		}), j && /* @__PURE__ */ l.jsx(u, {
			"data-testid": "stDownloadButtonError",
			children: j
		})]
	});
}
var M = (0, g.memo)(j);
//#endregion
export { M as default };

//# sourceMappingURL=DownloadButton-DmVVeFJl-DSGk7fyK.js.map