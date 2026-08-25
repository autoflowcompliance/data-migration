import { Cn as e, J as t, Ka as n, N as r, P as i, Pt as a, Ua as o, Un as s, Ur as c, dt as l, ii as ee, ma as u, nr as te, q as ne, sr as d, ti as f, z as re } from "./index-Dl4ETd_L-D2oMd1k2.js";
import { n as p } from "./moment-C29_LcvN-Dw52XTOQ.js";
import { t as ie } from "./WidgetLabel-CQfHGtry-udktvHE5.js";
import { t as ae } from "./WidgetLabelHelpIcon-C6IRqJ_I-BBI6AbZ-.js";
import { n as oe } from "./useBasicWidgetState-D3zHnRUK-Dsaz4YO6.js";
import { t as se } from "./ErrorOutline.esm-YgtldkCQ-yEmqiuMG.js";
import { i as ce, n as le, r as m, t as ue } from "./useIntlLocale-DdLGxiZO-BQljgqPP.js";
//#region ../react/build/DateInput-DY0AqEEz.js
var h = /* @__PURE__ */ n(o(), 1), g = 6048e5, _ = 864e5, v = /* @__PURE__ */ Symbol.for("constructDateFrom");
function y(e, t) {
	return typeof e == "function" ? e(t) : e && typeof e == "object" && v in e ? e[v](t) : e instanceof Date ? new e.constructor(t) : new Date(t);
}
function b(e, t) {
	return y(t || e, e);
}
var x = {};
function S() {
	return x;
}
function C(e, t) {
	let n = S(), r = t?.weekStartsOn ?? t?.locale?.options?.weekStartsOn ?? n.weekStartsOn ?? n.locale?.options?.weekStartsOn ?? 0, i = b(e, t?.in), a = i.getDay(), o = (a < r ? 7 : 0) + a - r;
	return i.setDate(i.getDate() - o), i.setHours(0, 0, 0, 0), i;
}
function w(e, t) {
	return C(e, {
		...t,
		weekStartsOn: 1
	});
}
function T(e, t) {
	let n = b(e, t?.in), r = n.getFullYear(), i = y(n, 0);
	i.setFullYear(r + 1, 0, 4), i.setHours(0, 0, 0, 0);
	let a = w(i), o = y(n, 0);
	o.setFullYear(r, 0, 4), o.setHours(0, 0, 0, 0);
	let s = w(o);
	return n.getTime() >= a.getTime() ? r + 1 : n.getTime() >= s.getTime() ? r : r - 1;
}
function E(e) {
	let t = b(e), n = new Date(Date.UTC(t.getFullYear(), t.getMonth(), t.getDate(), t.getHours(), t.getMinutes(), t.getSeconds(), t.getMilliseconds()));
	return n.setUTCFullYear(t.getFullYear()), e - +n;
}
function D(e, ...t) {
	let n = y.bind(null, t.find((e) => typeof e == "object"));
	return t.map(n);
}
function O(e, t) {
	let n = b(e, t?.in);
	return n.setHours(0, 0, 0, 0), n;
}
function k(e, t, n) {
	let [r, i] = D(n?.in, e, t), a = O(r), o = O(i), s = +a - E(a), c = +o - E(o);
	return Math.round((s - c) / _);
}
function A(e, t) {
	let n = T(e, t), r = y(e, 0);
	return r.setFullYear(n, 0, 4), r.setHours(0, 0, 0, 0), w(r);
}
function j(e) {
	return e instanceof Date || typeof e == "object" && Object.prototype.toString.call(e) === "[object Date]";
}
function M(e) {
	return !(!j(e) && typeof e != "number" || isNaN(+b(e)));
}
function N(e, t) {
	let n = b(e, t?.in);
	return n.setFullYear(n.getFullYear(), 0, 1), n.setHours(0, 0, 0, 0), n;
}
function P(e, t) {
	let n = b(e, t?.in);
	return k(n, N(n)) + 1;
}
function F(e, t) {
	let n = b(e, t?.in), r = w(n) - +A(n);
	return Math.round(r / g) + 1;
}
function I(e, t) {
	let n = b(e, t?.in), r = n.getFullYear(), i = S(), a = t?.firstWeekContainsDate ?? t?.locale?.options?.firstWeekContainsDate ?? i.firstWeekContainsDate ?? i.locale?.options?.firstWeekContainsDate ?? 1, o = y(t?.in || e, 0);
	o.setFullYear(r + 1, 0, a), o.setHours(0, 0, 0, 0);
	let s = C(o, t), c = y(t?.in || e, 0);
	c.setFullYear(r, 0, a), c.setHours(0, 0, 0, 0);
	let l = C(c, t);
	return +n >= +s ? r + 1 : +n >= +l ? r : r - 1;
}
function L(e, t) {
	let n = S(), r = t?.firstWeekContainsDate ?? t?.locale?.options?.firstWeekContainsDate ?? n.firstWeekContainsDate ?? n.locale?.options?.firstWeekContainsDate ?? 1, i = I(e, t), a = y(t?.in || e, 0);
	return a.setFullYear(i, 0, r), a.setHours(0, 0, 0, 0), C(a, t);
}
function R(e, t) {
	let n = b(e, t?.in), r = C(n, t) - +L(n, t);
	return Math.round(r / g) + 1;
}
function z(e, t) {
	return (e < 0 ? "-" : "") + Math.abs(e).toString().padStart(t, "0");
}
var B = {
	y(e, t) {
		let n = e.getFullYear(), r = n > 0 ? n : 1 - n;
		return z(t === "yy" ? r % 100 : r, t.length);
	},
	M(e, t) {
		let n = e.getMonth();
		return t === "M" ? String(n + 1) : z(n + 1, 2);
	},
	d(e, t) {
		return z(e.getDate(), t.length);
	},
	a(e, t) {
		let n = e.getHours() / 12 >= 1 ? "pm" : "am";
		switch (t) {
			case "a":
			case "aa": return n.toUpperCase();
			case "aaa": return n;
			case "aaaaa": return n[0];
			default: return n === "am" ? "a.m." : "p.m.";
		}
	},
	h(e, t) {
		return z(e.getHours() % 12 || 12, t.length);
	},
	H(e, t) {
		return z(e.getHours(), t.length);
	},
	m(e, t) {
		return z(e.getMinutes(), t.length);
	},
	s(e, t) {
		return z(e.getSeconds(), t.length);
	},
	S(e, t) {
		let n = t.length, r = e.getMilliseconds();
		return z(Math.trunc(r * 10 ** (n - 3)), t.length);
	}
}, V = {
	midnight: "midnight",
	noon: "noon",
	morning: "morning",
	afternoon: "afternoon",
	evening: "evening",
	night: "night"
}, H = {
	G: function(e, t, n) {
		let r = +(e.getFullYear() > 0);
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
			let t = e.getFullYear(), r = t > 0 ? t : 1 - t;
			return n.ordinalNumber(r, { unit: "year" });
		}
		return B.y(e, t);
	},
	Y: function(e, t, n, r) {
		let i = I(e, r), a = i > 0 ? i : 1 - i;
		return t === "YY" ? z(a % 100, 2) : t === "Yo" ? n.ordinalNumber(a, { unit: "year" }) : z(a, t.length);
	},
	R: function(e, t) {
		return z(T(e), t.length);
	},
	u: function(e, t) {
		return z(e.getFullYear(), t.length);
	},
	Q: function(e, t, n) {
		let r = Math.ceil((e.getMonth() + 1) / 3);
		switch (t) {
			case "Q": return String(r);
			case "QQ": return z(r, 2);
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
		let r = Math.ceil((e.getMonth() + 1) / 3);
		switch (t) {
			case "q": return String(r);
			case "qq": return z(r, 2);
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
		let r = e.getMonth();
		switch (t) {
			case "M":
			case "MM": return B.M(e, t);
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
		let r = e.getMonth();
		switch (t) {
			case "L": return String(r + 1);
			case "LL": return z(r + 1, 2);
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
		let i = R(e, r);
		return t === "wo" ? n.ordinalNumber(i, { unit: "week" }) : z(i, t.length);
	},
	I: function(e, t, n) {
		let r = F(e);
		return t === "Io" ? n.ordinalNumber(r, { unit: "week" }) : z(r, t.length);
	},
	d: function(e, t, n) {
		return t === "do" ? n.ordinalNumber(e.getDate(), { unit: "date" }) : B.d(e, t);
	},
	D: function(e, t, n) {
		let r = P(e);
		return t === "Do" ? n.ordinalNumber(r, { unit: "dayOfYear" }) : z(r, t.length);
	},
	E: function(e, t, n) {
		let r = e.getDay();
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
		let i = e.getDay(), a = (i - r.weekStartsOn + 8) % 7 || 7;
		switch (t) {
			case "e": return String(a);
			case "ee": return z(a, 2);
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
		let i = e.getDay(), a = (i - r.weekStartsOn + 8) % 7 || 7;
		switch (t) {
			case "c": return String(a);
			case "cc": return z(a, t.length);
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
		let r = e.getDay(), i = r === 0 ? 7 : r;
		switch (t) {
			case "i": return String(i);
			case "ii": return z(i, t.length);
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
		let r = e.getHours() / 12 >= 1 ? "pm" : "am";
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
		let r = e.getHours(), i;
		switch (i = r === 12 ? V.noon : r === 0 ? V.midnight : r / 12 >= 1 ? "pm" : "am", t) {
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
		let r = e.getHours(), i;
		switch (i = r >= 17 ? V.evening : r >= 12 ? V.afternoon : r >= 4 ? V.morning : V.night, t) {
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
			let t = e.getHours() % 12;
			return t === 0 && (t = 12), n.ordinalNumber(t, { unit: "hour" });
		}
		return B.h(e, t);
	},
	H: function(e, t, n) {
		return t === "Ho" ? n.ordinalNumber(e.getHours(), { unit: "hour" }) : B.H(e, t);
	},
	K: function(e, t, n) {
		let r = e.getHours() % 12;
		return t === "Ko" ? n.ordinalNumber(r, { unit: "hour" }) : z(r, t.length);
	},
	k: function(e, t, n) {
		let r = e.getHours();
		return r === 0 && (r = 24), t === "ko" ? n.ordinalNumber(r, { unit: "hour" }) : z(r, t.length);
	},
	m: function(e, t, n) {
		return t === "mo" ? n.ordinalNumber(e.getMinutes(), { unit: "minute" }) : B.m(e, t);
	},
	s: function(e, t, n) {
		return t === "so" ? n.ordinalNumber(e.getSeconds(), { unit: "second" }) : B.s(e, t);
	},
	S: function(e, t) {
		return B.S(e, t);
	},
	X: function(e, t, n) {
		let r = e.getTimezoneOffset();
		if (r === 0) return "Z";
		switch (t) {
			case "X": return W(r);
			case "XXXX":
			case "XX": return G(r);
			default: return G(r, ":");
		}
	},
	x: function(e, t, n) {
		let r = e.getTimezoneOffset();
		switch (t) {
			case "x": return W(r);
			case "xxxx":
			case "xx": return G(r);
			default: return G(r, ":");
		}
	},
	O: function(e, t, n) {
		let r = e.getTimezoneOffset();
		switch (t) {
			case "O":
			case "OO":
			case "OOO": return "GMT" + U(r, ":");
			default: return "GMT" + G(r, ":");
		}
	},
	z: function(e, t, n) {
		let r = e.getTimezoneOffset();
		switch (t) {
			case "z":
			case "zz":
			case "zzz": return "GMT" + U(r, ":");
			default: return "GMT" + G(r, ":");
		}
	},
	t: function(e, t, n) {
		return z(Math.trunc(e / 1e3), t.length);
	},
	T: function(e, t, n) {
		return z(+e, t.length);
	}
};
function U(e, t = "") {
	let n = e > 0 ? "-" : "+", r = Math.abs(e), i = Math.trunc(r / 60), a = r % 60;
	return a === 0 ? n + String(i) : n + String(i) + t + z(a, 2);
}
function W(e, t) {
	return e % 60 == 0 ? (e > 0 ? "-" : "+") + z(Math.abs(e) / 60, 2) : G(e, t);
}
function G(e, t = "") {
	let n = e > 0 ? "-" : "+", r = Math.abs(e), i = z(Math.trunc(r / 60), 2), a = z(r % 60, 2);
	return n + i + t + a;
}
var K = (e, t) => {
	switch (e) {
		case "P": return t.date({ width: "short" });
		case "PP": return t.date({ width: "medium" });
		case "PPP": return t.date({ width: "long" });
		default: return t.date({ width: "full" });
	}
}, q = (e, t) => {
	switch (e) {
		case "p": return t.time({ width: "short" });
		case "pp": return t.time({ width: "medium" });
		case "ppp": return t.time({ width: "long" });
		default: return t.time({ width: "full" });
	}
}, de = {
	p: q,
	P: (e, t) => {
		let n = e.match(/(P+)(p+)?/) || [], r = n[1], i = n[2];
		if (!i) return K(e, t);
		let a;
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
		return a.replace("{{date}}", K(r, t)).replace("{{time}}", q(i, t));
	}
}, fe = /^D+$/, pe = /^Y+$/, me = [
	"D",
	"DD",
	"YY",
	"YYYY"
];
function he(e) {
	return fe.test(e);
}
function ge(e) {
	return pe.test(e);
}
function _e(e, t, n) {
	let r = ve(e, t, n);
	if (console.warn(r), me.includes(e)) throw RangeError(r);
}
function ve(e, t, n) {
	let r = e[0] === "Y" ? "years" : "days of the month";
	return `Use \`${e.toLowerCase()}\` instead of \`${e}\` (in \`${t}\`) for formatting ${r} to the input \`${n}\`; see: https://github.com/date-fns/date-fns/blob/master/docs/unicodeTokens.md`;
}
var ye = /[yYQqMLwIdDecihHKkms]o|(\w)\1*|''|'(''|[^'])+('|$)|./g, be = /P+p+|P+|p+|''|'(''|[^'])+('|$)|./g, xe = /^'([^]*?)'?$/, Se = /''/g, Ce = /[a-zA-Z]/;
function J(e, t, n) {
	let r = S(), i = n?.locale ?? r.locale ?? m, a = n?.firstWeekContainsDate ?? n?.locale?.options?.firstWeekContainsDate ?? r.firstWeekContainsDate ?? r.locale?.options?.firstWeekContainsDate ?? 1, o = n?.weekStartsOn ?? n?.locale?.options?.weekStartsOn ?? r.weekStartsOn ?? r.locale?.options?.weekStartsOn ?? 0, s = b(e, n?.in);
	if (!M(s)) throw RangeError("Invalid time value");
	let c = t.match(be).map((e) => {
		let t = e[0];
		if (t === "p" || t === "P") {
			let n = de[t];
			return n(e, i.formatLong);
		}
		return e;
	}).join("").match(ye).map((e) => {
		if (e === "''") return {
			isToken: !1,
			value: "'"
		};
		let t = e[0];
		if (t === "'") return {
			isToken: !1,
			value: we(e)
		};
		if (H[t]) return {
			isToken: !0,
			value: e
		};
		if (t.match(Ce)) throw RangeError("Format string contains an unescaped latin alphabet character `" + t + "`");
		return {
			isToken: !1,
			value: e
		};
	});
	i.localize.preprocessor && (c = i.localize.preprocessor(s, c));
	let l = {
		firstWeekContainsDate: a,
		weekStartsOn: o,
		locale: i
	};
	return c.map((r) => {
		if (!r.isToken) return r.value;
		let a = r.value;
		(!n?.useAdditionalWeekYearTokens && ge(a) || !n?.useAdditionalDayOfYearTokens && he(a)) && _e(a, t, String(e));
		let o = H[a[0]];
		return o(s, a, i.localize, l);
	}).join("");
}
function we(e) {
	let t = e.match(xe);
	return t ? t[1].replace(Se, "'") : e;
}
var Y = "YYYY-MM-DD";
function X(e) {
	return e.map((e) => p(e, Y).toDate());
}
function Te(e) {
	return e ? e.map((e) => p(e).format(Y)) : [];
}
function Ee({ disabled: n, element: o, widgetMgr: m, fragmentId: g }) {
	let _ = u(), v = (0, h.useContext)(i), [y, b] = (0, h.useState)(!1), [x, S] = (0, h.useState)(null), C = (0, h.useCallback)(() => {
		S(null);
	}, []), w = (0, h.useCallback)(() => {
		C(), b(!1);
	}, [C]), [T, E] = oe({
		getStateFromWidgetMgr: De,
		getDefaultStateFromProto: Oe,
		getCurrStateFromProto: ke,
		updateWidgetMgrState: Ae,
		element: o,
		widgetMgr: m,
		fragmentId: g,
		queryParamBinding: o.queryParamKey ? {
			paramKey: o.queryParamKey,
			valueType: "string_array_value",
			clearable: o.default.length === 0,
			urlFormat: o.isRange ? "repeated" : void 0
		} : void 0,
		formClearBehavior: "resetValueAndRunCallback",
		onFormCleared: w
	}), { colors: D, fontSizes: O, fontWeights: k, lineHeights: A, spacing: j, sizes: M, zIndices: N } = u(), { locale: P } = (0, h.useContext)(re), F = ue(P), I = (0, h.useMemo)(() => p(o.min, Y).toDate(), [o.min]), L = (0, h.useMemo)(() => Q(o), [o]), R = (0, h.useMemo)(() => o.isRange ? I < p().subtract(2, "years").toDate() : !1, [o.isRange, I]), z = o.default.length === 0 && !n, B = (0, h.useMemo)(() => o.format.replaceAll(/[a-zA-Z]/g, "9"), [o.format]), V = (0, h.useMemo)(() => o.format.replaceAll("Y", "y").replaceAll("D", "d"), [o.format]), H = (0, h.useMemo)(() => J(I, V, { locale: F }), [
		I,
		V,
		F
	]), U = (0, h.useMemo)(() => L ? J(L, V, { locale: F }) : "", [
		L,
		V,
		F
	]), W = (0, h.useCallback)((e) => e ? o.isRange ? `**Error**: ${e} date set outside allowed range. Please select a date ${e === "End" ? `before ${U}` : `after ${H}`}.` : `**Error**: Date set outside allowed range. Please select a date between ${H} and ${U}.` : null, [
		o.isRange,
		U,
		H
	]), G = (0, h.useCallback)(({ date: e }) => {
		if (C(), c(e)) {
			E({
				value: [],
				fromUi: !0
			}), b(!0);
			return;
		}
		let { errorType: t, newDates: n } = Z(Array.isArray(e) ? e.filter((e) => !!e).map((e) => $(e)) : $(e), I, L);
		t && S(W(t)), E({
			value: n,
			fromUi: !0
		}), b(!n);
	}, [
		W,
		L,
		I,
		C,
		S,
		E
	]), K = (0, h.useCallback)(() => {
		if (!y) return;
		let e = X(o.default);
		E({
			value: e,
			fromUi: !0
		}), b(!e);
	}, [
		y,
		o,
		E
	]);
	return /* @__PURE__ */ f.jsxs("div", {
		className: "stDateInput",
		"data-testid": "stDateInput",
		children: [/* @__PURE__ */ f.jsx(ie, {
			label: o.label,
			disabled: n,
			labelVisibility: ee(o.labelVisibility?.value),
			children: o.help && /* @__PURE__ */ f.jsx(ae, {
				content: o.help,
				label: o.label
			})
		}), /* @__PURE__ */ f.jsx(le, {
			locale: F,
			density: ce.high,
			formatString: V,
			mask: o.isRange ? `${B} – ${B}` : B,
			placeholder: o.isRange ? `${o.format} – ${o.format}` : o.format,
			disabled: n,
			onChange: G,
			onClose: K,
			quickSelect: R,
			overrides: {
				Popover: { props: {
					ignoreBoundary: v,
					placement: ne.bottomLeft,
					popoverMargin: e(_.spacing.twoXS),
					overrides: { Body: { style: {
						...te(_),
						...d(_) && { borderWidth: _.spacing.none }
					} } }
				} },
				CalendarContainer: { style: {
					fontSize: O.sm,
					paddingRight: j.sm,
					paddingLeft: j.sm,
					paddingBottom: j.sm,
					paddingTop: j.sm,
					borderWidth: _.spacing.none
				} },
				Week: { style: { fontSize: O.sm } },
				Day: { style: ({ $pseudoHighlighted: e, $pseudoSelected: t, $selected: n, $isHovered: r }) => ({
					fontSize: O.sm,
					lineHeight: A.base,
					"::before": { backgroundColor: n || t || e || r ? `${D.darkenedBgMix15} !important` : D.transparent },
					"::after": { borderColor: D.transparent },
					...d(_) && r && t && !n ? { color: D.secondaryBg } : {}
				}) },
				PrevButton: { style: () => ({
					display: "flex",
					alignItems: "center",
					justifyContent: "center",
					":active": { backgroundColor: D.transparent },
					":focus": {
						backgroundColor: D.transparent,
						outline: 0
					}
				}) },
				NextButton: { style: {
					display: "flex",
					alignItems: "center",
					justifyContent: "center",
					":active": { backgroundColor: D.transparent },
					":focus": {
						backgroundColor: D.transparent,
						outline: 0
					}
				} },
				Input: { props: {
					maskChar: null,
					endEnhancer: x && /* @__PURE__ */ f.jsx(a, {
						content: /* @__PURE__ */ f.jsx(l, {
							source: x,
							allowHTML: !1
						}),
						placement: t.TOP_RIGHT,
						error: !0,
						children: /* @__PURE__ */ f.jsx(r, {
							content: se,
							size: "lg"
						})
					}),
					overrides: {
						EndEnhancer: { style: {
							color: D.redTextColor,
							backgroundColor: D.transparent
						} },
						Root: { style: ({ $isFocused: e }) => {
							let t = s(D, e);
							return {
								borderLeftWidth: M.borderWidth,
								borderRightWidth: M.borderWidth,
								borderTopWidth: M.borderWidth,
								borderBottomWidth: M.borderWidth,
								paddingRight: j.twoXS,
								borderTopColor: t,
								borderRightColor: t,
								borderBottomColor: t,
								borderLeftColor: t,
								...x && { backgroundColor: D.redBackgroundColor }
							};
						} },
						ClearIcon: { props: { overrides: { Svg: { style: {
							color: D.grayTextColor,
							padding: j.threeXS,
							height: M.clearIconSize,
							width: M.clearIconSize,
							":hover": { fill: D.bodyText }
						} } } } },
						InputContainer: { style: { backgroundColor: "transparent" } },
						Input: {
							style: {
								position: "relative",
								zIndex: N.priority,
								fontWeight: k.normal,
								paddingRight: j.sm,
								paddingLeft: `calc(${j.sm} + ${M.tagMarginInsideBorder})`,
								paddingBottom: j.sm,
								paddingTop: j.sm,
								lineHeight: A.inputWidget,
								"::placeholder": { color: D.fadedText60 },
								...x && { color: D.redTextColor }
							},
							props: { "data-testid": "stDateInputField" }
						}
					}
				} },
				QuickSelect: { props: { overrides: { ControlContainer: { style: {
					height: M.minElementHeight,
					borderLeftWidth: M.borderWidth,
					borderRightWidth: M.borderWidth,
					borderTopWidth: M.borderWidth,
					borderBottomWidth: M.borderWidth
				} } } } }
			},
			value: T,
			minDate: I,
			maxDate: L,
			range: o.isRange,
			clearable: z
		})]
	});
}
function De(e, t) {
	let n = e.getStringArrayValue(t);
	if (n !== void 0) return X(n);
}
function Oe(e) {
	return X(e.default) ?? [];
}
function ke(e) {
	return X(e.value) ?? [];
}
function Ae(e, t, n, r) {
	let i = p(e.min, Y).toDate(), a = Q(e), o = !0, { errorType: s } = Z((n.value || []).map((e) => $(e)), i, a);
	s && (o = !1), o && t.setStringArrayValue(e, Te(n.value), { fromUi: n.fromUi }, r);
}
function Z(e, t, n) {
	let r = [], i = null;
	return c(e) ? {
		errorType: null,
		newDates: []
	} : (Array.isArray(e) ? e.forEach((e) => {
		e && (n && e > n ? i = "End" : e < t && (i = "Start"), r.push(e));
	}) : e && (n && e > n ? i = "End" : e < t && (i = "Start"), r.push(e)), {
		errorType: i,
		newDates: r
	});
}
function Q(e) {
	let t = e.max;
	return t && t.length > 0 ? p(t, Y).toDate() : void 0;
}
function $(e) {
	let t = new Date(e.getTime());
	return t.setHours(0, 0, 0, 0), t;
}
var je = (0, h.memo)(Ee);
//#endregion
export { je as default };

//# sourceMappingURL=DateInput-DY0AqEEz-7FHjt78b.js.map