import { B as e, Jt as t, Ka as n, Kn as r, Ua as i, Ut as a, fi as o, tr as s } from "./index-Dl4ETd_L-D2oMd1k2.js";
import { t as c } from "./assertThisInitialized-C1dAyb4j-jFURGdZo.js";
import { i as l, n as u, r as d, s as f } from "./possibleConstructorReturn-BHiKHPYz-Bnf-j7Fb.js";
import { t as p } from "./createSuper-DfsXhqeB-ygQJQAOQ.js";
import { o as m, r as h } from "./select-DyvsciAf-DTdJ1yfK.js";
//#region ../react/build/timepicker-Bp949u0W.js
var g = /* @__PURE__ */ n(i(), 1);
function _(e) {
	if (e === null || e === !0 || e === !1) return NaN;
	var t = Number(e);
	return isNaN(t) ? t : t < 0 ? Math.ceil(t) : Math.floor(t);
}
function v(e, t) {
	if (t.length < e) throw TypeError(e + " argument" + (e > 1 ? "s" : "") + " required, but only " + t.length + " present");
}
function y(e) {
	v(1, arguments);
	var n = Object.prototype.toString.call(e);
	return e instanceof Date || t(e) === "object" && n === "[object Date]" ? new Date(e.getTime()) : typeof e == "number" || n === "[object Number]" ? new Date(e) : ((typeof e == "string" || n === "[object String]") && typeof console < "u" && (console.warn("Starting with v2.0.0-beta.1 date-fns doesn't accept strings as date arguments. Please use `parseISO` to parse strings. See: https://github.com/date-fns/date-fns/blob/master/docs/upgradeGuide.md#string-arguments"), console.warn((/* @__PURE__ */ Error()).stack)), /* @__PURE__ */ new Date(NaN));
}
function b(e, t) {
	v(2, arguments);
	var n = y(e), r = _(t);
	return isNaN(r) ? /* @__PURE__ */ new Date(NaN) : (r && n.setDate(n.getDate() + r), n);
}
function x(e, t) {
	v(2, arguments);
	var n = y(e).getTime(), r = _(t);
	return new Date(n + r);
}
function S(e, t) {
	return v(2, arguments), x(e, _(t) * 1e3);
}
var ee = 6e4;
function te(e, t) {
	return v(2, arguments), x(e, _(t) * ee);
}
var ne = 36e5;
function C(e, t) {
	return v(2, arguments), x(e, _(t) * ne);
}
function re(e, t) {
	return v(2, arguments), b(e, _(t) * 7);
}
function w(e, t) {
	v(2, arguments);
	var n = y(e), r = _(t);
	if (isNaN(r)) return /* @__PURE__ */ new Date(NaN);
	if (!r) return n;
	var i = n.getDate(), a = new Date(n.getTime());
	return a.setMonth(n.getMonth() + r + 1, 0), i >= a.getDate() ? a : (n.setFullYear(a.getFullYear(), a.getMonth(), i), n);
}
function ie(e, t) {
	return v(2, arguments), w(e, _(t) * 12);
}
function ae(e, t) {
	v(2, arguments);
	var n = y(e), r = y(t);
	return n.getFullYear() - r.getFullYear();
}
function T(e, t) {
	v(2, arguments);
	var n = y(e), r = y(t), i = n.getTime() - r.getTime();
	return i < 0 ? -1 : i > 0 ? 1 : i;
}
function E(e, t) {
	v(2, arguments);
	var n = y(e), r = y(t), i = T(n, r), a = Math.abs(ae(n, r));
	n.setFullYear(1584), r.setFullYear(1584);
	var o = T(n, r) === -i, s = i * (a - Number(o));
	return s === 0 ? 0 : s;
}
function oe(e, t) {
	v(2, arguments);
	var n = y(e), r = y(t), i = n.getFullYear() - r.getFullYear(), a = n.getMonth() - r.getMonth();
	return i * 12 + a;
}
function D(e) {
	v(1, arguments);
	var t = y(e);
	return t.setHours(23, 59, 59, 999), t;
}
function O(e) {
	v(1, arguments);
	var t = y(e), n = t.getMonth();
	return t.setFullYear(t.getFullYear(), n + 1, 0), t.setHours(23, 59, 59, 999), t;
}
function se(e) {
	v(1, arguments);
	var t = y(e);
	return D(t).getTime() === O(t).getTime();
}
function k(e, t) {
	v(2, arguments);
	var n = y(e), r = y(t), i = T(n, r), a = Math.abs(oe(n, r)), o;
	if (a < 1) o = 0;
	else {
		n.getMonth() === 1 && n.getDate() > 27 && n.setDate(30), n.setMonth(n.getMonth() - i * a);
		var s = T(n, r) === -i;
		se(y(e)) && a === 1 && T(e, r) === 1 && (s = !1), o = i * (a - Number(s));
	}
	return o === 0 ? 0 : o;
}
var ce = {
	ceil: Math.ceil,
	round: Math.round,
	floor: Math.floor,
	trunc: function(e) {
		return e < 0 ? Math.ceil(e) : Math.floor(e);
	}
}, le = "trunc";
function A(e) {
	return e ? ce[e] : ce[le];
}
function ue(e, t, n) {
	v(2, arguments);
	var r = k(e, t) / 3;
	return A(void 0)(r);
}
function de(e) {
	var t = new Date(Date.UTC(e.getFullYear(), e.getMonth(), e.getDate(), e.getHours(), e.getMinutes(), e.getSeconds(), e.getMilliseconds()));
	return t.setUTCFullYear(e.getFullYear()), e.getTime() - t.getTime();
}
function j(e) {
	v(1, arguments);
	var t = y(e);
	return t.setHours(0, 0, 0, 0), t;
}
var fe = 864e5;
function pe(e, t) {
	v(2, arguments);
	var n = j(e), r = j(t), i = n.getTime() - de(n), a = r.getTime() - de(r);
	return Math.round((i - a) / fe);
}
function me(e, t) {
	var n = e.getFullYear() - t.getFullYear() || e.getMonth() - t.getMonth() || e.getDate() - t.getDate() || e.getHours() - t.getHours() || e.getMinutes() - t.getMinutes() || e.getSeconds() - t.getSeconds() || e.getMilliseconds() - t.getMilliseconds();
	return n < 0 ? -1 : n > 0 ? 1 : n;
}
function he(e, t) {
	v(2, arguments);
	var n = y(e), r = y(t), i = me(n, r), a = Math.abs(pe(n, r));
	n.setDate(n.getDate() - i * a);
	var o = i * (a - +(me(n, r) === -i));
	return o === 0 ? 0 : o;
}
function ge(e, t, n) {
	v(2, arguments);
	var r = he(e, t) / 7;
	return A(void 0)(r);
}
var M = 6e4, _e = 36e5, ve = 1e3;
function ye(e, t) {
	return v(2, arguments), y(e).getTime() - y(t).getTime();
}
function be(e, t, n) {
	v(2, arguments);
	var r = ye(e, t) / _e;
	return A(void 0)(r);
}
function xe(e, t, n) {
	v(2, arguments);
	var r = ye(e, t) / M;
	return A(void 0)(r);
}
function Se(e, t, n) {
	v(2, arguments);
	var r = ye(e, t) / 1e3;
	return A(void 0)(r);
}
function Ce(e, t) {
	v(1, arguments);
	var n = e || {}, r = y(n.start), i = y(n.end).getTime();
	if (!(r.getTime() <= i)) throw RangeError("Invalid interval");
	var a = [], o = r;
	o.setHours(0, 0, 0, 0);
	var s = 1;
	if (s < 1 || isNaN(s)) throw RangeError("`options.step` must be a number greater than 1");
	for (; o.getTime() <= i;) a.push(y(o)), o.setDate(o.getDate() + s), o.setHours(0, 0, 0, 0);
	return a;
}
var we = {};
function N() {
	return we;
}
function Te(e, t) {
	var n, r, i, a;
	v(1, arguments);
	var o = N(), s = _(t?.weekStartsOn ?? (t == null || (n = t.locale) == null || (r = n.options) == null ? void 0 : r.weekStartsOn) ?? o.weekStartsOn ?? ((i = o.locale) == null || (a = i.options) == null ? void 0 : a.weekStartsOn) ?? 0);
	if (!(s >= 0 && s <= 6)) throw RangeError("weekStartsOn must be between 0 and 6 inclusively");
	var c = y(e), l = c.getDay(), u = (l < s ? -7 : 0) + 6 - (l - s);
	return c.setDate(c.getDate() + u), c.setHours(23, 59, 59, 999), c;
}
function Ee(e) {
	v(1, arguments);
	var t = y(e), n = t.getFullYear();
	return t.setFullYear(n + 1, 0, 0), t.setHours(23, 59, 59, 999), t;
}
function De(e) {
	return v(1, arguments), e instanceof Date || t(e) === "object" && Object.prototype.toString.call(e) === "[object Date]";
}
function Oe(e) {
	if (v(1, arguments), !De(e) && typeof e != "number") return !1;
	var t = y(e);
	return !isNaN(Number(t));
}
function ke(e, t) {
	return v(2, arguments), x(e, -_(t));
}
var Ae = 864e5;
function je(e) {
	v(1, arguments);
	var t = y(e), n = t.getTime();
	t.setUTCMonth(0, 1), t.setUTCHours(0, 0, 0, 0);
	var r = n - t.getTime();
	return Math.floor(r / Ae) + 1;
}
function P(e) {
	v(1, arguments);
	var t = 1, n = y(e), r = n.getUTCDay(), i = (r < t ? 7 : 0) + r - t;
	return n.setUTCDate(n.getUTCDate() - i), n.setUTCHours(0, 0, 0, 0), n;
}
function Me(e) {
	v(1, arguments);
	var t = y(e), n = t.getUTCFullYear(), r = /* @__PURE__ */ new Date(0);
	r.setUTCFullYear(n + 1, 0, 4), r.setUTCHours(0, 0, 0, 0);
	var i = P(r), a = /* @__PURE__ */ new Date(0);
	a.setUTCFullYear(n, 0, 4), a.setUTCHours(0, 0, 0, 0);
	var o = P(a);
	return t.getTime() >= i.getTime() ? n + 1 : t.getTime() >= o.getTime() ? n : n - 1;
}
function Ne(e) {
	v(1, arguments);
	var t = Me(e), n = /* @__PURE__ */ new Date(0);
	return n.setUTCFullYear(t, 0, 4), n.setUTCHours(0, 0, 0, 0), P(n);
}
var Pe = 6048e5;
function Fe(e) {
	v(1, arguments);
	var t = y(e), n = P(t).getTime() - Ne(t).getTime();
	return Math.round(n / Pe) + 1;
}
function F(e, t) {
	var n, r, i, a;
	v(1, arguments);
	var o = N(), s = _(t?.weekStartsOn ?? (t == null || (n = t.locale) == null || (r = n.options) == null ? void 0 : r.weekStartsOn) ?? o.weekStartsOn ?? ((i = o.locale) == null || (a = i.options) == null ? void 0 : a.weekStartsOn) ?? 0);
	if (!(s >= 0 && s <= 6)) throw RangeError("weekStartsOn must be between 0 and 6 inclusively");
	var c = y(e), l = c.getUTCDay(), u = (l < s ? 7 : 0) + l - s;
	return c.setUTCDate(c.getUTCDate() - u), c.setUTCHours(0, 0, 0, 0), c;
}
function Ie(e, t) {
	var n, r, i, a;
	v(1, arguments);
	var o = y(e), s = o.getUTCFullYear(), c = N(), l = _(t?.firstWeekContainsDate ?? (t == null || (n = t.locale) == null || (r = n.options) == null ? void 0 : r.firstWeekContainsDate) ?? c.firstWeekContainsDate ?? ((i = c.locale) == null || (a = i.options) == null ? void 0 : a.firstWeekContainsDate) ?? 1);
	if (!(l >= 1 && l <= 7)) throw RangeError("firstWeekContainsDate must be between 1 and 7 inclusively");
	var u = /* @__PURE__ */ new Date(0);
	u.setUTCFullYear(s + 1, 0, l), u.setUTCHours(0, 0, 0, 0);
	var d = F(u, t), f = /* @__PURE__ */ new Date(0);
	f.setUTCFullYear(s, 0, l), f.setUTCHours(0, 0, 0, 0);
	var p = F(f, t);
	return o.getTime() >= d.getTime() ? s + 1 : o.getTime() >= p.getTime() ? s : s - 1;
}
function Le(e, t) {
	var n, r, i, a;
	v(1, arguments);
	var o = N(), s = _(t?.firstWeekContainsDate ?? (t == null || (n = t.locale) == null || (r = n.options) == null ? void 0 : r.firstWeekContainsDate) ?? o.firstWeekContainsDate ?? ((i = o.locale) == null || (a = i.options) == null ? void 0 : a.firstWeekContainsDate) ?? 1), c = Ie(e, t), l = /* @__PURE__ */ new Date(0);
	return l.setUTCFullYear(c, 0, s), l.setUTCHours(0, 0, 0, 0), F(l, t);
}
var Re = 6048e5;
function ze(e, t) {
	v(1, arguments);
	var n = y(e), r = F(n, t).getTime() - Le(n, t).getTime();
	return Math.round(r / Re) + 1;
}
function I(e, t) {
	for (var n = e < 0 ? "-" : "", r = Math.abs(e).toString(); r.length < t;) r = "0" + r;
	return n + r;
}
var L = {
	y: function(e, t) {
		var n = e.getUTCFullYear(), r = n > 0 ? n : 1 - n;
		return I(t === "yy" ? r % 100 : r, t.length);
	},
	M: function(e, t) {
		var n = e.getUTCMonth();
		return t === "M" ? String(n + 1) : I(n + 1, 2);
	},
	d: function(e, t) {
		return I(e.getUTCDate(), t.length);
	},
	a: function(e, t) {
		var n = e.getUTCHours() / 12 >= 1 ? "pm" : "am";
		switch (t) {
			case "a":
			case "aa": return n.toUpperCase();
			case "aaa": return n;
			case "aaaaa": return n[0];
			default: return n === "am" ? "a.m." : "p.m.";
		}
	},
	h: function(e, t) {
		return I(e.getUTCHours() % 12 || 12, t.length);
	},
	H: function(e, t) {
		return I(e.getUTCHours(), t.length);
	},
	m: function(e, t) {
		return I(e.getUTCMinutes(), t.length);
	},
	s: function(e, t) {
		return I(e.getUTCSeconds(), t.length);
	},
	S: function(e, t) {
		var n = t.length, r = e.getUTCMilliseconds();
		return I(Math.floor(r * 10 ** (n - 3)), t.length);
	}
}, R = {
	midnight: "midnight",
	noon: "noon",
	morning: "morning",
	afternoon: "afternoon",
	evening: "evening",
	night: "night"
}, Be = {
	G: function(e, t, n) {
		var r = +(e.getUTCFullYear() > 0);
		switch (t) {
			case "G":
			case "GG":
			case "GGG": return n.era(r, { width: "abbreviated" });
			case "GGGGG": return n.era(r, { width: "narrow" });
			default: return n.era(r, { width: "wide" });
		}
	},
	y: function(e, t, n) {
		if (t === "yo") {
			var r = e.getUTCFullYear(), i = r > 0 ? r : 1 - r;
			return n.ordinalNumber(i, { unit: "year" });
		}
		return L.y(e, t);
	},
	Y: function(e, t, n, r) {
		var i = Ie(e, r), a = i > 0 ? i : 1 - i;
		return t === "YY" ? I(a % 100, 2) : t === "Yo" ? n.ordinalNumber(a, { unit: "year" }) : I(a, t.length);
	},
	R: function(e, t) {
		return I(Me(e), t.length);
	},
	u: function(e, t) {
		return I(e.getUTCFullYear(), t.length);
	},
	Q: function(e, t, n) {
		var r = Math.ceil((e.getUTCMonth() + 1) / 3);
		switch (t) {
			case "Q": return String(r);
			case "QQ": return I(r, 2);
			case "Qo": return n.ordinalNumber(r, { unit: "quarter" });
			case "QQQ": return n.quarter(r, {
				width: "abbreviated",
				context: "formatting"
			});
			case "QQQQQ": return n.quarter(r, {
				width: "narrow",
				context: "formatting"
			});
			default: return n.quarter(r, {
				width: "wide",
				context: "formatting"
			});
		}
	},
	q: function(e, t, n) {
		var r = Math.ceil((e.getUTCMonth() + 1) / 3);
		switch (t) {
			case "q": return String(r);
			case "qq": return I(r, 2);
			case "qo": return n.ordinalNumber(r, { unit: "quarter" });
			case "qqq": return n.quarter(r, {
				width: "abbreviated",
				context: "standalone"
			});
			case "qqqqq": return n.quarter(r, {
				width: "narrow",
				context: "standalone"
			});
			default: return n.quarter(r, {
				width: "wide",
				context: "standalone"
			});
		}
	},
	M: function(e, t, n) {
		var r = e.getUTCMonth();
		switch (t) {
			case "M":
			case "MM": return L.M(e, t);
			case "Mo": return n.ordinalNumber(r + 1, { unit: "month" });
			case "MMM": return n.month(r, {
				width: "abbreviated",
				context: "formatting"
			});
			case "MMMMM": return n.month(r, {
				width: "narrow",
				context: "formatting"
			});
			default: return n.month(r, {
				width: "wide",
				context: "formatting"
			});
		}
	},
	L: function(e, t, n) {
		var r = e.getUTCMonth();
		switch (t) {
			case "L": return String(r + 1);
			case "LL": return I(r + 1, 2);
			case "Lo": return n.ordinalNumber(r + 1, { unit: "month" });
			case "LLL": return n.month(r, {
				width: "abbreviated",
				context: "standalone"
			});
			case "LLLLL": return n.month(r, {
				width: "narrow",
				context: "standalone"
			});
			default: return n.month(r, {
				width: "wide",
				context: "standalone"
			});
		}
	},
	w: function(e, t, n, r) {
		var i = ze(e, r);
		return t === "wo" ? n.ordinalNumber(i, { unit: "week" }) : I(i, t.length);
	},
	I: function(e, t, n) {
		var r = Fe(e);
		return t === "Io" ? n.ordinalNumber(r, { unit: "week" }) : I(r, t.length);
	},
	d: function(e, t, n) {
		return t === "do" ? n.ordinalNumber(e.getUTCDate(), { unit: "date" }) : L.d(e, t);
	},
	D: function(e, t, n) {
		var r = je(e);
		return t === "Do" ? n.ordinalNumber(r, { unit: "dayOfYear" }) : I(r, t.length);
	},
	E: function(e, t, n) {
		var r = e.getUTCDay();
		switch (t) {
			case "E":
			case "EE":
			case "EEE": return n.day(r, {
				width: "abbreviated",
				context: "formatting"
			});
			case "EEEEE": return n.day(r, {
				width: "narrow",
				context: "formatting"
			});
			case "EEEEEE": return n.day(r, {
				width: "short",
				context: "formatting"
			});
			default: return n.day(r, {
				width: "wide",
				context: "formatting"
			});
		}
	},
	e: function(e, t, n, r) {
		var i = e.getUTCDay(), a = (i - r.weekStartsOn + 8) % 7 || 7;
		switch (t) {
			case "e": return String(a);
			case "ee": return I(a, 2);
			case "eo": return n.ordinalNumber(a, { unit: "day" });
			case "eee": return n.day(i, {
				width: "abbreviated",
				context: "formatting"
			});
			case "eeeee": return n.day(i, {
				width: "narrow",
				context: "formatting"
			});
			case "eeeeee": return n.day(i, {
				width: "short",
				context: "formatting"
			});
			default: return n.day(i, {
				width: "wide",
				context: "formatting"
			});
		}
	},
	c: function(e, t, n, r) {
		var i = e.getUTCDay(), a = (i - r.weekStartsOn + 8) % 7 || 7;
		switch (t) {
			case "c": return String(a);
			case "cc": return I(a, t.length);
			case "co": return n.ordinalNumber(a, { unit: "day" });
			case "ccc": return n.day(i, {
				width: "abbreviated",
				context: "standalone"
			});
			case "ccccc": return n.day(i, {
				width: "narrow",
				context: "standalone"
			});
			case "cccccc": return n.day(i, {
				width: "short",
				context: "standalone"
			});
			default: return n.day(i, {
				width: "wide",
				context: "standalone"
			});
		}
	},
	i: function(e, t, n) {
		var r = e.getUTCDay(), i = r === 0 ? 7 : r;
		switch (t) {
			case "i": return String(i);
			case "ii": return I(i, t.length);
			case "io": return n.ordinalNumber(i, { unit: "day" });
			case "iii": return n.day(r, {
				width: "abbreviated",
				context: "formatting"
			});
			case "iiiii": return n.day(r, {
				width: "narrow",
				context: "formatting"
			});
			case "iiiiii": return n.day(r, {
				width: "short",
				context: "formatting"
			});
			default: return n.day(r, {
				width: "wide",
				context: "formatting"
			});
		}
	},
	a: function(e, t, n) {
		var r = e.getUTCHours() / 12 >= 1 ? "pm" : "am";
		switch (t) {
			case "a":
			case "aa": return n.dayPeriod(r, {
				width: "abbreviated",
				context: "formatting"
			});
			case "aaa": return n.dayPeriod(r, {
				width: "abbreviated",
				context: "formatting"
			}).toLowerCase();
			case "aaaaa": return n.dayPeriod(r, {
				width: "narrow",
				context: "formatting"
			});
			default: return n.dayPeriod(r, {
				width: "wide",
				context: "formatting"
			});
		}
	},
	b: function(e, t, n) {
		var r = e.getUTCHours(), i;
		switch (i = r === 12 ? R.noon : r === 0 ? R.midnight : r / 12 >= 1 ? "pm" : "am", t) {
			case "b":
			case "bb": return n.dayPeriod(i, {
				width: "abbreviated",
				context: "formatting"
			});
			case "bbb": return n.dayPeriod(i, {
				width: "abbreviated",
				context: "formatting"
			}).toLowerCase();
			case "bbbbb": return n.dayPeriod(i, {
				width: "narrow",
				context: "formatting"
			});
			default: return n.dayPeriod(i, {
				width: "wide",
				context: "formatting"
			});
		}
	},
	B: function(e, t, n) {
		var r = e.getUTCHours(), i;
		switch (i = r >= 17 ? R.evening : r >= 12 ? R.afternoon : r >= 4 ? R.morning : R.night, t) {
			case "B":
			case "BB":
			case "BBB": return n.dayPeriod(i, {
				width: "abbreviated",
				context: "formatting"
			});
			case "BBBBB": return n.dayPeriod(i, {
				width: "narrow",
				context: "formatting"
			});
			default: return n.dayPeriod(i, {
				width: "wide",
				context: "formatting"
			});
		}
	},
	h: function(e, t, n) {
		if (t === "ho") {
			var r = e.getUTCHours() % 12;
			return r === 0 && (r = 12), n.ordinalNumber(r, { unit: "hour" });
		}
		return L.h(e, t);
	},
	H: function(e, t, n) {
		return t === "Ho" ? n.ordinalNumber(e.getUTCHours(), { unit: "hour" }) : L.H(e, t);
	},
	K: function(e, t, n) {
		var r = e.getUTCHours() % 12;
		return t === "Ko" ? n.ordinalNumber(r, { unit: "hour" }) : I(r, t.length);
	},
	k: function(e, t, n) {
		var r = e.getUTCHours();
		return r === 0 && (r = 24), t === "ko" ? n.ordinalNumber(r, { unit: "hour" }) : I(r, t.length);
	},
	m: function(e, t, n) {
		return t === "mo" ? n.ordinalNumber(e.getUTCMinutes(), { unit: "minute" }) : L.m(e, t);
	},
	s: function(e, t, n) {
		return t === "so" ? n.ordinalNumber(e.getUTCSeconds(), { unit: "second" }) : L.s(e, t);
	},
	S: function(e, t) {
		return L.S(e, t);
	},
	X: function(e, t, n, r) {
		var i = (r._originalDate || e).getTimezoneOffset();
		if (i === 0) return "Z";
		switch (t) {
			case "X": return He(i);
			case "XXXX":
			case "XX": return z(i);
			default: return z(i, ":");
		}
	},
	x: function(e, t, n, r) {
		var i = (r._originalDate || e).getTimezoneOffset();
		switch (t) {
			case "x": return He(i);
			case "xxxx":
			case "xx": return z(i);
			default: return z(i, ":");
		}
	},
	O: function(e, t, n, r) {
		var i = (r._originalDate || e).getTimezoneOffset();
		switch (t) {
			case "O":
			case "OO":
			case "OOO": return "GMT" + Ve(i, ":");
			default: return "GMT" + z(i, ":");
		}
	},
	z: function(e, t, n, r) {
		var i = (r._originalDate || e).getTimezoneOffset();
		switch (t) {
			case "z":
			case "zz":
			case "zzz": return "GMT" + Ve(i, ":");
			default: return "GMT" + z(i, ":");
		}
	},
	t: function(e, t, n, r) {
		var i = r._originalDate || e;
		return I(Math.floor(i.getTime() / 1e3), t.length);
	},
	T: function(e, t, n, r) {
		return I((r._originalDate || e).getTime(), t.length);
	}
};
function Ve(e, t) {
	var n = e > 0 ? "-" : "+", r = Math.abs(e), i = Math.floor(r / 60), a = r % 60;
	if (a === 0) return n + String(i);
	var o = t;
	return n + String(i) + o + I(a, 2);
}
function He(e, t) {
	return e % 60 == 0 ? (e > 0 ? "-" : "+") + I(Math.abs(e) / 60, 2) : z(e, t);
}
function z(e, t) {
	var n = t || "", r = e > 0 ? "-" : "+", i = Math.abs(e), a = I(Math.floor(i / 60), 2), o = I(i % 60, 2);
	return r + a + n + o;
}
var Ue = function(e, t) {
	switch (e) {
		case "P": return t.date({ width: "short" });
		case "PP": return t.date({ width: "medium" });
		case "PPP": return t.date({ width: "long" });
		default: return t.date({ width: "full" });
	}
}, We = function(e, t) {
	switch (e) {
		case "p": return t.time({ width: "short" });
		case "pp": return t.time({ width: "medium" });
		case "ppp": return t.time({ width: "long" });
		default: return t.time({ width: "full" });
	}
}, Ge = {
	p: We,
	P: function(e, t) {
		var n = e.match(/(P+)(p+)?/) || [], r = n[1], i = n[2];
		if (!i) return Ue(e, t);
		var a;
		switch (r) {
			case "P":
				a = t.dateTime({ width: "short" });
				break;
			case "PP":
				a = t.dateTime({ width: "medium" });
				break;
			case "PPP":
				a = t.dateTime({ width: "long" });
				break;
			default:
				a = t.dateTime({ width: "full" });
				break;
		}
		return a.replace("{{date}}", Ue(r, t)).replace("{{time}}", We(i, t));
	}
}, Ke = ["D", "DD"], qe = ["YY", "YYYY"];
function Je(e) {
	return Ke.indexOf(e) !== -1;
}
function Ye(e) {
	return qe.indexOf(e) !== -1;
}
function Xe(e, t, n) {
	if (e === "YYYY") throw RangeError(`Use \`yyyy\` instead of \`YYYY\` (in \`${t}\`) for formatting years to the input \`${n}\`; see: https://github.com/date-fns/date-fns/blob/master/docs/unicodeTokens.md`);
	if (e === "YY") throw RangeError(`Use \`yy\` instead of \`YY\` (in \`${t}\`) for formatting years to the input \`${n}\`; see: https://github.com/date-fns/date-fns/blob/master/docs/unicodeTokens.md`);
	if (e === "D") throw RangeError(`Use \`d\` instead of \`D\` (in \`${t}\`) for formatting days of the month to the input \`${n}\`; see: https://github.com/date-fns/date-fns/blob/master/docs/unicodeTokens.md`);
	if (e === "DD") throw RangeError(`Use \`dd\` instead of \`DD\` (in \`${t}\`) for formatting days of the month to the input \`${n}\`; see: https://github.com/date-fns/date-fns/blob/master/docs/unicodeTokens.md`);
}
var Ze = {
	lessThanXSeconds: {
		one: "less than a second",
		other: "less than {{count}} seconds"
	},
	xSeconds: {
		one: "1 second",
		other: "{{count}} seconds"
	},
	halfAMinute: "half a minute",
	lessThanXMinutes: {
		one: "less than a minute",
		other: "less than {{count}} minutes"
	},
	xMinutes: {
		one: "1 minute",
		other: "{{count}} minutes"
	},
	aboutXHours: {
		one: "about 1 hour",
		other: "about {{count}} hours"
	},
	xHours: {
		one: "1 hour",
		other: "{{count}} hours"
	},
	xDays: {
		one: "1 day",
		other: "{{count}} days"
	},
	aboutXWeeks: {
		one: "about 1 week",
		other: "about {{count}} weeks"
	},
	xWeeks: {
		one: "1 week",
		other: "{{count}} weeks"
	},
	aboutXMonths: {
		one: "about 1 month",
		other: "about {{count}} months"
	},
	xMonths: {
		one: "1 month",
		other: "{{count}} months"
	},
	aboutXYears: {
		one: "about 1 year",
		other: "about {{count}} years"
	},
	xYears: {
		one: "1 year",
		other: "{{count}} years"
	},
	overXYears: {
		one: "over 1 year",
		other: "over {{count}} years"
	},
	almostXYears: {
		one: "almost 1 year",
		other: "almost {{count}} years"
	}
}, Qe = function(e, t, n) {
	var r, i = Ze[e];
	return r = typeof i == "string" ? i : t === 1 ? i.one : i.other.replace("{{count}}", t.toString()), n != null && n.addSuffix ? n.comparison && n.comparison > 0 ? "in " + r : r + " ago" : r;
};
function $e(e) {
	return function() {
		var t = arguments.length > 0 && arguments[0] !== void 0 ? arguments[0] : {}, n = t.width ? String(t.width) : e.defaultWidth;
		return e.formats[n] || e.formats[e.defaultWidth];
	};
}
var et = {
	date: $e({
		formats: {
			full: "EEEE, MMMM do, y",
			long: "MMMM do, y",
			medium: "MMM d, y",
			short: "MM/dd/yyyy"
		},
		defaultWidth: "full"
	}),
	time: $e({
		formats: {
			full: "h:mm:ss a zzzz",
			long: "h:mm:ss a z",
			medium: "h:mm:ss a",
			short: "h:mm a"
		},
		defaultWidth: "full"
	}),
	dateTime: $e({
		formats: {
			full: "{{date}} 'at' {{time}}",
			long: "{{date}} 'at' {{time}}",
			medium: "{{date}}, {{time}}",
			short: "{{date}}, {{time}}"
		},
		defaultWidth: "full"
	})
}, tt = {
	lastWeek: "'last' eeee 'at' p",
	yesterday: "'yesterday at' p",
	today: "'today at' p",
	tomorrow: "'tomorrow at' p",
	nextWeek: "eeee 'at' p",
	other: "P"
}, nt = function(e, t, n, r) {
	return tt[e];
};
function B(e) {
	return function(t, n) {
		var r = n != null && n.context ? String(n.context) : "standalone", i;
		if (r === "formatting" && e.formattingValues) {
			var a = e.defaultFormattingWidth || e.defaultWidth, o = n != null && n.width ? String(n.width) : a;
			i = e.formattingValues[o] || e.formattingValues[a];
		} else {
			var s = e.defaultWidth, c = n != null && n.width ? String(n.width) : e.defaultWidth;
			i = e.values[c] || e.values[s];
		}
		var l = e.argumentCallback ? e.argumentCallback(t) : t;
		return i[l];
	};
}
var rt = {
	ordinalNumber: function(e, t) {
		var n = Number(e), r = n % 100;
		if (r > 20 || r < 10) switch (r % 10) {
			case 1: return n + "st";
			case 2: return n + "nd";
			case 3: return n + "rd";
		}
		return n + "th";
	},
	era: B({
		values: {
			narrow: ["B", "A"],
			abbreviated: ["BC", "AD"],
			wide: ["Before Christ", "Anno Domini"]
		},
		defaultWidth: "wide"
	}),
	quarter: B({
		values: {
			narrow: [
				"1",
				"2",
				"3",
				"4"
			],
			abbreviated: [
				"Q1",
				"Q2",
				"Q3",
				"Q4"
			],
			wide: [
				"1st quarter",
				"2nd quarter",
				"3rd quarter",
				"4th quarter"
			]
		},
		defaultWidth: "wide",
		argumentCallback: function(e) {
			return e - 1;
		}
	}),
	month: B({
		values: {
			narrow: [
				"J",
				"F",
				"M",
				"A",
				"M",
				"J",
				"J",
				"A",
				"S",
				"O",
				"N",
				"D"
			],
			abbreviated: [
				"Jan",
				"Feb",
				"Mar",
				"Apr",
				"May",
				"Jun",
				"Jul",
				"Aug",
				"Sep",
				"Oct",
				"Nov",
				"Dec"
			],
			wide: [
				"January",
				"February",
				"March",
				"April",
				"May",
				"June",
				"July",
				"August",
				"September",
				"October",
				"November",
				"December"
			]
		},
		defaultWidth: "wide"
	}),
	day: B({
		values: {
			narrow: [
				"S",
				"M",
				"T",
				"W",
				"T",
				"F",
				"S"
			],
			short: [
				"Su",
				"Mo",
				"Tu",
				"We",
				"Th",
				"Fr",
				"Sa"
			],
			abbreviated: [
				"Sun",
				"Mon",
				"Tue",
				"Wed",
				"Thu",
				"Fri",
				"Sat"
			],
			wide: [
				"Sunday",
				"Monday",
				"Tuesday",
				"Wednesday",
				"Thursday",
				"Friday",
				"Saturday"
			]
		},
		defaultWidth: "wide"
	}),
	dayPeriod: B({
		values: {
			narrow: {
				am: "a",
				pm: "p",
				midnight: "mi",
				noon: "n",
				morning: "morning",
				afternoon: "afternoon",
				evening: "evening",
				night: "night"
			},
			abbreviated: {
				am: "AM",
				pm: "PM",
				midnight: "midnight",
				noon: "noon",
				morning: "morning",
				afternoon: "afternoon",
				evening: "evening",
				night: "night"
			},
			wide: {
				am: "a.m.",
				pm: "p.m.",
				midnight: "midnight",
				noon: "noon",
				morning: "morning",
				afternoon: "afternoon",
				evening: "evening",
				night: "night"
			}
		},
		defaultWidth: "wide",
		formattingValues: {
			narrow: {
				am: "a",
				pm: "p",
				midnight: "mi",
				noon: "n",
				morning: "in the morning",
				afternoon: "in the afternoon",
				evening: "in the evening",
				night: "at night"
			},
			abbreviated: {
				am: "AM",
				pm: "PM",
				midnight: "midnight",
				noon: "noon",
				morning: "in the morning",
				afternoon: "in the afternoon",
				evening: "in the evening",
				night: "at night"
			},
			wide: {
				am: "a.m.",
				pm: "p.m.",
				midnight: "midnight",
				noon: "noon",
				morning: "in the morning",
				afternoon: "in the afternoon",
				evening: "in the evening",
				night: "at night"
			}
		},
		defaultFormattingWidth: "wide"
	})
};
function V(e) {
	return function(t) {
		var n = arguments.length > 1 && arguments[1] !== void 0 ? arguments[1] : {}, r = n.width, i = r && e.matchPatterns[r] || e.matchPatterns[e.defaultMatchWidth], a = t.match(i);
		if (!a) return null;
		var o = a[0], s = r && e.parsePatterns[r] || e.parsePatterns[e.defaultParseWidth], c = Array.isArray(s) ? at(s, function(e) {
			return e.test(o);
		}) : it(s, function(e) {
			return e.test(o);
		}), l = e.valueCallback ? e.valueCallback(c) : c;
		l = n.valueCallback ? n.valueCallback(l) : l;
		var u = t.slice(o.length);
		return {
			value: l,
			rest: u
		};
	};
}
function it(e, t) {
	for (var n in e) if (e.hasOwnProperty(n) && t(e[n])) return n;
}
function at(e, t) {
	for (var n = 0; n < e.length; n++) if (t(e[n])) return n;
}
function ot(e) {
	return function(t) {
		var n = arguments.length > 1 && arguments[1] !== void 0 ? arguments[1] : {}, r = t.match(e.matchPattern);
		if (!r) return null;
		var i = r[0], a = t.match(e.parsePattern);
		if (!a) return null;
		var o = e.valueCallback ? e.valueCallback(a[0]) : a[0];
		o = n.valueCallback ? n.valueCallback(o) : o;
		var s = t.slice(i.length);
		return {
			value: o,
			rest: s
		};
	};
}
var st = {
	code: "en-US",
	formatDistance: Qe,
	formatLong: et,
	formatRelative: nt,
	localize: rt,
	match: {
		ordinalNumber: ot({
			matchPattern: /^(\d+)(th|st|nd|rd)?/i,
			parsePattern: /\d+/i,
			valueCallback: function(e) {
				return parseInt(e, 10);
			}
		}),
		era: V({
			matchPatterns: {
				narrow: /^(b|a)/i,
				abbreviated: /^(b\.?\s?c\.?|b\.?\s?c\.?\s?e\.?|a\.?\s?d\.?|c\.?\s?e\.?)/i,
				wide: /^(before christ|before common era|anno domini|common era)/i
			},
			defaultMatchWidth: "wide",
			parsePatterns: { any: [/^b/i, /^(a|c)/i] },
			defaultParseWidth: "any"
		}),
		quarter: V({
			matchPatterns: {
				narrow: /^[1234]/i,
				abbreviated: /^q[1234]/i,
				wide: /^[1234](th|st|nd|rd)? quarter/i
			},
			defaultMatchWidth: "wide",
			parsePatterns: { any: [
				/1/i,
				/2/i,
				/3/i,
				/4/i
			] },
			defaultParseWidth: "any",
			valueCallback: function(e) {
				return e + 1;
			}
		}),
		month: V({
			matchPatterns: {
				narrow: /^[jfmasond]/i,
				abbreviated: /^(jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)/i,
				wide: /^(january|february|march|april|may|june|july|august|september|october|november|december)/i
			},
			defaultMatchWidth: "wide",
			parsePatterns: {
				narrow: [
					/^j/i,
					/^f/i,
					/^m/i,
					/^a/i,
					/^m/i,
					/^j/i,
					/^j/i,
					/^a/i,
					/^s/i,
					/^o/i,
					/^n/i,
					/^d/i
				],
				any: [
					/^ja/i,
					/^f/i,
					/^mar/i,
					/^ap/i,
					/^may/i,
					/^jun/i,
					/^jul/i,
					/^au/i,
					/^s/i,
					/^o/i,
					/^n/i,
					/^d/i
				]
			},
			defaultParseWidth: "any"
		}),
		day: V({
			matchPatterns: {
				narrow: /^[smtwf]/i,
				short: /^(su|mo|tu|we|th|fr|sa)/i,
				abbreviated: /^(sun|mon|tue|wed|thu|fri|sat)/i,
				wide: /^(sunday|monday|tuesday|wednesday|thursday|friday|saturday)/i
			},
			defaultMatchWidth: "wide",
			parsePatterns: {
				narrow: [
					/^s/i,
					/^m/i,
					/^t/i,
					/^w/i,
					/^t/i,
					/^f/i,
					/^s/i
				],
				any: [
					/^su/i,
					/^m/i,
					/^tu/i,
					/^w/i,
					/^th/i,
					/^f/i,
					/^sa/i
				]
			},
			defaultParseWidth: "any"
		}),
		dayPeriod: V({
			matchPatterns: {
				narrow: /^(a|p|mi|n|(in the|at) (morning|afternoon|evening|night))/i,
				any: /^([ap]\.?\s?m\.?|midnight|noon|(in the|at) (morning|afternoon|evening|night))/i
			},
			defaultMatchWidth: "any",
			parsePatterns: { any: {
				am: /^a/i,
				pm: /^p/i,
				midnight: /^mi/i,
				noon: /^no/i,
				morning: /morning/i,
				afternoon: /afternoon/i,
				evening: /evening/i,
				night: /night/i
			} },
			defaultParseWidth: "any"
		})
	},
	options: {
		weekStartsOn: 0,
		firstWeekContainsDate: 1
	}
}, ct = /[yYQqMLwIdDecihHKkms]o|(\w)\1*|''|'(''|[^'])+('|$)|./g, lt = /P+p+|P+|p+|''|'(''|[^'])+('|$)|./g, ut = /^'([^]*?)'?$/, dt = /''/g, ft = /[a-zA-Z]/;
function pt(e, t, n) {
	var r, i, a, o, s, c, l, u;
	v(2, arguments);
	var d = String(t), f = N(), p = n?.locale ?? f.locale ?? st, m = _(n?.firstWeekContainsDate ?? (n == null || (r = n.locale) == null || (i = r.options) == null ? void 0 : i.firstWeekContainsDate) ?? f.firstWeekContainsDate ?? ((a = f.locale) == null || (o = a.options) == null ? void 0 : o.firstWeekContainsDate) ?? 1);
	if (!(m >= 1 && m <= 7)) throw RangeError("firstWeekContainsDate must be between 1 and 7 inclusively");
	var h = _(n?.weekStartsOn ?? (n == null || (s = n.locale) == null || (c = s.options) == null ? void 0 : c.weekStartsOn) ?? f.weekStartsOn ?? ((l = f.locale) == null || (u = l.options) == null ? void 0 : u.weekStartsOn) ?? 0);
	if (!(h >= 0 && h <= 6)) throw RangeError("weekStartsOn must be between 0 and 6 inclusively");
	if (!p.localize) throw RangeError("locale must contain localize property");
	if (!p.formatLong) throw RangeError("locale must contain formatLong property");
	var g = y(e);
	if (!Oe(g)) throw RangeError("Invalid time value");
	var b = ke(g, de(g)), x = {
		firstWeekContainsDate: m,
		weekStartsOn: h,
		locale: p,
		_originalDate: g
	};
	return d.match(lt).map(function(e) {
		var t = e[0];
		if (t === "p" || t === "P") {
			var n = Ge[t];
			return n(e, p.formatLong);
		}
		return e;
	}).join("").match(ct).map(function(r) {
		if (r === "''") return "'";
		var i = r[0];
		if (i === "'") return mt(r);
		var a = Be[i];
		if (a) return !(n != null && n.useAdditionalWeekYearTokens) && Ye(r) && Xe(r, t, String(e)), !(n != null && n.useAdditionalDayOfYearTokens) && Je(r) && Xe(r, t, String(e)), a(b, r, p.localize, x);
		if (i.match(ft)) throw RangeError("Format string contains an unescaped latin alphabet character `" + i + "`");
		return r;
	}).join("");
}
function mt(e) {
	var t = e.match(ut);
	return t ? t[1].replace(dt, "'") : e;
}
function ht(e) {
	return v(1, arguments), y(e).getDate();
}
function gt(e) {
	return v(1, arguments), y(e).getDay();
}
function _t(e) {
	v(1, arguments);
	var t = y(e), n = t.getFullYear(), r = t.getMonth(), i = /* @__PURE__ */ new Date(0);
	return i.setFullYear(n, r + 1, 0), i.setHours(0, 0, 0, 0), i.getDate();
}
function vt(e) {
	return v(1, arguments), y(e).getHours();
}
function yt(e) {
	return v(1, arguments), y(e).getMinutes();
}
function bt(e) {
	return v(1, arguments), y(e).getMonth();
}
function xt(e) {
	return v(1, arguments), y(e).getSeconds();
}
function St(e) {
	return v(1, arguments), y(e).getFullYear();
}
function Ct(e, t) {
	v(2, arguments);
	var n = y(e), r = y(t);
	return n.getTime() > r.getTime();
}
function H(e, t) {
	v(2, arguments);
	var n = y(e), r = y(t);
	return n.getTime() < r.getTime();
}
function wt(e, t) {
	v(2, arguments);
	var n = y(e), r = y(t);
	return n.getTime() === r.getTime();
}
function Tt(e, t) {
	v(2, arguments);
	var n = j(e), r = j(t);
	return n.getTime() === r.getTime();
}
function Et(e, t) {
	v(2, arguments);
	var n = y(e), r = y(t);
	return n.getFullYear() === r.getFullYear();
}
function Dt(e, t) {
	v(2, arguments);
	var n = y(e), r = y(t);
	return n.getFullYear() === r.getFullYear() && n.getMonth() === r.getMonth();
}
function Ot(e) {
	v(1, arguments);
	var t = y(e);
	return t.setMinutes(0, 0, 0), t;
}
function kt(e, t) {
	v(2, arguments);
	var n = Ot(e), r = Ot(t);
	return n.getTime() === r.getTime();
}
function At(e, t) {
	var n = typeof Symbol < "u" && e[Symbol.iterator] || e["@@iterator"];
	if (!n) {
		if (Array.isArray(e) || (n = f(e)) || t) {
			n && (e = n);
			var r = 0, i = function() {};
			return {
				s: i,
				n: function() {
					return r >= e.length ? { done: !0 } : {
						done: !1,
						value: e[r++]
					};
				},
				e: function(e) {
					throw e;
				},
				f: i
			};
		}
		throw TypeError("Invalid attempt to iterate non-iterable instance.\nIn order to be iterable, non-array objects must have a [Symbol.iterator]() method.");
	}
	var a, o = !0, s = !1;
	return {
		s: function() {
			n = n.call(e);
		},
		n: function() {
			var e = n.next();
			return o = e.done, e;
		},
		e: function(e) {
			s = !0, a = e;
		},
		f: function() {
			try {
				o || n.return == null || n.return();
			} finally {
				if (s) throw a;
			}
		}
	};
}
function jt(e, t) {
	if (e == null) throw TypeError("assign requires that input parameter not be null or undefined");
	for (var n in t) Object.prototype.hasOwnProperty.call(t, n) && (e[n] = t[n]);
	return e;
}
var Mt = 10, Nt = /* @__PURE__ */ function() {
	function e() {
		d(this, e), a(this, "priority", void 0), a(this, "subPriority", 0);
	}
	return u(e, [{
		key: "validate",
		value: function(e, t) {
			return !0;
		}
	}]), e;
}(), Pt = /* @__PURE__ */ function(e) {
	l(n, e);
	var t = p(n);
	function n(e, r, i, a, o) {
		var s;
		return d(this, n), s = t.call(this), s.value = e, s.validateValue = r, s.setValue = i, s.priority = a, o && (s.subPriority = o), s;
	}
	return u(n, [{
		key: "validate",
		value: function(e, t) {
			return this.validateValue(e, this.value, t);
		}
	}, {
		key: "set",
		value: function(e, t, n) {
			return this.setValue(e, t, this.value, n);
		}
	}]), n;
}(Nt), Ft = /* @__PURE__ */ function(e) {
	l(n, e);
	var t = p(n);
	function n() {
		var e;
		d(this, n);
		var r = [...arguments];
		return e = t.call.apply(t, [this].concat(r)), a(c(e), "priority", Mt), a(c(e), "subPriority", -1), e;
	}
	return u(n, [{
		key: "set",
		value: function(e, t) {
			if (t.timestampIsSet) return e;
			var n = /* @__PURE__ */ new Date(0);
			return n.setFullYear(e.getUTCFullYear(), e.getUTCMonth(), e.getUTCDate()), n.setHours(e.getUTCHours(), e.getUTCMinutes(), e.getUTCSeconds(), e.getUTCMilliseconds()), n;
		}
	}]), n;
}(Nt), U = /* @__PURE__ */ function() {
	function e() {
		d(this, e), a(this, "incompatibleTokens", void 0), a(this, "priority", void 0), a(this, "subPriority", void 0);
	}
	return u(e, [{
		key: "run",
		value: function(e, t, n, r) {
			var i = this.parse(e, t, n, r);
			return i ? {
				setter: new Pt(i.value, this.validate, this.set, this.priority, this.subPriority),
				rest: i.rest
			} : null;
		}
	}, {
		key: "validate",
		value: function(e, t, n) {
			return !0;
		}
	}]), e;
}(), It = /* @__PURE__ */ function(e) {
	l(n, e);
	var t = p(n);
	function n() {
		var e;
		d(this, n);
		var r = [...arguments];
		return e = t.call.apply(t, [this].concat(r)), a(c(e), "priority", 140), a(c(e), "incompatibleTokens", [
			"R",
			"u",
			"t",
			"T"
		]), e;
	}
	return u(n, [{
		key: "parse",
		value: function(e, t, n) {
			switch (t) {
				case "G":
				case "GG":
				case "GGG": return n.era(e, { width: "abbreviated" }) || n.era(e, { width: "narrow" });
				case "GGGGG": return n.era(e, { width: "narrow" });
				default: return n.era(e, { width: "wide" }) || n.era(e, { width: "abbreviated" }) || n.era(e, { width: "narrow" });
			}
		}
	}, {
		key: "set",
		value: function(e, t, n) {
			return t.era = n, e.setUTCFullYear(n, 0, 1), e.setUTCHours(0, 0, 0, 0), e;
		}
	}]), n;
}(U), W = {
	month: /^(1[0-2]|0?\d)/,
	date: /^(3[0-1]|[0-2]?\d)/,
	dayOfYear: /^(36[0-6]|3[0-5]\d|[0-2]?\d?\d)/,
	week: /^(5[0-3]|[0-4]?\d)/,
	hour23h: /^(2[0-3]|[0-1]?\d)/,
	hour24h: /^(2[0-4]|[0-1]?\d)/,
	hour11h: /^(1[0-1]|0?\d)/,
	hour12h: /^(1[0-2]|0?\d)/,
	minute: /^[0-5]?\d/,
	second: /^[0-5]?\d/,
	singleDigit: /^\d/,
	twoDigits: /^\d{1,2}/,
	threeDigits: /^\d{1,3}/,
	fourDigits: /^\d{1,4}/,
	anyDigitsSigned: /^-?\d+/,
	singleDigitSigned: /^-?\d/,
	twoDigitsSigned: /^-?\d{1,2}/,
	threeDigitsSigned: /^-?\d{1,3}/,
	fourDigitsSigned: /^-?\d{1,4}/
}, G = {
	basicOptionalMinutes: /^([+-])(\d{2})(\d{2})?|Z/,
	basic: /^([+-])(\d{2})(\d{2})|Z/,
	basicOptionalSeconds: /^([+-])(\d{2})(\d{2})((\d{2}))?|Z/,
	extended: /^([+-])(\d{2}):(\d{2})|Z/,
	extendedOptionalSeconds: /^([+-])(\d{2}):(\d{2})(:(\d{2}))?|Z/
};
function K(e, t) {
	return e && {
		value: t(e.value),
		rest: e.rest
	};
}
function q(e, t) {
	var n = t.match(e);
	return n ? {
		value: parseInt(n[0], 10),
		rest: t.slice(n[0].length)
	} : null;
}
function J(e, t) {
	var n = t.match(e);
	if (!n) return null;
	if (n[0] === "Z") return {
		value: 0,
		rest: t.slice(1)
	};
	var r = n[1] === "+" ? 1 : -1, i = n[2] ? parseInt(n[2], 10) : 0, a = n[3] ? parseInt(n[3], 10) : 0, o = n[5] ? parseInt(n[5], 10) : 0;
	return {
		value: r * (i * _e + a * M + o * ve),
		rest: t.slice(n[0].length)
	};
}
function Lt(e) {
	return q(W.anyDigitsSigned, e);
}
function Y(e, t) {
	switch (e) {
		case 1: return q(W.singleDigit, t);
		case 2: return q(W.twoDigits, t);
		case 3: return q(W.threeDigits, t);
		case 4: return q(W.fourDigits, t);
		default: return q(RegExp("^\\d{1," + e + "}"), t);
	}
}
function Rt(e, t) {
	switch (e) {
		case 1: return q(W.singleDigitSigned, t);
		case 2: return q(W.twoDigitsSigned, t);
		case 3: return q(W.threeDigitsSigned, t);
		case 4: return q(W.fourDigitsSigned, t);
		default: return q(RegExp("^-?\\d{1," + e + "}"), t);
	}
}
function zt(e) {
	switch (e) {
		case "morning": return 4;
		case "evening": return 17;
		case "pm":
		case "noon":
		case "afternoon": return 12;
		default: return 0;
	}
}
function Bt(e, t) {
	var n = t > 0, r = n ? t : 1 - t, i;
	if (r <= 50) i = e || 100;
	else {
		var a = r + 50, o = Math.floor(a / 100) * 100, s = e >= a % 100;
		i = e + o - (s ? 100 : 0);
	}
	return n ? i : 1 - i;
}
function Vt(e) {
	return e % 400 == 0 || e % 4 == 0 && e % 100 != 0;
}
var Ht = /* @__PURE__ */ function(e) {
	l(n, e);
	var t = p(n);
	function n() {
		var e;
		d(this, n);
		var r = [...arguments];
		return e = t.call.apply(t, [this].concat(r)), a(c(e), "priority", 130), a(c(e), "incompatibleTokens", [
			"Y",
			"R",
			"u",
			"w",
			"I",
			"i",
			"e",
			"c",
			"t",
			"T"
		]), e;
	}
	return u(n, [
		{
			key: "parse",
			value: function(e, t, n) {
				var r = function(e) {
					return {
						year: e,
						isTwoDigitYear: t === "yy"
					};
				};
				switch (t) {
					case "y": return K(Y(4, e), r);
					case "yo": return K(n.ordinalNumber(e, { unit: "year" }), r);
					default: return K(Y(t.length, e), r);
				}
			}
		},
		{
			key: "validate",
			value: function(e, t) {
				return t.isTwoDigitYear || t.year > 0;
			}
		},
		{
			key: "set",
			value: function(e, t, n) {
				var r = e.getUTCFullYear();
				if (n.isTwoDigitYear) {
					var i = Bt(n.year, r);
					return e.setUTCFullYear(i, 0, 1), e.setUTCHours(0, 0, 0, 0), e;
				}
				var a = !("era" in t) || t.era === 1 ? n.year : 1 - n.year;
				return e.setUTCFullYear(a, 0, 1), e.setUTCHours(0, 0, 0, 0), e;
			}
		}
	]), n;
}(U), Ut = /* @__PURE__ */ function(e) {
	l(n, e);
	var t = p(n);
	function n() {
		var e;
		d(this, n);
		var r = [...arguments];
		return e = t.call.apply(t, [this].concat(r)), a(c(e), "priority", 130), a(c(e), "incompatibleTokens", [
			"y",
			"R",
			"u",
			"Q",
			"q",
			"M",
			"L",
			"I",
			"d",
			"D",
			"i",
			"t",
			"T"
		]), e;
	}
	return u(n, [
		{
			key: "parse",
			value: function(e, t, n) {
				var r = function(e) {
					return {
						year: e,
						isTwoDigitYear: t === "YY"
					};
				};
				switch (t) {
					case "Y": return K(Y(4, e), r);
					case "Yo": return K(n.ordinalNumber(e, { unit: "year" }), r);
					default: return K(Y(t.length, e), r);
				}
			}
		},
		{
			key: "validate",
			value: function(e, t) {
				return t.isTwoDigitYear || t.year > 0;
			}
		},
		{
			key: "set",
			value: function(e, t, n, r) {
				var i = Ie(e, r);
				if (n.isTwoDigitYear) {
					var a = Bt(n.year, i);
					return e.setUTCFullYear(a, 0, r.firstWeekContainsDate), e.setUTCHours(0, 0, 0, 0), F(e, r);
				}
				var o = !("era" in t) || t.era === 1 ? n.year : 1 - n.year;
				return e.setUTCFullYear(o, 0, r.firstWeekContainsDate), e.setUTCHours(0, 0, 0, 0), F(e, r);
			}
		}
	]), n;
}(U), Wt = /* @__PURE__ */ function(e) {
	l(n, e);
	var t = p(n);
	function n() {
		var e;
		d(this, n);
		var r = [...arguments];
		return e = t.call.apply(t, [this].concat(r)), a(c(e), "priority", 130), a(c(e), "incompatibleTokens", [
			"G",
			"y",
			"Y",
			"u",
			"Q",
			"q",
			"M",
			"L",
			"w",
			"d",
			"D",
			"e",
			"c",
			"t",
			"T"
		]), e;
	}
	return u(n, [{
		key: "parse",
		value: function(e, t) {
			return Rt(t === "R" ? 4 : t.length, e);
		}
	}, {
		key: "set",
		value: function(e, t, n) {
			var r = /* @__PURE__ */ new Date(0);
			return r.setUTCFullYear(n, 0, 4), r.setUTCHours(0, 0, 0, 0), P(r);
		}
	}]), n;
}(U), Gt = /* @__PURE__ */ function(e) {
	l(n, e);
	var t = p(n);
	function n() {
		var e;
		d(this, n);
		var r = [...arguments];
		return e = t.call.apply(t, [this].concat(r)), a(c(e), "priority", 130), a(c(e), "incompatibleTokens", [
			"G",
			"y",
			"Y",
			"R",
			"w",
			"I",
			"i",
			"e",
			"c",
			"t",
			"T"
		]), e;
	}
	return u(n, [{
		key: "parse",
		value: function(e, t) {
			return Rt(t === "u" ? 4 : t.length, e);
		}
	}, {
		key: "set",
		value: function(e, t, n) {
			return e.setUTCFullYear(n, 0, 1), e.setUTCHours(0, 0, 0, 0), e;
		}
	}]), n;
}(U), Kt = /* @__PURE__ */ function(e) {
	l(n, e);
	var t = p(n);
	function n() {
		var e;
		d(this, n);
		var r = [...arguments];
		return e = t.call.apply(t, [this].concat(r)), a(c(e), "priority", 120), a(c(e), "incompatibleTokens", [
			"Y",
			"R",
			"q",
			"M",
			"L",
			"w",
			"I",
			"d",
			"D",
			"i",
			"e",
			"c",
			"t",
			"T"
		]), e;
	}
	return u(n, [
		{
			key: "parse",
			value: function(e, t, n) {
				switch (t) {
					case "Q":
					case "QQ": return Y(t.length, e);
					case "Qo": return n.ordinalNumber(e, { unit: "quarter" });
					case "QQQ": return n.quarter(e, {
						width: "abbreviated",
						context: "formatting"
					}) || n.quarter(e, {
						width: "narrow",
						context: "formatting"
					});
					case "QQQQQ": return n.quarter(e, {
						width: "narrow",
						context: "formatting"
					});
					default: return n.quarter(e, {
						width: "wide",
						context: "formatting"
					}) || n.quarter(e, {
						width: "abbreviated",
						context: "formatting"
					}) || n.quarter(e, {
						width: "narrow",
						context: "formatting"
					});
				}
			}
		},
		{
			key: "validate",
			value: function(e, t) {
				return t >= 1 && t <= 4;
			}
		},
		{
			key: "set",
			value: function(e, t, n) {
				return e.setUTCMonth((n - 1) * 3, 1), e.setUTCHours(0, 0, 0, 0), e;
			}
		}
	]), n;
}(U), qt = /* @__PURE__ */ function(e) {
	l(n, e);
	var t = p(n);
	function n() {
		var e;
		d(this, n);
		var r = [...arguments];
		return e = t.call.apply(t, [this].concat(r)), a(c(e), "priority", 120), a(c(e), "incompatibleTokens", [
			"Y",
			"R",
			"Q",
			"M",
			"L",
			"w",
			"I",
			"d",
			"D",
			"i",
			"e",
			"c",
			"t",
			"T"
		]), e;
	}
	return u(n, [
		{
			key: "parse",
			value: function(e, t, n) {
				switch (t) {
					case "q":
					case "qq": return Y(t.length, e);
					case "qo": return n.ordinalNumber(e, { unit: "quarter" });
					case "qqq": return n.quarter(e, {
						width: "abbreviated",
						context: "standalone"
					}) || n.quarter(e, {
						width: "narrow",
						context: "standalone"
					});
					case "qqqqq": return n.quarter(e, {
						width: "narrow",
						context: "standalone"
					});
					default: return n.quarter(e, {
						width: "wide",
						context: "standalone"
					}) || n.quarter(e, {
						width: "abbreviated",
						context: "standalone"
					}) || n.quarter(e, {
						width: "narrow",
						context: "standalone"
					});
				}
			}
		},
		{
			key: "validate",
			value: function(e, t) {
				return t >= 1 && t <= 4;
			}
		},
		{
			key: "set",
			value: function(e, t, n) {
				return e.setUTCMonth((n - 1) * 3, 1), e.setUTCHours(0, 0, 0, 0), e;
			}
		}
	]), n;
}(U), Jt = /* @__PURE__ */ function(e) {
	l(n, e);
	var t = p(n);
	function n() {
		var e;
		d(this, n);
		var r = [...arguments];
		return e = t.call.apply(t, [this].concat(r)), a(c(e), "incompatibleTokens", [
			"Y",
			"R",
			"q",
			"Q",
			"L",
			"w",
			"I",
			"D",
			"i",
			"e",
			"c",
			"t",
			"T"
		]), a(c(e), "priority", 110), e;
	}
	return u(n, [
		{
			key: "parse",
			value: function(e, t, n) {
				var r = function(e) {
					return e - 1;
				};
				switch (t) {
					case "M": return K(q(W.month, e), r);
					case "MM": return K(Y(2, e), r);
					case "Mo": return K(n.ordinalNumber(e, { unit: "month" }), r);
					case "MMM": return n.month(e, {
						width: "abbreviated",
						context: "formatting"
					}) || n.month(e, {
						width: "narrow",
						context: "formatting"
					});
					case "MMMMM": return n.month(e, {
						width: "narrow",
						context: "formatting"
					});
					default: return n.month(e, {
						width: "wide",
						context: "formatting"
					}) || n.month(e, {
						width: "abbreviated",
						context: "formatting"
					}) || n.month(e, {
						width: "narrow",
						context: "formatting"
					});
				}
			}
		},
		{
			key: "validate",
			value: function(e, t) {
				return t >= 0 && t <= 11;
			}
		},
		{
			key: "set",
			value: function(e, t, n) {
				return e.setUTCMonth(n, 1), e.setUTCHours(0, 0, 0, 0), e;
			}
		}
	]), n;
}(U), Yt = /* @__PURE__ */ function(e) {
	l(n, e);
	var t = p(n);
	function n() {
		var e;
		d(this, n);
		var r = [...arguments];
		return e = t.call.apply(t, [this].concat(r)), a(c(e), "priority", 110), a(c(e), "incompatibleTokens", [
			"Y",
			"R",
			"q",
			"Q",
			"M",
			"w",
			"I",
			"D",
			"i",
			"e",
			"c",
			"t",
			"T"
		]), e;
	}
	return u(n, [
		{
			key: "parse",
			value: function(e, t, n) {
				var r = function(e) {
					return e - 1;
				};
				switch (t) {
					case "L": return K(q(W.month, e), r);
					case "LL": return K(Y(2, e), r);
					case "Lo": return K(n.ordinalNumber(e, { unit: "month" }), r);
					case "LLL": return n.month(e, {
						width: "abbreviated",
						context: "standalone"
					}) || n.month(e, {
						width: "narrow",
						context: "standalone"
					});
					case "LLLLL": return n.month(e, {
						width: "narrow",
						context: "standalone"
					});
					default: return n.month(e, {
						width: "wide",
						context: "standalone"
					}) || n.month(e, {
						width: "abbreviated",
						context: "standalone"
					}) || n.month(e, {
						width: "narrow",
						context: "standalone"
					});
				}
			}
		},
		{
			key: "validate",
			value: function(e, t) {
				return t >= 0 && t <= 11;
			}
		},
		{
			key: "set",
			value: function(e, t, n) {
				return e.setUTCMonth(n, 1), e.setUTCHours(0, 0, 0, 0), e;
			}
		}
	]), n;
}(U);
function Xt(e, t, n) {
	v(2, arguments);
	var r = y(e), i = _(t), a = ze(r, n) - i;
	return r.setUTCDate(r.getUTCDate() - a * 7), r;
}
var Zt = /* @__PURE__ */ function(e) {
	l(n, e);
	var t = p(n);
	function n() {
		var e;
		d(this, n);
		var r = [...arguments];
		return e = t.call.apply(t, [this].concat(r)), a(c(e), "priority", 100), a(c(e), "incompatibleTokens", [
			"y",
			"R",
			"u",
			"q",
			"Q",
			"M",
			"L",
			"I",
			"d",
			"D",
			"i",
			"t",
			"T"
		]), e;
	}
	return u(n, [
		{
			key: "parse",
			value: function(e, t, n) {
				switch (t) {
					case "w": return q(W.week, e);
					case "wo": return n.ordinalNumber(e, { unit: "week" });
					default: return Y(t.length, e);
				}
			}
		},
		{
			key: "validate",
			value: function(e, t) {
				return t >= 1 && t <= 53;
			}
		},
		{
			key: "set",
			value: function(e, t, n, r) {
				return F(Xt(e, n, r), r);
			}
		}
	]), n;
}(U);
function Qt(e, t) {
	v(2, arguments);
	var n = y(e), r = _(t), i = Fe(n) - r;
	return n.setUTCDate(n.getUTCDate() - i * 7), n;
}
var $t = /* @__PURE__ */ function(e) {
	l(n, e);
	var t = p(n);
	function n() {
		var e;
		d(this, n);
		var r = [...arguments];
		return e = t.call.apply(t, [this].concat(r)), a(c(e), "priority", 100), a(c(e), "incompatibleTokens", [
			"y",
			"Y",
			"u",
			"q",
			"Q",
			"M",
			"L",
			"w",
			"d",
			"D",
			"e",
			"c",
			"t",
			"T"
		]), e;
	}
	return u(n, [
		{
			key: "parse",
			value: function(e, t, n) {
				switch (t) {
					case "I": return q(W.week, e);
					case "Io": return n.ordinalNumber(e, { unit: "week" });
					default: return Y(t.length, e);
				}
			}
		},
		{
			key: "validate",
			value: function(e, t) {
				return t >= 1 && t <= 53;
			}
		},
		{
			key: "set",
			value: function(e, t, n) {
				return P(Qt(e, n));
			}
		}
	]), n;
}(U), en = [
	31,
	28,
	31,
	30,
	31,
	30,
	31,
	31,
	30,
	31,
	30,
	31
], tn = [
	31,
	29,
	31,
	30,
	31,
	30,
	31,
	31,
	30,
	31,
	30,
	31
], nn = /* @__PURE__ */ function(e) {
	l(n, e);
	var t = p(n);
	function n() {
		var e;
		d(this, n);
		var r = [...arguments];
		return e = t.call.apply(t, [this].concat(r)), a(c(e), "priority", 90), a(c(e), "subPriority", 1), a(c(e), "incompatibleTokens", [
			"Y",
			"R",
			"q",
			"Q",
			"w",
			"I",
			"D",
			"i",
			"e",
			"c",
			"t",
			"T"
		]), e;
	}
	return u(n, [
		{
			key: "parse",
			value: function(e, t, n) {
				switch (t) {
					case "d": return q(W.date, e);
					case "do": return n.ordinalNumber(e, { unit: "date" });
					default: return Y(t.length, e);
				}
			}
		},
		{
			key: "validate",
			value: function(e, t) {
				var n = Vt(e.getUTCFullYear()), r = e.getUTCMonth();
				return n ? t >= 1 && t <= tn[r] : t >= 1 && t <= en[r];
			}
		},
		{
			key: "set",
			value: function(e, t, n) {
				return e.setUTCDate(n), e.setUTCHours(0, 0, 0, 0), e;
			}
		}
	]), n;
}(U), rn = /* @__PURE__ */ function(e) {
	l(n, e);
	var t = p(n);
	function n() {
		var e;
		d(this, n);
		var r = [...arguments];
		return e = t.call.apply(t, [this].concat(r)), a(c(e), "priority", 90), a(c(e), "subpriority", 1), a(c(e), "incompatibleTokens", [
			"Y",
			"R",
			"q",
			"Q",
			"M",
			"L",
			"w",
			"I",
			"d",
			"E",
			"i",
			"e",
			"c",
			"t",
			"T"
		]), e;
	}
	return u(n, [
		{
			key: "parse",
			value: function(e, t, n) {
				switch (t) {
					case "D":
					case "DD": return q(W.dayOfYear, e);
					case "Do": return n.ordinalNumber(e, { unit: "date" });
					default: return Y(t.length, e);
				}
			}
		},
		{
			key: "validate",
			value: function(e, t) {
				return Vt(e.getUTCFullYear()) ? t >= 1 && t <= 366 : t >= 1 && t <= 365;
			}
		},
		{
			key: "set",
			value: function(e, t, n) {
				return e.setUTCMonth(0, n), e.setUTCHours(0, 0, 0, 0), e;
			}
		}
	]), n;
}(U);
function an(e, t, n) {
	var r, i, a, o;
	v(2, arguments);
	var s = N(), c = _(n?.weekStartsOn ?? (n == null || (r = n.locale) == null || (i = r.options) == null ? void 0 : i.weekStartsOn) ?? s.weekStartsOn ?? ((a = s.locale) == null || (o = a.options) == null ? void 0 : o.weekStartsOn) ?? 0);
	if (!(c >= 0 && c <= 6)) throw RangeError("weekStartsOn must be between 0 and 6 inclusively");
	var l = y(e), u = _(t), d = l.getUTCDay(), f = ((u % 7 + 7) % 7 < c ? 7 : 0) + u - d;
	return l.setUTCDate(l.getUTCDate() + f), l;
}
var on = /* @__PURE__ */ function(e) {
	l(n, e);
	var t = p(n);
	function n() {
		var e;
		d(this, n);
		var r = [...arguments];
		return e = t.call.apply(t, [this].concat(r)), a(c(e), "priority", 90), a(c(e), "incompatibleTokens", [
			"D",
			"i",
			"e",
			"c",
			"t",
			"T"
		]), e;
	}
	return u(n, [
		{
			key: "parse",
			value: function(e, t, n) {
				switch (t) {
					case "E":
					case "EE":
					case "EEE": return n.day(e, {
						width: "abbreviated",
						context: "formatting"
					}) || n.day(e, {
						width: "short",
						context: "formatting"
					}) || n.day(e, {
						width: "narrow",
						context: "formatting"
					});
					case "EEEEE": return n.day(e, {
						width: "narrow",
						context: "formatting"
					});
					case "EEEEEE": return n.day(e, {
						width: "short",
						context: "formatting"
					}) || n.day(e, {
						width: "narrow",
						context: "formatting"
					});
					default: return n.day(e, {
						width: "wide",
						context: "formatting"
					}) || n.day(e, {
						width: "abbreviated",
						context: "formatting"
					}) || n.day(e, {
						width: "short",
						context: "formatting"
					}) || n.day(e, {
						width: "narrow",
						context: "formatting"
					});
				}
			}
		},
		{
			key: "validate",
			value: function(e, t) {
				return t >= 0 && t <= 6;
			}
		},
		{
			key: "set",
			value: function(e, t, n, r) {
				return e = an(e, n, r), e.setUTCHours(0, 0, 0, 0), e;
			}
		}
	]), n;
}(U), sn = /* @__PURE__ */ function(e) {
	l(n, e);
	var t = p(n);
	function n() {
		var e;
		d(this, n);
		var r = [...arguments];
		return e = t.call.apply(t, [this].concat(r)), a(c(e), "priority", 90), a(c(e), "incompatibleTokens", [
			"y",
			"R",
			"u",
			"q",
			"Q",
			"M",
			"L",
			"I",
			"d",
			"D",
			"E",
			"i",
			"c",
			"t",
			"T"
		]), e;
	}
	return u(n, [
		{
			key: "parse",
			value: function(e, t, n, r) {
				var i = function(e) {
					var t = Math.floor((e - 1) / 7) * 7;
					return (e + r.weekStartsOn + 6) % 7 + t;
				};
				switch (t) {
					case "e":
					case "ee": return K(Y(t.length, e), i);
					case "eo": return K(n.ordinalNumber(e, { unit: "day" }), i);
					case "eee": return n.day(e, {
						width: "abbreviated",
						context: "formatting"
					}) || n.day(e, {
						width: "short",
						context: "formatting"
					}) || n.day(e, {
						width: "narrow",
						context: "formatting"
					});
					case "eeeee": return n.day(e, {
						width: "narrow",
						context: "formatting"
					});
					case "eeeeee": return n.day(e, {
						width: "short",
						context: "formatting"
					}) || n.day(e, {
						width: "narrow",
						context: "formatting"
					});
					default: return n.day(e, {
						width: "wide",
						context: "formatting"
					}) || n.day(e, {
						width: "abbreviated",
						context: "formatting"
					}) || n.day(e, {
						width: "short",
						context: "formatting"
					}) || n.day(e, {
						width: "narrow",
						context: "formatting"
					});
				}
			}
		},
		{
			key: "validate",
			value: function(e, t) {
				return t >= 0 && t <= 6;
			}
		},
		{
			key: "set",
			value: function(e, t, n, r) {
				return e = an(e, n, r), e.setUTCHours(0, 0, 0, 0), e;
			}
		}
	]), n;
}(U), cn = /* @__PURE__ */ function(e) {
	l(n, e);
	var t = p(n);
	function n() {
		var e;
		d(this, n);
		var r = [...arguments];
		return e = t.call.apply(t, [this].concat(r)), a(c(e), "priority", 90), a(c(e), "incompatibleTokens", [
			"y",
			"R",
			"u",
			"q",
			"Q",
			"M",
			"L",
			"I",
			"d",
			"D",
			"E",
			"i",
			"e",
			"t",
			"T"
		]), e;
	}
	return u(n, [
		{
			key: "parse",
			value: function(e, t, n, r) {
				var i = function(e) {
					var t = Math.floor((e - 1) / 7) * 7;
					return (e + r.weekStartsOn + 6) % 7 + t;
				};
				switch (t) {
					case "c":
					case "cc": return K(Y(t.length, e), i);
					case "co": return K(n.ordinalNumber(e, { unit: "day" }), i);
					case "ccc": return n.day(e, {
						width: "abbreviated",
						context: "standalone"
					}) || n.day(e, {
						width: "short",
						context: "standalone"
					}) || n.day(e, {
						width: "narrow",
						context: "standalone"
					});
					case "ccccc": return n.day(e, {
						width: "narrow",
						context: "standalone"
					});
					case "cccccc": return n.day(e, {
						width: "short",
						context: "standalone"
					}) || n.day(e, {
						width: "narrow",
						context: "standalone"
					});
					default: return n.day(e, {
						width: "wide",
						context: "standalone"
					}) || n.day(e, {
						width: "abbreviated",
						context: "standalone"
					}) || n.day(e, {
						width: "short",
						context: "standalone"
					}) || n.day(e, {
						width: "narrow",
						context: "standalone"
					});
				}
			}
		},
		{
			key: "validate",
			value: function(e, t) {
				return t >= 0 && t <= 6;
			}
		},
		{
			key: "set",
			value: function(e, t, n, r) {
				return e = an(e, n, r), e.setUTCHours(0, 0, 0, 0), e;
			}
		}
	]), n;
}(U);
function ln(e, t) {
	v(2, arguments);
	var n = _(t);
	n % 7 == 0 && (n -= 7);
	var r = 1, i = y(e), a = i.getUTCDay(), o = ((n % 7 + 7) % 7 < r ? 7 : 0) + n - a;
	return i.setUTCDate(i.getUTCDate() + o), i;
}
var un = /* @__PURE__ */ function(e) {
	l(n, e);
	var t = p(n);
	function n() {
		var e;
		d(this, n);
		var r = [...arguments];
		return e = t.call.apply(t, [this].concat(r)), a(c(e), "priority", 90), a(c(e), "incompatibleTokens", [
			"y",
			"Y",
			"u",
			"q",
			"Q",
			"M",
			"L",
			"w",
			"d",
			"D",
			"E",
			"e",
			"c",
			"t",
			"T"
		]), e;
	}
	return u(n, [
		{
			key: "parse",
			value: function(e, t, n) {
				var r = function(e) {
					return e === 0 ? 7 : e;
				};
				switch (t) {
					case "i":
					case "ii": return Y(t.length, e);
					case "io": return n.ordinalNumber(e, { unit: "day" });
					case "iii": return K(n.day(e, {
						width: "abbreviated",
						context: "formatting"
					}) || n.day(e, {
						width: "short",
						context: "formatting"
					}) || n.day(e, {
						width: "narrow",
						context: "formatting"
					}), r);
					case "iiiii": return K(n.day(e, {
						width: "narrow",
						context: "formatting"
					}), r);
					case "iiiiii": return K(n.day(e, {
						width: "short",
						context: "formatting"
					}) || n.day(e, {
						width: "narrow",
						context: "formatting"
					}), r);
					default: return K(n.day(e, {
						width: "wide",
						context: "formatting"
					}) || n.day(e, {
						width: "abbreviated",
						context: "formatting"
					}) || n.day(e, {
						width: "short",
						context: "formatting"
					}) || n.day(e, {
						width: "narrow",
						context: "formatting"
					}), r);
				}
			}
		},
		{
			key: "validate",
			value: function(e, t) {
				return t >= 1 && t <= 7;
			}
		},
		{
			key: "set",
			value: function(e, t, n) {
				return e = ln(e, n), e.setUTCHours(0, 0, 0, 0), e;
			}
		}
	]), n;
}(U), dn = /* @__PURE__ */ function(e) {
	l(n, e);
	var t = p(n);
	function n() {
		var e;
		d(this, n);
		var r = [...arguments];
		return e = t.call.apply(t, [this].concat(r)), a(c(e), "priority", 80), a(c(e), "incompatibleTokens", [
			"b",
			"B",
			"H",
			"k",
			"t",
			"T"
		]), e;
	}
	return u(n, [{
		key: "parse",
		value: function(e, t, n) {
			switch (t) {
				case "a":
				case "aa":
				case "aaa": return n.dayPeriod(e, {
					width: "abbreviated",
					context: "formatting"
				}) || n.dayPeriod(e, {
					width: "narrow",
					context: "formatting"
				});
				case "aaaaa": return n.dayPeriod(e, {
					width: "narrow",
					context: "formatting"
				});
				default: return n.dayPeriod(e, {
					width: "wide",
					context: "formatting"
				}) || n.dayPeriod(e, {
					width: "abbreviated",
					context: "formatting"
				}) || n.dayPeriod(e, {
					width: "narrow",
					context: "formatting"
				});
			}
		}
	}, {
		key: "set",
		value: function(e, t, n) {
			return e.setUTCHours(zt(n), 0, 0, 0), e;
		}
	}]), n;
}(U), fn = /* @__PURE__ */ function(e) {
	l(n, e);
	var t = p(n);
	function n() {
		var e;
		d(this, n);
		var r = [...arguments];
		return e = t.call.apply(t, [this].concat(r)), a(c(e), "priority", 80), a(c(e), "incompatibleTokens", [
			"a",
			"B",
			"H",
			"k",
			"t",
			"T"
		]), e;
	}
	return u(n, [{
		key: "parse",
		value: function(e, t, n) {
			switch (t) {
				case "b":
				case "bb":
				case "bbb": return n.dayPeriod(e, {
					width: "abbreviated",
					context: "formatting"
				}) || n.dayPeriod(e, {
					width: "narrow",
					context: "formatting"
				});
				case "bbbbb": return n.dayPeriod(e, {
					width: "narrow",
					context: "formatting"
				});
				default: return n.dayPeriod(e, {
					width: "wide",
					context: "formatting"
				}) || n.dayPeriod(e, {
					width: "abbreviated",
					context: "formatting"
				}) || n.dayPeriod(e, {
					width: "narrow",
					context: "formatting"
				});
			}
		}
	}, {
		key: "set",
		value: function(e, t, n) {
			return e.setUTCHours(zt(n), 0, 0, 0), e;
		}
	}]), n;
}(U), pn = /* @__PURE__ */ function(e) {
	l(n, e);
	var t = p(n);
	function n() {
		var e;
		d(this, n);
		var r = [...arguments];
		return e = t.call.apply(t, [this].concat(r)), a(c(e), "priority", 80), a(c(e), "incompatibleTokens", [
			"a",
			"b",
			"t",
			"T"
		]), e;
	}
	return u(n, [{
		key: "parse",
		value: function(e, t, n) {
			switch (t) {
				case "B":
				case "BB":
				case "BBB": return n.dayPeriod(e, {
					width: "abbreviated",
					context: "formatting"
				}) || n.dayPeriod(e, {
					width: "narrow",
					context: "formatting"
				});
				case "BBBBB": return n.dayPeriod(e, {
					width: "narrow",
					context: "formatting"
				});
				default: return n.dayPeriod(e, {
					width: "wide",
					context: "formatting"
				}) || n.dayPeriod(e, {
					width: "abbreviated",
					context: "formatting"
				}) || n.dayPeriod(e, {
					width: "narrow",
					context: "formatting"
				});
			}
		}
	}, {
		key: "set",
		value: function(e, t, n) {
			return e.setUTCHours(zt(n), 0, 0, 0), e;
		}
	}]), n;
}(U), mn = /* @__PURE__ */ function(e) {
	l(n, e);
	var t = p(n);
	function n() {
		var e;
		d(this, n);
		var r = [...arguments];
		return e = t.call.apply(t, [this].concat(r)), a(c(e), "priority", 70), a(c(e), "incompatibleTokens", [
			"H",
			"K",
			"k",
			"t",
			"T"
		]), e;
	}
	return u(n, [
		{
			key: "parse",
			value: function(e, t, n) {
				switch (t) {
					case "h": return q(W.hour12h, e);
					case "ho": return n.ordinalNumber(e, { unit: "hour" });
					default: return Y(t.length, e);
				}
			}
		},
		{
			key: "validate",
			value: function(e, t) {
				return t >= 1 && t <= 12;
			}
		},
		{
			key: "set",
			value: function(e, t, n) {
				var r = e.getUTCHours() >= 12;
				return r && n < 12 ? e.setUTCHours(n + 12, 0, 0, 0) : !r && n === 12 ? e.setUTCHours(0, 0, 0, 0) : e.setUTCHours(n, 0, 0, 0), e;
			}
		}
	]), n;
}(U), hn = /* @__PURE__ */ function(e) {
	l(n, e);
	var t = p(n);
	function n() {
		var e;
		d(this, n);
		var r = [...arguments];
		return e = t.call.apply(t, [this].concat(r)), a(c(e), "priority", 70), a(c(e), "incompatibleTokens", [
			"a",
			"b",
			"h",
			"K",
			"k",
			"t",
			"T"
		]), e;
	}
	return u(n, [
		{
			key: "parse",
			value: function(e, t, n) {
				switch (t) {
					case "H": return q(W.hour23h, e);
					case "Ho": return n.ordinalNumber(e, { unit: "hour" });
					default: return Y(t.length, e);
				}
			}
		},
		{
			key: "validate",
			value: function(e, t) {
				return t >= 0 && t <= 23;
			}
		},
		{
			key: "set",
			value: function(e, t, n) {
				return e.setUTCHours(n, 0, 0, 0), e;
			}
		}
	]), n;
}(U), gn = /* @__PURE__ */ function(e) {
	l(n, e);
	var t = p(n);
	function n() {
		var e;
		d(this, n);
		var r = [...arguments];
		return e = t.call.apply(t, [this].concat(r)), a(c(e), "priority", 70), a(c(e), "incompatibleTokens", [
			"h",
			"H",
			"k",
			"t",
			"T"
		]), e;
	}
	return u(n, [
		{
			key: "parse",
			value: function(e, t, n) {
				switch (t) {
					case "K": return q(W.hour11h, e);
					case "Ko": return n.ordinalNumber(e, { unit: "hour" });
					default: return Y(t.length, e);
				}
			}
		},
		{
			key: "validate",
			value: function(e, t) {
				return t >= 0 && t <= 11;
			}
		},
		{
			key: "set",
			value: function(e, t, n) {
				return e.getUTCHours() >= 12 && n < 12 ? e.setUTCHours(n + 12, 0, 0, 0) : e.setUTCHours(n, 0, 0, 0), e;
			}
		}
	]), n;
}(U), _n = /* @__PURE__ */ function(e) {
	l(n, e);
	var t = p(n);
	function n() {
		var e;
		d(this, n);
		var r = [...arguments];
		return e = t.call.apply(t, [this].concat(r)), a(c(e), "priority", 70), a(c(e), "incompatibleTokens", [
			"a",
			"b",
			"h",
			"H",
			"K",
			"t",
			"T"
		]), e;
	}
	return u(n, [
		{
			key: "parse",
			value: function(e, t, n) {
				switch (t) {
					case "k": return q(W.hour24h, e);
					case "ko": return n.ordinalNumber(e, { unit: "hour" });
					default: return Y(t.length, e);
				}
			}
		},
		{
			key: "validate",
			value: function(e, t) {
				return t >= 1 && t <= 24;
			}
		},
		{
			key: "set",
			value: function(e, t, n) {
				var r = n <= 24 ? n % 24 : n;
				return e.setUTCHours(r, 0, 0, 0), e;
			}
		}
	]), n;
}(U), vn = /* @__PURE__ */ function(e) {
	l(n, e);
	var t = p(n);
	function n() {
		var e;
		d(this, n);
		var r = [...arguments];
		return e = t.call.apply(t, [this].concat(r)), a(c(e), "priority", 60), a(c(e), "incompatibleTokens", ["t", "T"]), e;
	}
	return u(n, [
		{
			key: "parse",
			value: function(e, t, n) {
				switch (t) {
					case "m": return q(W.minute, e);
					case "mo": return n.ordinalNumber(e, { unit: "minute" });
					default: return Y(t.length, e);
				}
			}
		},
		{
			key: "validate",
			value: function(e, t) {
				return t >= 0 && t <= 59;
			}
		},
		{
			key: "set",
			value: function(e, t, n) {
				return e.setUTCMinutes(n, 0, 0), e;
			}
		}
	]), n;
}(U), yn = /* @__PURE__ */ function(e) {
	l(n, e);
	var t = p(n);
	function n() {
		var e;
		d(this, n);
		var r = [...arguments];
		return e = t.call.apply(t, [this].concat(r)), a(c(e), "priority", 50), a(c(e), "incompatibleTokens", ["t", "T"]), e;
	}
	return u(n, [
		{
			key: "parse",
			value: function(e, t, n) {
				switch (t) {
					case "s": return q(W.second, e);
					case "so": return n.ordinalNumber(e, { unit: "second" });
					default: return Y(t.length, e);
				}
			}
		},
		{
			key: "validate",
			value: function(e, t) {
				return t >= 0 && t <= 59;
			}
		},
		{
			key: "set",
			value: function(e, t, n) {
				return e.setUTCSeconds(n, 0), e;
			}
		}
	]), n;
}(U), bn = /* @__PURE__ */ function(e) {
	l(n, e);
	var t = p(n);
	function n() {
		var e;
		d(this, n);
		var r = [...arguments];
		return e = t.call.apply(t, [this].concat(r)), a(c(e), "priority", 30), a(c(e), "incompatibleTokens", ["t", "T"]), e;
	}
	return u(n, [{
		key: "parse",
		value: function(e, t) {
			return K(Y(t.length, e), function(e) {
				return Math.floor(e * 10 ** (-t.length + 3));
			});
		}
	}, {
		key: "set",
		value: function(e, t, n) {
			return e.setUTCMilliseconds(n), e;
		}
	}]), n;
}(U), xn = /* @__PURE__ */ function(e) {
	l(n, e);
	var t = p(n);
	function n() {
		var e;
		d(this, n);
		var r = [...arguments];
		return e = t.call.apply(t, [this].concat(r)), a(c(e), "priority", 10), a(c(e), "incompatibleTokens", [
			"t",
			"T",
			"x"
		]), e;
	}
	return u(n, [{
		key: "parse",
		value: function(e, t) {
			switch (t) {
				case "X": return J(G.basicOptionalMinutes, e);
				case "XX": return J(G.basic, e);
				case "XXXX": return J(G.basicOptionalSeconds, e);
				case "XXXXX": return J(G.extendedOptionalSeconds, e);
				default: return J(G.extended, e);
			}
		}
	}, {
		key: "set",
		value: function(e, t, n) {
			return t.timestampIsSet ? e : new Date(e.getTime() - n);
		}
	}]), n;
}(U), Sn = /* @__PURE__ */ function(e) {
	l(n, e);
	var t = p(n);
	function n() {
		var e;
		d(this, n);
		var r = [...arguments];
		return e = t.call.apply(t, [this].concat(r)), a(c(e), "priority", 10), a(c(e), "incompatibleTokens", [
			"t",
			"T",
			"X"
		]), e;
	}
	return u(n, [{
		key: "parse",
		value: function(e, t) {
			switch (t) {
				case "x": return J(G.basicOptionalMinutes, e);
				case "xx": return J(G.basic, e);
				case "xxxx": return J(G.basicOptionalSeconds, e);
				case "xxxxx": return J(G.extendedOptionalSeconds, e);
				default: return J(G.extended, e);
			}
		}
	}, {
		key: "set",
		value: function(e, t, n) {
			return t.timestampIsSet ? e : new Date(e.getTime() - n);
		}
	}]), n;
}(U), Cn = /* @__PURE__ */ function(e) {
	l(n, e);
	var t = p(n);
	function n() {
		var e;
		d(this, n);
		var r = [...arguments];
		return e = t.call.apply(t, [this].concat(r)), a(c(e), "priority", 40), a(c(e), "incompatibleTokens", "*"), e;
	}
	return u(n, [{
		key: "parse",
		value: function(e) {
			return Lt(e);
		}
	}, {
		key: "set",
		value: function(e, t, n) {
			return [/* @__PURE__ */ new Date(n * 1e3), { timestampIsSet: !0 }];
		}
	}]), n;
}(U), wn = /* @__PURE__ */ function(e) {
	l(n, e);
	var t = p(n);
	function n() {
		var e;
		d(this, n);
		var r = [...arguments];
		return e = t.call.apply(t, [this].concat(r)), a(c(e), "priority", 20), a(c(e), "incompatibleTokens", "*"), e;
	}
	return u(n, [{
		key: "parse",
		value: function(e) {
			return Lt(e);
		}
	}, {
		key: "set",
		value: function(e, t, n) {
			return [new Date(n), { timestampIsSet: !0 }];
		}
	}]), n;
}(U), Tn = {
	G: new It(),
	y: new Ht(),
	Y: new Ut(),
	R: new Wt(),
	u: new Gt(),
	Q: new Kt(),
	q: new qt(),
	M: new Jt(),
	L: new Yt(),
	w: new Zt(),
	I: new $t(),
	d: new nn(),
	D: new rn(),
	E: new on(),
	e: new sn(),
	c: new cn(),
	i: new un(),
	a: new dn(),
	b: new fn(),
	B: new pn(),
	h: new mn(),
	H: new hn(),
	K: new gn(),
	k: new _n(),
	m: new vn(),
	s: new yn(),
	S: new bn(),
	X: new xn(),
	x: new Sn(),
	t: new Cn(),
	T: new wn()
}, En = /[yYQqMLwIdDecihHKkms]o|(\w)\1*|''|'(''|[^'])+('|$)|./g, Dn = /P+p+|P+|p+|''|'(''|[^'])+('|$)|./g, On = /^'([^]*?)'?$/, kn = /''/g, An = /\S/, jn = /[a-zA-Z]/;
function Mn(e, n, r, i) {
	var a, o, s, c, l, u, d, f;
	v(3, arguments);
	var p = String(e), m = String(n), h = N(), g = i?.locale ?? h.locale ?? st;
	if (!g.match) throw RangeError("locale must contain match property");
	var b = _(i?.firstWeekContainsDate ?? (i == null || (a = i.locale) == null || (o = a.options) == null ? void 0 : o.firstWeekContainsDate) ?? h.firstWeekContainsDate ?? ((s = h.locale) == null || (c = s.options) == null ? void 0 : c.firstWeekContainsDate) ?? 1);
	if (!(b >= 1 && b <= 7)) throw RangeError("firstWeekContainsDate must be between 1 and 7 inclusively");
	var x = _(i?.weekStartsOn ?? (i == null || (l = i.locale) == null || (u = l.options) == null ? void 0 : u.weekStartsOn) ?? h.weekStartsOn ?? ((d = h.locale) == null || (f = d.options) == null ? void 0 : f.weekStartsOn) ?? 0);
	if (!(x >= 0 && x <= 6)) throw RangeError("weekStartsOn must be between 0 and 6 inclusively");
	if (m === "") return p === "" ? y(r) : /* @__PURE__ */ new Date(NaN);
	var S = {
		firstWeekContainsDate: b,
		weekStartsOn: x,
		locale: g
	}, ee = [new Ft()], te = m.match(Dn).map(function(e) {
		var t = e[0];
		if (t in Ge) {
			var n = Ge[t];
			return n(e, g.formatLong);
		}
		return e;
	}).join("").match(En), ne = [], C = At(te), re;
	try {
		var w = function() {
			var t = re.value;
			!(i != null && i.useAdditionalWeekYearTokens) && Ye(t) && Xe(t, m, e), !(i != null && i.useAdditionalDayOfYearTokens) && Je(t) && Xe(t, m, e);
			var n = t[0], r = Tn[n];
			if (r) {
				var a = r.incompatibleTokens;
				if (Array.isArray(a)) {
					var o = ne.find(function(e) {
						return a.includes(e.token) || e.token === n;
					});
					if (o) throw RangeError(`The format string mustn't contain \`${o.fullToken}\` and \`${t}\` at the same time`);
				} else if (r.incompatibleTokens === "*" && ne.length > 0) throw RangeError(`The format string mustn't contain \`${t}\` and any other token at the same time`);
				ne.push({
					token: n,
					fullToken: t
				});
				var s = r.run(p, t, g.match, S);
				if (!s) return { v: /* @__PURE__ */ new Date(NaN) };
				ee.push(s.setter), p = s.rest;
			} else {
				if (n.match(jn)) throw RangeError("Format string contains an unescaped latin alphabet character `" + n + "`");
				if (t === "''" ? t = "'" : n === "'" && (t = Nn(t)), p.indexOf(t) === 0) p = p.slice(t.length);
				else return { v: /* @__PURE__ */ new Date(NaN) };
			}
		};
		for (C.s(); !(re = C.n()).done;) {
			var ie = w();
			if (t(ie) === "object") return ie.v;
		}
	} catch (e) {
		C.e(e);
	} finally {
		C.f();
	}
	if (p.length > 0 && An.test(p)) return /* @__PURE__ */ new Date(NaN);
	var ae = ee.map(function(e) {
		return e.priority;
	}).sort(function(e, t) {
		return t - e;
	}).filter(function(e, t, n) {
		return n.indexOf(e) === t;
	}).map(function(e) {
		return ee.filter(function(t) {
			return t.priority === e;
		}).sort(function(e, t) {
			return t.subPriority - e.subPriority;
		});
	}).map(function(e) {
		return e[0];
	}), T = y(r);
	if (isNaN(T.getTime())) return /* @__PURE__ */ new Date(NaN);
	var E = ke(T, de(T)), oe = {}, D = At(ae), O;
	try {
		for (D.s(); !(O = D.n()).done;) {
			var se = O.value;
			if (!se.validate(E, S)) return /* @__PURE__ */ new Date(NaN);
			var k = se.set(E, oe, S);
			Array.isArray(k) ? (E = k[0], jt(oe, k[1])) : E = k;
		}
	} catch (e) {
		D.e(e);
	} finally {
		D.f();
	}
	return E;
}
function Nn(e) {
	return e.match(On)[1].replace(kn, "'");
}
function Pn(e, t) {
	v(2, arguments);
	var n = y(e), r = _(t);
	return n.setDate(r), n;
}
function Fn(e, t) {
	v(2, arguments);
	var n = y(e), r = _(t);
	return n.setHours(r), n;
}
function In(e, t) {
	v(2, arguments);
	var n = y(e), r = _(t);
	return n.setMinutes(r), n;
}
function Ln(e, t) {
	v(2, arguments);
	var n = y(e), r = _(t), i = n.getFullYear(), a = n.getDate(), o = /* @__PURE__ */ new Date(0);
	o.setFullYear(i, r, 15), o.setHours(0, 0, 0, 0);
	var s = _t(o);
	return n.setMonth(r, Math.min(a, s)), n;
}
function Rn(e, t) {
	v(2, arguments);
	var n = y(e), r = _(t);
	return n.setSeconds(r), n;
}
function zn(e, t) {
	v(2, arguments);
	var n = y(e), r = _(t);
	return isNaN(n.getTime()) ? /* @__PURE__ */ new Date(NaN) : (n.setFullYear(r), n);
}
function Bn(e) {
	v(1, arguments);
	var t = y(e);
	return t.setDate(1), t.setHours(0, 0, 0, 0), t;
}
function Vn(e, t) {
	var n, r, i, a;
	v(1, arguments);
	var o = N(), s = _(t?.weekStartsOn ?? (t == null || (n = t.locale) == null || (r = n.options) == null ? void 0 : r.weekStartsOn) ?? o.weekStartsOn ?? ((i = o.locale) == null || (a = i.options) == null ? void 0 : a.weekStartsOn) ?? 0);
	if (!(s >= 0 && s <= 6)) throw RangeError("weekStartsOn must be between 0 and 6 inclusively");
	var c = y(e), l = c.getDay(), u = (l < s ? 7 : 0) + l - s;
	return c.setDate(c.getDate() - u), c.setHours(0, 0, 0, 0), c;
}
function Hn(e) {
	v(1, arguments);
	var t = y(e), n = /* @__PURE__ */ new Date(0);
	return n.setFullYear(t.getFullYear(), 0, 1), n.setHours(0, 0, 0, 0), n;
}
function Un(e, t) {
	v(1, arguments);
	var n = _(2);
	if (n !== 2 && n !== 1 && n !== 0) throw RangeError("additionalDigits must be 0, 1 or 2");
	if (!(typeof e == "string" || Object.prototype.toString.call(e) === "[object String]")) return /* @__PURE__ */ new Date(NaN);
	var r = Jn(e), i;
	if (r.date) {
		var a = Yn(r.date, n);
		i = Xn(a.restDateString, a.year);
	}
	if (!i || isNaN(i.getTime())) return /* @__PURE__ */ new Date(NaN);
	var o = i.getTime(), s = 0, c;
	if (r.time && (s = Zn(r.time), isNaN(s))) return /* @__PURE__ */ new Date(NaN);
	if (r.timezone) {
		if (c = $n(r.timezone), isNaN(c)) return /* @__PURE__ */ new Date(NaN);
	} else {
		var l = new Date(o + s), u = /* @__PURE__ */ new Date(0);
		return u.setFullYear(l.getUTCFullYear(), l.getUTCMonth(), l.getUTCDate()), u.setHours(l.getUTCHours(), l.getUTCMinutes(), l.getUTCSeconds(), l.getUTCMilliseconds()), u;
	}
	return new Date(o + s + c);
}
var Wn = {
	dateTimeDelimiter: /[T ]/,
	timeZoneDelimiter: /[Z ]/i,
	timezone: /([Z+-].*)$/
}, Gn = /^-?(?:(\d{3})|(\d{2})(?:-?(\d{2}))?|W(\d{2})(?:-?(\d{1}))?|)$/, Kn = /^(\d{2}(?:[.,]\d*)?)(?::?(\d{2}(?:[.,]\d*)?))?(?::?(\d{2}(?:[.,]\d*)?))?$/, qn = /^([+-])(\d{2})(?::?(\d{2}))?$/;
function Jn(e) {
	var t = {}, n = e.split(Wn.dateTimeDelimiter), r;
	if (n.length > 2) return t;
	if (/:/.test(n[0]) ? r = n[0] : (t.date = n[0], r = n[1], Wn.timeZoneDelimiter.test(t.date) && (t.date = e.split(Wn.timeZoneDelimiter)[0], r = e.substr(t.date.length, e.length))), r) {
		var i = Wn.timezone.exec(r);
		i ? (t.time = r.replace(i[1], ""), t.timezone = i[1]) : t.time = r;
	}
	return t;
}
function Yn(e, t) {
	var n = RegExp("^(?:(\\d{4}|[+-]\\d{" + (4 + t) + "})|(\\d{2}|[+-]\\d{" + (2 + t) + "})$)"), r = e.match(n);
	if (!r) return {
		year: NaN,
		restDateString: ""
	};
	var i = r[1] ? parseInt(r[1]) : null, a = r[2] ? parseInt(r[2]) : null;
	return {
		year: a === null ? i : a * 100,
		restDateString: e.slice((r[1] || r[2]).length)
	};
}
function Xn(e, t) {
	if (t === null) return /* @__PURE__ */ new Date(NaN);
	var n = e.match(Gn);
	if (!n) return /* @__PURE__ */ new Date(NaN);
	var r = !!n[4], i = X(n[1]), a = X(n[2]) - 1, o = X(n[3]), s = X(n[4]), c = X(n[5]) - 1;
	if (r) return ar(t, s, c) ? er(t, s, c) : /* @__PURE__ */ new Date(NaN);
	var l = /* @__PURE__ */ new Date(0);
	return !rr(t, a, o) || !ir(t, i) ? /* @__PURE__ */ new Date(NaN) : (l.setUTCFullYear(t, a, Math.max(i, o)), l);
}
function X(e) {
	return e ? parseInt(e) : 1;
}
function Zn(e) {
	var t = e.match(Kn);
	if (!t) return NaN;
	var n = Qn(t[1]), r = Qn(t[2]), i = Qn(t[3]);
	return or(n, r, i) ? n * _e + r * M + i * 1e3 : NaN;
}
function Qn(e) {
	return e && parseFloat(e.replace(",", ".")) || 0;
}
function $n(e) {
	if (e === "Z") return 0;
	var t = e.match(qn);
	if (!t) return 0;
	var n = t[1] === "+" ? -1 : 1, r = parseInt(t[2]), i = t[3] && parseInt(t[3]) || 0;
	return sr(r, i) ? n * (r * _e + i * M) : NaN;
}
function er(e, t, n) {
	var r = /* @__PURE__ */ new Date(0);
	r.setUTCFullYear(e, 0, 4);
	var i = r.getUTCDay() || 7, a = (t - 1) * 7 + n + 1 - i;
	return r.setUTCDate(r.getUTCDate() + a), r;
}
var tr = [
	31,
	null,
	31,
	30,
	31,
	30,
	31,
	31,
	30,
	31,
	30,
	31
];
function nr(e) {
	return e % 400 == 0 || e % 4 == 0 && e % 100 != 0;
}
function rr(e, t, n) {
	return t >= 0 && t <= 11 && n >= 1 && n <= (tr[t] || (nr(e) ? 29 : 28));
}
function ir(e, t) {
	return t >= 1 && t <= (nr(e) ? 366 : 365);
}
function ar(e, t, n) {
	return t >= 1 && t <= 53 && n >= 0 && n <= 6;
}
function or(e, t, n) {
	return e === 24 ? t === 0 && n === 0 : n >= 0 && n < 60 && t >= 0 && t < 60 && e >= 0 && e < 25;
}
function sr(e, t) {
	return t >= 0 && t <= 59;
}
function cr(e, t) {
	v(1, arguments);
	var n = y(e);
	if (isNaN(n.getTime())) throw RangeError("Invalid time value");
	var r = String(t?.format ?? "extended"), i = String(t?.representation ?? "complete");
	if (r !== "extended" && r !== "basic") throw RangeError("format must be 'extended' or 'basic'");
	if (i !== "date" && i !== "time" && i !== "complete") throw RangeError("representation must be 'date', 'time', or 'complete'");
	var a = "", o = "", s = r === "extended" ? "-" : "", c = r === "extended" ? ":" : "";
	if (i !== "time") {
		var l = I(n.getDate(), 2), u = I(n.getMonth() + 1, 2), d = I(n.getFullYear(), 4);
		a = "".concat(d, s, u, s, l);
	}
	if (i !== "date") {
		var f = n.getTimezoneOffset();
		if (f !== 0) {
			var p = Math.abs(f), m = I(Math.floor(p / 60), 2), h = I(p % 60, 2);
			o = `${f < 0 ? "+" : "-"}${m}:${h}`;
		} else o = "Z";
		var g = I(n.getHours(), 2), _ = I(n.getMinutes(), 2), b = I(n.getSeconds(), 2), x = a === "" ? "" : "T", S = [
			g,
			_,
			b
		].join(c);
		a = `${a}${x}${S}${o}`;
	}
	return a;
}
function lr(e, t) {
	v(2, arguments);
	var n = y(e).getTime(), r = y(t.start).getTime(), i = y(t.end).getTime();
	if (!(r <= i)) throw RangeError("Invalid interval");
	return n >= r && n <= i;
}
var ur = { exports: {} }, dr;
function fr() {
	return dr || (dr = 1, function(e, t) {
		Object.defineProperty(t, "__esModule", { value: !0 }), t.default = void 0;
		var n = function(e, t) {
			switch (e) {
				case "P": return t.date({ width: "short" });
				case "PP": return t.date({ width: "medium" });
				case "PPP": return t.date({ width: "long" });
				default: return t.date({ width: "full" });
			}
		}, r = function(e, t) {
			switch (e) {
				case "p": return t.time({ width: "short" });
				case "pp": return t.time({ width: "medium" });
				case "ppp": return t.time({ width: "long" });
				default: return t.time({ width: "full" });
			}
		};
		t.default = {
			p: r,
			P: function(e, t) {
				var i = e.match(/(P+)(p+)?/) || [], a = i[1], o = i[2];
				if (!o) return n(e, t);
				var s;
				switch (a) {
					case "P":
						s = t.dateTime({ width: "short" });
						break;
					case "PP":
						s = t.dateTime({ width: "medium" });
						break;
					case "PPP":
						s = t.dateTime({ width: "long" });
						break;
					default:
						s = t.dateTime({ width: "full" });
						break;
				}
				return s.replace("{{date}}", n(a, t)).replace("{{time}}", r(o, t));
			}
		}, e.exports = t.default;
	}(ur, ur.exports)), ur.exports;
}
var pr = /* @__PURE__ */ r(/* @__PURE__ */ fr()), mr = {
	dayOfMonth: "d",
	fullDate: "PP",
	fullDateWithWeekday: "PPPP",
	fullDateTime: "PP p",
	fullDateTime12h: "PP hh:mm aaa",
	fullDateTime24h: "PP HH:mm",
	fullTime: "p",
	fullTime12h: "hh:mm aaa",
	fullTime24h: "HH:mm",
	hours12h: "hh",
	hours24h: "HH",
	keyboardDate: "P",
	keyboardDateTime: "P p",
	keyboardDateTime12h: "P hh:mm aaa",
	keyboardDateTime24h: "P HH:mm",
	minutes: "mm",
	month: "LLLL",
	monthAndDate: "MMMM d",
	monthAndYear: "LLLL yyyy",
	monthShort: "MMM",
	weekday: "EEEE",
	weekdayShort: "EEE",
	normalDate: "d MMMM",
	normalDateWithWeekday: "EEE, MMM d",
	seconds: "ss",
	shortDate: "MMM d",
	year: "yyyy"
}, hr = new class {
	constructor({ locale: e, formats: t } = {}) {
		this.lib = "date-fns", this.is12HourCycleInCurrentLocale = () => this.locale ? /a/.test(this.locale.formatLong?.time()) : !0, this.getFormatHelperText = (e) => {
			let t = /P+p+|P+|p+|''|'(''|[^'])+('|$)|./g, n = this.locale || st;
			return e.match(t)?.map((e) => {
				let t = e[0];
				if (t === "p" || t === "P") {
					let r = pr[t];
					return r(e, n.formatLong, {});
				}
				return e;
			}).join("").replace(/(aaa|aa|a)/g, "(a|p)m").toLocaleLowerCase() ?? e;
		}, this.parseISO = (e) => Un(e), this.toISO = (e) => cr(e, { format: "extended" }), this.getCurrentLocaleCode = () => this.locale?.code || "en-US", this.addSeconds = (e, t) => S(e, t), this.addMinutes = (e, t) => te(e, t), this.addHours = (e, t) => C(e, t), this.addDays = (e, t) => b(e, t), this.addWeeks = (e, t) => re(e, t), this.addMonths = (e, t) => w(e, t), this.addYears = (e, t) => ie(e, t), this.isValid = (e) => Oe(this.date(e)), this.getDiff = (e, t, n) => {
			let r = this.date(t) ?? e;
			if (!this.isValid(r)) return 0;
			switch (n) {
				case "years": return E(e, r);
				case "quarters": return ue(e, r);
				case "months": return k(e, r);
				case "weeks": return ge(e, r);
				case "days": return he(e, r);
				case "hours": return be(e, r);
				case "minutes": return xe(e, r);
				case "seconds": return Se(e, r);
				default: return ye(e, r);
			}
		}, this.isAfter = (e, t) => Ct(e, t), this.isBefore = (e, t) => H(e, t), this.startOfDay = (e) => j(e), this.endOfDay = (e) => D(e), this.getHours = (e) => vt(e), this.setHours = (e, t) => Fn(e, t), this.setMinutes = (e, t) => In(e, t), this.getSeconds = (e) => xt(e), this.setSeconds = (e, t) => Rn(e, t), this.isSameDay = (e, t) => Tt(e, t), this.isSameMonth = (e, t) => Dt(e, t), this.isSameYear = (e, t) => Et(e, t), this.isSameHour = (e, t) => kt(e, t), this.startOfYear = (e) => Hn(e), this.endOfYear = (e) => Ee(e), this.startOfMonth = (e) => Bn(e), this.endOfMonth = (e) => O(e), this.startOfWeek = (e) => Vn(e, { locale: this.locale }), this.endOfWeek = (e) => Te(e, { locale: this.locale }), this.getYear = (e) => St(e), this.setYear = (e, t) => zn(e, t), this.date = (e) => typeof e > "u" ? /* @__PURE__ */ new Date() : e === null ? null : new Date(e), this.toJsDate = (e) => e, this.parse = (e, t) => e === "" ? null : Mn(e, t, /* @__PURE__ */ new Date(), { locale: this.locale }), this.format = (e, t) => this.formatByString(e, this.formats[t]), this.formatByString = (e, t) => pt(e, t, { locale: this.locale }), this.isEqual = (e, t) => e === null && t === null ? !0 : wt(e, t), this.isNull = (e) => e === null, this.isAfterDay = (e, t) => Ct(e, D(t)), this.isBeforeDay = (e, t) => H(e, j(t)), this.isBeforeYear = (e, t) => H(e, Hn(t)), this.isAfterYear = (e, t) => Ct(e, Ee(t)), this.isWithinRange = (e, [t, n]) => lr(e, {
			start: t,
			end: n
		}), this.formatNumber = (e) => e, this.getMinutes = (e) => yt(e), this.getDate = (e) => ht(e), this.setDate = (e, t) => Pn(e, t), this.getMonth = (e) => bt(e), this.getDaysInMonth = (e) => _t(e), this.setMonth = (e, t) => Ln(e, t), this.getMeridiemText = (e) => e === "am" ? "AM" : "PM", this.getNextMonth = (e) => w(e, 1), this.getPreviousMonth = (e) => w(e, -1), this.getMonthArray = (e) => {
			let t = [Hn(e)];
			for (; t.length < 12;) {
				let e = t[t.length - 1];
				t.push(this.getNextMonth(e));
			}
			return t;
		}, this.mergeDateAndTime = (e, t) => this.setSeconds(this.setMinutes(this.setHours(e, this.getHours(t)), this.getMinutes(t)), this.getSeconds(t)), this.getWeekdays = () => {
			let e = /* @__PURE__ */ new Date();
			return Ce({
				start: Vn(e, { locale: this.locale }),
				end: Te(e, { locale: this.locale })
			}).map((e) => this.formatByString(e, "EEEEEE"));
		}, this.getWeekArray = (e) => {
			let t = Vn(Bn(e), { locale: this.locale }), n = Te(O(e), { locale: this.locale }), r = 0, i = t, a = [], o = null;
			for (; H(i, n);) {
				let e = Math.floor(r / 7);
				a[e] = a[e] || [];
				let t = gt(i);
				o !== t && (o = t, a[e].push(i), r += 1), i = b(i, 1);
			}
			return a;
		}, this.getYearRange = (e, t) => {
			let n = Hn(e), r = Ee(t), i = [], a = n;
			for (; H(a, r);) i.push(a), a = ie(a, 1);
			return i;
		}, this.locale = e, this.formats = Object.assign({}, mr, t);
	}
	isBeforeMonth(e, t) {
		return H(e, Bn(t));
	}
	isAfterMonth(e, t) {
		return Ct(e, Bn(t));
	}
}({});
function gr(e, t) {
	return xr(e) || br(e, t) || vr(e, t) || _r();
}
function _r() {
	throw TypeError("Invalid attempt to destructure non-iterable instance.\nIn order to be iterable, non-array objects must have a [Symbol.iterator]() method.");
}
function vr(e, t) {
	if (e) {
		if (typeof e == "string") return yr(e, t);
		var n = Object.prototype.toString.call(e).slice(8, -1);
		if (n === "Object" && e.constructor && (n = e.constructor.name), n === "Map" || n === "Set") return Array.from(e);
		if (n === "Arguments" || /^(?:Ui|I)nt(?:8|16|32)(?:Clamped)?Array$/.test(n)) return yr(e, t);
	}
}
function yr(e, t) {
	(t == null || t > e.length) && (t = e.length);
	for (var n = 0, r = Array(t); n < t; n++) r[n] = e[n];
	return r;
}
function br(e, t) {
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
function xr(e) {
	if (Array.isArray(e)) return e;
}
function Sr(e, t) {
	var n = Object.keys(e);
	if (Object.getOwnPropertySymbols) {
		var r = Object.getOwnPropertySymbols(e);
		t && (r = r.filter(function(t) {
			return Object.getOwnPropertyDescriptor(e, t).enumerable;
		})), n.push.apply(n, r);
	}
	return n;
}
function Cr(e) {
	for (var t = 1; t < arguments.length; t++) {
		var n = arguments[t] == null ? {} : arguments[t];
		t % 2 ? Sr(Object(n), !0).forEach(function(t) {
			Z(e, t, n[t]);
		}) : Object.getOwnPropertyDescriptors ? Object.defineProperties(e, Object.getOwnPropertyDescriptors(n)) : Sr(Object(n)).forEach(function(t) {
			Object.defineProperty(e, t, Object.getOwnPropertyDescriptor(n, t));
		});
	}
	return e;
}
function wr(e, t, n) {
	return Object.defineProperty(e, "prototype", { writable: !1 }), e;
}
function Tr(e, t) {
	if (!(e instanceof t)) throw TypeError("Cannot call a class as a function");
}
function Z(e, t, n) {
	return t in e ? Object.defineProperty(e, t, {
		value: n,
		enumerable: !0,
		configurable: !0,
		writable: !0
	}) : e[t] = n, e;
}
var Er = 60, Dr = Er * 60, Or = /* @__PURE__ */ wr(function e(t) {
	var n = this;
	Tr(this, e), Z(this, "adapter", void 0), Z(this, "cloneAdapter", function(e, t) {
		var n = {
			MomentUtils: { formats: {
				monthNumber: "M",
				dayOfMonthNumber: "D",
				fullOrdinalWeek: "dddd, MMMM Do YYYY",
				slashDate: "YYYY/MM/DD",
				weekday: "dddd",
				weekdaymin: "dd",
				quarter: "[Q]Q"
			} },
			DateFnsUtils: { formats: {
				monthNumber: "M",
				dayOfMonthNumber: "d",
				weekday: "EEEE",
				weekdaymin: "EEEEEE",
				slashDate: "yyyy/MM/dd",
				fullOrdinalWeek: "EEEE, MMMM do yyyy",
				quarter: "QQQ"
			} },
			LuxonUtils: { formats: {
				monthNumber: "M",
				dayOfMonthNumber: "d",
				weekday: "EEEE",
				weekdaymin: "EEEEE",
				slashDate: "yyyy/MM/dd",
				fullOrdinalWeek: "EEEE, MMMM dd yyyy",
				quarter: "Qq"
			} }
		}, r = function(e) {
			return {
				formats: e.formats,
				locale: e.locale
			};
		}, i = t || r, a = e.constructor, o = n[e.constructor.name] || n.DateFnsUtils, s = o.getOptions, c = s === void 0 ? r : s, l = o.formats, u = c(e);
		return new a(Object.assign({}, i(Object.assign({}, u, { formats: Object.assign({}, u.formats, l) }))));
	}), Z(this, "format", function(e, t, r) {
		return (r ? n.getAdapterWithNewLocale(r) : n.adapter).format(e, t);
	}), Z(this, "getAdapterWithNewLocale", function(e) {
		return n.cloneAdapter(n.adapter, function(t) {
			return Cr(Cr({}, t), {}, { locale: e });
		});
	}), Z(this, "date", function(e) {
		return n.adapter.date(e);
	}), Z(this, "dateToSeconds", function(e) {
		var t = n.adapter.getSeconds(e), r = n.adapter.getMinutes(e) * Er, i = n.adapter.getHours(e) * Dr;
		return t + r + i;
	}), Z(this, "secondsToHourMinute", function(e) {
		var t = n.adapter.toJsDate(n.adapter.date(e * 1e3));
		return [t.getUTCHours(), t.getUTCMinutes()];
	}), Z(this, "differenceInCalendarMonths", function(e, t) {
		var r = n.adapter.getYear(e) - n.adapter.getYear(t), i = n.adapter.getMonth(e) - n.adapter.getMonth(t);
		return r * 12 + i;
	}), Z(this, "getStartOfWeek", function(e, t) {
		var r = t ? n.getAdapterWithNewLocale(t) : n.adapter;
		return r.startOfWeek(r.date(e));
	}), Z(this, "formatDate", function(e, t, r) {
		return (r ? n.getAdapterWithNewLocale(r) : n.adapter).formatByString(e, t);
	}), Z(this, "getWeekdayMinInLocale", function(e, t) {
		return n.getAdapterWithNewLocale(t).format(e, "weekdaymin");
	}), Z(this, "getMonthInLocale", function(e, t) {
		var r = n.getAdapterWithNewLocale(t);
		return r.format(r.setMonth(r.date(), e), "month");
	}), Z(this, "getWeekdayInLocale", function(e, t) {
		return n.getAdapterWithNewLocale(t).format(e, "weekday");
	}), Z(this, "getQuarterInLocale", function(e, t) {
		var r = n.getAdapterWithNewLocale(t);
		return r.format(r.setMonth(r.date(), e * 3), "quarter");
	}), Z(this, "getEndOfWeek", function(e) {
		return n.adapter.endOfWeek(e);
	}), Z(this, "getDay", function(e) {
		return Number(n.adapter.formatByString(e, "e")) - 1;
	}), Z(this, "addWeeks", function(e, t) {
		return n.adapter.addDays(e, t * 7);
	}), Z(this, "subWeeks", function(e, t) {
		return n.addWeeks(e, t * -1);
	}), Z(this, "addYears", function(e, t) {
		return n.adapter.addMonths(e, t * 12);
	}), Z(this, "subYears", function(e, t) {
		return n.addYears(e, t * -1);
	}), Z(this, "isSameYear", function(e, t) {
		return e && t ? n.adapter.isSameYear(e, t) : !1;
	}), Z(this, "isStartOfMonth", function(e) {
		return n.adapter.isSameDay(e, n.adapter.startOfMonth(e));
	}), Z(this, "isEndOfMonth", function(e) {
		return n.adapter.isSameDay(e, n.adapter.endOfMonth(e));
	}), Z(this, "isDayInRange", function(e, t, r) {
		return n.adapter.isWithinRange(e, [t, r]);
	}), Z(this, "isSameDay", function(e, t) {
		return e && t ? n.adapter.isSameDay(e, t) : !1;
	}), Z(this, "isSameMonth", function(e, t) {
		return e && t ? n.adapter.isSameMonth(e, t) : !1;
	}), Z(this, "dateRangeIncludesDates", function(e, t) {
		var r = gr(e, 2), i = r[0], a = r[1];
		if (i && a && Array.isArray(t) && t.length) for (var o = 0; o < t.length; o++) {
			var s = t[o];
			if (n.isDayInRange(s, i, a)) return !0;
		}
		return !1;
	}), Z(this, "subDays", function(e, t) {
		return n.adapter.addDays(e, t * -1);
	}), Z(this, "subMonths", function(e, t) {
		return n.adapter.addMonths(e, t * -1);
	}), Z(this, "min", function(e) {
		return e.reduce(function(e, t) {
			return n.adapter.isBefore(t, e) ? t : e;
		});
	}), Z(this, "max", function(e) {
		return e.reduce(function(e, t) {
			return n.adapter.isAfter(t, e) ? t : e;
		});
	}), Z(this, "getEffectiveMinDate", function(e) {
		var t = e.minDate, r = e.includeDates;
		if (r && t) {
			var i = r.filter(function(e) {
				return n.isOnOrAfterDay(e, t);
			});
			return n.min(i);
		} else {
			if (r && r.length) return n.min(r);
			if (!(r && r.length) && t) return t;
		}
		return n.adapter.date();
	}), Z(this, "getEffectiveMaxDate", function(e) {
		var t = e.maxDate, r = e.includeDates;
		if (r && t) {
			var i = r.filter(function(e) {
				return n.isOnOrBeforeDay(e, t);
			});
			return n.max(i);
		} else {
			if (r) return n.max(r);
			if (!r && t) return t;
		}
		return n.adapter.date();
	}), Z(this, "monthDisabledBefore", function(e) {
		var t = arguments.length > 1 && arguments[1] !== void 0 ? arguments[1] : {}, r = t.minDate, i = t.includeDates, a = n.subMonths(e, 1);
		return !!r && n.differenceInCalendarMonths(r, a) > 0 || !!i && i.every(function(e) {
			return n.differenceInCalendarMonths(e, a) > 0;
		}) || !1;
	}), Z(this, "monthDisabledAfter", function(e) {
		var t = arguments.length > 1 && arguments[1] !== void 0 ? arguments[1] : {}, r = t.maxDate, i = t.includeDates, a = n.adapter.addMonths(e, 1);
		return !!r && n.differenceInCalendarMonths(a, r) > 0 || !!i && i.every(function(e) {
			return n.differenceInCalendarMonths(a, e) > 0;
		}) || !1;
	}), Z(this, "setDate", function(e, t) {
		var r = n.adapter.startOfMonth(e), i = n.adapter.mergeDateAndTime(r, e), a = n.adapter.setSeconds(i, n.adapter.getSeconds(e));
		return n.adapter.addDays(a, t - 1);
	}), Z(this, "getDate", function(e) {
		return Number(n.adapter.format(e, "dayOfMonthNumber"));
	}), Z(this, "applyDateToTime", function(e, t) {
		if (!e) return t;
		var r = n.adapter.getYear(t), i = n.adapter.getMonth(t), a = n.getDate(t), o = n.adapter.setYear(e, r), s = n.adapter.setMonth(o, i);
		return n.setDate(s, a);
	}), Z(this, "applyTimeToDate", function(e, t) {
		return e ? n.adapter.setSeconds(n.adapter.mergeDateAndTime(e, t), 0) : t;
	}), Z(this, "isDayDisabled", function(e) {
		var t = arguments.length > 1 && arguments[1] !== void 0 ? arguments[1] : {}, r = t.minDate, i = t.maxDate, a = t.excludeDates, o = t.includeDates, s = t.filterDate;
		return n.isOutOfBounds(e, {
			minDate: r,
			maxDate: i
		}) || a && a.some(function(t) {
			return n.adapter.isSameDay(e, t);
		}) || o && !o.some(function(t) {
			return n.adapter.isSameDay(e, t);
		}) || s && !s(e) || !1;
	}), Z(this, "isOnOrAfterDay", function(e, t) {
		return n.adapter.isSameDay(e, t) ? !0 : n.adapter.isAfter(e, t);
	}), Z(this, "isOnOrBeforeDay", function(e, t) {
		return n.adapter.isSameDay(e, t) ? !0 : n.adapter.isBefore(e, t);
	}), Z(this, "isOutOfBounds", function(e) {
		var t = arguments.length > 1 && arguments[1] !== void 0 ? arguments[1] : {}, r = t.minDate, i = t.maxDate;
		return !!r && !n.isOnOrAfterDay(e, r) || !!i && !n.isOnOrBeforeDay(e, i);
	}), Z(this, "parseString", function(e, t, r) {
		return (r ? n.getAdapterWithNewLocale(r) : n.adapter).parse(e, t);
	}), Z(this, "parse", function(e, t, r) {
		var i = r ? n.getAdapterWithNewLocale(r) : n.adapter;
		return i.parse(e, i.formats[t]);
	}), Z(this, "setMilliseconds", function(e, t) {
		return n.adapter.date(n.adapter.getSeconds(n.adapter.startOfDay(e)) * 1e3 + t);
	}), Z(this, "set", function(e, t) {
		var r = e;
		return t.year != null && (r = n.setYear(r, t.year)), t.month != null && (r = n.setMonth(r, t.month)), t.date != null && (r = n.setDate(r, Number(t.date))), t.hours != null && (r = n.setHours(r, Number(t.hours))), t.minutes != null && (r = n.setMinutes(r, Number(t.minutes))), t.seconds != null && (r = n.setSeconds(r, Number(t.seconds))), r;
	}), Z(this, "getQuarter", function(e) {
		return Math.floor(n.getMonth(e) / 3) + 1;
	}), Z(this, "setSeconds", function(e, t) {
		return n.adapter.setSeconds(e, t);
	}), Z(this, "setMinutes", function(e, t) {
		return n.adapter.setMinutes(e, t);
	}), Z(this, "setHours", function(e, t) {
		return n.adapter.setHours(e, t);
	}), Z(this, "setMonth", function(e, t) {
		return n.adapter.setMonth(e, t);
	}), Z(this, "setYear", function(e, t) {
		return n.adapter.setYear(e, t);
	}), Z(this, "getMinutes", function(e) {
		return n.adapter.getMinutes(e);
	}), Z(this, "getHours", function(e) {
		return n.adapter.getHours(e);
	}), Z(this, "getMonth", function(e) {
		return n.adapter.getMonth(e);
	}), Z(this, "getYear", function(e) {
		return n.adapter.getYear(e);
	}), Z(this, "getStartOfMonth", function(e) {
		return n.adapter.startOfMonth(e);
	}), Z(this, "getEndOfMonth", function(e) {
		return n.adapter.endOfMonth(e);
	}), Z(this, "addDays", function(e, t) {
		return n.adapter.addDays(e, t);
	}), Z(this, "addMonths", function(e, t) {
		return n.adapter.addMonths(e, t);
	}), Z(this, "isBefore", function(e, t) {
		return n.adapter.isBefore(e, t);
	}), Z(this, "isAfter", function(e, t) {
		return n.adapter.isAfter(e, t);
	}), Z(this, "isEqual", function(e, t) {
		return n.adapter.isEqual(e, t);
	}), Z(this, "isValid", function(e) {
		return n.adapter.isValid(e);
	}), this.adapter = this.cloneAdapter(t);
});
function kr(e) {
	"@babel/helpers - typeof";
	return kr = typeof Symbol == "function" && typeof Symbol.iterator == "symbol" ? function(e) {
		return typeof e;
	} : function(e) {
		return e && typeof Symbol == "function" && e.constructor === Symbol && e !== Symbol.prototype ? "symbol" : typeof e;
	}, kr(e);
}
function Ar() {
	return Ar = Object.assign ? Object.assign.bind() : function(e) {
		for (var t = 1; t < arguments.length; t++) {
			var n = arguments[t];
			for (var r in n) Object.prototype.hasOwnProperty.call(n, r) && (e[r] = n[r]);
		}
		return e;
	}, Ar.apply(this, arguments);
}
function jr(e, t) {
	return Ir(e) || Fr(e, t) || Nr(e, t) || Mr();
}
function Mr() {
	throw TypeError("Invalid attempt to destructure non-iterable instance.\nIn order to be iterable, non-array objects must have a [Symbol.iterator]() method.");
}
function Nr(e, t) {
	if (e) {
		if (typeof e == "string") return Pr(e, t);
		var n = Object.prototype.toString.call(e).slice(8, -1);
		if (n === "Object" && e.constructor && (n = e.constructor.name), n === "Map" || n === "Set") return Array.from(e);
		if (n === "Arguments" || /^(?:Ui|I)nt(?:8|16|32)(?:Clamped)?Array$/.test(n)) return Pr(e, t);
	}
}
function Pr(e, t) {
	(t == null || t > e.length) && (t = e.length);
	for (var n = 0, r = Array(t); n < t; n++) r[n] = e[n];
	return r;
}
function Fr(e, t) {
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
function Ir(e) {
	if (Array.isArray(e)) return e;
}
function Lr(e, t) {
	if (!(e instanceof t)) throw TypeError("Cannot call a class as a function");
}
function Rr(e, t) {
	for (var n = 0; n < t.length; n++) {
		var r = t[n];
		r.enumerable = r.enumerable || !1, r.configurable = !0, "value" in r && (r.writable = !0), Object.defineProperty(e, r.key, r);
	}
}
function zr(e, t, n) {
	return t && Rr(e.prototype, t), Object.defineProperty(e, "prototype", { writable: !1 }), e;
}
function Br(e, t) {
	if (typeof t != "function" && t !== null) throw TypeError("Super expression must either be null or a function");
	e.prototype = Object.create(t && t.prototype, { constructor: {
		value: e,
		writable: !0,
		configurable: !0
	} }), Object.defineProperty(e, "prototype", { writable: !1 }), t && Vr(e, t);
}
function Vr(e, t) {
	return Vr = Object.setPrototypeOf ? Object.setPrototypeOf.bind() : function(e, t) {
		return e.__proto__ = t, e;
	}, Vr(e, t);
}
function Hr(e) {
	var t = Wr();
	return function() {
		var n = Gr(e), r;
		if (t) {
			var i = Gr(this).constructor;
			r = Reflect.construct(n, arguments, i);
		} else r = n.apply(this, arguments);
		return Ur(this, r);
	};
}
function Ur(e, t) {
	if (t && (kr(t) === "object" || typeof t == "function")) return t;
	if (t !== void 0) throw TypeError("Derived constructors may only return object or undefined");
	return Q(e);
}
function Q(e) {
	if (e === void 0) throw ReferenceError("this hasn't been initialised - super() hasn't been called");
	return e;
}
function Wr() {
	if (typeof Reflect > "u" || !Reflect.construct || Reflect.construct.sham) return !1;
	if (typeof Proxy == "function") return !0;
	try {
		return Boolean.prototype.valueOf.call(Reflect.construct(Boolean, [], function() {})), !0;
	} catch {
		return !1;
	}
}
function Gr(e) {
	return Gr = Object.setPrototypeOf ? Object.getPrototypeOf.bind() : function(e) {
		return e.__proto__ || Object.getPrototypeOf(e);
	}, Gr(e);
}
function $(e, t, n) {
	return t in e ? Object.defineProperty(e, t, {
		value: n,
		enumerable: !0,
		configurable: !0,
		writable: !0
	}) : e[t] = n, e;
}
var Kr = 3600 * 24 / 2, qr = /* @__PURE__ */ function(t) {
	Br(r, t);
	var n = Hr(r);
	function r(e) {
		var t;
		return Lr(this, r), t = n.call(this, e), $(Q(t), "dateHelpers", void 0), $(Q(t), "state", {
			steps: [],
			value: null
		}), $(Q(t), "onChange", function(e) {
			if (t.setState({ value: e.value[0] }), e.value.length === 0) {
				t.props.nullable && t.props.onChange && t.props.onChange(null);
				return;
			}
			var n = typeof e.value[0].id == "string" ? parseInt(e.value[0].id, 10) : e.value[0].id || 0;
			t.handleChange(n);
		}), $(Q(t), "secondsToLabel", function(e, n) {
			var r = jr(t.dateHelpers.secondsToHourMinute(e), 2), i = r[0], a = r[1], o = function(e) {
				return e < 10 ? `0${e}` : e;
			};
			if (n === "12") {
				var s = e >= Kr;
				return s && (i -= 12), i === 0 && (i = 12), `${i}:${o(a)} ${s ? "PM" : "AM"}`;
			}
			return `${o(i)}:${o(a)}`;
		}), $(Q(t), "stringToOptions", function(e) {
			var n = arguments.length > 1 && arguments[1] !== void 0 ? arguments[1] : "12", r = n === "12" ? /^(1[0-2]|0?[1-9]):([0-5][0-9]) ?([AaPp][Mm]?)?$/ : /^([0-9]|0[0-9]|1[0-9]|2[0-3]):([0-5][0-9])$/, i = e.match(r);
			if (!i) return [];
			var a = Number(i[1]), o = Number(i[2]), s = [];
			switch (n) {
				case "24":
					s = [{
						hours: a,
						minutes: o
					}];
					break;
				default:
					var c = a % 12, l = i[3];
					s = l ? [{
						hours: l.toLowerCase()[0] === "a" ? c : c + 12,
						minutes: o
					}] : [{
						hours: c,
						minutes: o
					}, {
						hours: c + 12,
						minutes: o
					}];
					break;
			}
			return s.map(function(e) {
				var r = e.hours, i = e.minutes, a = r * 3600 + i * 60;
				return {
					id: a,
					label: t.secondsToLabel(a, n)
				};
			});
		}), $(Q(t), "handleChange", function(e) {
			var n = jr(t.dateHelpers.secondsToHourMinute(e), 2), r = n[0], i = n[1], a = t.setTime(t.props.value, r, i, 0);
			t.props.onChange && t.props.onChange(a);
		}), $(Q(t), "setTime", function(e, n, r, i) {
			var a = t.dateHelpers, o = a.setSeconds, s = a.setMinutes, c = a.setHours;
			return o(s(c(t.props.adapter.startOfDay(t.props.adapter.date(e || void 0)), n), r), i);
		}), $(Q(t), "getTimeWindowInSeconds", function(e) {
			var n = t.props, r = n.minTime, i = n.maxTime, a = n.ignoreMinMaxDateComponent, o = t.setTime(t.props.value, 0, 0, 0), s = t.setTime(t.props.value, 24, 0, 0);
			r = !r || t.props.adapter.isBefore(r, o) && !a ? o : t.setTime(t.props.value, t.props.adapter.getHours(r), t.props.adapter.getMinutes(r), t.props.adapter.getSeconds(r)), i = !i || t.props.adapter.isAfter(i, s) && !a ? s : t.setTime(t.props.value, t.props.adapter.getHours(i), t.props.adapter.getMinutes(i), t.props.adapter.getSeconds(i) + 1);
			var c = t.props.adapter.toJsDate(r), l = t.props.adapter.toJsDate(i), u = t.props.adapter.toJsDate(o);
			return {
				start: (c - u) / 1e3,
				end: (l - u) / 1e3
			};
		}), $(Q(t), "buildSteps", function() {
			var e = t.props.step, n = e === void 0 ? 900 : e, r = t.getTimeWindowInSeconds(n), i = (r.end - r.start) / n;
			Number.isInteger(i) || (i = Math.round(i));
			for (var a = [], o = r.start; o < r.end; o += n) a.push(o);
			return a;
		}), $(Q(t), "creatableFilterOptions", function(e, n, r, i) {
			var a = t.stringToOptions(n, t.props.format);
			return a.length ? a : m(e, n, r, i);
		}), $(Q(t), "buildSelectedOption", function(e) {
			var n = arguments.length > 1 && arguments[1] !== void 0 ? arguments[1] : "12", r = t.dateHelpers.dateToSeconds(e);
			return {
				id: r,
				label: t.secondsToLabel(r, n || "12")
			};
		}), t.dateHelpers = new Or(e.adapter), t;
	}
	return zr(r, [
		{
			key: "componentDidMount",
			value: function() {
				var e = this.buildSteps();
				if (this.props.value && this.props.adapter.isValid(this.props.value)) this.setState({
					steps: e,
					value: this.buildSelectedOption(this.props.value, this.props.format)
				});
				else {
					var t = this.dateHelpers.dateToSeconds(this.props.adapter.date()), n = Kr;
					e.forEach(function(e) {
						Math.abs(e - t) < Math.abs(n - t) && (n = e);
					}), this.setState({
						steps: e,
						value: this.props.nullable ? void 0 : {
							id: n,
							label: this.secondsToLabel(n, this.props.format)
						}
					}), (this.props.value || !this.props.nullable && !this.props.value) && this.handleChange(n);
				}
			}
		},
		{
			key: "componentDidUpdate",
			value: function(e) {
				var t = e.format !== this.props.format, n = e.step !== this.props.step, r = e.adapter !== this.props.adapter, i = e.minTime !== this.props.minTime, a = e.maxTime !== this.props.maxTime;
				if (r && (this.dateHelpers = new Or(this.props.adapter)), t || n || i || a) {
					var o = this.buildSteps();
					this.setState({ steps: o });
				}
				e.value && !this.props.value && this.setState({ value: null });
			}
		},
		{
			key: "render",
			value: function() {
				var t = this, n = this.props, r = n.format, i = n.overrides, a = i === void 0 ? {} : i, c = n.adapter, l = jr(s(a.Select, h), 2), u = l[0], d = l[1];
				d.overrides = o({ Dropdown: { style: { maxHeight: "126px" } } }, d.overrides);
				var f = this.props.value && c.isValid(this.props.value) ? this.buildSelectedOption(this.props.value, this.props.format) : this.state.value;
				return /* @__PURE__ */ g.createElement(e.Consumer, null, function(e) {
					var n = r === "12" ? e.datepicker.timePickerAriaLabel12Hour : e.datepicker.timePickerAriaLabel24Hour;
					return /* @__PURE__ */ g.createElement(u, Ar({
						"aria-label": n,
						disabled: t.props.disabled,
						error: t.props.error,
						positive: t.props.positive,
						size: t.props.size,
						placeholder: t.props.placeholder || "HH:mm",
						options: t.state.steps.map(function(e) {
							return {
								id: e,
								label: t.secondsToLabel(e, t.props.format)
							};
						}),
						filterOptions: t.props.creatable ? t.creatableFilterOptions : void 0,
						onChange: t.onChange,
						value: f && [f],
						clearable: !1,
						backspaceRemoves: !1,
						valueKey: "label"
					}, d));
				});
			}
		}
	]), r;
}(g.Component);
$(qr, "defaultProps", {
	format: "12",
	step: 900,
	creatable: !1,
	adapter: hr,
	ignoreMinMaxDateComponent: !1
});
//#endregion
export { qr as n, hr as r, Or as t };

//# sourceMappingURL=timepicker-Bp949u0W-KUvR56zU.js.map