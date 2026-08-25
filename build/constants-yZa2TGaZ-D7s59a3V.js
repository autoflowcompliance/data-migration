import { Ca as e, Ka as t, M as n, Ua as r, di as i, ia as a } from "./index-Dl4ETd_L-D2oMd1k2.js";
//#region ../react/build/constants-yZa2TGaZ.js
var o = /* @__PURE__ */ t(r(), 1), s = [
	"title",
	"size",
	"color",
	"overrides"
];
function c() {
	return c = Object.assign ? Object.assign.bind() : function(e) {
		for (var t = 1; t < arguments.length; t++) {
			var n = arguments[t];
			for (var r in n) Object.prototype.hasOwnProperty.call(n, r) && (e[r] = n[r]);
		}
		return e;
	}, c.apply(this, arguments);
}
function l(e, t) {
	if (e == null) return {};
	var n = u(e, t), r, i;
	if (Object.getOwnPropertySymbols) {
		var a = Object.getOwnPropertySymbols(e);
		for (i = 0; i < a.length; i++) r = a[i], !(t.indexOf(r) >= 0) && Object.prototype.propertyIsEnumerable.call(e, r) && (n[r] = e[r]);
	}
	return n;
}
function u(e, t) {
	if (e == null) return {};
	var n = {}, r = Object.keys(e), i, a;
	for (a = 0; a < r.length; a++) i = r[a], !(t.indexOf(i) >= 0) && (n[i] = e[i]);
	return n;
}
function d(e, t) {
	return g(e) || h(e, t) || p(e, t) || f();
}
function f() {
	throw TypeError("Invalid attempt to destructure non-iterable instance.\nIn order to be iterable, non-array objects must have a [Symbol.iterator]() method.");
}
function p(e, t) {
	if (e) {
		if (typeof e == "string") return m(e, t);
		var n = Object.prototype.toString.call(e).slice(8, -1);
		if (n === "Object" && e.constructor && (n = e.constructor.name), n === "Map" || n === "Set") return Array.from(e);
		if (n === "Arguments" || /^(?:Ui|I)nt(?:8|16|32)(?:Clamped)?Array$/.test(n)) return m(e, t);
	}
}
function m(e, t) {
	(t == null || t > e.length) && (t = e.length);
	for (var n = 0, r = Array(t); n < t; n++) r[n] = e[n];
	return r;
}
function h(e, t) {
	var n = e == null ? null : typeof Symbol < "u" && e[Symbol.iterator] || e["@@iterator"];
	if (n != null) {
		var r = [], i = !0, a = !1, o, s;
		try {
			for (n = n.call(e); !(i = (o = n.next()).done) && (r.push(o.value), !(t && r.length === t)); i = !0);
		} catch (e) {
			a = !0, s = e;
		} finally {
			try {
				!i && n.return != null && n.return();
			} finally {
				if (a) throw s;
			}
		}
		return r;
	}
}
function g(e) {
	if (Array.isArray(e)) return e;
}
function _(t, r) {
	var u = d(e(), 2)[1], f = t.title, p = f === void 0 ? "Delete Alt" : f, m = t.size, h = t.color, g = t.overrides, _ = g === void 0 ? {} : g, v = l(t, s), y = i({ component: u.icons && u.icons.DeleteAlt ? u.icons.DeleteAlt : null }, _ && _.Svg ? a(_.Svg) : {});
	return /* @__PURE__ */ o.createElement(n, c({
		viewBox: "0 0 24 24",
		ref: r,
		title: p,
		size: m,
		color: h,
		overrides: { Svg: y }
	}, v), /* @__PURE__ */ o.createElement("path", {
		fillRule: "evenodd",
		clipRule: "evenodd",
		d: "M12 20C16.4183 20 20 16.4183 20 12C20 7.58173 16.4183 4 12 4C7.58173 4 4 7.58173 4 12C4 16.4183 7.58173 20 12 20ZM10.0303 8.96967C9.73743 8.67679 9.26257 8.67679 8.96967 8.96967C8.67676 9.26257 8.67676 9.73743 8.96967 10.0303L10.9393 12L8.96967 13.9697C8.67676 14.2626 8.67676 14.7374 8.96967 15.0303C9.26257 15.3232 9.73743 15.3232 10.0303 15.0303L12 13.0607L13.9697 15.0303C14.2626 15.3232 14.7374 15.3232 15.0303 15.0303C15.3232 14.7374 15.3232 14.2626 15.0303 13.9697L13.0607 12L15.0303 10.0303C15.3232 9.73743 15.3232 9.26257 15.0303 8.96967C14.7374 8.67679 14.2626 8.67679 13.9697 8.96967L12 10.9393L10.0303 8.96967Z"
	}));
}
var v = /* @__PURE__ */ o.forwardRef(_), y = { textarea: "textarea" }, b = {
	none: "none",
	left: "left",
	right: "right",
	both: "both"
}, x = {
	mini: "mini",
	default: "default",
	compact: "compact",
	large: "large"
}, S = {
	start: "start",
	end: "end"
};
//#endregion
export { b as a, v as i, S as n, y as r, x as t };

//# sourceMappingURL=constants-yZa2TGaZ-D7s59a3V.js.map