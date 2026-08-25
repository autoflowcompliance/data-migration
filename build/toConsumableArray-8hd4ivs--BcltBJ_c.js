import { Ka as e, S as t, Ua as n, Wt as r } from "./index-Dl4ETd_L-D2oMd1k2.js";
import { o as i, s as a } from "./possibleConstructorReturn-BHiKHPYz-Bnf-j7Fb.js";
//#region ../react/build/toConsumableArray-8hd4ivs-.js
var o = /* @__PURE__ */ e(n(), 1), s = /* @__PURE__ */ o.forwardRef(function(e, n) {
	return /* @__PURE__ */ o.createElement(t, r({
		iconAttrs: {
			fill: "currentColor",
			xmlns: "http://www.w3.org/2000/svg"
		},
		iconVerticalAlign: "middle",
		iconViewBox: "0 0 24 24"
	}, e, { ref: n }), /* @__PURE__ */ o.createElement("path", {
		fill: "none",
		d: "M0 0h24v24H0V0z"
	}), /* @__PURE__ */ o.createElement("path", { d: "M19 6.41L17.59 5 12 10.59 6.41 5 5 6.41 10.59 12 5 17.59 6.41 19 12 13.41 17.59 19 19 17.59 13.41 12 19 6.41z" }));
});
s.displayName = "Close";
function c(e) {
	if (Array.isArray(e)) return e;
}
function l(e, t) {
	var n = e == null ? null : typeof Symbol < "u" && e[Symbol.iterator] || e["@@iterator"];
	if (n != null) {
		var r, i, a, o, s = [], c = !0, l = !1;
		try {
			if (a = (n = n.call(e)).next, t === 0) {
				if (Object(n) !== n) return;
				c = !1;
			} else for (; !(c = (r = a.call(n)).done) && (s.push(r.value), s.length !== t); c = !0);
		} catch (e) {
			l = !0, i = e;
		} finally {
			try {
				if (!c && n.return != null && (o = n.return(), Object(o) !== o)) return;
			} finally {
				if (l) throw i;
			}
		}
		return s;
	}
}
function u() {
	throw TypeError("Invalid attempt to destructure non-iterable instance.\nIn order to be iterable, non-array objects must have a [Symbol.iterator]() method.");
}
function d(e, t) {
	return c(e) || l(e, t) || a(e, t) || u();
}
function f(e) {
	if (Array.isArray(e)) return i(e);
}
function p(e) {
	if (typeof Symbol < "u" && e[Symbol.iterator] != null || e["@@iterator"] != null) return Array.from(e);
}
function m() {
	throw TypeError("Invalid attempt to spread non-iterable instance.\nIn order to be iterable, non-array objects must have a [Symbol.iterator]() method.");
}
function h(e) {
	return f(e) || p(e) || a(e) || m();
}
//#endregion
export { s as n, h as r, d as t };

//# sourceMappingURL=toConsumableArray-8hd4ivs--BcltBJ_c.js.map