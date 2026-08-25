import { a as e, f as t, k as n, l as r, o as i, r as a } from "./value-YcFXbvJe-DIeu1yzI.js";
//#region ../react/build/threshold-F1JftlUw.js
function o(e, t) {
	return e == null || t == null ? NaN : e < t ? -1 : e > t ? 1 : e >= t ? 0 : NaN;
}
function s(e, t) {
	return e == null || t == null ? NaN : t < e ? -1 : t > e ? 1 : t >= e ? 0 : NaN;
}
function c(e) {
	let t, n, r;
	e.length === 2 ? (t = e === o || e === s ? e : l, n = e, r = e) : (t = o, n = (t, n) => o(e(t), n), r = (t, n) => e(t) - n);
	function i(e, r, i = 0, a = e.length) {
		if (i < a) {
			if (t(r, r) !== 0) return a;
			do {
				let t = i + a >>> 1;
				n(e[t], r) < 0 ? i = t + 1 : a = t;
			} while (i < a);
		}
		return i;
	}
	function a(e, r, i = 0, a = e.length) {
		if (i < a) {
			if (t(r, r) !== 0) return a;
			do {
				let t = i + a >>> 1;
				n(e[t], r) <= 0 ? i = t + 1 : a = t;
			} while (i < a);
		}
		return i;
	}
	function c(e, t, n = 0, a = e.length) {
		let o = i(e, t, n, a - 1);
		return o > n && r(e[o - 1], t) > -r(e[o], t) ? o - 1 : o;
	}
	return {
		left: i,
		center: c,
		right: a
	};
}
function l() {
	return 0;
}
function u(e) {
	return e === null ? NaN : +e;
}
function* d(e, t) {
	if (t === void 0) for (let t of e) t != null && (t = +t) >= t && (yield t);
	else {
		let n = -1;
		for (let r of e) (r = t(r, ++n, e)) != null && (r = +r) >= r && (yield r);
	}
}
var f = c(o), p = f.right, m = f.left;
c(u).center;
var h = Math.sqrt(50), g = Math.sqrt(10), _ = Math.sqrt(2);
function v(e, t, n) {
	let r = (t - e) / Math.max(0, n), i = Math.floor(Math.log10(r)), a = r / 10 ** i, o = a >= h ? 10 : a >= g ? 5 : a >= _ ? 2 : 1, s, c, l;
	return i < 0 ? (l = 10 ** -i / o, s = Math.round(e * l), c = Math.round(t * l), s / l < e && ++s, c / l > t && --c, l = -l) : (l = 10 ** i * o, s = Math.round(e / l), c = Math.round(t / l), s * l < e && ++s, c * l > t && --c), c < s && .5 <= n && n < 2 ? v(e, t, n * 2) : [
		s,
		c,
		l
	];
}
function y(e, t, n) {
	if (t = +t, e = +e, n = +n, !(n > 0)) return [];
	if (e === t) return [e];
	let r = t < e, [i, a, o] = r ? v(t, e, n) : v(e, t, n);
	if (!(a >= i)) return [];
	let s = a - i + 1, c = Array(s);
	if (r) if (o < 0) for (let e = 0; e < s; ++e) c[e] = (a - e) / -o;
	else for (let e = 0; e < s; ++e) c[e] = (a - e) * o;
	else if (o < 0) for (let e = 0; e < s; ++e) c[e] = (i + e) / -o;
	else for (let e = 0; e < s; ++e) c[e] = (i + e) * o;
	return c;
}
function b(e, t, n) {
	return t = +t, e = +e, n = +n, v(e, t, n)[2];
}
function x(e, t, n) {
	t = +t, e = +e, n = +n;
	let r = t < e, i = r ? b(t, e, n) : b(e, t, n);
	return (r ? -1 : 1) * (i < 0 ? 1 / -i : i);
}
function S(e) {
	return Math.max(0, -n(Math.abs(e)));
}
function C(e, t) {
	return Math.max(0, Math.max(-8, Math.min(8, Math.floor(n(t) / 3))) * 3 - n(Math.abs(e)));
}
function w(e, t) {
	return e = Math.abs(e), t = Math.abs(t) - e, Math.max(0, n(t) - n(e)) + 1;
}
function T(e, t) {
	switch (arguments.length) {
		case 0: break;
		case 1:
			this.range(e);
			break;
		default:
			this.range(t).domain(e);
			break;
	}
	return this;
}
function E(e, t) {
	switch (arguments.length) {
		case 0: break;
		case 1:
			typeof e == "function" ? this.interpolator(e) : this.range(e);
			break;
		default:
			this.domain(e), typeof t == "function" ? this.interpolator(t) : this.range(t);
			break;
	}
	return this;
}
function D(e, t) {
	return e = +e, t = +t, function(n) {
		return Math.round(e * (1 - n) + t * n);
	};
}
function O(e) {
	return function() {
		return e;
	};
}
function k(e) {
	return +e;
}
var A = [0, 1];
function j(e) {
	return e;
}
function M(e, t) {
	return (t -= e = +e) ? function(n) {
		return (n - e) / t;
	} : O(isNaN(t) ? NaN : .5);
}
function N(e, t) {
	var n;
	return e > t && (n = e, e = t, t = n), function(n) {
		return Math.max(e, Math.min(t, n));
	};
}
function P(e, t, n) {
	var r = e[0], i = e[1], a = t[0], o = t[1];
	return i < r ? (r = M(i, r), a = n(o, a)) : (r = M(r, i), a = n(a, o)), function(e) {
		return a(r(e));
	};
}
function F(e, t, n) {
	var r = Math.min(e.length, t.length) - 1, i = Array(r), a = Array(r), o = -1;
	for (e[r] < e[0] && (e = e.slice().reverse(), t = t.slice().reverse()); ++o < r;) i[o] = M(e[o], e[o + 1]), a[o] = n(t[o], t[o + 1]);
	return function(t) {
		var n = p(e, t, 1, r) - 1;
		return a[n](i[n](t));
	};
}
function I(e, t) {
	return t.domain(e.domain()).range(e.range()).interpolate(e.interpolate()).clamp(e.clamp()).unknown(e.unknown());
}
function L() {
	var t = A, n = A, r = e, a, o, s, c = j, l, u, d;
	function f() {
		var e = Math.min(t.length, n.length);
		return c !== j && (c = N(t[0], t[e - 1])), l = e > 2 ? F : P, u = d = null, p;
	}
	function p(e) {
		return e == null || isNaN(e = +e) ? s : (u ||= l(t.map(a), n, r))(a(c(e)));
	}
	return p.invert = function(e) {
		return c(o((d ||= l(n, t.map(a), i))(e)));
	}, p.domain = function(e) {
		return arguments.length ? (t = Array.from(e, k), f()) : t.slice();
	}, p.range = function(e) {
		return arguments.length ? (n = Array.from(e), f()) : n.slice();
	}, p.rangeRound = function(e) {
		return n = Array.from(e), r = D, f();
	}, p.clamp = function(e) {
		return arguments.length ? (c = e ? !0 : j, f()) : c !== j;
	}, p.interpolate = function(e) {
		return arguments.length ? (r = e, f()) : r;
	}, p.unknown = function(e) {
		return arguments.length ? (s = e, p) : s;
	}, function(e, t) {
		return a = e, o = t, f();
	};
}
function R() {
	return L()(j, j);
}
function z(e, n, i, o) {
	var s = x(e, n, i), c;
	switch (o = t(o ?? ",f"), o.type) {
		case "s":
			var l = Math.max(Math.abs(e), Math.abs(n));
			return o.precision == null && !isNaN(c = C(s, l)) && (o.precision = c), a(o, l);
		case "":
		case "e":
		case "g":
		case "p":
		case "r":
			o.precision == null && !isNaN(c = w(s, Math.max(Math.abs(e), Math.abs(n)))) && (o.precision = c - (o.type === "e"));
			break;
		case "f":
		case "%":
			o.precision == null && !isNaN(c = S(s)) && (o.precision = c - (o.type === "%") * 2);
			break;
	}
	return r(o);
}
function B(e) {
	var t = e.domain;
	return e.ticks = function(e) {
		var n = t();
		return y(n[0], n[n.length - 1], e ?? 10);
	}, e.tickFormat = function(e, n) {
		var r = t();
		return z(r[0], r[r.length - 1], e ?? 10, n);
	}, e.nice = function(n) {
		n ??= 10;
		var r = t(), i = 0, a = r.length - 1, o = r[i], s = r[a], c, l, u = 10;
		for (s < o && (l = o, o = s, s = l, l = i, i = a, a = l); u-- > 0;) {
			if (l = b(o, s, n), l === c) return r[i] = o, r[a] = s, t(r);
			if (l > 0) o = Math.floor(o / l) * l, s = Math.ceil(s / l) * l;
			else if (l < 0) o = Math.ceil(o * l) / l, s = Math.floor(s * l) / l;
			else break;
			c = l;
		}
		return e;
	}, e;
}
function V() {
	var e = R();
	return e.copy = function() {
		return I(e, V());
	}, T.apply(e, arguments), B(e);
}
function H() {
	var e = [.5], t = [0, 1], n, r = 1;
	function i(i) {
		return i != null && i <= i ? t[p(e, i, 0, r)] : n;
	}
	return i.domain = function(n) {
		return arguments.length ? (e = Array.from(n), r = Math.min(e.length, t.length - 1), i) : e.slice();
	}, i.range = function(n) {
		return arguments.length ? (t = Array.from(n), r = Math.min(e.length, t.length - 1), i) : t.slice();
	}, i.invertExtent = function(n) {
		var r = t.indexOf(n);
		return [e[r - 1], e[r]];
	}, i.unknown = function(e) {
		return arguments.length ? (n = e, i) : n;
	}, i.copy = function() {
		return H().domain(e).range(t).unknown(n);
	}, T.apply(i, arguments);
}
//#endregion
export { p as C, c as S, T as _, k as a, d as b, S as c, L as d, R as f, H as g, V as h, D as i, u as l, B as m, w as n, x as o, z as p, y as r, o as s, C as t, I as u, m as v, E as x, j as y };

//# sourceMappingURL=threshold-F1JftlUw-Dpm01mWO.js.map