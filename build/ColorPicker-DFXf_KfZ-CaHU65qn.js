import { Cn as e, En as t, J as n, Ka as r, Kn as i, Q as a, Ua as o, ct as s, ha as c, ii as l, ma as u, nr as d, ti as f } from "./index-Dl4ETd_L-D2oMd1k2.js";
import { C as p, D as m, E as h, F as g, L as _, M as v, N as y, O as b, P as ee, S as te, T as ne, _ as x, a as re, b as ie, c as ae, f as oe, g as se, j as ce, k as S, m as C, o as le, p as ue, r as de, s as fe, t as pe, u as me, v as w, w as he, y as ge } from "./_baseAssignValue-CvLdsscI-DZvAeBHf.js";
import { t as _e } from "./WidgetLabel-CQfHGtry-udktvHE5.js";
import { t as ve } from "./WidgetLabelHelpIconInline-BTmzKeRa-CZ4j9Xyg.js";
import { n as ye } from "./useBasicWidgetState-D3zHnRUK-Dsaz4YO6.js";
//#region ../react/build/ColorPicker-DFXf_KfZ.js
var T = /* @__PURE__ */ r(o(), 1), E = {}, D = {}, be, xe;
function Se() {
	if (xe) return be;
	xe = 1;
	var e = g(), t = fe(), n = he(), r = "[object String]";
	function i(i) {
		return typeof i == "string" || !t(i) && n(i) && e(i) == r;
	}
	return be = i, be;
}
var Ce, we;
function Te() {
	if (we) return Ce;
	we = 1;
	var e = v();
	function t(t) {
		return typeof t == "function" ? t : e;
	}
	return Ce = t, Ce;
}
var Ee, De;
function Oe() {
	if (De) return Ee;
	De = 1;
	var e = ge(), t = Te();
	function n(n, r) {
		return n && e(n, t(r));
	}
	return Ee = n, Ee;
}
var ke, O;
function Ae() {
	return O ? ke : (O = 1, ke = me()(Object.getPrototypeOf, Object), ke);
}
var je, Me;
function Ne() {
	if (Me) return je;
	Me = 1;
	var e = g(), t = Ae(), n = he(), r = "[object Object]", i = Function.prototype, a = Object.prototype, o = i.toString, s = a.hasOwnProperty, c = o.call(Object);
	function l(i) {
		if (!n(i) || e(i) != r) return !1;
		var a = t(i);
		if (a === null) return !0;
		var l = s.call(a, "constructor") && a.constructor;
		return typeof l == "function" && l instanceof l && o.call(l) == c;
	}
	return je = l, je;
}
var Pe, Fe;
function Ie() {
	if (Fe) return Pe;
	Fe = 1;
	var e = ie(), t = ee();
	function n(n, r) {
		var i = -1, a = t(n) ? Array(n.length) : [];
		return e(n, function(e, t, n) {
			a[++i] = r(e, t, n);
		}), a;
	}
	return Pe = n, Pe;
}
var Le, Re;
function ze() {
	if (Re) return Le;
	Re = 1;
	var e = S(), t = te(), n = Ie(), r = fe();
	function i(i, a) {
		return (r(i) ? e : n)(i, t(a, 3));
	}
	return Le = i, Le;
}
var Be;
function Ve() {
	if (Be) return D;
	Be = 1, Object.defineProperty(D, "__esModule", { value: !0 }), D.flattenNames = void 0;
	var e = i(Se()), t = i(Oe()), n = i(Ne()), r = i(ze());
	function i(e) {
		return e && e.__esModule ? e : { default: e };
	}
	return D.default = D.flattenNames = function i() {
		var a = arguments.length > 0 && arguments[0] !== void 0 ? arguments[0] : [], o = [];
		return (0, r.default)(a, function(r) {
			Array.isArray(r) ? i(r).map(function(e) {
				return o.push(e);
			}) : (0, n.default)(r) ? (0, t.default)(r, function(e, t) {
				e === !0 && o.push(t), o.push(t + "-" + e);
			}) : (0, e.default)(r) && o.push(r);
		}), o;
	}, D;
}
var He = {}, Ue, We;
function Ge() {
	if (We) return Ue;
	We = 1;
	function e(e, t) {
		for (var n = -1, r = e == null ? 0 : e.length; ++n < r && t(e[n], n, e) !== !1;);
		return e;
	}
	return Ue = e, Ue;
}
var Ke, qe;
function Je() {
	if (qe) return Ke;
	qe = 1;
	var e = ce(), t = ae(), n = Object.prototype.hasOwnProperty;
	function r(r, i, a) {
		var o = r[i];
		(!(n.call(r, i) && t(o, a)) || a === void 0 && !(i in r)) && e(r, i, a);
	}
	return Ke = r, Ke;
}
var Ye, Xe;
function Ze() {
	if (Xe) return Ye;
	Xe = 1;
	var e = Je(), t = ce();
	function n(n, r, i, a) {
		var o = !i;
		i ||= {};
		for (var s = -1, c = r.length; ++s < c;) {
			var l = r[s], u = a ? a(i[l], n[l], l, i, n) : void 0;
			u === void 0 && (u = n[l]), o ? t(i, l, u) : e(i, l, u);
		}
		return i;
	}
	return Ye = n, Ye;
}
var Qe, $e;
function et() {
	if ($e) return Qe;
	$e = 1;
	var e = Ze(), t = p();
	function n(n, r) {
		return n && e(r, t(r), n);
	}
	return Qe = n, Qe;
}
var tt, nt;
function rt() {
	if (nt) return tt;
	nt = 1;
	function e(e) {
		var t = [];
		if (e != null) for (var n in Object(e)) t.push(n);
		return t;
	}
	return tt = e, tt;
}
var it, at;
function ot() {
	if (at) return it;
	at = 1;
	var e = b(), t = x(), n = rt(), r = Object.prototype.hasOwnProperty;
	function i(i) {
		if (!e(i)) return n(i);
		var a = t(i), o = [];
		for (var s in i) s == "constructor" && (a || !r.call(i, s)) || o.push(s);
		return o;
	}
	return it = i, it;
}
var st, ct;
function lt() {
	if (ct) return st;
	ct = 1;
	var e = C(), t = ot(), n = ee();
	function r(r) {
		return n(r) ? e(r, !0) : t(r);
	}
	return st = r, st;
}
var ut, dt;
function ft() {
	if (dt) return ut;
	dt = 1;
	var e = Ze(), t = lt();
	function n(n, r) {
		return n && e(r, t(r), n);
	}
	return ut = n, ut;
}
var pt = { exports: {} };
pt.exports;
var mt;
function ht() {
	return mt || (mt = 1, function(e, t) {
		var n = y(), r = t && !t.nodeType && t, i = r && e && !e.nodeType && e, a = i && i.exports === r ? n.Buffer : void 0, o = a ? a.allocUnsafe : void 0;
		function s(e, t) {
			if (t) return e.slice();
			var n = e.length, r = o ? o(n) : new e.constructor(n);
			return e.copy(r), r;
		}
		e.exports = s;
	}(pt, pt.exports)), pt.exports;
}
var gt, _t;
function vt() {
	if (_t) return gt;
	_t = 1;
	function e(e, t) {
		var n = -1, r = e.length;
		for (t ||= Array(r); ++n < r;) t[n] = e[n];
		return t;
	}
	return gt = e, gt;
}
var yt, bt;
function xt() {
	if (bt) return yt;
	bt = 1;
	var e = Ze(), t = _();
	function n(n, r) {
		return e(n, t(n), r);
	}
	return yt = n, yt;
}
var St, Ct;
function wt() {
	if (Ct) return St;
	Ct = 1;
	var e = le(), t = Ae(), n = _(), r = oe();
	return St = Object.getOwnPropertySymbols ? function(r) {
		for (var i = []; r;) e(i, n(r)), r = t(r);
		return i;
	} : r, St;
}
var Tt, Et;
function Dt() {
	if (Et) return Tt;
	Et = 1;
	var e = Ze(), t = wt();
	function n(n, r) {
		return e(n, t(n), r);
	}
	return Tt = n, Tt;
}
var Ot, kt;
function At() {
	if (kt) return Ot;
	kt = 1;
	var e = pe(), t = wt(), n = lt();
	function r(r) {
		return e(r, n, t);
	}
	return Ot = r, Ot;
}
var jt, Mt;
function Nt() {
	if (Mt) return jt;
	Mt = 1;
	var e = Object.prototype.hasOwnProperty;
	function t(t) {
		var n = t.length, r = new t.constructor(n);
		return n && typeof t[0] == "string" && e.call(t, "index") && (r.index = t.index, r.input = t.input), r;
	}
	return jt = t, jt;
}
var Pt, Ft;
function It() {
	if (Ft) return Pt;
	Ft = 1;
	var e = ne();
	function t(t) {
		var n = new t.constructor(t.byteLength);
		return new e(n).set(new e(t)), n;
	}
	return Pt = t, Pt;
}
var Lt, Rt;
function zt() {
	if (Rt) return Lt;
	Rt = 1;
	var e = It();
	function t(t, n) {
		var r = n ? e(t.buffer) : t.buffer;
		return new t.constructor(r, t.byteOffset, t.byteLength);
	}
	return Lt = t, Lt;
}
var Bt, Vt;
function Ht() {
	if (Vt) return Bt;
	Vt = 1;
	var e = /\w*$/;
	function t(t) {
		var n = new t.constructor(t.source, e.exec(t));
		return n.lastIndex = t.lastIndex, n;
	}
	return Bt = t, Bt;
}
var Ut, Wt;
function Gt() {
	if (Wt) return Ut;
	Wt = 1;
	var e = re(), t = e ? e.prototype : void 0, n = t ? t.valueOf : void 0;
	function r(e) {
		return n ? Object(n.call(e)) : {};
	}
	return Ut = r, Ut;
}
var Kt, qt;
function Jt() {
	if (qt) return Kt;
	qt = 1;
	var e = It();
	function t(t, n) {
		var r = n ? e(t.buffer) : t.buffer;
		return new t.constructor(r, t.byteOffset, t.length);
	}
	return Kt = t, Kt;
}
var Yt, Xt;
function Zt() {
	if (Xt) return Yt;
	Xt = 1;
	var e = It(), t = zt(), n = Ht(), r = Gt(), i = Jt(), a = "[object Boolean]", o = "[object Date]", s = "[object Map]", c = "[object Number]", l = "[object RegExp]", u = "[object Set]", d = "[object String]", f = "[object Symbol]", p = "[object ArrayBuffer]", m = "[object DataView]", h = "[object Float32Array]", g = "[object Float64Array]", _ = "[object Int8Array]", v = "[object Int16Array]", y = "[object Int32Array]", b = "[object Uint8Array]", ee = "[object Uint8ClampedArray]", te = "[object Uint16Array]", ne = "[object Uint32Array]";
	function x(x, re, ie) {
		var ae = x.constructor;
		switch (re) {
			case p: return e(x);
			case a:
			case o: return new ae(+x);
			case m: return t(x, ie);
			case h:
			case g:
			case _:
			case v:
			case y:
			case b:
			case ee:
			case te:
			case ne: return i(x, ie);
			case s: return new ae();
			case c:
			case d: return new ae(x);
			case l: return n(x);
			case u: return new ae();
			case f: return r(x);
		}
	}
	return Yt = x, Yt;
}
var Qt, $t;
function en() {
	if ($t) return Qt;
	$t = 1;
	var e = b(), t = Object.create;
	return Qt = /* @__PURE__ */ function() {
		function n() {}
		return function(r) {
			if (!e(r)) return {};
			if (t) return t(r);
			n.prototype = r;
			var i = new n();
			return n.prototype = void 0, i;
		};
	}(), Qt;
}
var tn, nn;
function rn() {
	if (nn) return tn;
	nn = 1;
	var e = en(), t = Ae(), n = x();
	function r(r) {
		return typeof r.constructor == "function" && !n(r) ? e(t(r)) : {};
	}
	return tn = r, tn;
}
var an, on;
function sn() {
	if (on) return an;
	on = 1;
	var e = ue(), t = he(), n = "[object Map]";
	function r(r) {
		return t(r) && e(r) == n;
	}
	return an = r, an;
}
var cn, ln;
function un() {
	if (ln) return cn;
	ln = 1;
	var e = sn(), t = se(), n = w(), r = n && n.isMap;
	return cn = r ? t(r) : e, cn;
}
var dn, fn;
function pn() {
	if (fn) return dn;
	fn = 1;
	var e = ue(), t = he(), n = "[object Set]";
	function r(r) {
		return t(r) && e(r) == n;
	}
	return dn = r, dn;
}
var mn, hn;
function gn() {
	if (hn) return mn;
	hn = 1;
	var e = pn(), t = se(), n = w(), r = n && n.isSet;
	return mn = r ? t(r) : e, mn;
}
var _n, vn;
function yn() {
	if (vn) return _n;
	vn = 1;
	var e = de(), t = Ge(), n = Je(), r = et(), i = ft(), a = ht(), o = vt(), s = xt(), c = Dt(), l = h(), u = At(), d = ue(), f = Nt(), g = Zt(), _ = rn(), v = fe(), y = m(), ee = un(), te = b(), ne = gn(), x = p(), re = lt(), ie = 1, ae = 2, oe = 4, se = "[object Arguments]", ce = "[object Array]", S = "[object Boolean]", C = "[object Date]", le = "[object Error]", pe = "[object Function]", me = "[object GeneratorFunction]", w = "[object Map]", he = "[object Number]", ge = "[object Object]", _e = "[object RegExp]", ve = "[object Set]", ye = "[object String]", T = "[object Symbol]", E = "[object WeakMap]", D = "[object ArrayBuffer]", be = "[object DataView]", xe = "[object Float32Array]", Se = "[object Float64Array]", Ce = "[object Int8Array]", we = "[object Int16Array]", Te = "[object Int32Array]", Ee = "[object Uint8Array]", De = "[object Uint8ClampedArray]", Oe = "[object Uint16Array]", ke = "[object Uint32Array]", O = {};
	O[se] = O[ce] = O[D] = O[be] = O[S] = O[C] = O[xe] = O[Se] = O[Ce] = O[we] = O[Te] = O[w] = O[he] = O[ge] = O[_e] = O[ve] = O[ye] = O[T] = O[Ee] = O[De] = O[Oe] = O[ke] = !0, O[le] = O[pe] = O[E] = !1;
	function Ae(p, m, h, b, ce, S) {
		var C, le = m & ie, ue = m & ae, de = m & oe;
		if (h && (C = ce ? h(p, b, ce, S) : h(p)), C !== void 0) return C;
		if (!te(p)) return p;
		var fe = v(p);
		if (fe) {
			if (C = f(p), !le) return o(p, C);
		} else {
			var w = d(p), he = w == pe || w == me;
			if (y(p)) return a(p, le);
			if (w == ge || w == se || he && !ce) {
				if (C = ue || he ? {} : _(p), !le) return ue ? c(p, i(C, p)) : s(p, r(C, p));
			} else {
				if (!O[w]) return ce ? p : {};
				C = g(p, w, le);
			}
		}
		S ||= new e();
		var _e = S.get(p);
		if (_e) return _e;
		S.set(p, C), ne(p) ? p.forEach(function(e) {
			C.add(Ae(e, m, h, e, p, S));
		}) : ee(p) && p.forEach(function(e, t) {
			C.set(t, Ae(e, m, h, t, p, S));
		});
		var ve = fe ? void 0 : (de ? ue ? u : l : ue ? re : x)(p);
		return t(ve || p, function(e, t) {
			ve && (t = e, e = p[t]), n(C, t, Ae(e, m, h, t, p, S));
		}), C;
	}
	return _n = Ae, _n;
}
var bn, xn;
function Sn() {
	if (xn) return bn;
	xn = 1;
	var e = yn(), t = 1, n = 4;
	function r(r) {
		return e(r, t | n);
	}
	return bn = r, bn;
}
var Cn;
function wn() {
	if (Cn) return He;
	Cn = 1, Object.defineProperty(He, "__esModule", { value: !0 }), He.mergeClasses = void 0;
	var e = r(Oe()), t = r(Sn()), n = Object.assign || function(e) {
		for (var t = 1; t < arguments.length; t++) {
			var n = arguments[t];
			for (var r in n) Object.prototype.hasOwnProperty.call(n, r) && (e[r] = n[r]);
		}
		return e;
	};
	function r(e) {
		return e && e.__esModule ? e : { default: e };
	}
	return He.default = He.mergeClasses = function(r) {
		var i = arguments.length > 1 && arguments[1] !== void 0 ? arguments[1] : [], a = r.default && (0, t.default)(r.default) || {};
		return i.map(function(t) {
			var i = r[t];
			return i && (0, e.default)(i, function(e, t) {
				a[t] || (a[t] = {}), a[t] = n({}, a[t], i[t]);
			}), t;
		}), a;
	}, He;
}
var Tn = {}, En;
function Dn() {
	if (En) return Tn;
	En = 1, Object.defineProperty(Tn, "__esModule", { value: !0 }), Tn.autoprefix = void 0;
	var e = n(Oe()), t = Object.assign || function(e) {
		for (var t = 1; t < arguments.length; t++) {
			var n = arguments[t];
			for (var r in n) Object.prototype.hasOwnProperty.call(n, r) && (e[r] = n[r]);
		}
		return e;
	};
	function n(e) {
		return e && e.__esModule ? e : { default: e };
	}
	var r = {
		borderRadius: function(e) {
			return {
				msBorderRadius: e,
				MozBorderRadius: e,
				OBorderRadius: e,
				WebkitBorderRadius: e,
				borderRadius: e
			};
		},
		boxShadow: function(e) {
			return {
				msBoxShadow: e,
				MozBoxShadow: e,
				OBoxShadow: e,
				WebkitBoxShadow: e,
				boxShadow: e
			};
		},
		userSelect: function(e) {
			return {
				WebkitTouchCallout: e,
				KhtmlUserSelect: e,
				MozUserSelect: e,
				msUserSelect: e,
				WebkitUserSelect: e,
				userSelect: e
			};
		},
		flex: function(e) {
			return {
				WebkitBoxFlex: e,
				MozBoxFlex: e,
				WebkitFlex: e,
				msFlex: e,
				flex: e
			};
		},
		flexBasis: function(e) {
			return {
				WebkitFlexBasis: e,
				flexBasis: e
			};
		},
		justifyContent: function(e) {
			return {
				WebkitJustifyContent: e,
				justifyContent: e
			};
		},
		transition: function(e) {
			return {
				msTransition: e,
				MozTransition: e,
				OTransition: e,
				WebkitTransition: e,
				transition: e
			};
		},
		transform: function(e) {
			return {
				msTransform: e,
				MozTransform: e,
				OTransform: e,
				WebkitTransform: e,
				transform: e
			};
		},
		absolute: function(e) {
			var t = e && e.split(" ");
			return {
				position: "absolute",
				top: t && t[0],
				right: t && t[1],
				bottom: t && t[2],
				left: t && t[3]
			};
		},
		extend: function(e, t) {
			return t[e] || { extend: e };
		}
	};
	return Tn.default = Tn.autoprefix = function(n) {
		var i = {};
		return (0, e.default)(n, function(n, a) {
			var o = {};
			(0, e.default)(n, function(e, n) {
				var i = r[n];
				i ? o = t({}, o, i(e)) : o[n] = e;
			}), i[a] = o;
		}), i;
	}, Tn;
}
var On = {}, kn;
function An() {
	if (kn) return On;
	kn = 1, Object.defineProperty(On, "__esModule", { value: !0 }), On.hover = void 0;
	var e = Object.assign || function(e) {
		for (var t = 1; t < arguments.length; t++) {
			var n = arguments[t];
			for (var r in n) Object.prototype.hasOwnProperty.call(n, r) && (e[r] = n[r]);
		}
		return e;
	}, t = n(T.default);
	function n(e) {
		return e && e.__esModule ? e : { default: e };
	}
	function r(e, t) {
		if (!(e instanceof t)) throw TypeError("Cannot call a class as a function");
	}
	function i(e, t) {
		if (!e) throw ReferenceError("this hasn't been initialised - super() hasn't been called");
		return t && (typeof t == "object" || typeof t == "function") ? t : e;
	}
	function a(e, t) {
		if (typeof t != "function" && t !== null) throw TypeError("Super expression must either be null or a function, not " + typeof t);
		e.prototype = Object.create(t && t.prototype, { constructor: {
			value: e,
			enumerable: !1,
			writable: !0,
			configurable: !0
		} }), t && (Object.setPrototypeOf ? Object.setPrototypeOf(e, t) : e.__proto__ = t);
	}
	return On.default = On.hover = function(n) {
		var o = arguments.length > 1 && arguments[1] !== void 0 ? arguments[1] : "span";
		return function(s) {
			a(c, s);
			function c() {
				var a, s, l, u;
				r(this, c);
				var d = [...arguments];
				return u = (s = (l = i(this, (a = c.__proto__ || Object.getPrototypeOf(c)).call.apply(a, [this].concat(d))), l), l.state = { hover: !1 }, l.handleMouseOver = function() {
					return l.setState({ hover: !0 });
				}, l.handleMouseOut = function() {
					return l.setState({ hover: !1 });
				}, l.render = function() {
					return t.default.createElement(o, {
						onMouseOver: l.handleMouseOver,
						onMouseOut: l.handleMouseOut
					}, t.default.createElement(n, e({}, l.props, l.state)));
				}, s), i(l, u);
			}
			return c;
		}(t.default.Component);
	}, On;
}
var jn = {}, Mn;
function Nn() {
	if (Mn) return jn;
	Mn = 1, Object.defineProperty(jn, "__esModule", { value: !0 }), jn.active = void 0;
	var e = Object.assign || function(e) {
		for (var t = 1; t < arguments.length; t++) {
			var n = arguments[t];
			for (var r in n) Object.prototype.hasOwnProperty.call(n, r) && (e[r] = n[r]);
		}
		return e;
	}, t = n(T.default);
	function n(e) {
		return e && e.__esModule ? e : { default: e };
	}
	function r(e, t) {
		if (!(e instanceof t)) throw TypeError("Cannot call a class as a function");
	}
	function i(e, t) {
		if (!e) throw ReferenceError("this hasn't been initialised - super() hasn't been called");
		return t && (typeof t == "object" || typeof t == "function") ? t : e;
	}
	function a(e, t) {
		if (typeof t != "function" && t !== null) throw TypeError("Super expression must either be null or a function, not " + typeof t);
		e.prototype = Object.create(t && t.prototype, { constructor: {
			value: e,
			enumerable: !1,
			writable: !0,
			configurable: !0
		} }), t && (Object.setPrototypeOf ? Object.setPrototypeOf(e, t) : e.__proto__ = t);
	}
	return jn.default = jn.active = function(n) {
		var o = arguments.length > 1 && arguments[1] !== void 0 ? arguments[1] : "span";
		return function(s) {
			a(c, s);
			function c() {
				var a, s, l, u;
				r(this, c);
				var d = [...arguments];
				return u = (s = (l = i(this, (a = c.__proto__ || Object.getPrototypeOf(c)).call.apply(a, [this].concat(d))), l), l.state = { active: !1 }, l.handleMouseDown = function() {
					return l.setState({ active: !0 });
				}, l.handleMouseUp = function() {
					return l.setState({ active: !1 });
				}, l.render = function() {
					return t.default.createElement(o, {
						onMouseDown: l.handleMouseDown,
						onMouseUp: l.handleMouseUp
					}, t.default.createElement(n, e({}, l.props, l.state)));
				}, s), i(l, u);
			}
			return c;
		}(t.default.Component);
	}, jn;
}
var Pn = {}, Fn;
function In() {
	return Fn ? Pn : (Fn = 1, Object.defineProperty(Pn, "__esModule", { value: !0 }), Pn.default = function(e, t) {
		var n = {}, r = function(e) {
			n[e] = arguments.length > 1 && arguments[1] !== void 0 ? arguments[1] : !0;
		};
		return e === 0 && r("first-child"), e === t - 1 && r("last-child"), (e === 0 || e % 2 == 0) && r("even"), Math.abs(e % 2) === 1 && r("odd"), r("nth-child", e), n;
	}, Pn);
}
var Ln;
function Rn() {
	if (Ln) return E;
	Ln = 1, Object.defineProperty(E, "__esModule", { value: !0 }), E.ReactCSS = E.loop = E.handleActive = E.handleHover = E.hover = void 0;
	var e = o(Ve()), t = o(wn()), n = o(Dn()), r = o(An()), i = o(Nn()), a = o(In());
	function o(e) {
		return e && e.__esModule ? e : { default: e };
	}
	return E.hover = r.default, E.handleHover = r.default, E.handleActive = i.default, E.loop = a.default, E.default = E.ReactCSS = function(r) {
		var i = [...arguments].slice(1), a = (0, e.default)(i), o = (0, t.default)(r, a);
		return (0, n.default)(o);
	}, E;
}
var zn = Rn(), k = /* @__PURE__ */ i(zn), Bn = function(e, t, n, r, i) {
	var a = i.clientWidth, o = i.clientHeight, s = typeof e.pageX == "number" ? e.pageX : e.touches[0].pageX, c = typeof e.pageY == "number" ? e.pageY : e.touches[0].pageY, l = s - (i.getBoundingClientRect().left + window.pageXOffset), u = c - (i.getBoundingClientRect().top + window.pageYOffset);
	if (n === "vertical") {
		var d = void 0;
		if (d = u < 0 ? 0 : u > o ? 1 : Math.round(u * 100 / o) / 100, t.a !== d) return {
			h: t.h,
			s: t.s,
			l: t.l,
			a: d,
			source: "rgb"
		};
	} else {
		var f = void 0;
		if (f = l < 0 ? 0 : l > a ? 1 : Math.round(l * 100 / a) / 100, r !== f) return {
			h: t.h,
			s: t.s,
			l: t.l,
			a: f,
			source: "rgb"
		};
	}
	return null;
}, Vn = {}, Hn = function(e, t, n, r) {
	if (typeof document > "u" && !r) return null;
	var i = r ? new r() : document.createElement("canvas");
	i.width = n * 2, i.height = n * 2;
	var a = i.getContext("2d");
	return a ? (a.fillStyle = e, a.fillRect(0, 0, i.width, i.height), a.fillStyle = t, a.fillRect(0, 0, n, n), a.translate(n, n), a.fillRect(0, 0, n, n), i.toDataURL()) : null;
}, Un = function(e, t, n, r) {
	var i = e + "-" + t + "-" + n + (r ? "-server" : "");
	if (Vn[i]) return Vn[i];
	var a = Hn(e, t, n, r);
	return Vn[i] = a, a;
}, Wn = Object.assign || function(e) {
	for (var t = 1; t < arguments.length; t++) {
		var n = arguments[t];
		for (var r in n) Object.prototype.hasOwnProperty.call(n, r) && (e[r] = n[r]);
	}
	return e;
}, Gn = function(e) {
	var t = e.white, n = e.grey, r = e.size, i = e.renderers, a = e.borderRadius, o = e.boxShadow, s = e.children, c = k({ default: { grid: {
		borderRadius: a,
		boxShadow: o,
		absolute: "0px 0px 0px 0px",
		background: "url(" + Un(t, n, r, i.canvas) + ") center left"
	} } });
	return (0, T.isValidElement)(s) ? T.cloneElement(s, Wn({}, s.props, { style: Wn({}, s.props.style, c.grid) })) : T.createElement("div", { style: c.grid });
};
Gn.defaultProps = {
	size: 8,
	white: "transparent",
	grey: "rgba(0,0,0,.08)",
	renderers: {}
};
var Kn = Object.assign || function(e) {
	for (var t = 1; t < arguments.length; t++) {
		var n = arguments[t];
		for (var r in n) Object.prototype.hasOwnProperty.call(n, r) && (e[r] = n[r]);
	}
	return e;
}, qn = /* @__PURE__ */ function() {
	function e(e, t) {
		for (var n = 0; n < t.length; n++) {
			var r = t[n];
			r.enumerable = r.enumerable || !1, r.configurable = !0, "value" in r && (r.writable = !0), Object.defineProperty(e, r.key, r);
		}
	}
	return function(t, n, r) {
		return n && e(t.prototype, n), r && e(t, r), t;
	};
}();
function Jn(e, t) {
	if (!(e instanceof t)) throw TypeError("Cannot call a class as a function");
}
function Yn(e, t) {
	if (!e) throw ReferenceError("this hasn't been initialised - super() hasn't been called");
	return t && (typeof t == "object" || typeof t == "function") ? t : e;
}
function Xn(e, t) {
	if (typeof t != "function" && t !== null) throw TypeError("Super expression must either be null or a function, not " + typeof t);
	e.prototype = Object.create(t && t.prototype, { constructor: {
		value: e,
		enumerable: !1,
		writable: !0,
		configurable: !0
	} }), t && (Object.setPrototypeOf ? Object.setPrototypeOf(e, t) : e.__proto__ = t);
}
var Zn = function(e) {
	Xn(t, e);
	function t() {
		var e, n, r, i;
		Jn(this, t);
		var a = [...arguments];
		return i = (n = (r = Yn(this, (e = t.__proto__ || Object.getPrototypeOf(t)).call.apply(e, [this].concat(a))), r), r.handleChange = function(e) {
			var t = Bn(e, r.props.hsl, r.props.direction, r.props.a, r.container);
			t && typeof r.props.onChange == "function" && r.props.onChange(t, e);
		}, r.handleMouseDown = function(e) {
			r.handleChange(e), window.addEventListener("mousemove", r.handleChange), window.addEventListener("mouseup", r.handleMouseUp);
		}, r.handleMouseUp = function() {
			r.unbindEventListeners();
		}, r.unbindEventListeners = function() {
			window.removeEventListener("mousemove", r.handleChange), window.removeEventListener("mouseup", r.handleMouseUp);
		}, n), Yn(r, i);
	}
	return qn(t, [{
		key: "componentWillUnmount",
		value: function() {
			this.unbindEventListeners();
		}
	}, {
		key: "render",
		value: function() {
			var e = this, t = this.props.rgb, n = k({
				default: {
					alpha: {
						absolute: "0px 0px 0px 0px",
						borderRadius: this.props.radius
					},
					checkboard: {
						absolute: "0px 0px 0px 0px",
						overflow: "hidden",
						borderRadius: this.props.radius
					},
					gradient: {
						absolute: "0px 0px 0px 0px",
						background: "linear-gradient(to right, rgba(" + t.r + "," + t.g + "," + t.b + ", 0) 0%,\n           rgba(" + t.r + "," + t.g + "," + t.b + ", 1) 100%)",
						boxShadow: this.props.shadow,
						borderRadius: this.props.radius
					},
					container: {
						position: "relative",
						height: "100%",
						margin: "0 3px"
					},
					pointer: {
						position: "absolute",
						left: t.a * 100 + "%"
					},
					slider: {
						width: "4px",
						borderRadius: "1px",
						height: "8px",
						boxShadow: "0 0 2px rgba(0, 0, 0, .6)",
						background: "#fff",
						marginTop: "1px",
						transform: "translateX(-2px)"
					}
				},
				vertical: {
					gradient: { background: "linear-gradient(to bottom, rgba(" + t.r + "," + t.g + "," + t.b + ", 0) 0%,\n           rgba(" + t.r + "," + t.g + "," + t.b + ", 1) 100%)" },
					pointer: {
						left: 0,
						top: t.a * 100 + "%"
					}
				},
				overwrite: Kn({}, this.props.style)
			}, {
				vertical: this.props.direction === "vertical",
				overwrite: !0
			});
			return T.createElement("div", { style: n.alpha }, T.createElement("div", { style: n.checkboard }, T.createElement(Gn, { renderers: this.props.renderers })), T.createElement("div", { style: n.gradient }), T.createElement("div", {
				style: n.container,
				ref: function(t) {
					return e.container = t;
				},
				onMouseDown: this.handleMouseDown,
				onTouchMove: this.handleChange,
				onTouchStart: this.handleChange
			}, T.createElement("div", { style: n.pointer }, this.props.pointer ? T.createElement(this.props.pointer, this.props) : T.createElement("div", { style: n.slider }))));
		}
	}]), t;
}(T.PureComponent || T.Component), Qn = /* @__PURE__ */ function() {
	function e(e, t) {
		for (var n = 0; n < t.length; n++) {
			var r = t[n];
			r.enumerable = r.enumerable || !1, r.configurable = !0, "value" in r && (r.writable = !0), Object.defineProperty(e, r.key, r);
		}
	}
	return function(t, n, r) {
		return n && e(t.prototype, n), r && e(t, r), t;
	};
}();
function $n(e, t, n) {
	return t in e ? Object.defineProperty(e, t, {
		value: n,
		enumerable: !0,
		configurable: !0,
		writable: !0
	}) : e[t] = n, e;
}
function er(e, t) {
	if (!(e instanceof t)) throw TypeError("Cannot call a class as a function");
}
function tr(e, t) {
	if (!e) throw ReferenceError("this hasn't been initialised - super() hasn't been called");
	return t && (typeof t == "object" || typeof t == "function") ? t : e;
}
function nr(e, t) {
	if (typeof t != "function" && t !== null) throw TypeError("Super expression must either be null or a function, not " + typeof t);
	e.prototype = Object.create(t && t.prototype, { constructor: {
		value: e,
		enumerable: !1,
		writable: !0,
		configurable: !0
	} }), t && (Object.setPrototypeOf ? Object.setPrototypeOf(e, t) : e.__proto__ = t);
}
var rr = 1, ir = 38, ar = [ir, 40], or = function(e) {
	return ar.indexOf(e) > -1;
}, sr = function(e) {
	return Number(String(e).replace(/%/g, ""));
}, cr = 1, A = function(e) {
	nr(t, e);
	function t(e) {
		er(this, t);
		var n = tr(this, (t.__proto__ || Object.getPrototypeOf(t)).call(this));
		return n.handleBlur = function() {
			n.state.blurValue && n.setState({
				value: n.state.blurValue,
				blurValue: null
			});
		}, n.handleChange = function(e) {
			n.setUpdatedValue(e.target.value, e);
		}, n.handleKeyDown = function(e) {
			var t = sr(e.target.value);
			if (!isNaN(t) && or(e.keyCode)) {
				var r = n.getArrowOffset(), i = e.keyCode === ir ? t + r : t - r;
				n.setUpdatedValue(i, e);
			}
		}, n.handleDrag = function(e) {
			if (n.props.dragLabel) {
				var t = Math.round(n.props.value + e.movementX);
				t >= 0 && t <= n.props.dragMax && n.props.onChange && n.props.onChange(n.getValueObjectWithLabel(t), e);
			}
		}, n.handleMouseDown = function(e) {
			n.props.dragLabel && (e.preventDefault(), n.handleDrag(e), window.addEventListener("mousemove", n.handleDrag), window.addEventListener("mouseup", n.handleMouseUp));
		}, n.handleMouseUp = function() {
			n.unbindEventListeners();
		}, n.unbindEventListeners = function() {
			window.removeEventListener("mousemove", n.handleDrag), window.removeEventListener("mouseup", n.handleMouseUp);
		}, n.state = {
			value: String(e.value).toUpperCase(),
			blurValue: String(e.value).toUpperCase()
		}, n.inputId = "rc-editable-input-" + cr++, n;
	}
	return Qn(t, [
		{
			key: "componentDidUpdate",
			value: function(e, t) {
				this.props.value !== this.state.value && (e.value !== this.props.value || t.value !== this.state.value) && (this.input === document.activeElement ? this.setState({ blurValue: String(this.props.value).toUpperCase() }) : this.setState({
					value: String(this.props.value).toUpperCase(),
					blurValue: !this.state.blurValue && String(this.props.value).toUpperCase()
				}));
			}
		},
		{
			key: "componentWillUnmount",
			value: function() {
				this.unbindEventListeners();
			}
		},
		{
			key: "getValueObjectWithLabel",
			value: function(e) {
				return $n({}, this.props.label, e);
			}
		},
		{
			key: "getArrowOffset",
			value: function() {
				return this.props.arrowOffset || rr;
			}
		},
		{
			key: "setUpdatedValue",
			value: function(e, t) {
				var n = this.props.label ? this.getValueObjectWithLabel(e) : e;
				this.props.onChange && this.props.onChange(n, t), this.setState({ value: e });
			}
		},
		{
			key: "render",
			value: function() {
				var e = this, t = k({
					default: { wrap: { position: "relative" } },
					"user-override": {
						wrap: this.props.style && this.props.style.wrap ? this.props.style.wrap : {},
						input: this.props.style && this.props.style.input ? this.props.style.input : {},
						label: this.props.style && this.props.style.label ? this.props.style.label : {}
					},
					"dragLabel-true": { label: { cursor: "ew-resize" } }
				}, { "user-override": !0 }, this.props);
				return T.createElement("div", { style: t.wrap }, T.createElement("input", {
					id: this.inputId,
					style: t.input,
					ref: function(t) {
						return e.input = t;
					},
					value: this.state.value,
					onKeyDown: this.handleKeyDown,
					onChange: this.handleChange,
					onBlur: this.handleBlur,
					placeholder: this.props.placeholder,
					spellCheck: "false"
				}), this.props.label && !this.props.hideLabel ? T.createElement("label", {
					htmlFor: this.inputId,
					style: t.label,
					onMouseDown: this.handleMouseDown
				}, this.props.label) : null);
			}
		}
	]), t;
}(T.PureComponent || T.Component), lr = function(e, t, n, r) {
	var i = r.clientWidth, a = r.clientHeight, o = typeof e.pageX == "number" ? e.pageX : e.touches[0].pageX, s = typeof e.pageY == "number" ? e.pageY : e.touches[0].pageY, c = o - (r.getBoundingClientRect().left + window.pageXOffset), l = s - (r.getBoundingClientRect().top + window.pageYOffset);
	if (t === "vertical") {
		var u = void 0;
		if (u = l < 0 ? 359 : l > a ? 0 : 360 * (-(l * 100 / a) + 100) / 100, n.h !== u) return {
			h: u,
			s: n.s,
			l: n.l,
			a: n.a,
			source: "hsl"
		};
	} else {
		var d = void 0;
		if (d = c < 0 ? 0 : c > i ? 359 : 360 * (c * 100 / i) / 100, n.h !== d) return {
			h: d,
			s: n.s,
			l: n.l,
			a: n.a,
			source: "hsl"
		};
	}
	return null;
}, ur = /* @__PURE__ */ function() {
	function e(e, t) {
		for (var n = 0; n < t.length; n++) {
			var r = t[n];
			r.enumerable = r.enumerable || !1, r.configurable = !0, "value" in r && (r.writable = !0), Object.defineProperty(e, r.key, r);
		}
	}
	return function(t, n, r) {
		return n && e(t.prototype, n), r && e(t, r), t;
	};
}();
function dr(e, t) {
	if (!(e instanceof t)) throw TypeError("Cannot call a class as a function");
}
function fr(e, t) {
	if (!e) throw ReferenceError("this hasn't been initialised - super() hasn't been called");
	return t && (typeof t == "object" || typeof t == "function") ? t : e;
}
function pr(e, t) {
	if (typeof t != "function" && t !== null) throw TypeError("Super expression must either be null or a function, not " + typeof t);
	e.prototype = Object.create(t && t.prototype, { constructor: {
		value: e,
		enumerable: !1,
		writable: !0,
		configurable: !0
	} }), t && (Object.setPrototypeOf ? Object.setPrototypeOf(e, t) : e.__proto__ = t);
}
var mr = function(e) {
	pr(t, e);
	function t() {
		var e, n, r, i;
		dr(this, t);
		var a = [...arguments];
		return i = (n = (r = fr(this, (e = t.__proto__ || Object.getPrototypeOf(t)).call.apply(e, [this].concat(a))), r), r.handleChange = function(e) {
			var t = lr(e, r.props.direction, r.props.hsl, r.container);
			t && typeof r.props.onChange == "function" && r.props.onChange(t, e);
		}, r.handleMouseDown = function(e) {
			r.handleChange(e), window.addEventListener("mousemove", r.handleChange), window.addEventListener("mouseup", r.handleMouseUp);
		}, r.handleMouseUp = function() {
			r.unbindEventListeners();
		}, n), fr(r, i);
	}
	return ur(t, [
		{
			key: "componentWillUnmount",
			value: function() {
				this.unbindEventListeners();
			}
		},
		{
			key: "unbindEventListeners",
			value: function() {
				window.removeEventListener("mousemove", this.handleChange), window.removeEventListener("mouseup", this.handleMouseUp);
			}
		},
		{
			key: "render",
			value: function() {
				var e = this, t = this.props.direction, n = t === void 0 ? "horizontal" : t, r = k({
					default: {
						hue: {
							absolute: "0px 0px 0px 0px",
							borderRadius: this.props.radius,
							boxShadow: this.props.shadow
						},
						container: {
							padding: "0 2px",
							position: "relative",
							height: "100%",
							borderRadius: this.props.radius
						},
						pointer: {
							position: "absolute",
							left: this.props.hsl.h * 100 / 360 + "%"
						},
						slider: {
							marginTop: "1px",
							width: "4px",
							borderRadius: "1px",
							height: "8px",
							boxShadow: "0 0 2px rgba(0, 0, 0, .6)",
							background: "#fff",
							transform: "translateX(-2px)"
						}
					},
					vertical: { pointer: {
						left: "0px",
						top: -(this.props.hsl.h * 100 / 360) + 100 + "%"
					} }
				}, { vertical: n === "vertical" });
				return T.createElement("div", { style: r.hue }, T.createElement("div", {
					className: "hue-" + n,
					style: r.container,
					ref: function(t) {
						return e.container = t;
					},
					onMouseDown: this.handleMouseDown,
					onTouchMove: this.handleChange,
					onTouchStart: this.handleChange
				}, T.createElement("style", null, "\n            .hue-horizontal {\n              background: linear-gradient(to right, #f00 0%, #ff0 17%, #0f0\n                33%, #0ff 50%, #00f 67%, #f0f 83%, #f00 100%);\n              background: -webkit-linear-gradient(to right, #f00 0%, #ff0\n                17%, #0f0 33%, #0ff 50%, #00f 67%, #f0f 83%, #f00 100%);\n            }\n\n            .hue-vertical {\n              background: linear-gradient(to top, #f00 0%, #ff0 17%, #0f0 33%,\n                #0ff 50%, #00f 67%, #f0f 83%, #f00 100%);\n              background: -webkit-linear-gradient(to top, #f00 0%, #ff0 17%,\n                #0f0 33%, #0ff 50%, #00f 67%, #f0f 83%, #f00 100%);\n            }\n          "), T.createElement("div", { style: r.pointer }, this.props.pointer ? T.createElement(this.props.pointer, this.props) : T.createElement("div", { style: r.slider }))));
			}
		}
	]), t;
}(T.PureComponent || T.Component);
function hr() {
	this.__data__ = [], this.size = 0;
}
function gr(e, t) {
	return e === t || e !== e && t !== t;
}
function _r(e, t) {
	for (var n = e.length; n--;) if (gr(e[n][0], t)) return n;
	return -1;
}
var vr = Array.prototype.splice;
function yr(e) {
	var t = this.__data__, n = _r(t, e);
	return n < 0 ? !1 : (n == t.length - 1 ? t.pop() : vr.call(t, n, 1), --this.size, !0);
}
function br(e) {
	var t = this.__data__, n = _r(t, e);
	return n < 0 ? void 0 : t[n][1];
}
function xr(e) {
	return _r(this.__data__, e) > -1;
}
function Sr(e, t) {
	var n = this.__data__, r = _r(n, e);
	return r < 0 ? (++this.size, n.push([e, t])) : n[r][1] = t, this;
}
function j(e) {
	var t = -1, n = e == null ? 0 : e.length;
	for (this.clear(); ++t < n;) {
		var r = e[t];
		this.set(r[0], r[1]);
	}
}
j.prototype.clear = hr, j.prototype.delete = yr, j.prototype.get = br, j.prototype.has = xr, j.prototype.set = Sr;
function Cr() {
	this.__data__ = new j(), this.size = 0;
}
function wr(e) {
	var t = this.__data__, n = t.delete(e);
	return this.size = t.size, n;
}
function Tr(e) {
	return this.__data__.get(e);
}
function Er(e) {
	return this.__data__.has(e);
}
var Dr = typeof global == "object" && global && global.Object === Object && global, Or = typeof self == "object" && self && self.Object === Object && self, M = Dr || Or || Function("return this")(), N = M.Symbol, kr = Object.prototype, Ar = kr.hasOwnProperty, jr = kr.toString, Mr = N ? N.toStringTag : void 0;
function Nr(e) {
	var t = Ar.call(e, Mr), n = e[Mr];
	try {
		e[Mr] = void 0;
		var r = !0;
	} catch {}
	var i = jr.call(e);
	return r && (t ? e[Mr] = n : delete e[Mr]), i;
}
var Pr = Object.prototype.toString;
function Fr(e) {
	return Pr.call(e);
}
var Ir = "[object Null]", Lr = "[object Undefined]", Rr = N ? N.toStringTag : void 0;
function P(e) {
	return e == null ? e === void 0 ? Lr : Ir : Rr && Rr in Object(e) ? Nr(e) : Fr(e);
}
function F(e) {
	var t = typeof e;
	return e != null && (t == "object" || t == "function");
}
var zr = "[object AsyncFunction]", Br = "[object Function]", Vr = "[object GeneratorFunction]", Hr = "[object Proxy]";
function Ur(e) {
	if (!F(e)) return !1;
	var t = P(e);
	return t == Br || t == Vr || t == zr || t == Hr;
}
var Wr = M["__core-js_shared__"], Gr = function() {
	var e = /[^.]+$/.exec(Wr && Wr.keys && Wr.keys.IE_PROTO || "");
	return e ? "Symbol(src)_1." + e : "";
}();
function Kr(e) {
	return !!Gr && Gr in e;
}
var qr = Function.prototype.toString;
function I(e) {
	if (e != null) {
		try {
			return qr.call(e);
		} catch {}
		try {
			return e + "";
		} catch {}
	}
	return "";
}
var Jr = /[\\^$.*+?()[\]{}|]/g, Yr = /^\[object .+?Constructor\]$/, Xr = Function.prototype, Zr = Object.prototype, Qr = Xr.toString, $r = Zr.hasOwnProperty, ei = RegExp("^" + Qr.call($r).replace(Jr, "\\$&").replace(/hasOwnProperty|(function).*?(?=\\\()| for .+?(?=\\\])/g, "$1.*?") + "$");
function ti(e) {
	return !F(e) || Kr(e) ? !1 : (Ur(e) ? ei : Yr).test(I(e));
}
function ni(e, t) {
	return e?.[t];
}
function L(e, t) {
	var n = ni(e, t);
	return ti(n) ? n : void 0;
}
var ri = L(M, "Map"), ii = L(Object, "create");
function ai() {
	this.__data__ = ii ? ii(null) : {}, this.size = 0;
}
function oi(e) {
	var t = this.has(e) && delete this.__data__[e];
	return this.size -= +!!t, t;
}
var si = "__lodash_hash_undefined__", ci = Object.prototype.hasOwnProperty;
function li(e) {
	var t = this.__data__;
	if (ii) {
		var n = t[e];
		return n === si ? void 0 : n;
	}
	return ci.call(t, e) ? t[e] : void 0;
}
var ui = Object.prototype.hasOwnProperty;
function di(e) {
	var t = this.__data__;
	return ii ? t[e] !== void 0 : ui.call(t, e);
}
var fi = "__lodash_hash_undefined__";
function pi(e, t) {
	var n = this.__data__;
	return this.size += +!this.has(e), n[e] = ii && t === void 0 ? fi : t, this;
}
function R(e) {
	var t = -1, n = e == null ? 0 : e.length;
	for (this.clear(); ++t < n;) {
		var r = e[t];
		this.set(r[0], r[1]);
	}
}
R.prototype.clear = ai, R.prototype.delete = oi, R.prototype.get = li, R.prototype.has = di, R.prototype.set = pi;
function mi() {
	this.size = 0, this.__data__ = {
		hash: new R(),
		map: new (ri || j)(),
		string: new R()
	};
}
function hi(e) {
	var t = typeof e;
	return t == "string" || t == "number" || t == "symbol" || t == "boolean" ? e !== "__proto__" : e === null;
}
function gi(e, t) {
	var n = e.__data__;
	return hi(t) ? n[typeof t == "string" ? "string" : "hash"] : n.map;
}
function _i(e) {
	var t = gi(this, e).delete(e);
	return this.size -= +!!t, t;
}
function vi(e) {
	return gi(this, e).get(e);
}
function yi(e) {
	return gi(this, e).has(e);
}
function bi(e, t) {
	var n = gi(this, e), r = n.size;
	return n.set(e, t), this.size += n.size == r ? 0 : 1, this;
}
function z(e) {
	var t = -1, n = e == null ? 0 : e.length;
	for (this.clear(); ++t < n;) {
		var r = e[t];
		this.set(r[0], r[1]);
	}
}
z.prototype.clear = mi, z.prototype.delete = _i, z.prototype.get = vi, z.prototype.has = yi, z.prototype.set = bi;
var xi = 200;
function Si(e, t) {
	var n = this.__data__;
	if (n instanceof j) {
		var r = n.__data__;
		if (!ri || r.length < xi - 1) return r.push([e, t]), this.size = ++n.size, this;
		n = this.__data__ = new z(r);
	}
	return n.set(e, t), this.size = n.size, this;
}
function B(e) {
	var t = this.__data__ = new j(e);
	this.size = t.size;
}
B.prototype.clear = Cr, B.prototype.delete = wr, B.prototype.get = Tr, B.prototype.has = Er, B.prototype.set = Si;
var Ci = function() {
	try {
		var e = L(Object, "defineProperty");
		return e({}, "", {}), e;
	} catch {}
}();
function wi(e, t, n) {
	t == "__proto__" && Ci ? Ci(e, t, {
		configurable: !0,
		enumerable: !0,
		value: n,
		writable: !0
	}) : e[t] = n;
}
function Ti(e, t, n) {
	(n !== void 0 && !gr(e[t], n) || n === void 0 && !(t in e)) && wi(e, t, n);
}
function Ei(e) {
	return function(e, t, n) {
		for (var r = -1, i = Object(e), a = n(e), o = a.length; o--;) {
			var s = a[++r];
			if (t(i[s], s, i) === !1) break;
		}
		return e;
	};
}
var Di = Ei(), Oi = typeof exports == "object" && exports && !exports.nodeType && exports, ki = Oi && typeof module == "object" && module && !module.nodeType && module, Ai = ki && ki.exports === Oi ? M.Buffer : void 0;
Ai && Ai.allocUnsafe;
function ji(e, t) {
	return e.slice();
}
var Mi = M.Uint8Array;
function Ni(e) {
	var t = new e.constructor(e.byteLength);
	return new Mi(t).set(new Mi(e)), t;
}
function Pi(e, t) {
	var n = Ni(e.buffer);
	return new e.constructor(n, e.byteOffset, e.length);
}
function Fi(e, t) {
	var n = -1, r = e.length;
	for (t ||= Array(r); ++n < r;) t[n] = e[n];
	return t;
}
var Ii = Object.create, Li = /* @__PURE__ */ function() {
	function e() {}
	return function(t) {
		if (!F(t)) return {};
		if (Ii) return Ii(t);
		e.prototype = t;
		var n = new e();
		return e.prototype = void 0, n;
	};
}();
function Ri(e, t) {
	return function(n) {
		return e(t(n));
	};
}
var zi = Ri(Object.getPrototypeOf, Object), Bi = Object.prototype;
function Vi(e) {
	var t = e && e.constructor;
	return e === (typeof t == "function" && t.prototype || Bi);
}
function Hi(e) {
	return typeof e.constructor == "function" && !Vi(e) ? Li(zi(e)) : {};
}
function V(e) {
	return typeof e == "object" && !!e;
}
var Ui = "[object Arguments]";
function Wi(e) {
	return V(e) && P(e) == Ui;
}
var Gi = Object.prototype, Ki = Gi.hasOwnProperty, qi = Gi.propertyIsEnumerable, Ji = Wi(/* @__PURE__ */ function() {
	return arguments;
}()) ? Wi : function(e) {
	return V(e) && Ki.call(e, "callee") && !qi.call(e, "callee");
}, H = Array.isArray, Yi = 9007199254740991;
function Xi(e) {
	return typeof e == "number" && e > -1 && e % 1 == 0 && e <= Yi;
}
function Zi(e) {
	return e != null && Xi(e.length) && !Ur(e);
}
function Qi(e) {
	return V(e) && Zi(e);
}
function $i() {
	return !1;
}
var ea = typeof exports == "object" && exports && !exports.nodeType && exports, ta = ea && typeof module == "object" && module && !module.nodeType && module, na = ta && ta.exports === ea ? M.Buffer : void 0, ra = (na ? na.isBuffer : void 0) || $i, ia = "[object Object]", aa = Function.prototype, oa = Object.prototype, sa = aa.toString, ca = oa.hasOwnProperty, la = sa.call(Object);
function ua(e) {
	if (!V(e) || P(e) != ia) return !1;
	var t = zi(e);
	if (t === null) return !0;
	var n = ca.call(t, "constructor") && t.constructor;
	return typeof n == "function" && n instanceof n && sa.call(n) == la;
}
var da = "[object Arguments]", fa = "[object Array]", pa = "[object Boolean]", ma = "[object Date]", ha = "[object Error]", ga = "[object Function]", _a = "[object Map]", va = "[object Number]", ya = "[object Object]", ba = "[object RegExp]", xa = "[object Set]", Sa = "[object String]", Ca = "[object WeakMap]", wa = "[object ArrayBuffer]", Ta = "[object DataView]", Ea = "[object Float32Array]", Da = "[object Float64Array]", Oa = "[object Int8Array]", ka = "[object Int16Array]", Aa = "[object Int32Array]", ja = "[object Uint8Array]", Ma = "[object Uint8ClampedArray]", Na = "[object Uint16Array]", Pa = "[object Uint32Array]", U = {};
U[Ea] = U[Da] = U[Oa] = U[ka] = U[Aa] = U[ja] = U[Ma] = U[Na] = U[Pa] = !0, U[da] = U[fa] = U[wa] = U[pa] = U[Ta] = U[ma] = U[ha] = U[ga] = U[_a] = U[va] = U[ya] = U[ba] = U[xa] = U[Sa] = U[Ca] = !1;
function Fa(e) {
	return V(e) && Xi(e.length) && !!U[P(e)];
}
function Ia(e) {
	return function(t) {
		return e(t);
	};
}
var La = typeof exports == "object" && exports && !exports.nodeType && exports, Ra = La && typeof module == "object" && module && !module.nodeType && module, za = Ra && Ra.exports === La && Dr.process, Ba = function() {
	try {
		return Ra && Ra.require && Ra.require("util").types || za && za.binding && za.binding("util");
	} catch {}
}(), Va = Ba && Ba.isTypedArray, Ha = Va ? Ia(Va) : Fa;
function Ua(e, t) {
	if (!(t === "constructor" && typeof e[t] == "function") && t != "__proto__") return e[t];
}
var Wa = Object.prototype.hasOwnProperty;
function Ga(e, t, n) {
	var r = e[t];
	(!(Wa.call(e, t) && gr(r, n)) || n === void 0 && !(t in e)) && wi(e, t, n);
}
function Ka(e, t, n, r) {
	var i = !n;
	n ||= {};
	for (var a = -1, o = t.length; ++a < o;) {
		var s = t[a], c = void 0;
		c === void 0 && (c = e[s]), i ? wi(n, s, c) : Ga(n, s, c);
	}
	return n;
}
function qa(e, t) {
	for (var n = -1, r = Array(e); ++n < e;) r[n] = t(n);
	return r;
}
var Ja = 9007199254740991, Ya = /^(?:0|[1-9]\d*)$/;
function Xa(e, t) {
	var n = typeof e;
	return t ??= Ja, !!t && (n == "number" || n != "symbol" && Ya.test(e)) && e > -1 && e % 1 == 0 && e < t;
}
var Za = Object.prototype.hasOwnProperty;
function Qa(e, t) {
	var n = H(e), r = !n && Ji(e), i = !n && !r && ra(e), a = !n && !r && !i && Ha(e), o = n || r || i || a, s = o ? qa(e.length, String) : [], c = s.length;
	for (var l in e) (t || Za.call(e, l)) && !(o && (l == "length" || i && (l == "offset" || l == "parent") || a && (l == "buffer" || l == "byteLength" || l == "byteOffset") || Xa(l, c))) && s.push(l);
	return s;
}
function $a(e) {
	var t = [];
	if (e != null) for (var n in Object(e)) t.push(n);
	return t;
}
var eo = Object.prototype.hasOwnProperty;
function to(e) {
	if (!F(e)) return $a(e);
	var t = Vi(e), n = [];
	for (var r in e) r == "constructor" && (t || !eo.call(e, r)) || n.push(r);
	return n;
}
function no(e) {
	return Zi(e) ? Qa(e, !0) : to(e);
}
function ro(e) {
	return Ka(e, no(e));
}
function io(e, t, n, r, i, a, o) {
	var s = Ua(e, n), c = Ua(t, n), l = o.get(c);
	if (l) {
		Ti(e, n, l);
		return;
	}
	var u = a ? a(s, c, n + "", e, t, o) : void 0, d = u === void 0;
	if (d) {
		var f = H(c), p = !f && ra(c), m = !f && !p && Ha(c);
		u = c, f || p || m ? H(s) ? u = s : Qi(s) ? u = Fi(s) : p ? (d = !1, u = ji(c)) : m ? (d = !1, u = Pi(c)) : u = [] : ua(c) || Ji(c) ? (u = s, Ji(s) ? u = ro(s) : (!F(s) || Ur(s)) && (u = Hi(c))) : d = !1;
	}
	d && (o.set(c, u), i(u, c, r, a, o), o.delete(c)), Ti(e, n, u);
}
function ao(e, t, n, r, i) {
	e !== t && Di(t, function(a, o) {
		if (i ||= new B(), F(a)) io(e, t, o, n, ao, r, i);
		else {
			var s = r ? r(Ua(e, o), a, o + "", e, t, i) : void 0;
			s === void 0 && (s = a), Ti(e, o, s);
		}
	}, no);
}
function oo(e) {
	return e;
}
function so(e, t, n) {
	switch (n.length) {
		case 0: return e.call(t);
		case 1: return e.call(t, n[0]);
		case 2: return e.call(t, n[0], n[1]);
		case 3: return e.call(t, n[0], n[1], n[2]);
	}
	return e.apply(t, n);
}
var co = Math.max;
function lo(e, t, n) {
	return t = co(t === void 0 ? e.length - 1 : t, 0), function() {
		for (var r = arguments, i = -1, a = co(r.length - t, 0), o = Array(a); ++i < a;) o[i] = r[t + i];
		i = -1;
		for (var s = Array(t + 1); ++i < t;) s[i] = r[i];
		return s[t] = n(o), so(e, this, s);
	};
}
function uo(e) {
	return function() {
		return e;
	};
}
var fo = Ci ? function(e, t) {
	return Ci(e, "toString", {
		configurable: !0,
		enumerable: !1,
		value: uo(t),
		writable: !0
	});
} : oo, po = 800, mo = 16, ho = Date.now;
function go(e) {
	var t = 0, n = 0;
	return function() {
		var r = ho(), i = mo - (r - n);
		if (n = r, i > 0) {
			if (++t >= po) return arguments[0];
		} else t = 0;
		return e.apply(void 0, arguments);
	};
}
var _o = go(fo);
function vo(e, t) {
	return _o(lo(e, t, oo), e + "");
}
function yo(e, t, n) {
	if (!F(n)) return !1;
	var r = typeof t;
	return (r == "number" ? Zi(n) && Xa(t, n.length) : r == "string" && t in n) ? gr(n[t], e) : !1;
}
function bo(e) {
	return vo(function(t, n) {
		var r = -1, i = n.length, a = i > 1 ? n[i - 1] : void 0, o = i > 2 ? n[2] : void 0;
		for (a = e.length > 3 && typeof a == "function" ? (i--, a) : void 0, o && yo(n[0], n[1], o) && (a = i < 3 ? void 0 : a, i = 1), t = Object(t); ++r < i;) {
			var s = n[r];
			s && e(t, s, r, a);
		}
		return t;
	});
}
var W = bo(function(e, t, n) {
	ao(e, t, n);
}), xo = function(e) {
	var t = e.zDepth, n = e.radius, r = e.background, i = e.children, a = e.styles, o = a === void 0 ? {} : a, s = k(W({
		default: {
			wrap: {
				position: "relative",
				display: "inline-block"
			},
			content: { position: "relative" },
			bg: {
				absolute: "0px 0px 0px 0px",
				boxShadow: "0 " + t + "px " + t * 4 + "px rgba(0,0,0,.24)",
				borderRadius: n,
				background: r
			}
		},
		"zDepth-0": { bg: { boxShadow: "none" } },
		"zDepth-1": { bg: { boxShadow: "0 2px 10px rgba(0,0,0,.12), 0 2px 5px rgba(0,0,0,.16)" } },
		"zDepth-2": { bg: { boxShadow: "0 6px 20px rgba(0,0,0,.19), 0 8px 17px rgba(0,0,0,.2)" } },
		"zDepth-3": { bg: { boxShadow: "0 17px 50px rgba(0,0,0,.19), 0 12px 15px rgba(0,0,0,.24)" } },
		"zDepth-4": { bg: { boxShadow: "0 25px 55px rgba(0,0,0,.21), 0 16px 28px rgba(0,0,0,.22)" } },
		"zDepth-5": { bg: { boxShadow: "0 40px 77px rgba(0,0,0,.22), 0 27px 24px rgba(0,0,0,.2)" } },
		square: { bg: { borderRadius: "0" } },
		circle: { bg: { borderRadius: "50%" } }
	}, o), { "zDepth-1": t === 1 });
	return T.createElement("div", { style: s.wrap }, T.createElement("div", { style: s.bg }), T.createElement("div", { style: s.content }, i));
};
xo.propTypes = {
	background: a.string,
	zDepth: a.oneOf([
		0,
		1,
		2,
		3,
		4,
		5
	]),
	radius: a.number,
	styles: a.object
}, xo.defaultProps = {
	background: "#fff",
	zDepth: 1,
	radius: 2,
	styles: {}
};
var So = function() {
	return M.Date.now();
}, Co = /\s/;
function wo(e) {
	for (var t = e.length; t-- && Co.test(e.charAt(t)););
	return t;
}
var To = /^\s+/;
function Eo(e) {
	return e && e.slice(0, wo(e) + 1).replace(To, "");
}
var Do = "[object Symbol]";
function Oo(e) {
	return typeof e == "symbol" || V(e) && P(e) == Do;
}
var ko = NaN, Ao = /^[-+]0x[0-9a-f]+$/i, jo = /^0b[01]+$/i, Mo = /^0o[0-7]+$/i, No = parseInt;
function Po(e) {
	if (typeof e == "number") return e;
	if (Oo(e)) return ko;
	if (F(e)) {
		var t = typeof e.valueOf == "function" ? e.valueOf() : e;
		e = F(t) ? t + "" : t;
	}
	if (typeof e != "string") return e === 0 ? e : +e;
	e = Eo(e);
	var n = jo.test(e);
	return n || Mo.test(e) ? No(e.slice(2), n ? 2 : 8) : Ao.test(e) ? ko : +e;
}
var Fo = "Expected a function", Io = Math.max, Lo = Math.min;
function Ro(e, t, n) {
	var r, i, a, o, s, c, l = 0, u = !1, d = !1, f = !0;
	if (typeof e != "function") throw TypeError(Fo);
	t = Po(t) || 0, F(n) && (u = !!n.leading, d = "maxWait" in n, a = d ? Io(Po(n.maxWait) || 0, t) : a, f = "trailing" in n ? !!n.trailing : f);
	function p(t) {
		var n = r, a = i;
		return r = i = void 0, l = t, o = e.apply(a, n), o;
	}
	function m(e) {
		return l = e, s = setTimeout(_, t), u ? p(e) : o;
	}
	function h(e) {
		var n = e - c, r = e - l, i = t - n;
		return d ? Lo(i, a - r) : i;
	}
	function g(e) {
		var n = e - c, r = e - l;
		return c === void 0 || n >= t || n < 0 || d && r >= a;
	}
	function _() {
		var e = So();
		if (g(e)) return v(e);
		s = setTimeout(_, h(e));
	}
	function v(e) {
		return s = void 0, f && r ? p(e) : (r = i = void 0, o);
	}
	function y() {
		s !== void 0 && clearTimeout(s), l = 0, r = c = i = s = void 0;
	}
	function b() {
		return s === void 0 ? o : v(So());
	}
	function ee() {
		var e = So(), n = g(e);
		if (r = arguments, i = this, c = e, n) {
			if (s === void 0) return m(c);
			if (d) return clearTimeout(s), s = setTimeout(_, t), p(c);
		}
		return s === void 0 && (s = setTimeout(_, t)), o;
	}
	return ee.cancel = y, ee.flush = b, ee;
}
var zo = "Expected a function";
function Bo(e, t, n) {
	var r = !0, i = !0;
	if (typeof e != "function") throw TypeError(zo);
	return F(n) && (r = "leading" in n ? !!n.leading : r, i = "trailing" in n ? !!n.trailing : i), Ro(e, t, {
		leading: r,
		maxWait: t,
		trailing: i
	});
}
var Vo = function(e, t, n) {
	var r = n.getBoundingClientRect(), i = r.width, a = r.height, o = typeof e.pageX == "number" ? e.pageX : e.touches[0].pageX, s = typeof e.pageY == "number" ? e.pageY : e.touches[0].pageY, c = o - (n.getBoundingClientRect().left + window.pageXOffset), l = s - (n.getBoundingClientRect().top + window.pageYOffset);
	c < 0 ? c = 0 : c > i && (c = i), l < 0 ? l = 0 : l > a && (l = a);
	var u = c / i, d = 1 - l / a;
	return {
		h: t.h,
		s: u,
		v: d,
		a: t.a,
		source: "hsv"
	};
}, Ho = /* @__PURE__ */ function() {
	function e(e, t) {
		for (var n = 0; n < t.length; n++) {
			var r = t[n];
			r.enumerable = r.enumerable || !1, r.configurable = !0, "value" in r && (r.writable = !0), Object.defineProperty(e, r.key, r);
		}
	}
	return function(t, n, r) {
		return n && e(t.prototype, n), r && e(t, r), t;
	};
}();
function Uo(e, t) {
	if (!(e instanceof t)) throw TypeError("Cannot call a class as a function");
}
function Wo(e, t) {
	if (!e) throw ReferenceError("this hasn't been initialised - super() hasn't been called");
	return t && (typeof t == "object" || typeof t == "function") ? t : e;
}
function Go(e, t) {
	if (typeof t != "function" && t !== null) throw TypeError("Super expression must either be null or a function, not " + typeof t);
	e.prototype = Object.create(t && t.prototype, { constructor: {
		value: e,
		enumerable: !1,
		writable: !0,
		configurable: !0
	} }), t && (Object.setPrototypeOf ? Object.setPrototypeOf(e, t) : e.__proto__ = t);
}
var Ko = function(e) {
	Go(t, e);
	function t(e) {
		Uo(this, t);
		var n = Wo(this, (t.__proto__ || Object.getPrototypeOf(t)).call(this, e));
		return n.handleChange = function(e) {
			typeof n.props.onChange == "function" && n.throttle(n.props.onChange, Vo(e, n.props.hsl, n.container), e);
		}, n.handleMouseDown = function(e) {
			n.handleChange(e);
			var t = n.getContainerRenderWindow();
			t.addEventListener("mousemove", n.handleChange), t.addEventListener("mouseup", n.handleMouseUp);
		}, n.handleMouseUp = function() {
			n.unbindEventListeners();
		}, n.throttle = Bo(function(e, t, n) {
			e(t, n);
		}, 50), n;
	}
	return Ho(t, [
		{
			key: "componentWillUnmount",
			value: function() {
				this.throttle.cancel(), this.unbindEventListeners();
			}
		},
		{
			key: "getContainerRenderWindow",
			value: function() {
				for (var e = this.container, t = window; !t.document.contains(e) && t.parent !== t;) t = t.parent;
				return t;
			}
		},
		{
			key: "unbindEventListeners",
			value: function() {
				var e = this.getContainerRenderWindow();
				e.removeEventListener("mousemove", this.handleChange), e.removeEventListener("mouseup", this.handleMouseUp);
			}
		},
		{
			key: "render",
			value: function() {
				var e = this, t = this.props.style || {}, n = t.color, r = t.white, i = t.black, a = t.pointer, o = t.circle, s = k({
					default: {
						color: {
							absolute: "0px 0px 0px 0px",
							background: "hsl(" + this.props.hsl.h + ",100%, 50%)",
							borderRadius: this.props.radius
						},
						white: {
							absolute: "0px 0px 0px 0px",
							borderRadius: this.props.radius
						},
						black: {
							absolute: "0px 0px 0px 0px",
							boxShadow: this.props.shadow,
							borderRadius: this.props.radius
						},
						pointer: {
							position: "absolute",
							top: -(this.props.hsv.v * 100) + 100 + "%",
							left: this.props.hsv.s * 100 + "%",
							cursor: "default"
						},
						circle: {
							width: "4px",
							height: "4px",
							boxShadow: "0 0 0 1.5px #fff, inset 0 0 1px 1px rgba(0,0,0,.3),\n            0 0 1px 2px rgba(0,0,0,.4)",
							borderRadius: "50%",
							cursor: "hand",
							transform: "translate(-2px, -2px)"
						}
					},
					custom: {
						color: n,
						white: r,
						black: i,
						pointer: a,
						circle: o
					}
				}, { custom: !!this.props.style });
				return T.createElement("div", {
					style: s.color,
					ref: function(t) {
						return e.container = t;
					},
					onMouseDown: this.handleMouseDown,
					onTouchMove: this.handleChange,
					onTouchStart: this.handleChange
				}, T.createElement("style", null, "\n          .saturation-white {\n            background: -webkit-linear-gradient(to right, #fff, rgba(255,255,255,0));\n            background: linear-gradient(to right, #fff, rgba(255,255,255,0));\n          }\n          .saturation-black {\n            background: -webkit-linear-gradient(to top, #000, rgba(0,0,0,0));\n            background: linear-gradient(to top, #000, rgba(0,0,0,0));\n          }\n        "), T.createElement("div", {
					style: s.white,
					className: "saturation-white"
				}, T.createElement("div", {
					style: s.black,
					className: "saturation-black"
				}), T.createElement("div", { style: s.pointer }, this.props.pointer ? T.createElement(this.props.pointer, this.props) : T.createElement("div", { style: s.circle }))));
			}
		}
	]), t;
}(T.PureComponent || T.Component);
function qo(e, t) {
	for (var n = -1, r = e == null ? 0 : e.length; ++n < r && t(e[n], n, e) !== !1;);
	return e;
}
var Jo = Ri(Object.keys, Object), Yo = Object.prototype.hasOwnProperty;
function Xo(e) {
	if (!Vi(e)) return Jo(e);
	var t = [];
	for (var n in Object(e)) Yo.call(e, n) && n != "constructor" && t.push(n);
	return t;
}
function Zo(e) {
	return Zi(e) ? Qa(e) : Xo(e);
}
function Qo(e, t) {
	return e && Di(e, t, Zo);
}
function $o(e, t) {
	return function(t, n) {
		if (t == null) return t;
		if (!Zi(t)) return e(t, n);
		for (var r = t.length, i = -1, a = Object(t); ++i < r && n(a[i], i, a) !== !1;);
		return t;
	};
}
var es = $o(Qo);
function ts(e) {
	return typeof e == "function" ? e : oo;
}
function ns(e, t) {
	return (H(e) ? qo : es)(e, ts(t));
}
function rs(e) {
	"@babel/helpers - typeof";
	return rs = typeof Symbol == "function" && typeof Symbol.iterator == "symbol" ? function(e) {
		return typeof e;
	} : function(e) {
		return e && typeof Symbol == "function" && e.constructor === Symbol && e !== Symbol.prototype ? "symbol" : typeof e;
	}, rs(e);
}
var is = /^\s+/, as = /\s+$/;
function G(e, t) {
	if (e ||= "", t ||= {}, e instanceof G) return e;
	if (!(this instanceof G)) return new G(e, t);
	var n = os(e);
	this._originalInput = e, this._r = n.r, this._g = n.g, this._b = n.b, this._a = n.a, this._roundA = Math.round(100 * this._a) / 100, this._format = t.format || n.format, this._gradientType = t.gradientType, this._r < 1 && (this._r = Math.round(this._r)), this._g < 1 && (this._g = Math.round(this._g)), this._b < 1 && (this._b = Math.round(this._b)), this._ok = n.ok;
}
G.prototype = {
	isDark: function() {
		return this.getBrightness() < 128;
	},
	isLight: function() {
		return !this.isDark();
	},
	isValid: function() {
		return this._ok;
	},
	getOriginalInput: function() {
		return this._originalInput;
	},
	getFormat: function() {
		return this._format;
	},
	getAlpha: function() {
		return this._a;
	},
	getBrightness: function() {
		var e = this.toRgb();
		return (e.r * 299 + e.g * 587 + e.b * 114) / 1e3;
	},
	getLuminance: function() {
		var e = this.toRgb(), t, n, r, i, a, o;
		return t = e.r / 255, n = e.g / 255, r = e.b / 255, i = t <= .03928 ? t / 12.92 : ((t + .055) / 1.055) ** 2.4, a = n <= .03928 ? n / 12.92 : ((n + .055) / 1.055) ** 2.4, o = r <= .03928 ? r / 12.92 : ((r + .055) / 1.055) ** 2.4, .2126 * i + .7152 * a + .0722 * o;
	},
	setAlpha: function(e) {
		return this._a = As(e), this._roundA = Math.round(100 * this._a) / 100, this;
	},
	toHsv: function() {
		var e = us(this._r, this._g, this._b);
		return {
			h: e.h * 360,
			s: e.s,
			v: e.v,
			a: this._a
		};
	},
	toHsvString: function() {
		var e = us(this._r, this._g, this._b), t = Math.round(e.h * 360), n = Math.round(e.s * 100), r = Math.round(e.v * 100);
		return this._a == 1 ? "hsv(" + t + ", " + n + "%, " + r + "%)" : "hsva(" + t + ", " + n + "%, " + r + "%, " + this._roundA + ")";
	},
	toHsl: function() {
		var e = cs(this._r, this._g, this._b);
		return {
			h: e.h * 360,
			s: e.s,
			l: e.l,
			a: this._a
		};
	},
	toHslString: function() {
		var e = cs(this._r, this._g, this._b), t = Math.round(e.h * 360), n = Math.round(e.s * 100), r = Math.round(e.l * 100);
		return this._a == 1 ? "hsl(" + t + ", " + n + "%, " + r + "%)" : "hsla(" + t + ", " + n + "%, " + r + "%, " + this._roundA + ")";
	},
	toHex: function(e) {
		return fs(this._r, this._g, this._b, e);
	},
	toHexString: function(e) {
		return "#" + this.toHex(e);
	},
	toHex8: function(e) {
		return ps(this._r, this._g, this._b, this._a, e);
	},
	toHex8String: function(e) {
		return "#" + this.toHex8(e);
	},
	toRgb: function() {
		return {
			r: Math.round(this._r),
			g: Math.round(this._g),
			b: Math.round(this._b),
			a: this._a
		};
	},
	toRgbString: function() {
		return this._a == 1 ? "rgb(" + Math.round(this._r) + ", " + Math.round(this._g) + ", " + Math.round(this._b) + ")" : "rgba(" + Math.round(this._r) + ", " + Math.round(this._g) + ", " + Math.round(this._b) + ", " + this._roundA + ")";
	},
	toPercentageRgb: function() {
		return {
			r: Math.round(K(this._r, 255) * 100) + "%",
			g: Math.round(K(this._g, 255) * 100) + "%",
			b: Math.round(K(this._b, 255) * 100) + "%",
			a: this._a
		};
	},
	toPercentageRgbString: function() {
		return this._a == 1 ? "rgb(" + Math.round(K(this._r, 255) * 100) + "%, " + Math.round(K(this._g, 255) * 100) + "%, " + Math.round(K(this._b, 255) * 100) + "%)" : "rgba(" + Math.round(K(this._r, 255) * 100) + "%, " + Math.round(K(this._g, 255) * 100) + "%, " + Math.round(K(this._b, 255) * 100) + "%, " + this._roundA + ")";
	},
	toName: function() {
		return this._a === 0 ? "transparent" : this._a < 1 ? !1 : Os[fs(this._r, this._g, this._b, !0)] || !1;
	},
	toFilter: function(e) {
		var t = "#" + ms(this._r, this._g, this._b, this._a), n = t, r = this._gradientType ? "GradientType = 1, " : "";
		if (e) {
			var i = G(e);
			n = "#" + ms(i._r, i._g, i._b, i._a);
		}
		return "progid:DXImageTransform.Microsoft.gradient(" + r + "startColorstr=" + t + ",endColorstr=" + n + ")";
	},
	toString: function(e) {
		var t = !!e;
		e ||= this._format;
		var n = !1, r = this._a < 1 && this._a >= 0;
		return !t && r && (e === "hex" || e === "hex6" || e === "hex3" || e === "hex4" || e === "hex8" || e === "name") ? e === "name" && this._a === 0 ? this.toName() : this.toRgbString() : (e === "rgb" && (n = this.toRgbString()), e === "prgb" && (n = this.toPercentageRgbString()), (e === "hex" || e === "hex6") && (n = this.toHexString()), e === "hex3" && (n = this.toHexString(!0)), e === "hex4" && (n = this.toHex8String(!0)), e === "hex8" && (n = this.toHex8String()), e === "name" && (n = this.toName()), e === "hsl" && (n = this.toHslString()), e === "hsv" && (n = this.toHsvString()), n || this.toHexString());
	},
	clone: function() {
		return G(this.toString());
	},
	_applyModification: function(e, t) {
		var n = e.apply(null, [this].concat([].slice.call(t)));
		return this._r = n._r, this._g = n._g, this._b = n._b, this.setAlpha(n._a), this;
	},
	lighten: function() {
		return this._applyModification(vs, arguments);
	},
	brighten: function() {
		return this._applyModification(ys, arguments);
	},
	darken: function() {
		return this._applyModification(bs, arguments);
	},
	desaturate: function() {
		return this._applyModification(hs, arguments);
	},
	saturate: function() {
		return this._applyModification(gs, arguments);
	},
	greyscale: function() {
		return this._applyModification(_s, arguments);
	},
	spin: function() {
		return this._applyModification(xs, arguments);
	},
	_applyCombination: function(e, t) {
		return e.apply(null, [this].concat([].slice.call(t)));
	},
	analogous: function() {
		return this._applyCombination(Ts, arguments);
	},
	complement: function() {
		return this._applyCombination(Ss, arguments);
	},
	monochromatic: function() {
		return this._applyCombination(Es, arguments);
	},
	splitcomplement: function() {
		return this._applyCombination(ws, arguments);
	},
	triad: function() {
		return this._applyCombination(Cs, [3]);
	},
	tetrad: function() {
		return this._applyCombination(Cs, [4]);
	}
}, G.fromRatio = function(e, t) {
	if (rs(e) == "object") {
		var n = {};
		for (var r in e) e.hasOwnProperty(r) && (r === "a" ? n[r] = e[r] : n[r] = Ps(e[r]));
		e = n;
	}
	return G(e, t);
};
function os(e) {
	var t = {
		r: 0,
		g: 0,
		b: 0
	}, n = 1, r = null, i = null, a = null, o = !1, s = !1;
	return typeof e == "string" && (e = Ls(e)), rs(e) == "object" && (X(e.r) && X(e.g) && X(e.b) ? (t = ss(e.r, e.g, e.b), o = !0, s = String(e.r).substr(-1) === "%" ? "prgb" : "rgb") : X(e.h) && X(e.s) && X(e.v) ? (r = Ps(e.s), i = Ps(e.v), t = ds(e.h, r, i), o = !0, s = "hsv") : X(e.h) && X(e.s) && X(e.l) && (r = Ps(e.s), a = Ps(e.l), t = ls(e.h, r, a), o = !0, s = "hsl"), e.hasOwnProperty("a") && (n = e.a)), n = As(n), {
		ok: o,
		format: e.format || s,
		r: Math.min(255, Math.max(t.r, 0)),
		g: Math.min(255, Math.max(t.g, 0)),
		b: Math.min(255, Math.max(t.b, 0)),
		a: n
	};
}
function ss(e, t, n) {
	return {
		r: K(e, 255) * 255,
		g: K(t, 255) * 255,
		b: K(n, 255) * 255
	};
}
function cs(e, t, n) {
	e = K(e, 255), t = K(t, 255), n = K(n, 255);
	var r = Math.max(e, t, n), i = Math.min(e, t, n), a, o, s = (r + i) / 2;
	if (r == i) a = o = 0;
	else {
		var c = r - i;
		switch (o = s > .5 ? c / (2 - r - i) : c / (r + i), r) {
			case e:
				a = (t - n) / c + (t < n ? 6 : 0);
				break;
			case t:
				a = (n - e) / c + 2;
				break;
			case n:
				a = (e - t) / c + 4;
				break;
		}
		a /= 6;
	}
	return {
		h: a,
		s: o,
		l: s
	};
}
function ls(e, t, n) {
	var r, i, a;
	e = K(e, 360), t = K(t, 100), n = K(n, 100);
	function o(e, t, n) {
		return n < 0 && (n += 1), n > 1 && --n, n < 1 / 6 ? e + (t - e) * 6 * n : n < 1 / 2 ? t : n < 2 / 3 ? e + (t - e) * (2 / 3 - n) * 6 : e;
	}
	if (t === 0) r = i = a = n;
	else {
		var s = n < .5 ? n * (1 + t) : n + t - n * t, c = 2 * n - s;
		r = o(c, s, e + 1 / 3), i = o(c, s, e), a = o(c, s, e - 1 / 3);
	}
	return {
		r: r * 255,
		g: i * 255,
		b: a * 255
	};
}
function us(e, t, n) {
	e = K(e, 255), t = K(t, 255), n = K(n, 255);
	var r = Math.max(e, t, n), i = Math.min(e, t, n), a, o, s = r, c = r - i;
	if (o = r === 0 ? 0 : c / r, r == i) a = 0;
	else {
		switch (r) {
			case e:
				a = (t - n) / c + (t < n ? 6 : 0);
				break;
			case t:
				a = (n - e) / c + 2;
				break;
			case n:
				a = (e - t) / c + 4;
				break;
		}
		a /= 6;
	}
	return {
		h: a,
		s: o,
		v: s
	};
}
function ds(e, t, n) {
	e = K(e, 360) * 6, t = K(t, 100), n = K(n, 100);
	var r = Math.floor(e), i = e - r, a = n * (1 - t), o = n * (1 - i * t), s = n * (1 - (1 - i) * t), c = r % 6, l = [
		n,
		o,
		a,
		a,
		s,
		n
	][c], u = [
		s,
		n,
		n,
		o,
		a,
		a
	][c], d = [
		a,
		a,
		s,
		n,
		n,
		o
	][c];
	return {
		r: l * 255,
		g: u * 255,
		b: d * 255
	};
}
function fs(e, t, n, r) {
	var i = [
		J(Math.round(e).toString(16)),
		J(Math.round(t).toString(16)),
		J(Math.round(n).toString(16))
	];
	return r && i[0].charAt(0) == i[0].charAt(1) && i[1].charAt(0) == i[1].charAt(1) && i[2].charAt(0) == i[2].charAt(1) ? i[0].charAt(0) + i[1].charAt(0) + i[2].charAt(0) : i.join("");
}
function ps(e, t, n, r, i) {
	var a = [
		J(Math.round(e).toString(16)),
		J(Math.round(t).toString(16)),
		J(Math.round(n).toString(16)),
		J(Fs(r))
	];
	return i && a[0].charAt(0) == a[0].charAt(1) && a[1].charAt(0) == a[1].charAt(1) && a[2].charAt(0) == a[2].charAt(1) && a[3].charAt(0) == a[3].charAt(1) ? a[0].charAt(0) + a[1].charAt(0) + a[2].charAt(0) + a[3].charAt(0) : a.join("");
}
function ms(e, t, n, r) {
	return [
		J(Fs(r)),
		J(Math.round(e).toString(16)),
		J(Math.round(t).toString(16)),
		J(Math.round(n).toString(16))
	].join("");
}
G.equals = function(e, t) {
	return !e || !t ? !1 : G(e).toRgbString() == G(t).toRgbString();
}, G.random = function() {
	return G.fromRatio({
		r: Math.random(),
		g: Math.random(),
		b: Math.random()
	});
};
function hs(e, t) {
	t = t === 0 ? 0 : t || 10;
	var n = G(e).toHsl();
	return n.s -= t / 100, n.s = js(n.s), G(n);
}
function gs(e, t) {
	t = t === 0 ? 0 : t || 10;
	var n = G(e).toHsl();
	return n.s += t / 100, n.s = js(n.s), G(n);
}
function _s(e) {
	return G(e).desaturate(100);
}
function vs(e, t) {
	t = t === 0 ? 0 : t || 10;
	var n = G(e).toHsl();
	return n.l += t / 100, n.l = js(n.l), G(n);
}
function ys(e, t) {
	t = t === 0 ? 0 : t || 10;
	var n = G(e).toRgb();
	return n.r = Math.max(0, Math.min(255, n.r - Math.round(255 * -(t / 100)))), n.g = Math.max(0, Math.min(255, n.g - Math.round(255 * -(t / 100)))), n.b = Math.max(0, Math.min(255, n.b - Math.round(255 * -(t / 100)))), G(n);
}
function bs(e, t) {
	t = t === 0 ? 0 : t || 10;
	var n = G(e).toHsl();
	return n.l -= t / 100, n.l = js(n.l), G(n);
}
function xs(e, t) {
	var n = G(e).toHsl(), r = (n.h + t) % 360;
	return n.h = r < 0 ? 360 + r : r, G(n);
}
function Ss(e) {
	var t = G(e).toHsl();
	return t.h = (t.h + 180) % 360, G(t);
}
function Cs(e, t) {
	if (isNaN(t) || t <= 0) throw Error("Argument to polyad must be a positive number");
	for (var n = G(e).toHsl(), r = [G(e)], i = 360 / t, a = 1; a < t; a++) r.push(G({
		h: (n.h + a * i) % 360,
		s: n.s,
		l: n.l
	}));
	return r;
}
function ws(e) {
	var t = G(e).toHsl(), n = t.h;
	return [
		G(e),
		G({
			h: (n + 72) % 360,
			s: t.s,
			l: t.l
		}),
		G({
			h: (n + 216) % 360,
			s: t.s,
			l: t.l
		})
	];
}
function Ts(e, t, n) {
	t ||= 6, n ||= 30;
	var r = G(e).toHsl(), i = 360 / n, a = [G(e)];
	for (r.h = (r.h - (i * t >> 1) + 720) % 360; --t;) r.h = (r.h + i) % 360, a.push(G(r));
	return a;
}
function Es(e, t) {
	t ||= 6;
	for (var n = G(e).toHsv(), r = n.h, i = n.s, a = n.v, o = [], s = 1 / t; t--;) o.push(G({
		h: r,
		s: i,
		v: a
	})), a = (a + s) % 1;
	return o;
}
G.mix = function(e, t, n) {
	n = n === 0 ? 0 : n || 50;
	var r = G(e).toRgb(), i = G(t).toRgb(), a = n / 100;
	return G({
		r: (i.r - r.r) * a + r.r,
		g: (i.g - r.g) * a + r.g,
		b: (i.b - r.b) * a + r.b,
		a: (i.a - r.a) * a + r.a
	});
}, G.readability = function(e, t) {
	var n = G(e), r = G(t);
	return (Math.max(n.getLuminance(), r.getLuminance()) + .05) / (Math.min(n.getLuminance(), r.getLuminance()) + .05);
}, G.isReadable = function(e, t, n) {
	var r = G.readability(e, t), i, a;
	switch (a = !1, i = Rs(n), i.level + i.size) {
		case "AAsmall":
		case "AAAlarge":
			a = r >= 4.5;
			break;
		case "AAlarge":
			a = r >= 3;
			break;
		case "AAAsmall":
			a = r >= 7;
			break;
	}
	return a;
}, G.mostReadable = function(e, t, n) {
	var r = null, i = 0, a, o, s, c;
	n ||= {}, o = n.includeFallbackColors, s = n.level, c = n.size;
	for (var l = 0; l < t.length; l++) a = G.readability(e, t[l]), a > i && (i = a, r = G(t[l]));
	return G.isReadable(e, r, {
		level: s,
		size: c
	}) || !o ? r : (n.includeFallbackColors = !1, G.mostReadable(e, ["#fff", "#000"], n));
};
var Ds = G.names = {
	aliceblue: "f0f8ff",
	antiquewhite: "faebd7",
	aqua: "0ff",
	aquamarine: "7fffd4",
	azure: "f0ffff",
	beige: "f5f5dc",
	bisque: "ffe4c4",
	black: "000",
	blanchedalmond: "ffebcd",
	blue: "00f",
	blueviolet: "8a2be2",
	brown: "a52a2a",
	burlywood: "deb887",
	burntsienna: "ea7e5d",
	cadetblue: "5f9ea0",
	chartreuse: "7fff00",
	chocolate: "d2691e",
	coral: "ff7f50",
	cornflowerblue: "6495ed",
	cornsilk: "fff8dc",
	crimson: "dc143c",
	cyan: "0ff",
	darkblue: "00008b",
	darkcyan: "008b8b",
	darkgoldenrod: "b8860b",
	darkgray: "a9a9a9",
	darkgreen: "006400",
	darkgrey: "a9a9a9",
	darkkhaki: "bdb76b",
	darkmagenta: "8b008b",
	darkolivegreen: "556b2f",
	darkorange: "ff8c00",
	darkorchid: "9932cc",
	darkred: "8b0000",
	darksalmon: "e9967a",
	darkseagreen: "8fbc8f",
	darkslateblue: "483d8b",
	darkslategray: "2f4f4f",
	darkslategrey: "2f4f4f",
	darkturquoise: "00ced1",
	darkviolet: "9400d3",
	deeppink: "ff1493",
	deepskyblue: "00bfff",
	dimgray: "696969",
	dimgrey: "696969",
	dodgerblue: "1e90ff",
	firebrick: "b22222",
	floralwhite: "fffaf0",
	forestgreen: "228b22",
	fuchsia: "f0f",
	gainsboro: "dcdcdc",
	ghostwhite: "f8f8ff",
	gold: "ffd700",
	goldenrod: "daa520",
	gray: "808080",
	green: "008000",
	greenyellow: "adff2f",
	grey: "808080",
	honeydew: "f0fff0",
	hotpink: "ff69b4",
	indianred: "cd5c5c",
	indigo: "4b0082",
	ivory: "fffff0",
	khaki: "f0e68c",
	lavender: "e6e6fa",
	lavenderblush: "fff0f5",
	lawngreen: "7cfc00",
	lemonchiffon: "fffacd",
	lightblue: "add8e6",
	lightcoral: "f08080",
	lightcyan: "e0ffff",
	lightgoldenrodyellow: "fafad2",
	lightgray: "d3d3d3",
	lightgreen: "90ee90",
	lightgrey: "d3d3d3",
	lightpink: "ffb6c1",
	lightsalmon: "ffa07a",
	lightseagreen: "20b2aa",
	lightskyblue: "87cefa",
	lightslategray: "789",
	lightslategrey: "789",
	lightsteelblue: "b0c4de",
	lightyellow: "ffffe0",
	lime: "0f0",
	limegreen: "32cd32",
	linen: "faf0e6",
	magenta: "f0f",
	maroon: "800000",
	mediumaquamarine: "66cdaa",
	mediumblue: "0000cd",
	mediumorchid: "ba55d3",
	mediumpurple: "9370db",
	mediumseagreen: "3cb371",
	mediumslateblue: "7b68ee",
	mediumspringgreen: "00fa9a",
	mediumturquoise: "48d1cc",
	mediumvioletred: "c71585",
	midnightblue: "191970",
	mintcream: "f5fffa",
	mistyrose: "ffe4e1",
	moccasin: "ffe4b5",
	navajowhite: "ffdead",
	navy: "000080",
	oldlace: "fdf5e6",
	olive: "808000",
	olivedrab: "6b8e23",
	orange: "ffa500",
	orangered: "ff4500",
	orchid: "da70d6",
	palegoldenrod: "eee8aa",
	palegreen: "98fb98",
	paleturquoise: "afeeee",
	palevioletred: "db7093",
	papayawhip: "ffefd5",
	peachpuff: "ffdab9",
	peru: "cd853f",
	pink: "ffc0cb",
	plum: "dda0dd",
	powderblue: "b0e0e6",
	purple: "800080",
	rebeccapurple: "663399",
	red: "f00",
	rosybrown: "bc8f8f",
	royalblue: "4169e1",
	saddlebrown: "8b4513",
	salmon: "fa8072",
	sandybrown: "f4a460",
	seagreen: "2e8b57",
	seashell: "fff5ee",
	sienna: "a0522d",
	silver: "c0c0c0",
	skyblue: "87ceeb",
	slateblue: "6a5acd",
	slategray: "708090",
	slategrey: "708090",
	snow: "fffafa",
	springgreen: "00ff7f",
	steelblue: "4682b4",
	tan: "d2b48c",
	teal: "008080",
	thistle: "d8bfd8",
	tomato: "ff6347",
	turquoise: "40e0d0",
	violet: "ee82ee",
	wheat: "f5deb3",
	white: "fff",
	whitesmoke: "f5f5f5",
	yellow: "ff0",
	yellowgreen: "9acd32"
}, Os = G.hexNames = ks(Ds);
function ks(e) {
	var t = {};
	for (var n in e) e.hasOwnProperty(n) && (t[e[n]] = n);
	return t;
}
function As(e) {
	return e = parseFloat(e), (isNaN(e) || e < 0 || e > 1) && (e = 1), e;
}
function K(e, t) {
	Ms(e) && (e = "100%");
	var n = Ns(e);
	return e = Math.min(t, Math.max(0, parseFloat(e))), n && (e = parseInt(e * t, 10) / 100), Math.abs(e - t) < 1e-6 ? 1 : e % t / parseFloat(t);
}
function js(e) {
	return Math.min(1, Math.max(0, e));
}
function q(e) {
	return parseInt(e, 16);
}
function Ms(e) {
	return typeof e == "string" && e.indexOf(".") != -1 && parseFloat(e) === 1;
}
function Ns(e) {
	return typeof e == "string" && e.indexOf("%") != -1;
}
function J(e) {
	return e.length == 1 ? "0" + e : "" + e;
}
function Ps(e) {
	return e <= 1 && (e = e * 100 + "%"), e;
}
function Fs(e) {
	return Math.round(parseFloat(e) * 255).toString(16);
}
function Is(e) {
	return q(e) / 255;
}
var Y = function() {
	var e = "(?:[-\\+]?\\d*\\.\\d+%?)|(?:[-\\+]?\\d+%?)", t = "[\\s|\\(]+(" + e + ")[,|\\s]+(" + e + ")[,|\\s]+(" + e + ")\\s*\\)?", n = "[\\s|\\(]+(" + e + ")[,|\\s]+(" + e + ")[,|\\s]+(" + e + ")[,|\\s]+(" + e + ")\\s*\\)?";
	return {
		CSS_UNIT: new RegExp(e),
		rgb: RegExp("rgb" + t),
		rgba: RegExp("rgba" + n),
		hsl: RegExp("hsl" + t),
		hsla: RegExp("hsla" + n),
		hsv: RegExp("hsv" + t),
		hsva: RegExp("hsva" + n),
		hex3: /^#?([0-9a-fA-F]{1})([0-9a-fA-F]{1})([0-9a-fA-F]{1})$/,
		hex6: /^#?([0-9a-fA-F]{2})([0-9a-fA-F]{2})([0-9a-fA-F]{2})$/,
		hex4: /^#?([0-9a-fA-F]{1})([0-9a-fA-F]{1})([0-9a-fA-F]{1})([0-9a-fA-F]{1})$/,
		hex8: /^#?([0-9a-fA-F]{2})([0-9a-fA-F]{2})([0-9a-fA-F]{2})([0-9a-fA-F]{2})$/
	};
}();
function X(e) {
	return !!Y.CSS_UNIT.exec(e);
}
function Ls(e) {
	e = e.replace(is, "").replace(as, "").toLowerCase();
	var t = !1;
	if (Ds[e]) e = Ds[e], t = !0;
	else if (e == "transparent") return {
		r: 0,
		g: 0,
		b: 0,
		a: 0,
		format: "name"
	};
	var n;
	return (n = Y.rgb.exec(e)) ? {
		r: n[1],
		g: n[2],
		b: n[3]
	} : (n = Y.rgba.exec(e)) ? {
		r: n[1],
		g: n[2],
		b: n[3],
		a: n[4]
	} : (n = Y.hsl.exec(e)) ? {
		h: n[1],
		s: n[2],
		l: n[3]
	} : (n = Y.hsla.exec(e)) ? {
		h: n[1],
		s: n[2],
		l: n[3],
		a: n[4]
	} : (n = Y.hsv.exec(e)) ? {
		h: n[1],
		s: n[2],
		v: n[3]
	} : (n = Y.hsva.exec(e)) ? {
		h: n[1],
		s: n[2],
		v: n[3],
		a: n[4]
	} : (n = Y.hex8.exec(e)) ? {
		r: q(n[1]),
		g: q(n[2]),
		b: q(n[3]),
		a: Is(n[4]),
		format: t ? "name" : "hex8"
	} : (n = Y.hex6.exec(e)) ? {
		r: q(n[1]),
		g: q(n[2]),
		b: q(n[3]),
		format: t ? "name" : "hex"
	} : (n = Y.hex4.exec(e)) ? {
		r: q(n[1] + "" + n[1]),
		g: q(n[2] + "" + n[2]),
		b: q(n[3] + "" + n[3]),
		a: Is(n[4] + "" + n[4]),
		format: t ? "name" : "hex8"
	} : (n = Y.hex3.exec(e)) ? {
		r: q(n[1] + "" + n[1]),
		g: q(n[2] + "" + n[2]),
		b: q(n[3] + "" + n[3]),
		format: t ? "name" : "hex"
	} : !1;
}
function Rs(e) {
	var t, n;
	return e ||= {
		level: "AA",
		size: "small"
	}, t = (e.level || "AA").toUpperCase(), n = (e.size || "small").toLowerCase(), t !== "AA" && t !== "AAA" && (t = "AA"), n !== "small" && n !== "large" && (n = "small"), {
		level: t,
		size: n
	};
}
var zs = function(e) {
	var t = [
		"r",
		"g",
		"b",
		"a",
		"h",
		"s",
		"l",
		"v"
	], n = 0, r = 0;
	return ns(t, function(t) {
		e[t] && (n += 1, isNaN(e[t]) || (r += 1), t === "s" || t === "l") && /^\d+%$/.test(e[t]) && (r += 1);
	}), n === r ? e : !1;
}, Bs = function(e, t) {
	var n = e.hex ? G(e.hex) : G(e), r = n.toHsl(), i = n.toHsv(), a = n.toRgb(), o = n.toHex();
	return r.s === 0 && (r.h = t || 0, i.h = t || 0), {
		hsl: r,
		hex: o === "000000" && a.a === 0 ? "transparent" : "#" + o,
		rgb: a,
		hsv: i,
		oldHue: e.h || t || r.h,
		source: e.source
	};
}, Z = function(e) {
	if (e === "transparent") return !0;
	var t = +(String(e).charAt(0) === "#");
	return e.length !== 4 + t && e.length < 7 + t && G(e).isValid();
}, Vs = function(e) {
	if (!e) return "#fff";
	var t = Bs(e);
	return t.hex === "transparent" ? "rgba(0,0,0,0.4)" : (t.rgb.r * 299 + t.rgb.g * 587 + t.rgb.b * 114) / 1e3 >= 128 ? "#000" : "#fff";
}, Hs = function(e, t) {
	var n = e.replace("°", "");
	return G(t + " (" + n + ")")._ok;
}, Us = Object.assign || function(e) {
	for (var t = 1; t < arguments.length; t++) {
		var n = arguments[t];
		for (var r in n) Object.prototype.hasOwnProperty.call(n, r) && (e[r] = n[r]);
	}
	return e;
}, Ws = /* @__PURE__ */ function() {
	function e(e, t) {
		for (var n = 0; n < t.length; n++) {
			var r = t[n];
			r.enumerable = r.enumerable || !1, r.configurable = !0, "value" in r && (r.writable = !0), Object.defineProperty(e, r.key, r);
		}
	}
	return function(t, n, r) {
		return n && e(t.prototype, n), r && e(t, r), t;
	};
}();
function Gs(e, t) {
	if (!(e instanceof t)) throw TypeError("Cannot call a class as a function");
}
function Ks(e, t) {
	if (!e) throw ReferenceError("this hasn't been initialised - super() hasn't been called");
	return t && (typeof t == "object" || typeof t == "function") ? t : e;
}
function qs(e, t) {
	if (typeof t != "function" && t !== null) throw TypeError("Super expression must either be null or a function, not " + typeof t);
	e.prototype = Object.create(t && t.prototype, { constructor: {
		value: e,
		enumerable: !1,
		writable: !0,
		configurable: !0
	} }), t && (Object.setPrototypeOf ? Object.setPrototypeOf(e, t) : e.__proto__ = t);
}
var Q = function(e) {
	var t = function(t) {
		qs(n, t);
		function n(e) {
			Gs(this, n);
			var t = Ks(this, (n.__proto__ || Object.getPrototypeOf(n)).call(this));
			return t.handleChange = function(e, n) {
				if (zs(e)) {
					var r = Bs(e, e.h || t.state.oldHue);
					t.setState(r), t.props.onChangeComplete && t.debounce(t.props.onChangeComplete, r, n), t.props.onChange && t.props.onChange(r, n);
				}
			}, t.handleSwatchHover = function(e, n) {
				if (zs(e)) {
					var r = Bs(e, e.h || t.state.oldHue);
					t.props.onSwatchHover && t.props.onSwatchHover(r, n);
				}
			}, t.state = Us({}, Bs(e.color, 0)), t.debounce = Ro(function(e, t, n) {
				e(t, n);
			}, 100), t;
		}
		return Ws(n, [{
			key: "render",
			value: function() {
				var t = {};
				return this.props.onSwatchHover && (t.onSwatchHover = this.handleSwatchHover), T.createElement(e, Us({}, this.props, this.state, { onChange: this.handleChange }, t));
			}
		}], [{
			key: "getDerivedStateFromProps",
			value: function(e, t) {
				return Us({}, Bs(e.color, t.oldHue));
			}
		}]), n;
	}(T.PureComponent || T.Component);
	return t.propTypes = Us({}, e.propTypes), t.defaultProps = Us({}, e.defaultProps, { color: {
		h: 250,
		s: .5,
		l: .2,
		a: 1
	} }), t;
}, Js = Object.assign || function(e) {
	for (var t = 1; t < arguments.length; t++) {
		var n = arguments[t];
		for (var r in n) Object.prototype.hasOwnProperty.call(n, r) && (e[r] = n[r]);
	}
	return e;
}, Ys = /* @__PURE__ */ function() {
	function e(e, t) {
		for (var n = 0; n < t.length; n++) {
			var r = t[n];
			r.enumerable = r.enumerable || !1, r.configurable = !0, "value" in r && (r.writable = !0), Object.defineProperty(e, r.key, r);
		}
	}
	return function(t, n, r) {
		return n && e(t.prototype, n), r && e(t, r), t;
	};
}();
function Xs(e, t) {
	if (!(e instanceof t)) throw TypeError("Cannot call a class as a function");
}
function Zs(e, t) {
	if (!e) throw ReferenceError("this hasn't been initialised - super() hasn't been called");
	return t && (typeof t == "object" || typeof t == "function") ? t : e;
}
function Qs(e, t) {
	if (typeof t != "function" && t !== null) throw TypeError("Super expression must either be null or a function, not " + typeof t);
	e.prototype = Object.create(t && t.prototype, { constructor: {
		value: e,
		enumerable: !1,
		writable: !0,
		configurable: !0
	} }), t && (Object.setPrototypeOf ? Object.setPrototypeOf(e, t) : e.__proto__ = t);
}
var $s = function(e) {
	var t = arguments.length > 1 && arguments[1] !== void 0 ? arguments[1] : "span";
	return function(n) {
		Qs(r, n);
		function r() {
			var e, t, n, i;
			Xs(this, r);
			var a = [...arguments];
			return i = (t = (n = Zs(this, (e = r.__proto__ || Object.getPrototypeOf(r)).call.apply(e, [this].concat(a))), n), n.state = { focus: !1 }, n.handleFocus = function() {
				return n.setState({ focus: !0 });
			}, n.handleBlur = function() {
				return n.setState({ focus: !1 });
			}, t), Zs(n, i);
		}
		return Ys(r, [{
			key: "render",
			value: function() {
				return T.createElement(t, {
					onFocus: this.handleFocus,
					onBlur: this.handleBlur
				}, T.createElement(e, Js({}, this.props, this.state)));
			}
		}]), r;
	}(T.Component);
}, ec = Object.assign || function(e) {
	for (var t = 1; t < arguments.length; t++) {
		var n = arguments[t];
		for (var r in n) Object.prototype.hasOwnProperty.call(n, r) && (e[r] = n[r]);
	}
	return e;
}, tc = 13, nc = $s(function(e) {
	var t = e.color, n = e.style, r = e.onClick, i = r === void 0 ? function() {} : r, a = e.onHover, o = e.title, s = o === void 0 ? t : o, c = e.children, l = e.focus, u = e.focusStyle, d = u === void 0 ? {} : u, f = t === "transparent", p = k({ default: { swatch: ec({
		background: t,
		height: "100%",
		width: "100%",
		cursor: "pointer",
		position: "relative",
		outline: "none"
	}, n, l ? d : {}) } }), m = function(e) {
		return i(t, e);
	}, h = function(e) {
		return e.keyCode === tc && i(t, e);
	}, g = function(e) {
		return a(t, e);
	}, _ = {};
	return a && (_.onMouseOver = g), T.createElement("div", ec({
		style: p.swatch,
		onClick: m,
		title: s,
		tabIndex: 0,
		onKeyDown: h
	}, _), c, f && T.createElement(Gn, {
		borderRadius: p.swatch.borderRadius,
		boxShadow: "inset 0 0 0 1px rgba(0,0,0,0.1)"
	}));
}), rc = function(e) {
	var t = e.direction, n = k({
		default: { picker: {
			width: "18px",
			height: "18px",
			borderRadius: "50%",
			transform: "translate(-9px, -1px)",
			backgroundColor: "rgb(248, 248, 248)",
			boxShadow: "0 1px 4px 0 rgba(0, 0, 0, 0.37)"
		} },
		vertical: { picker: { transform: "translate(-3px, -9px)" } }
	}, { vertical: t === "vertical" });
	return T.createElement("div", { style: n.picker });
}, ic = Object.assign || function(e) {
	for (var t = 1; t < arguments.length; t++) {
		var n = arguments[t];
		for (var r in n) Object.prototype.hasOwnProperty.call(n, r) && (e[r] = n[r]);
	}
	return e;
}, ac = function(e) {
	var t = e.rgb, n = e.hsl, r = e.width, i = e.height, a = e.onChange, o = e.direction, s = e.style, c = e.renderers, l = e.pointer, u = e.className, d = u === void 0 ? "" : u, f = k({ default: {
		picker: {
			position: "relative",
			width: r,
			height: i
		},
		alpha: {
			radius: "2px",
			style: s
		}
	} });
	return T.createElement("div", {
		style: f.picker,
		className: "alpha-picker " + d
	}, T.createElement(Zn, ic({}, f.alpha, {
		rgb: t,
		hsl: n,
		pointer: l,
		renderers: c,
		onChange: a,
		direction: o
	})));
};
ac.defaultProps = {
	width: "316px",
	height: "16px",
	direction: "horizontal",
	pointer: rc
}, Q(ac);
function oc(e, t) {
	for (var n = -1, r = e == null ? 0 : e.length, i = Array(r); ++n < r;) i[n] = t(e[n], n, e);
	return i;
}
var sc = "__lodash_hash_undefined__";
function cc(e) {
	return this.__data__.set(e, sc), this;
}
function lc(e) {
	return this.__data__.has(e);
}
function uc(e) {
	var t = -1, n = e == null ? 0 : e.length;
	for (this.__data__ = new z(); ++t < n;) this.add(e[t]);
}
uc.prototype.add = uc.prototype.push = cc, uc.prototype.has = lc;
function dc(e, t) {
	for (var n = -1, r = e == null ? 0 : e.length; ++n < r;) if (t(e[n], n, e)) return !0;
	return !1;
}
function fc(e, t) {
	return e.has(t);
}
var pc = 1, mc = 2;
function hc(e, t, n, r, i, a) {
	var o = n & pc, s = e.length, c = t.length;
	if (s != c && !(o && c > s)) return !1;
	var l = a.get(e), u = a.get(t);
	if (l && u) return l == t && u == e;
	var d = -1, f = !0, p = n & mc ? new uc() : void 0;
	for (a.set(e, t), a.set(t, e); ++d < s;) {
		var m = e[d], h = t[d];
		if (r) var g = o ? r(h, m, d, t, e, a) : r(m, h, d, e, t, a);
		if (g !== void 0) {
			if (g) continue;
			f = !1;
			break;
		}
		if (p) {
			if (!dc(t, function(e, t) {
				if (!fc(p, t) && (m === e || i(m, e, n, r, a))) return p.push(t);
			})) {
				f = !1;
				break;
			}
		} else if (!(m === h || i(m, h, n, r, a))) {
			f = !1;
			break;
		}
	}
	return a.delete(e), a.delete(t), f;
}
function gc(e) {
	var t = -1, n = Array(e.size);
	return e.forEach(function(e, r) {
		n[++t] = [r, e];
	}), n;
}
function _c(e) {
	var t = -1, n = Array(e.size);
	return e.forEach(function(e) {
		n[++t] = e;
	}), n;
}
var vc = 1, yc = 2, bc = "[object Boolean]", xc = "[object Date]", Sc = "[object Error]", Cc = "[object Map]", wc = "[object Number]", Tc = "[object RegExp]", Ec = "[object Set]", Dc = "[object String]", Oc = "[object Symbol]", kc = "[object ArrayBuffer]", Ac = "[object DataView]", jc = N ? N.prototype : void 0, Mc = jc ? jc.valueOf : void 0;
function Nc(e, t, n, r, i, a, o) {
	switch (n) {
		case Ac:
			if (e.byteLength != t.byteLength || e.byteOffset != t.byteOffset) return !1;
			e = e.buffer, t = t.buffer;
		case kc: return !(e.byteLength != t.byteLength || !a(new Mi(e), new Mi(t)));
		case bc:
		case xc:
		case wc: return gr(+e, +t);
		case Sc: return e.name == t.name && e.message == t.message;
		case Tc:
		case Dc: return e == t + "";
		case Cc: var s = gc;
		case Ec:
			var c = r & vc;
			if (s ||= _c, e.size != t.size && !c) return !1;
			var l = o.get(e);
			if (l) return l == t;
			r |= yc, o.set(e, t);
			var u = hc(s(e), s(t), r, i, a, o);
			return o.delete(e), u;
		case Oc: if (Mc) return Mc.call(e) == Mc.call(t);
	}
	return !1;
}
function Pc(e, t) {
	for (var n = -1, r = t.length, i = e.length; ++n < r;) e[i + n] = t[n];
	return e;
}
function Fc(e, t, n) {
	var r = t(e);
	return H(e) ? r : Pc(r, n(e));
}
function Ic(e, t) {
	for (var n = -1, r = e == null ? 0 : e.length, i = 0, a = []; ++n < r;) {
		var o = e[n];
		t(o, n, e) && (a[i++] = o);
	}
	return a;
}
function Lc() {
	return [];
}
var Rc = Object.prototype.propertyIsEnumerable, zc = Object.getOwnPropertySymbols, Bc = zc ? function(e) {
	return e == null ? [] : (e = Object(e), Ic(zc(e), function(t) {
		return Rc.call(e, t);
	}));
} : Lc;
function Vc(e) {
	return Fc(e, Zo, Bc);
}
var Hc = 1, Uc = Object.prototype.hasOwnProperty;
function Wc(e, t, n, r, i, a) {
	var o = n & Hc, s = Vc(e), c = s.length;
	if (c != Vc(t).length && !o) return !1;
	for (var l = c; l--;) {
		var u = s[l];
		if (!(o ? u in t : Uc.call(t, u))) return !1;
	}
	var d = a.get(e), f = a.get(t);
	if (d && f) return d == t && f == e;
	var p = !0;
	a.set(e, t), a.set(t, e);
	for (var m = o; ++l < c;) {
		u = s[l];
		var h = e[u], g = t[u];
		if (r) var _ = o ? r(g, h, u, t, e, a) : r(h, g, u, e, t, a);
		if (!(_ === void 0 ? h === g || i(h, g, n, r, a) : _)) {
			p = !1;
			break;
		}
		m ||= u == "constructor";
	}
	if (p && !m) {
		var v = e.constructor, y = t.constructor;
		v != y && "constructor" in e && "constructor" in t && !(typeof v == "function" && v instanceof v && typeof y == "function" && y instanceof y) && (p = !1);
	}
	return a.delete(e), a.delete(t), p;
}
var Gc = L(M, "DataView"), Kc = L(M, "Promise"), qc = L(M, "Set"), Jc = L(M, "WeakMap"), Yc = "[object Map]", Xc = "[object Object]", Zc = "[object Promise]", Qc = "[object Set]", $c = "[object WeakMap]", el = "[object DataView]", tl = I(Gc), nl = I(ri), rl = I(Kc), il = I(qc), al = I(Jc), $ = P;
(Gc && $(new Gc(/* @__PURE__ */ new ArrayBuffer(1))) != el || ri && $(new ri()) != Yc || Kc && $(Kc.resolve()) != Zc || qc && $(new qc()) != Qc || Jc && $(new Jc()) != $c) && ($ = function(e) {
	var t = P(e), n = t == Xc ? e.constructor : void 0, r = n ? I(n) : "";
	if (r) switch (r) {
		case tl: return el;
		case nl: return Yc;
		case rl: return Zc;
		case il: return Qc;
		case al: return $c;
	}
	return t;
});
var ol = 1, sl = "[object Arguments]", cl = "[object Array]", ll = "[object Object]", ul = Object.prototype.hasOwnProperty;
function dl(e, t, n, r, i, a) {
	var o = H(e), s = H(t), c = o ? cl : $(e), l = s ? cl : $(t);
	c = c == sl ? ll : c, l = l == sl ? ll : l;
	var u = c == ll, d = l == ll, f = c == l;
	if (f && ra(e)) {
		if (!ra(t)) return !1;
		o = !0, u = !1;
	}
	if (f && !u) return a ||= new B(), o || Ha(e) ? hc(e, t, n, r, i, a) : Nc(e, t, c, n, r, i, a);
	if (!(n & ol)) {
		var p = u && ul.call(e, "__wrapped__"), m = d && ul.call(t, "__wrapped__");
		if (p || m) {
			var h = p ? e.value() : e, g = m ? t.value() : t;
			return a ||= new B(), i(h, g, n, r, a);
		}
	}
	return f ? (a ||= new B(), Wc(e, t, n, r, i, a)) : !1;
}
function fl(e, t, n, r, i) {
	return e === t ? !0 : e == null || t == null || !V(e) && !V(t) ? e !== e && t !== t : dl(e, t, n, r, fl, i);
}
var pl = 1, ml = 2;
function hl(e, t, n, r) {
	var i = n.length, a = i;
	if (e == null) return !a;
	for (e = Object(e); i--;) {
		var o = n[i];
		if (o[2] ? o[1] !== e[o[0]] : !(o[0] in e)) return !1;
	}
	for (; ++i < a;) {
		o = n[i];
		var s = o[0], c = e[s], l = o[1];
		if (o[2]) {
			if (c === void 0 && !(s in e)) return !1;
		} else {
			var u = new B(), d;
			if (!(d === void 0 ? fl(l, c, pl | ml, r, u) : d)) return !1;
		}
	}
	return !0;
}
function gl(e) {
	return e === e && !F(e);
}
function _l(e) {
	for (var t = Zo(e), n = t.length; n--;) {
		var r = t[n], i = e[r];
		t[n] = [
			r,
			i,
			gl(i)
		];
	}
	return t;
}
function vl(e, t) {
	return function(n) {
		return n == null ? !1 : n[e] === t && (t !== void 0 || e in Object(n));
	};
}
function yl(e) {
	var t = _l(e);
	return t.length == 1 && t[0][2] ? vl(t[0][0], t[0][1]) : function(n) {
		return n === e || hl(n, e, t);
	};
}
var bl = /\.|\[(?:[^[\]]*|(["'])(?:(?!\1)[^\\]|\\.)*?\1)\]/, xl = /^\w*$/;
function Sl(e, t) {
	if (H(e)) return !1;
	var n = typeof e;
	return n == "number" || n == "symbol" || n == "boolean" || e == null || Oo(e) ? !0 : xl.test(e) || !bl.test(e) || t != null && e in Object(t);
}
var Cl = "Expected a function";
function wl(e, t) {
	if (typeof e != "function" || t != null && typeof t != "function") throw TypeError(Cl);
	var n = function() {
		var r = arguments, i = t ? t.apply(this, r) : r[0], a = n.cache;
		if (a.has(i)) return a.get(i);
		var o = e.apply(this, r);
		return n.cache = a.set(i, o) || a, o;
	};
	return n.cache = new (wl.Cache || z)(), n;
}
wl.Cache = z;
var Tl = 500;
function El(e) {
	var t = wl(e, function(e) {
		return n.size === Tl && n.clear(), e;
	}), n = t.cache;
	return t;
}
var Dl = /[^.[\]]+|\[(?:(-?\d+(?:\.\d+)?)|(["'])((?:(?!\2)[^\\]|\\.)*?)\2)\]|(?=(?:\.|\[\])(?:\.|\[\]|$))/g, Ol = /\\(\\)?/g, kl = El(function(e) {
	var t = [];
	return e.charCodeAt(0) === 46 && t.push(""), e.replace(Dl, function(e, n, r, i) {
		t.push(r ? i.replace(Ol, "$1") : n || e);
	}), t;
}), Al = N ? N.prototype : void 0, jl = Al ? Al.toString : void 0;
function Ml(e) {
	if (typeof e == "string") return e;
	if (H(e)) return oc(e, Ml) + "";
	if (Oo(e)) return jl ? jl.call(e) : "";
	var t = e + "";
	return t == "0" && 1 / e == -Infinity ? "-0" : t;
}
function Nl(e) {
	return e == null ? "" : Ml(e);
}
function Pl(e, t) {
	return H(e) ? e : Sl(e, t) ? [e] : kl(Nl(e));
}
function Fl(e) {
	if (typeof e == "string" || Oo(e)) return e;
	var t = e + "";
	return t == "0" && 1 / e == -Infinity ? "-0" : t;
}
function Il(e, t) {
	t = Pl(t, e);
	for (var n = 0, r = t.length; e != null && n < r;) e = e[Fl(t[n++])];
	return n && n == r ? e : void 0;
}
function Ll(e, t, n) {
	var r = e == null ? void 0 : Il(e, t);
	return r === void 0 ? n : r;
}
function Rl(e, t) {
	return e != null && t in Object(e);
}
function zl(e, t, n) {
	t = Pl(t, e);
	for (var r = -1, i = t.length, a = !1; ++r < i;) {
		var o = Fl(t[r]);
		if (!(a = e != null && n(e, o))) break;
		e = e[o];
	}
	return a || ++r != i ? a : (i = e == null ? 0 : e.length, !!i && Xi(i) && Xa(o, i) && (H(e) || Ji(e)));
}
function Bl(e, t) {
	return e != null && zl(e, t, Rl);
}
var Vl = 1, Hl = 2;
function Ul(e, t) {
	return Sl(e) && gl(t) ? vl(Fl(e), t) : function(n) {
		var r = Ll(n, e);
		return r === void 0 && r === t ? Bl(n, e) : fl(t, r, Vl | Hl);
	};
}
function Wl(e) {
	return function(t) {
		return t?.[e];
	};
}
function Gl(e) {
	return function(t) {
		return Il(t, e);
	};
}
function Kl(e) {
	return Sl(e) ? Wl(Fl(e)) : Gl(e);
}
function ql(e) {
	return typeof e == "function" ? e : e == null ? oo : typeof e == "object" ? H(e) ? Ul(e[0], e[1]) : yl(e) : Kl(e);
}
function Jl(e, t) {
	var n = -1, r = Zi(e) ? Array(e.length) : [];
	return es(e, function(e, i, a) {
		r[++n] = t(e, i, a);
	}), r;
}
function Yl(e, t) {
	return (H(e) ? oc : Jl)(e, ql(t));
}
var Xl = function(e) {
	var t = e.colors, n = e.onClick, r = e.onSwatchHover, i = k({ default: {
		swatches: { marginRight: "-10px" },
		swatch: {
			width: "22px",
			height: "22px",
			float: "left",
			marginRight: "10px",
			marginBottom: "10px",
			borderRadius: "4px"
		},
		clear: { clear: "both" }
	} });
	return T.createElement("div", { style: i.swatches }, Yl(t, function(e) {
		return T.createElement(nc, {
			key: e,
			color: e,
			style: i.swatch,
			onClick: n,
			onHover: r,
			focusStyle: { boxShadow: "0 0 4px " + e }
		});
	}), T.createElement("div", { style: i.clear }));
}, Zl = function(e) {
	var t = e.onChange, n = e.onSwatchHover, r = e.hex, i = e.colors, a = e.width, o = e.triangle, s = e.styles, c = s === void 0 ? {} : s, l = e.className, u = l === void 0 ? "" : l, d = r === "transparent", f = function(e, n) {
		Z(e) && t({
			hex: e,
			source: "hex"
		}, n);
	}, p = k(W({
		default: {
			card: {
				width: a,
				background: "#fff",
				boxShadow: "0 1px rgba(0,0,0,.1)",
				borderRadius: "6px",
				position: "relative"
			},
			head: {
				height: "110px",
				background: r,
				borderRadius: "6px 6px 0 0",
				display: "flex",
				alignItems: "center",
				justifyContent: "center",
				position: "relative"
			},
			body: { padding: "10px" },
			label: {
				fontSize: "18px",
				color: Vs(r),
				position: "relative"
			},
			triangle: {
				width: "0px",
				height: "0px",
				borderStyle: "solid",
				borderWidth: "0 10px 10px 10px",
				borderColor: "transparent transparent " + r + " transparent",
				position: "absolute",
				top: "-10px",
				left: "50%",
				marginLeft: "-10px"
			},
			input: {
				width: "100%",
				fontSize: "12px",
				color: "#666",
				border: "0px",
				outline: "none",
				height: "22px",
				boxShadow: "inset 0 0 0 1px #ddd",
				borderRadius: "4px",
				padding: "0 7px",
				boxSizing: "border-box"
			}
		},
		"hide-triangle": { triangle: { display: "none" } }
	}, c), { "hide-triangle": o === "hide" });
	return T.createElement("div", {
		style: p.card,
		className: "block-picker " + u
	}, T.createElement("div", { style: p.triangle }), T.createElement("div", { style: p.head }, d && T.createElement(Gn, { borderRadius: "6px 6px 0 0" }), T.createElement("div", { style: p.label }, r)), T.createElement("div", { style: p.body }, T.createElement(Xl, {
		colors: i,
		onClick: f,
		onSwatchHover: n
	}), T.createElement(A, {
		style: { input: p.input },
		value: r,
		onChange: f
	})));
};
Zl.propTypes = {
	width: a.oneOfType([a.string, a.number]),
	colors: a.arrayOf(a.string),
	triangle: a.oneOf(["top", "hide"]),
	styles: a.object
}, Zl.defaultProps = {
	width: 170,
	colors: [
		"#D9E3F0",
		"#F47373",
		"#697689",
		"#37D67A",
		"#2CCCE4",
		"#555555",
		"#dce775",
		"#ff8a65",
		"#ba68c8"
	],
	triangle: "top",
	styles: {}
}, Q(Zl);
var Ql = {
	100: "#ffcdd2",
	300: "#e57373",
	500: "#f44336",
	700: "#d32f2f",
	900: "#b71c1c"
}, $l = {
	100: "#f8bbd0",
	300: "#f06292",
	500: "#e91e63",
	700: "#c2185b",
	900: "#880e4f"
}, eu = {
	100: "#e1bee7",
	300: "#ba68c8",
	500: "#9c27b0",
	700: "#7b1fa2",
	900: "#4a148c"
}, tu = {
	100: "#d1c4e9",
	300: "#9575cd",
	500: "#673ab7",
	700: "#512da8",
	900: "#311b92"
}, nu = {
	100: "#c5cae9",
	300: "#7986cb",
	500: "#3f51b5",
	700: "#303f9f",
	900: "#1a237e"
}, ru = {
	100: "#bbdefb",
	300: "#64b5f6",
	500: "#2196f3",
	700: "#1976d2",
	900: "#0d47a1"
}, iu = {
	100: "#b3e5fc",
	300: "#4fc3f7",
	500: "#03a9f4",
	700: "#0288d1",
	900: "#01579b"
}, au = {
	100: "#b2ebf2",
	300: "#4dd0e1",
	500: "#00bcd4",
	700: "#0097a7",
	900: "#006064"
}, ou = {
	100: "#b2dfdb",
	300: "#4db6ac",
	500: "#009688",
	700: "#00796b",
	900: "#004d40"
}, su = {
	100: "#c8e6c9",
	300: "#81c784",
	500: "#4caf50",
	700: "#388e3c"
}, cu = {
	100: "#dcedc8",
	300: "#aed581",
	500: "#8bc34a",
	700: "#689f38",
	900: "#33691e"
}, lu = {
	100: "#f0f4c3",
	300: "#dce775",
	500: "#cddc39",
	700: "#afb42b",
	900: "#827717"
}, uu = {
	100: "#fff9c4",
	300: "#fff176",
	500: "#ffeb3b",
	700: "#fbc02d",
	900: "#f57f17"
}, du = {
	100: "#ffecb3",
	300: "#ffd54f",
	500: "#ffc107",
	700: "#ffa000",
	900: "#ff6f00"
}, fu = {
	100: "#ffe0b2",
	300: "#ffb74d",
	500: "#ff9800",
	700: "#f57c00",
	900: "#e65100"
}, pu = {
	100: "#ffccbc",
	300: "#ff8a65",
	500: "#ff5722",
	700: "#e64a19",
	900: "#bf360c"
}, mu = {
	100: "#d7ccc8",
	300: "#a1887f",
	500: "#795548",
	700: "#5d4037",
	900: "#3e2723"
}, hu = {
	100: "#cfd8dc",
	300: "#90a4ae",
	500: "#607d8b",
	700: "#455a64",
	900: "#263238"
}, gu = function(e) {
	var t = e.color, n = e.onClick, r = e.onSwatchHover, i = e.hover, a = e.active, o = e.circleSize, s = e.circleSpacing, c = k({
		default: {
			swatch: {
				width: o,
				height: o,
				marginRight: s,
				marginBottom: s,
				transform: "scale(1)",
				transition: "100ms transform ease"
			},
			Swatch: {
				borderRadius: "50%",
				background: "transparent",
				boxShadow: "inset 0 0 0 " + (o / 2 + 1) + "px " + t,
				transition: "100ms box-shadow ease"
			}
		},
		hover: { swatch: { transform: "scale(1.2)" } },
		active: { Swatch: { boxShadow: "inset 0 0 0 3px " + t } }
	}, {
		hover: i,
		active: a
	});
	return T.createElement("div", { style: c.swatch }, T.createElement(nc, {
		style: c.Swatch,
		color: t,
		onClick: n,
		onHover: r,
		focusStyle: { boxShadow: c.Swatch.boxShadow + ", 0 0 5px " + t }
	}));
};
gu.defaultProps = {
	circleSize: 28,
	circleSpacing: 14
};
var _u = zn.handleHover(gu), vu = function(e) {
	var t = e.width, n = e.onChange, r = e.onSwatchHover, i = e.colors, a = e.hex, o = e.circleSize, s = e.styles, c = s === void 0 ? {} : s, l = e.circleSpacing, u = e.className, d = u === void 0 ? "" : u, f = k(W({ default: { card: {
		width: t,
		display: "flex",
		flexWrap: "wrap",
		marginRight: -l,
		marginBottom: -l
	} } }, c)), p = function(e, t) {
		return n({
			hex: e,
			source: "hex"
		}, t);
	};
	return T.createElement("div", {
		style: f.card,
		className: "circle-picker " + d
	}, Yl(i, function(e) {
		return T.createElement(_u, {
			key: e,
			color: e,
			onClick: p,
			onSwatchHover: r,
			active: a === e.toLowerCase(),
			circleSize: o,
			circleSpacing: l
		});
	}));
};
vu.propTypes = {
	width: a.oneOfType([a.string, a.number]),
	circleSize: a.number,
	circleSpacing: a.number,
	styles: a.object
}, vu.defaultProps = {
	width: 252,
	circleSize: 28,
	circleSpacing: 14,
	colors: [
		Ql[500],
		$l[500],
		eu[500],
		tu[500],
		nu[500],
		ru[500],
		iu[500],
		au[500],
		ou[500],
		su[500],
		cu[500],
		lu[500],
		uu[500],
		du[500],
		fu[500],
		pu[500],
		mu[500],
		hu[500]
	],
	styles: {}
}, Q(vu);
function yu(e) {
	return e === void 0;
}
var bu = {}, xu;
function Su() {
	if (xu) return bu;
	xu = 1, Object.defineProperty(bu, "__esModule", { value: !0 });
	var e = Object.assign || function(e) {
		for (var t = 1; t < arguments.length; t++) {
			var n = arguments[t];
			for (var r in n) Object.prototype.hasOwnProperty.call(n, r) && (e[r] = n[r]);
		}
		return e;
	}, t = n(T.default);
	function n(e) {
		return e && e.__esModule ? e : { default: e };
	}
	function r(e, t) {
		var n = {};
		for (var r in e) t.indexOf(r) >= 0 || Object.prototype.hasOwnProperty.call(e, r) && (n[r] = e[r]);
		return n;
	}
	var i = 24;
	return bu.default = function(n) {
		var a = n.fill, o = a === void 0 ? "currentColor" : a, s = n.width, c = s === void 0 ? i : s, l = n.height, u = l === void 0 ? i : l, d = n.style, f = d === void 0 ? {} : d, p = r(n, [
			"fill",
			"width",
			"height",
			"style"
		]);
		return t.default.createElement("svg", e({
			viewBox: "0 0 " + i + " " + i,
			style: e({
				fill: o,
				width: c,
				height: u
			}, f)
		}, p), t.default.createElement("path", { d: "M12,18.17L8.83,15L7.42,16.41L12,21L16.59,16.41L15.17,15M12,5.83L15.17,9L16.58,7.59L12,3L7.41,7.59L8.83,9L12,5.83Z" }));
	}, bu;
}
var Cu = /* @__PURE__ */ i(Su()), wu = /* @__PURE__ */ function() {
	function e(e, t) {
		for (var n = 0; n < t.length; n++) {
			var r = t[n];
			r.enumerable = r.enumerable || !1, r.configurable = !0, "value" in r && (r.writable = !0), Object.defineProperty(e, r.key, r);
		}
	}
	return function(t, n, r) {
		return n && e(t.prototype, n), r && e(t, r), t;
	};
}();
function Tu(e, t) {
	if (!(e instanceof t)) throw TypeError("Cannot call a class as a function");
}
function Eu(e, t) {
	if (!e) throw ReferenceError("this hasn't been initialised - super() hasn't been called");
	return t && (typeof t == "object" || typeof t == "function") ? t : e;
}
function Du(e, t) {
	if (typeof t != "function" && t !== null) throw TypeError("Super expression must either be null or a function, not " + typeof t);
	e.prototype = Object.create(t && t.prototype, { constructor: {
		value: e,
		enumerable: !1,
		writable: !0,
		configurable: !0
	} }), t && (Object.setPrototypeOf ? Object.setPrototypeOf(e, t) : e.__proto__ = t);
}
var Ou = function(e) {
	Du(t, e);
	function t(e) {
		Tu(this, t);
		var n = Eu(this, (t.__proto__ || Object.getPrototypeOf(t)).call(this));
		return n.toggleViews = function() {
			n.state.view === "hex" ? n.setState({ view: "rgb" }) : n.state.view === "rgb" ? n.setState({ view: "hsl" }) : n.state.view === "hsl" && (n.props.hsl.a === 1 ? n.setState({ view: "hex" }) : n.setState({ view: "rgb" }));
		}, n.handleChange = function(e, t) {
			e.hex ? Z(e.hex) && n.props.onChange({
				hex: e.hex,
				source: "hex"
			}, t) : e.r || e.g || e.b ? n.props.onChange({
				r: e.r || n.props.rgb.r,
				g: e.g || n.props.rgb.g,
				b: e.b || n.props.rgb.b,
				source: "rgb"
			}, t) : e.a ? (e.a < 0 ? e.a = 0 : e.a > 1 && (e.a = 1), n.props.onChange({
				h: n.props.hsl.h,
				s: n.props.hsl.s,
				l: n.props.hsl.l,
				a: Math.round(e.a * 100) / 100,
				source: "rgb"
			}, t)) : (e.h || e.s || e.l) && (typeof e.s == "string" && e.s.includes("%") && (e.s = e.s.replace("%", "")), typeof e.l == "string" && e.l.includes("%") && (e.l = e.l.replace("%", "")), e.s == 1 ? e.s = .01 : e.l == 1 && (e.l = .01), n.props.onChange({
				h: e.h || n.props.hsl.h,
				s: Number(yu(e.s) ? n.props.hsl.s : e.s),
				l: Number(yu(e.l) ? n.props.hsl.l : e.l),
				source: "hsl"
			}, t));
		}, n.showHighlight = function(e) {
			e.currentTarget.style.background = "#eee";
		}, n.hideHighlight = function(e) {
			e.currentTarget.style.background = "transparent";
		}, e.hsl.a !== 1 && e.view === "hex" ? n.state = { view: "rgb" } : n.state = { view: e.view }, n;
	}
	return wu(t, [{
		key: "render",
		value: function() {
			var e = this, t = k({
				default: {
					wrap: {
						paddingTop: "16px",
						display: "flex"
					},
					fields: {
						flex: "1",
						display: "flex",
						marginLeft: "-6px"
					},
					field: {
						paddingLeft: "6px",
						width: "100%"
					},
					alpha: {
						paddingLeft: "6px",
						width: "100%"
					},
					toggle: {
						width: "32px",
						textAlign: "right",
						position: "relative"
					},
					icon: {
						marginRight: "-4px",
						marginTop: "12px",
						cursor: "pointer",
						position: "relative"
					},
					iconHighlight: {
						position: "absolute",
						width: "24px",
						height: "28px",
						background: "#eee",
						borderRadius: "4px",
						top: "10px",
						left: "12px",
						display: "none"
					},
					input: {
						fontSize: "11px",
						color: "#333",
						width: "100%",
						borderRadius: "2px",
						border: "none",
						boxShadow: "inset 0 0 0 1px #dadada",
						height: "21px",
						textAlign: "center"
					},
					label: {
						textTransform: "uppercase",
						fontSize: "11px",
						lineHeight: "11px",
						color: "#969696",
						textAlign: "center",
						display: "block",
						marginTop: "12px"
					},
					svg: {
						fill: "#333",
						width: "24px",
						height: "24px",
						border: "1px transparent solid",
						borderRadius: "5px"
					}
				},
				disableAlpha: { alpha: { display: "none" } }
			}, this.props, this.state), n = void 0;
			return this.state.view === "hex" ? n = T.createElement("div", {
				style: t.fields,
				className: "flexbox-fix"
			}, T.createElement("div", { style: t.field }, T.createElement(A, {
				style: {
					input: t.input,
					label: t.label
				},
				label: "hex",
				value: this.props.hex,
				onChange: this.handleChange
			}))) : this.state.view === "rgb" ? n = T.createElement("div", {
				style: t.fields,
				className: "flexbox-fix"
			}, T.createElement("div", { style: t.field }, T.createElement(A, {
				style: {
					input: t.input,
					label: t.label
				},
				label: "r",
				value: this.props.rgb.r,
				onChange: this.handleChange
			})), T.createElement("div", { style: t.field }, T.createElement(A, {
				style: {
					input: t.input,
					label: t.label
				},
				label: "g",
				value: this.props.rgb.g,
				onChange: this.handleChange
			})), T.createElement("div", { style: t.field }, T.createElement(A, {
				style: {
					input: t.input,
					label: t.label
				},
				label: "b",
				value: this.props.rgb.b,
				onChange: this.handleChange
			})), T.createElement("div", { style: t.alpha }, T.createElement(A, {
				style: {
					input: t.input,
					label: t.label
				},
				label: "a",
				value: this.props.rgb.a,
				arrowOffset: .01,
				onChange: this.handleChange
			}))) : this.state.view === "hsl" && (n = T.createElement("div", {
				style: t.fields,
				className: "flexbox-fix"
			}, T.createElement("div", { style: t.field }, T.createElement(A, {
				style: {
					input: t.input,
					label: t.label
				},
				label: "h",
				value: Math.round(this.props.hsl.h),
				onChange: this.handleChange
			})), T.createElement("div", { style: t.field }, T.createElement(A, {
				style: {
					input: t.input,
					label: t.label
				},
				label: "s",
				value: Math.round(this.props.hsl.s * 100) + "%",
				onChange: this.handleChange
			})), T.createElement("div", { style: t.field }, T.createElement(A, {
				style: {
					input: t.input,
					label: t.label
				},
				label: "l",
				value: Math.round(this.props.hsl.l * 100) + "%",
				onChange: this.handleChange
			})), T.createElement("div", { style: t.alpha }, T.createElement(A, {
				style: {
					input: t.input,
					label: t.label
				},
				label: "a",
				value: this.props.hsl.a,
				arrowOffset: .01,
				onChange: this.handleChange
			})))), T.createElement("div", {
				style: t.wrap,
				className: "flexbox-fix"
			}, n, T.createElement("div", { style: t.toggle }, T.createElement("div", {
				style: t.icon,
				onClick: this.toggleViews,
				ref: function(t) {
					return e.icon = t;
				}
			}, T.createElement(Cu, {
				style: t.svg,
				onMouseOver: this.showHighlight,
				onMouseEnter: this.showHighlight,
				onMouseOut: this.hideHighlight
			}))));
		}
	}], [{
		key: "getDerivedStateFromProps",
		value: function(e, t) {
			return e.hsl.a !== 1 && t.view === "hex" ? { view: "rgb" } : null;
		}
	}]), t;
}(T.Component);
Ou.defaultProps = { view: "hex" };
var ku = function() {
	var e = k({ default: { picker: {
		width: "12px",
		height: "12px",
		borderRadius: "6px",
		transform: "translate(-6px, -1px)",
		backgroundColor: "rgb(248, 248, 248)",
		boxShadow: "0 1px 4px 0 rgba(0, 0, 0, 0.37)"
	} } });
	return T.createElement("div", { style: e.picker });
}, Au = function() {
	var e = k({ default: { picker: {
		width: "12px",
		height: "12px",
		borderRadius: "6px",
		boxShadow: "inset 0 0 0 1px #fff",
		transform: "translate(-6px, -6px)"
	} } });
	return T.createElement("div", { style: e.picker });
}, ju = function(e) {
	var t = e.width, n = e.onChange, r = e.disableAlpha, i = e.rgb, a = e.hsl, o = e.hsv, s = e.hex, c = e.renderers, l = e.styles, u = l === void 0 ? {} : l, d = e.className, f = d === void 0 ? "" : d, p = e.defaultView, m = k(W({
		default: {
			picker: {
				width: t,
				background: "#fff",
				borderRadius: "2px",
				boxShadow: "0 0 2px rgba(0,0,0,.3), 0 4px 8px rgba(0,0,0,.3)",
				boxSizing: "initial",
				fontFamily: "Menlo"
			},
			saturation: {
				width: "100%",
				paddingBottom: "55%",
				position: "relative",
				borderRadius: "2px 2px 0 0",
				overflow: "hidden"
			},
			Saturation: { radius: "2px 2px 0 0" },
			body: { padding: "16px 16px 12px" },
			controls: { display: "flex" },
			color: { width: "32px" },
			swatch: {
				marginTop: "6px",
				width: "16px",
				height: "16px",
				borderRadius: "8px",
				position: "relative",
				overflow: "hidden"
			},
			active: {
				absolute: "0px 0px 0px 0px",
				borderRadius: "8px",
				boxShadow: "inset 0 0 0 1px rgba(0,0,0,.1)",
				background: "rgba(" + i.r + ", " + i.g + ", " + i.b + ", " + i.a + ")",
				zIndex: "2"
			},
			toggles: { flex: "1" },
			hue: {
				height: "10px",
				position: "relative",
				marginBottom: "8px"
			},
			Hue: { radius: "2px" },
			alpha: {
				height: "10px",
				position: "relative"
			},
			Alpha: { radius: "2px" }
		},
		disableAlpha: {
			color: { width: "22px" },
			alpha: { display: "none" },
			hue: { marginBottom: "0px" },
			swatch: {
				width: "10px",
				height: "10px",
				marginTop: "0px"
			}
		}
	}, u), { disableAlpha: r });
	return T.createElement("div", {
		style: m.picker,
		className: "chrome-picker " + f
	}, T.createElement("div", { style: m.saturation }, T.createElement(Ko, {
		style: m.Saturation,
		hsl: a,
		hsv: o,
		pointer: Au,
		onChange: n
	})), T.createElement("div", { style: m.body }, T.createElement("div", {
		style: m.controls,
		className: "flexbox-fix"
	}, T.createElement("div", { style: m.color }, T.createElement("div", { style: m.swatch }, T.createElement("div", { style: m.active }), T.createElement(Gn, { renderers: c }))), T.createElement("div", { style: m.toggles }, T.createElement("div", { style: m.hue }, T.createElement(mr, {
		style: m.Hue,
		hsl: a,
		pointer: ku,
		onChange: n
	})), T.createElement("div", { style: m.alpha }, T.createElement(Zn, {
		style: m.Alpha,
		rgb: i,
		hsl: a,
		pointer: ku,
		renderers: c,
		onChange: n
	})))), T.createElement(Ou, {
		rgb: i,
		hsl: a,
		hex: s,
		view: p,
		onChange: n,
		disableAlpha: r
	})));
};
ju.propTypes = {
	width: a.oneOfType([a.string, a.number]),
	disableAlpha: a.bool,
	styles: a.object,
	defaultView: a.oneOf([
		"hex",
		"rgb",
		"hsl"
	])
}, ju.defaultProps = {
	width: 225,
	disableAlpha: !1,
	styles: {}
};
var Mu = Q(ju), Nu = function(e) {
	var t = e.color, n = e.onClick, r = n === void 0 ? function() {} : n, i = e.onSwatchHover, a = e.active, o = k({
		default: {
			color: {
				background: t,
				width: "15px",
				height: "15px",
				float: "left",
				marginRight: "5px",
				marginBottom: "5px",
				position: "relative",
				cursor: "pointer"
			},
			dot: {
				absolute: "5px 5px 5px 5px",
				background: Vs(t),
				borderRadius: "50%",
				opacity: "0"
			}
		},
		active: { dot: { opacity: "1" } },
		"color-#FFFFFF": {
			color: { boxShadow: "inset 0 0 0 1px #ddd" },
			dot: { background: "#000" }
		},
		transparent: { dot: { background: "#000" } }
	}, {
		active: a,
		"color-#FFFFFF": t === "#FFFFFF",
		transparent: t === "transparent"
	});
	return T.createElement(nc, {
		style: o.color,
		color: t,
		onClick: r,
		onHover: i,
		focusStyle: { boxShadow: "0 0 4px " + t }
	}, T.createElement("div", { style: o.dot }));
}, Pu = function(e) {
	var t = e.hex, n = e.rgb, r = e.onChange, i = k({ default: {
		fields: {
			display: "flex",
			paddingBottom: "6px",
			paddingRight: "5px",
			position: "relative"
		},
		active: {
			position: "absolute",
			top: "6px",
			left: "5px",
			height: "9px",
			width: "9px",
			background: t
		},
		HEXwrap: {
			flex: "6",
			position: "relative"
		},
		HEXinput: {
			width: "80%",
			padding: "0px",
			paddingLeft: "20%",
			border: "none",
			outline: "none",
			background: "none",
			fontSize: "12px",
			color: "#333",
			height: "16px"
		},
		HEXlabel: { display: "none" },
		RGBwrap: {
			flex: "3",
			position: "relative"
		},
		RGBinput: {
			width: "70%",
			padding: "0px",
			paddingLeft: "30%",
			border: "none",
			outline: "none",
			background: "none",
			fontSize: "12px",
			color: "#333",
			height: "16px"
		},
		RGBlabel: {
			position: "absolute",
			top: "3px",
			left: "0px",
			lineHeight: "16px",
			textTransform: "uppercase",
			fontSize: "12px",
			color: "#999"
		}
	} }), a = function(e, t) {
		e.r || e.g || e.b ? r({
			r: e.r || n.r,
			g: e.g || n.g,
			b: e.b || n.b,
			source: "rgb"
		}, t) : r({
			hex: e.hex,
			source: "hex"
		}, t);
	};
	return T.createElement("div", {
		style: i.fields,
		className: "flexbox-fix"
	}, T.createElement("div", { style: i.active }), T.createElement(A, {
		style: {
			wrap: i.HEXwrap,
			input: i.HEXinput,
			label: i.HEXlabel
		},
		label: "hex",
		value: t,
		onChange: a
	}), T.createElement(A, {
		style: {
			wrap: i.RGBwrap,
			input: i.RGBinput,
			label: i.RGBlabel
		},
		label: "r",
		value: n.r,
		onChange: a
	}), T.createElement(A, {
		style: {
			wrap: i.RGBwrap,
			input: i.RGBinput,
			label: i.RGBlabel
		},
		label: "g",
		value: n.g,
		onChange: a
	}), T.createElement(A, {
		style: {
			wrap: i.RGBwrap,
			input: i.RGBinput,
			label: i.RGBlabel
		},
		label: "b",
		value: n.b,
		onChange: a
	}));
}, Fu = function(e) {
	var t = e.onChange, n = e.onSwatchHover, r = e.colors, i = e.hex, a = e.rgb, o = e.styles, s = o === void 0 ? {} : o, c = e.className, l = c === void 0 ? "" : c, u = k(W({ default: {
		Compact: {
			background: "#f6f6f6",
			radius: "4px"
		},
		compact: {
			paddingTop: "5px",
			paddingLeft: "5px",
			boxSizing: "initial",
			width: "240px"
		},
		clear: { clear: "both" }
	} }, s)), d = function(e, n) {
		e.hex ? Z(e.hex) && t({
			hex: e.hex,
			source: "hex"
		}, n) : t(e, n);
	};
	return T.createElement(xo, {
		style: u.Compact,
		styles: s
	}, T.createElement("div", {
		style: u.compact,
		className: "compact-picker " + l
	}, T.createElement("div", null, Yl(r, function(e) {
		return T.createElement(Nu, {
			key: e,
			color: e,
			active: e.toLowerCase() === i,
			onClick: d,
			onSwatchHover: n
		});
	}), T.createElement("div", { style: u.clear })), T.createElement(Pu, {
		hex: i,
		rgb: a,
		onChange: d
	})));
};
Fu.propTypes = {
	colors: a.arrayOf(a.string),
	styles: a.object
}, Fu.defaultProps = {
	colors: /* @__PURE__ */ "#4D4D4D.#999999.#FFFFFF.#F44E3B.#FE9200.#FCDC00.#DBDF00.#A4DD00.#68CCCA.#73D8FF.#AEA1FF.#FDA1FF.#333333.#808080.#cccccc.#D33115.#E27300.#FCC400.#B0BC00.#68BC00.#16A5A5.#009CE0.#7B64FF.#FA28FF.#000000.#666666.#B3B3B3.#9F0500.#C45100.#FB9E00.#808900.#194D33.#0C797D.#0062B1.#653294.#AB149E".split("."),
	styles: {}
}, Q(Fu);
var Iu = zn.handleHover(function(e) {
	var t = e.hover, n = e.color, r = e.onClick, i = e.onSwatchHover, a = {
		position: "relative",
		zIndex: "2",
		outline: "2px solid #fff",
		boxShadow: "0 0 5px 2px rgba(0,0,0,0.25)"
	}, o = k({
		default: { swatch: {
			width: "25px",
			height: "25px",
			fontSize: "0"
		} },
		hover: { swatch: a }
	}, { hover: t });
	return T.createElement("div", { style: o.swatch }, T.createElement(nc, {
		color: n,
		onClick: r,
		onHover: i,
		focusStyle: a
	}));
}), Lu = function(e) {
	var t = e.width, n = e.colors, r = e.onChange, i = e.onSwatchHover, a = e.triangle, o = e.styles, s = o === void 0 ? {} : o, c = e.className, l = c === void 0 ? "" : c, u = k(W({
		default: {
			card: {
				width: t,
				background: "#fff",
				border: "1px solid rgba(0,0,0,0.2)",
				boxShadow: "0 3px 12px rgba(0,0,0,0.15)",
				borderRadius: "4px",
				position: "relative",
				padding: "5px",
				display: "flex",
				flexWrap: "wrap"
			},
			triangle: {
				position: "absolute",
				border: "7px solid transparent",
				borderBottomColor: "#fff"
			},
			triangleShadow: {
				position: "absolute",
				border: "8px solid transparent",
				borderBottomColor: "rgba(0,0,0,0.15)"
			}
		},
		"hide-triangle": {
			triangle: { display: "none" },
			triangleShadow: { display: "none" }
		},
		"top-left-triangle": {
			triangle: {
				top: "-14px",
				left: "10px"
			},
			triangleShadow: {
				top: "-16px",
				left: "9px"
			}
		},
		"top-right-triangle": {
			triangle: {
				top: "-14px",
				right: "10px"
			},
			triangleShadow: {
				top: "-16px",
				right: "9px"
			}
		},
		"bottom-left-triangle": {
			triangle: {
				top: "35px",
				left: "10px",
				transform: "rotate(180deg)"
			},
			triangleShadow: {
				top: "37px",
				left: "9px",
				transform: "rotate(180deg)"
			}
		},
		"bottom-right-triangle": {
			triangle: {
				top: "35px",
				right: "10px",
				transform: "rotate(180deg)"
			},
			triangleShadow: {
				top: "37px",
				right: "9px",
				transform: "rotate(180deg)"
			}
		}
	}, s), {
		"hide-triangle": a === "hide",
		"top-left-triangle": a === "top-left",
		"top-right-triangle": a === "top-right",
		"bottom-left-triangle": a === "bottom-left",
		"bottom-right-triangle": a === "bottom-right"
	}), d = function(e, t) {
		return r({
			hex: e,
			source: "hex"
		}, t);
	};
	return T.createElement("div", {
		style: u.card,
		className: "github-picker " + l
	}, T.createElement("div", { style: u.triangleShadow }), T.createElement("div", { style: u.triangle }), Yl(n, function(e) {
		return T.createElement(Iu, {
			color: e,
			key: e,
			onClick: d,
			onSwatchHover: i
		});
	}));
};
Lu.propTypes = {
	width: a.oneOfType([a.string, a.number]),
	colors: a.arrayOf(a.string),
	triangle: a.oneOf([
		"hide",
		"top-left",
		"top-right",
		"bottom-left",
		"bottom-right"
	]),
	styles: a.object
}, Lu.defaultProps = {
	width: 200,
	colors: [
		"#B80000",
		"#DB3E00",
		"#FCCB00",
		"#008B02",
		"#006B76",
		"#1273DE",
		"#004DCF",
		"#5300EB",
		"#EB9694",
		"#FAD0C3",
		"#FEF3BD",
		"#C1E1C5",
		"#BEDADC",
		"#C4DEF6",
		"#BED3F3",
		"#D4C4FB"
	],
	triangle: "top-left",
	styles: {}
}, Q(Lu);
var Ru = function(e) {
	var t = e.direction, n = k({
		default: { picker: {
			width: "18px",
			height: "18px",
			borderRadius: "50%",
			transform: "translate(-9px, -1px)",
			backgroundColor: "rgb(248, 248, 248)",
			boxShadow: "0 1px 4px 0 rgba(0, 0, 0, 0.37)"
		} },
		vertical: { picker: { transform: "translate(-3px, -9px)" } }
	}, { vertical: t === "vertical" });
	return T.createElement("div", { style: n.picker });
}, zu = Object.assign || function(e) {
	for (var t = 1; t < arguments.length; t++) {
		var n = arguments[t];
		for (var r in n) Object.prototype.hasOwnProperty.call(n, r) && (e[r] = n[r]);
	}
	return e;
}, Bu = function(e) {
	var t = e.width, n = e.height, r = e.onChange, i = e.hsl, a = e.direction, o = e.pointer, s = e.styles, c = s === void 0 ? {} : s, l = e.className, u = l === void 0 ? "" : l, d = k(W({ default: {
		picker: {
			position: "relative",
			width: t,
			height: n
		},
		hue: { radius: "2px" }
	} }, c));
	return T.createElement("div", {
		style: d.picker,
		className: "hue-picker " + u
	}, T.createElement(mr, zu({}, d.hue, {
		hsl: i,
		pointer: o,
		onChange: function(e) {
			return r({
				a: 1,
				h: e.h,
				l: .5,
				s: 1
			});
		},
		direction: a
	})));
};
Bu.propTypes = { styles: a.object }, Bu.defaultProps = {
	width: "316px",
	height: "16px",
	direction: "horizontal",
	pointer: Ru,
	styles: {}
}, Q(Bu), Q(function(e) {
	var t = e.onChange, n = e.hex, r = e.rgb, i = e.styles, a = i === void 0 ? {} : i, o = e.className, s = o === void 0 ? "" : o, c = k(W({ default: {
		material: {
			width: "98px",
			height: "98px",
			padding: "16px",
			fontFamily: "Roboto"
		},
		HEXwrap: { position: "relative" },
		HEXinput: {
			width: "100%",
			marginTop: "12px",
			fontSize: "15px",
			color: "#333",
			padding: "0px",
			border: "0px",
			borderBottom: "2px solid " + n,
			outline: "none",
			height: "30px"
		},
		HEXlabel: {
			position: "absolute",
			top: "0px",
			left: "0px",
			fontSize: "11px",
			color: "#999999",
			textTransform: "capitalize"
		},
		Hex: { style: {} },
		RGBwrap: { position: "relative" },
		RGBinput: {
			width: "100%",
			marginTop: "12px",
			fontSize: "15px",
			color: "#333",
			padding: "0px",
			border: "0px",
			borderBottom: "1px solid #eee",
			outline: "none",
			height: "30px"
		},
		RGBlabel: {
			position: "absolute",
			top: "0px",
			left: "0px",
			fontSize: "11px",
			color: "#999999",
			textTransform: "capitalize"
		},
		split: {
			display: "flex",
			marginRight: "-10px",
			paddingTop: "11px"
		},
		third: {
			flex: "1",
			paddingRight: "10px"
		}
	} }, a)), l = function(e, n) {
		e.hex ? Z(e.hex) && t({
			hex: e.hex,
			source: "hex"
		}, n) : (e.r || e.g || e.b) && t({
			r: e.r || r.r,
			g: e.g || r.g,
			b: e.b || r.b,
			source: "rgb"
		}, n);
	};
	return T.createElement(xo, { styles: a }, T.createElement("div", {
		style: c.material,
		className: "material-picker " + s
	}, T.createElement(A, {
		style: {
			wrap: c.HEXwrap,
			input: c.HEXinput,
			label: c.HEXlabel
		},
		label: "hex",
		value: n,
		onChange: l
	}), T.createElement("div", {
		style: c.split,
		className: "flexbox-fix"
	}, T.createElement("div", { style: c.third }, T.createElement(A, {
		style: {
			wrap: c.RGBwrap,
			input: c.RGBinput,
			label: c.RGBlabel
		},
		label: "r",
		value: r.r,
		onChange: l
	})), T.createElement("div", { style: c.third }, T.createElement(A, {
		style: {
			wrap: c.RGBwrap,
			input: c.RGBinput,
			label: c.RGBlabel
		},
		label: "g",
		value: r.g,
		onChange: l
	})), T.createElement("div", { style: c.third }, T.createElement(A, {
		style: {
			wrap: c.RGBwrap,
			input: c.RGBinput,
			label: c.RGBlabel
		},
		label: "b",
		value: r.b,
		onChange: l
	})))));
});
var Vu = function(e) {
	var t = e.onChange, n = e.rgb, r = e.hsv, i = e.hex, a = k({ default: {
		fields: {
			paddingTop: "5px",
			paddingBottom: "9px",
			width: "80px",
			position: "relative"
		},
		divider: { height: "5px" },
		RGBwrap: { position: "relative" },
		RGBinput: {
			marginLeft: "40%",
			width: "40%",
			height: "18px",
			border: "1px solid #888888",
			boxShadow: "inset 0 1px 1px rgba(0,0,0,.1), 0 1px 0 0 #ECECEC",
			marginBottom: "5px",
			fontSize: "13px",
			paddingLeft: "3px",
			marginRight: "10px"
		},
		RGBlabel: {
			left: "0px",
			top: "0px",
			width: "34px",
			textTransform: "uppercase",
			fontSize: "13px",
			height: "18px",
			lineHeight: "22px",
			position: "absolute"
		},
		HEXwrap: { position: "relative" },
		HEXinput: {
			marginLeft: "20%",
			width: "80%",
			height: "18px",
			border: "1px solid #888888",
			boxShadow: "inset 0 1px 1px rgba(0,0,0,.1), 0 1px 0 0 #ECECEC",
			marginBottom: "6px",
			fontSize: "13px",
			paddingLeft: "3px"
		},
		HEXlabel: {
			position: "absolute",
			top: "0px",
			left: "0px",
			width: "14px",
			textTransform: "uppercase",
			fontSize: "13px",
			height: "18px",
			lineHeight: "22px"
		},
		fieldSymbols: {
			position: "absolute",
			top: "5px",
			right: "-7px",
			fontSize: "13px"
		},
		symbol: {
			height: "20px",
			lineHeight: "22px",
			paddingBottom: "7px"
		}
	} }), o = function(e, i) {
		e["#"] ? Z(e["#"]) && t({
			hex: e["#"],
			source: "hex"
		}, i) : e.r || e.g || e.b ? t({
			r: e.r || n.r,
			g: e.g || n.g,
			b: e.b || n.b,
			source: "rgb"
		}, i) : (e.h || e.s || e.v) && t({
			h: e.h || r.h,
			s: e.s || r.s,
			v: e.v || r.v,
			source: "hsv"
		}, i);
	};
	return T.createElement("div", { style: a.fields }, T.createElement(A, {
		style: {
			wrap: a.RGBwrap,
			input: a.RGBinput,
			label: a.RGBlabel
		},
		label: "h",
		value: Math.round(r.h),
		onChange: o
	}), T.createElement(A, {
		style: {
			wrap: a.RGBwrap,
			input: a.RGBinput,
			label: a.RGBlabel
		},
		label: "s",
		value: Math.round(r.s * 100),
		onChange: o
	}), T.createElement(A, {
		style: {
			wrap: a.RGBwrap,
			input: a.RGBinput,
			label: a.RGBlabel
		},
		label: "v",
		value: Math.round(r.v * 100),
		onChange: o
	}), T.createElement("div", { style: a.divider }), T.createElement(A, {
		style: {
			wrap: a.RGBwrap,
			input: a.RGBinput,
			label: a.RGBlabel
		},
		label: "r",
		value: n.r,
		onChange: o
	}), T.createElement(A, {
		style: {
			wrap: a.RGBwrap,
			input: a.RGBinput,
			label: a.RGBlabel
		},
		label: "g",
		value: n.g,
		onChange: o
	}), T.createElement(A, {
		style: {
			wrap: a.RGBwrap,
			input: a.RGBinput,
			label: a.RGBlabel
		},
		label: "b",
		value: n.b,
		onChange: o
	}), T.createElement("div", { style: a.divider }), T.createElement(A, {
		style: {
			wrap: a.HEXwrap,
			input: a.HEXinput,
			label: a.HEXlabel
		},
		label: "#",
		value: i.replace("#", ""),
		onChange: o
	}), T.createElement("div", { style: a.fieldSymbols }, T.createElement("div", { style: a.symbol }, "°"), T.createElement("div", { style: a.symbol }, "%"), T.createElement("div", { style: a.symbol }, "%")));
}, Hu = function(e) {
	var t = e.hsl, n = k({
		default: { picker: {
			width: "12px",
			height: "12px",
			borderRadius: "6px",
			boxShadow: "inset 0 0 0 1px #fff",
			transform: "translate(-6px, -6px)"
		} },
		"black-outline": { picker: { boxShadow: "inset 0 0 0 1px #000" } }
	}, { "black-outline": t.l > .5 });
	return T.createElement("div", { style: n.picker });
}, Uu = function() {
	var e = k({ default: {
		triangle: {
			width: 0,
			height: 0,
			borderStyle: "solid",
			borderWidth: "4px 0 4px 6px",
			borderColor: "transparent transparent transparent #fff",
			position: "absolute",
			top: "1px",
			left: "1px"
		},
		triangleBorder: {
			width: 0,
			height: 0,
			borderStyle: "solid",
			borderWidth: "5px 0 5px 8px",
			borderColor: "transparent transparent transparent #555"
		},
		left: {
			Extend: "triangleBorder",
			transform: "translate(-13px, -4px)"
		},
		leftInside: {
			Extend: "triangle",
			transform: "translate(-8px, -5px)"
		},
		right: {
			Extend: "triangleBorder",
			transform: "translate(20px, -14px) rotate(180deg)"
		},
		rightInside: {
			Extend: "triangle",
			transform: "translate(-8px, -5px)"
		}
	} });
	return T.createElement("div", { style: e.pointer }, T.createElement("div", { style: e.left }, T.createElement("div", { style: e.leftInside })), T.createElement("div", { style: e.right }, T.createElement("div", { style: e.rightInside })));
}, Wu = function(e) {
	var t = e.onClick, n = e.label, r = e.children, i = e.active, a = k({
		default: { button: {
			backgroundImage: "linear-gradient(-180deg, #FFFFFF 0%, #E6E6E6 100%)",
			border: "1px solid #878787",
			borderRadius: "2px",
			height: "20px",
			boxShadow: "0 1px 0 0 #EAEAEA",
			fontSize: "14px",
			color: "#000",
			lineHeight: "20px",
			textAlign: "center",
			marginBottom: "10px",
			cursor: "pointer"
		} },
		active: { button: { boxShadow: "0 0 0 1px #878787" } }
	}, { active: i });
	return T.createElement("div", {
		style: a.button,
		onClick: t
	}, n || r);
}, Gu = function(e) {
	var t = e.rgb, n = e.currentColor, r = k({ default: {
		swatches: {
			border: "1px solid #B3B3B3",
			borderBottom: "1px solid #F0F0F0",
			marginBottom: "2px",
			marginTop: "1px"
		},
		new: {
			height: "34px",
			background: "rgb(" + t.r + "," + t.g + ", " + t.b + ")",
			boxShadow: "inset 1px 0 0 #000, inset -1px 0 0 #000, inset 0 1px 0 #000"
		},
		current: {
			height: "34px",
			background: n,
			boxShadow: "inset 1px 0 0 #000, inset -1px 0 0 #000, inset 0 -1px 0 #000"
		},
		label: {
			fontSize: "14px",
			color: "#000",
			textAlign: "center"
		}
	} });
	return T.createElement("div", null, T.createElement("div", { style: r.label }, "new"), T.createElement("div", { style: r.swatches }, T.createElement("div", { style: r.new }), T.createElement("div", { style: r.current })), T.createElement("div", { style: r.label }, "current"));
}, Ku = /* @__PURE__ */ function() {
	function e(e, t) {
		for (var n = 0; n < t.length; n++) {
			var r = t[n];
			r.enumerable = r.enumerable || !1, r.configurable = !0, "value" in r && (r.writable = !0), Object.defineProperty(e, r.key, r);
		}
	}
	return function(t, n, r) {
		return n && e(t.prototype, n), r && e(t, r), t;
	};
}();
function qu(e, t) {
	if (!(e instanceof t)) throw TypeError("Cannot call a class as a function");
}
function Ju(e, t) {
	if (!e) throw ReferenceError("this hasn't been initialised - super() hasn't been called");
	return t && (typeof t == "object" || typeof t == "function") ? t : e;
}
function Yu(e, t) {
	if (typeof t != "function" && t !== null) throw TypeError("Super expression must either be null or a function, not " + typeof t);
	e.prototype = Object.create(t && t.prototype, { constructor: {
		value: e,
		enumerable: !1,
		writable: !0,
		configurable: !0
	} }), t && (Object.setPrototypeOf ? Object.setPrototypeOf(e, t) : e.__proto__ = t);
}
var Xu = function(e) {
	Yu(t, e);
	function t(e) {
		qu(this, t);
		var n = Ju(this, (t.__proto__ || Object.getPrototypeOf(t)).call(this));
		return n.state = { currentColor: e.hex }, n;
	}
	return Ku(t, [{
		key: "render",
		value: function() {
			var e = this.props, t = e.styles, n = t === void 0 ? {} : t, r = e.className, i = r === void 0 ? "" : r, a = k(W({ default: {
				picker: {
					background: "#DCDCDC",
					borderRadius: "4px",
					boxShadow: "0 0 0 1px rgba(0,0,0,.25), 0 8px 16px rgba(0,0,0,.15)",
					boxSizing: "initial",
					width: "513px"
				},
				head: {
					backgroundImage: "linear-gradient(-180deg, #F0F0F0 0%, #D4D4D4 100%)",
					borderBottom: "1px solid #B1B1B1",
					boxShadow: "inset 0 1px 0 0 rgba(255,255,255,.2), inset 0 -1px 0 0 rgba(0,0,0,.02)",
					height: "23px",
					lineHeight: "24px",
					borderRadius: "4px 4px 0 0",
					fontSize: "13px",
					color: "#4D4D4D",
					textAlign: "center"
				},
				body: {
					padding: "15px 15px 0",
					display: "flex"
				},
				saturation: {
					width: "256px",
					height: "256px",
					position: "relative",
					border: "2px solid #B3B3B3",
					borderBottom: "2px solid #F0F0F0",
					overflow: "hidden"
				},
				hue: {
					position: "relative",
					height: "256px",
					width: "19px",
					marginLeft: "10px",
					border: "2px solid #B3B3B3",
					borderBottom: "2px solid #F0F0F0"
				},
				controls: {
					width: "180px",
					marginLeft: "10px"
				},
				top: { display: "flex" },
				previews: { width: "60px" },
				actions: {
					flex: "1",
					marginLeft: "20px"
				}
			} }, n));
			return T.createElement("div", {
				style: a.picker,
				className: "photoshop-picker " + i
			}, T.createElement("div", { style: a.head }, this.props.header), T.createElement("div", {
				style: a.body,
				className: "flexbox-fix"
			}, T.createElement("div", { style: a.saturation }, T.createElement(Ko, {
				hsl: this.props.hsl,
				hsv: this.props.hsv,
				pointer: Hu,
				onChange: this.props.onChange
			})), T.createElement("div", { style: a.hue }, T.createElement(mr, {
				direction: "vertical",
				hsl: this.props.hsl,
				pointer: Uu,
				onChange: this.props.onChange
			})), T.createElement("div", { style: a.controls }, T.createElement("div", {
				style: a.top,
				className: "flexbox-fix"
			}, T.createElement("div", { style: a.previews }, T.createElement(Gu, {
				rgb: this.props.rgb,
				currentColor: this.state.currentColor
			})), T.createElement("div", { style: a.actions }, T.createElement(Wu, {
				label: "OK",
				onClick: this.props.onAccept,
				active: !0
			}), T.createElement(Wu, {
				label: "Cancel",
				onClick: this.props.onCancel
			}), T.createElement(Vu, {
				onChange: this.props.onChange,
				rgb: this.props.rgb,
				hsv: this.props.hsv,
				hex: this.props.hex
			}))))));
		}
	}]), t;
}(T.Component);
Xu.propTypes = {
	header: a.string,
	styles: a.object
}, Xu.defaultProps = {
	header: "Color Picker",
	styles: {}
}, Q(Xu);
var Zu = function(e) {
	var t = e.onChange, n = e.rgb, r = e.hsl, i = e.hex, a = e.disableAlpha, o = k({
		default: {
			fields: {
				display: "flex",
				paddingTop: "4px"
			},
			single: {
				flex: "1",
				paddingLeft: "6px"
			},
			alpha: {
				flex: "1",
				paddingLeft: "6px"
			},
			double: { flex: "2" },
			input: {
				width: "80%",
				padding: "4px 10% 3px",
				border: "none",
				boxShadow: "inset 0 0 0 1px #ccc",
				fontSize: "11px"
			},
			label: {
				display: "block",
				textAlign: "center",
				fontSize: "11px",
				color: "#222",
				paddingTop: "3px",
				paddingBottom: "4px",
				textTransform: "capitalize"
			}
		},
		disableAlpha: { alpha: { display: "none" } }
	}, { disableAlpha: a }), s = function(e, i) {
		e.hex ? Z(e.hex) && t({
			hex: e.hex,
			source: "hex"
		}, i) : e.r || e.g || e.b ? t({
			r: e.r || n.r,
			g: e.g || n.g,
			b: e.b || n.b,
			a: n.a,
			source: "rgb"
		}, i) : e.a && (e.a < 0 ? e.a = 0 : e.a > 100 && (e.a = 100), e.a /= 100, t({
			h: r.h,
			s: r.s,
			l: r.l,
			a: e.a,
			source: "rgb"
		}, i));
	};
	return T.createElement("div", {
		style: o.fields,
		className: "flexbox-fix"
	}, T.createElement("div", { style: o.double }, T.createElement(A, {
		style: {
			input: o.input,
			label: o.label
		},
		label: "hex",
		value: i.replace("#", ""),
		onChange: s
	})), T.createElement("div", { style: o.single }, T.createElement(A, {
		style: {
			input: o.input,
			label: o.label
		},
		label: "r",
		value: n.r,
		onChange: s,
		dragLabel: "true",
		dragMax: "255"
	})), T.createElement("div", { style: o.single }, T.createElement(A, {
		style: {
			input: o.input,
			label: o.label
		},
		label: "g",
		value: n.g,
		onChange: s,
		dragLabel: "true",
		dragMax: "255"
	})), T.createElement("div", { style: o.single }, T.createElement(A, {
		style: {
			input: o.input,
			label: o.label
		},
		label: "b",
		value: n.b,
		onChange: s,
		dragLabel: "true",
		dragMax: "255"
	})), T.createElement("div", { style: o.alpha }, T.createElement(A, {
		style: {
			input: o.input,
			label: o.label
		},
		label: "a",
		value: Math.round(n.a * 100),
		onChange: s,
		dragLabel: "true",
		dragMax: "100"
	})));
}, Qu = Object.assign || function(e) {
	for (var t = 1; t < arguments.length; t++) {
		var n = arguments[t];
		for (var r in n) Object.prototype.hasOwnProperty.call(n, r) && (e[r] = n[r]);
	}
	return e;
}, $u = function(e) {
	var t = e.colors, n = e.onClick, r = n === void 0 ? function() {} : n, i = e.onSwatchHover, a = k({
		default: {
			colors: {
				margin: "0 -10px",
				padding: "10px 0 0 10px",
				borderTop: "1px solid #eee",
				display: "flex",
				flexWrap: "wrap",
				position: "relative"
			},
			swatchWrap: {
				width: "16px",
				height: "16px",
				margin: "0 10px 10px 0"
			},
			swatch: {
				borderRadius: "3px",
				boxShadow: "inset 0 0 0 1px rgba(0,0,0,.15)"
			}
		},
		"no-presets": { colors: { display: "none" } }
	}, { "no-presets": !t || !t.length }), o = function(e, t) {
		r({
			hex: e,
			source: "hex"
		}, t);
	};
	return T.createElement("div", {
		style: a.colors,
		className: "flexbox-fix"
	}, t.map(function(e) {
		var t = typeof e == "string" ? { color: e } : e, n = "" + t.color + (t.title || "");
		return T.createElement("div", {
			key: n,
			style: a.swatchWrap
		}, T.createElement(nc, Qu({}, t, {
			style: a.swatch,
			onClick: o,
			onHover: i,
			focusStyle: { boxShadow: "inset 0 0 0 1px rgba(0,0,0,.15), 0 0 4px " + t.color }
		})));
	}));
};
$u.propTypes = { colors: a.arrayOf(a.oneOfType([a.string, a.shape({
	color: a.string,
	title: a.string
})])).isRequired };
var ed = Object.assign || function(e) {
	for (var t = 1; t < arguments.length; t++) {
		var n = arguments[t];
		for (var r in n) Object.prototype.hasOwnProperty.call(n, r) && (e[r] = n[r]);
	}
	return e;
}, td = function(e) {
	var t = e.width, n = e.rgb, r = e.hex, i = e.hsv, a = e.hsl, o = e.onChange, s = e.onSwatchHover, c = e.disableAlpha, l = e.presetColors, u = e.renderers, d = e.styles, f = d === void 0 ? {} : d, p = e.className, m = p === void 0 ? "" : p, h = k(W({
		default: ed({
			picker: {
				width: t,
				padding: "10px 10px 0",
				boxSizing: "initial",
				background: "#fff",
				borderRadius: "4px",
				boxShadow: "0 0 0 1px rgba(0,0,0,.15), 0 8px 16px rgba(0,0,0,.15)"
			},
			saturation: {
				width: "100%",
				paddingBottom: "75%",
				position: "relative",
				overflow: "hidden"
			},
			Saturation: {
				radius: "3px",
				shadow: "inset 0 0 0 1px rgba(0,0,0,.15), inset 0 0 4px rgba(0,0,0,.25)"
			},
			controls: { display: "flex" },
			sliders: {
				padding: "4px 0",
				flex: "1"
			},
			color: {
				width: "24px",
				height: "24px",
				position: "relative",
				marginTop: "4px",
				marginLeft: "4px",
				borderRadius: "3px"
			},
			activeColor: {
				absolute: "0px 0px 0px 0px",
				borderRadius: "2px",
				background: "rgba(" + n.r + "," + n.g + "," + n.b + "," + n.a + ")",
				boxShadow: "inset 0 0 0 1px rgba(0,0,0,.15), inset 0 0 4px rgba(0,0,0,.25)"
			},
			hue: {
				position: "relative",
				height: "10px",
				overflow: "hidden"
			},
			Hue: {
				radius: "2px",
				shadow: "inset 0 0 0 1px rgba(0,0,0,.15), inset 0 0 4px rgba(0,0,0,.25)"
			},
			alpha: {
				position: "relative",
				height: "10px",
				marginTop: "4px",
				overflow: "hidden"
			},
			Alpha: {
				radius: "2px",
				shadow: "inset 0 0 0 1px rgba(0,0,0,.15), inset 0 0 4px rgba(0,0,0,.25)"
			}
		}, f),
		disableAlpha: {
			color: { height: "10px" },
			hue: { height: "10px" },
			alpha: { display: "none" }
		}
	}, f), { disableAlpha: c });
	return T.createElement("div", {
		style: h.picker,
		className: "sketch-picker " + m
	}, T.createElement("div", { style: h.saturation }, T.createElement(Ko, {
		style: h.Saturation,
		hsl: a,
		hsv: i,
		onChange: o
	})), T.createElement("div", {
		style: h.controls,
		className: "flexbox-fix"
	}, T.createElement("div", { style: h.sliders }, T.createElement("div", { style: h.hue }, T.createElement(mr, {
		style: h.Hue,
		hsl: a,
		onChange: o
	})), T.createElement("div", { style: h.alpha }, T.createElement(Zn, {
		style: h.Alpha,
		rgb: n,
		hsl: a,
		renderers: u,
		onChange: o
	}))), T.createElement("div", { style: h.color }, T.createElement(Gn, null), T.createElement("div", { style: h.activeColor }))), T.createElement(Zu, {
		rgb: n,
		hsl: a,
		hex: r,
		onChange: o,
		disableAlpha: c
	}), T.createElement($u, {
		colors: l,
		onClick: o,
		onSwatchHover: s
	}));
};
td.propTypes = {
	disableAlpha: a.bool,
	width: a.oneOfType([a.string, a.number]),
	styles: a.object
}, td.defaultProps = {
	disableAlpha: !1,
	width: 200,
	styles: {},
	presetColors: [
		"#D0021B",
		"#F5A623",
		"#F8E71C",
		"#8B572A",
		"#7ED321",
		"#417505",
		"#BD10E0",
		"#9013FE",
		"#4A90E2",
		"#50E3C2",
		"#B8E986",
		"#000000",
		"#4A4A4A",
		"#9B9B9B",
		"#FFFFFF"
	]
}, Q(td);
var nd = function(e) {
	var t = e.hsl, n = e.offset, r = e.onClick, i = r === void 0 ? function() {} : r, a = e.active, o = e.first, s = e.last, c = k({
		default: { swatch: {
			height: "12px",
			background: "hsl(" + t.h + ", 50%, " + n * 100 + "%)",
			cursor: "pointer"
		} },
		first: { swatch: { borderRadius: "2px 0 0 2px" } },
		last: { swatch: { borderRadius: "0 2px 2px 0" } },
		active: { swatch: {
			transform: "scaleY(1.8)",
			borderRadius: "3.6px/2px"
		} }
	}, {
		active: a,
		first: o,
		last: s
	});
	return T.createElement("div", {
		style: c.swatch,
		onClick: function(e) {
			return i({
				h: t.h,
				s: .5,
				l: n,
				source: "hsl"
			}, e);
		}
	});
}, rd = function(e) {
	var t = e.onClick, n = e.hsl, r = k({ default: {
		swatches: { marginTop: "20px" },
		swatch: {
			boxSizing: "border-box",
			width: "20%",
			paddingRight: "1px",
			float: "left"
		},
		clear: { clear: "both" }
	} }), i = .1;
	return T.createElement("div", { style: r.swatches }, T.createElement("div", { style: r.swatch }, T.createElement(nd, {
		hsl: n,
		offset: ".80",
		active: Math.abs(n.l - .8) < i && Math.abs(n.s - .5) < i,
		onClick: t,
		first: !0
	})), T.createElement("div", { style: r.swatch }, T.createElement(nd, {
		hsl: n,
		offset: ".65",
		active: Math.abs(n.l - .65) < i && Math.abs(n.s - .5) < i,
		onClick: t
	})), T.createElement("div", { style: r.swatch }, T.createElement(nd, {
		hsl: n,
		offset: ".50",
		active: Math.abs(n.l - .5) < i && Math.abs(n.s - .5) < i,
		onClick: t
	})), T.createElement("div", { style: r.swatch }, T.createElement(nd, {
		hsl: n,
		offset: ".35",
		active: Math.abs(n.l - .35) < i && Math.abs(n.s - .5) < i,
		onClick: t
	})), T.createElement("div", { style: r.swatch }, T.createElement(nd, {
		hsl: n,
		offset: ".20",
		active: Math.abs(n.l - .2) < i && Math.abs(n.s - .5) < i,
		onClick: t,
		last: !0
	})), T.createElement("div", { style: r.clear }));
}, id = function() {
	var e = k({ default: { picker: {
		width: "14px",
		height: "14px",
		borderRadius: "6px",
		transform: "translate(-7px, -1px)",
		backgroundColor: "rgb(248, 248, 248)",
		boxShadow: "0 1px 4px 0 rgba(0, 0, 0, 0.37)"
	} } });
	return T.createElement("div", { style: e.picker });
}, ad = function(e) {
	var t = e.hsl, n = e.onChange, r = e.pointer, i = e.styles, a = i === void 0 ? {} : i, o = e.className, s = o === void 0 ? "" : o, c = k(W({ default: {
		hue: {
			height: "12px",
			position: "relative"
		},
		Hue: { radius: "2px" }
	} }, a));
	return T.createElement("div", {
		style: c.wrap || {},
		className: "slider-picker " + s
	}, T.createElement("div", { style: c.hue }, T.createElement(mr, {
		style: c.Hue,
		hsl: t,
		pointer: r,
		onChange: n
	})), T.createElement("div", { style: c.swatches }, T.createElement(rd, {
		hsl: t,
		onClick: n
	})));
};
ad.propTypes = { styles: a.object }, ad.defaultProps = {
	pointer: id,
	styles: {}
}, Q(ad);
var od = {}, sd;
function cd() {
	if (sd) return od;
	sd = 1, Object.defineProperty(od, "__esModule", { value: !0 });
	var e = Object.assign || function(e) {
		for (var t = 1; t < arguments.length; t++) {
			var n = arguments[t];
			for (var r in n) Object.prototype.hasOwnProperty.call(n, r) && (e[r] = n[r]);
		}
		return e;
	}, t = n(T.default);
	function n(e) {
		return e && e.__esModule ? e : { default: e };
	}
	function r(e, t) {
		var n = {};
		for (var r in e) t.indexOf(r) >= 0 || Object.prototype.hasOwnProperty.call(e, r) && (n[r] = e[r]);
		return n;
	}
	var i = 24;
	return od.default = function(n) {
		var a = n.fill, o = a === void 0 ? "currentColor" : a, s = n.width, c = s === void 0 ? i : s, l = n.height, u = l === void 0 ? i : l, d = n.style, f = d === void 0 ? {} : d, p = r(n, [
			"fill",
			"width",
			"height",
			"style"
		]);
		return t.default.createElement("svg", e({
			viewBox: "0 0 " + i + " " + i,
			style: e({
				fill: o,
				width: c,
				height: u
			}, f)
		}, p), t.default.createElement("path", { d: "M21,7L9,19L3.5,13.5L4.91,12.09L9,16.17L19.59,5.59L21,7Z" }));
	}, od;
}
var ld = /* @__PURE__ */ i(cd()), ud = function(e) {
	var t = e.color, n = e.onClick, r = n === void 0 ? function() {} : n, i = e.onSwatchHover, a = e.first, o = e.last, s = e.active, c = k({
		default: {
			color: {
				width: "40px",
				height: "24px",
				cursor: "pointer",
				background: t,
				marginBottom: "1px"
			},
			check: {
				color: Vs(t),
				marginLeft: "8px",
				display: "none"
			}
		},
		first: { color: {
			overflow: "hidden",
			borderRadius: "2px 2px 0 0"
		} },
		last: { color: {
			overflow: "hidden",
			borderRadius: "0 0 2px 2px"
		} },
		active: { check: { display: "block" } },
		"color-#FFFFFF": {
			color: { boxShadow: "inset 0 0 0 1px #ddd" },
			check: { color: "#333" }
		},
		transparent: { check: { color: "#333" } }
	}, {
		first: a,
		last: o,
		active: s,
		"color-#FFFFFF": t === "#FFFFFF",
		transparent: t === "transparent"
	});
	return T.createElement(nc, {
		color: t,
		style: c.color,
		onClick: r,
		onHover: i,
		focusStyle: { boxShadow: "0 0 4px " + t }
	}, T.createElement("div", { style: c.check }, T.createElement(ld, null)));
}, dd = function(e) {
	var t = e.onClick, n = e.onSwatchHover, r = e.group, i = e.active, a = k({ default: { group: {
		paddingBottom: "10px",
		width: "40px",
		float: "left",
		marginRight: "10px"
	} } });
	return T.createElement("div", { style: a.group }, Yl(r, function(e, a) {
		return T.createElement(ud, {
			key: e,
			color: e,
			active: e.toLowerCase() === i,
			first: a === 0,
			last: a === r.length - 1,
			onClick: t,
			onSwatchHover: n
		});
	}));
}, fd = function(e) {
	var t = e.width, n = e.height, r = e.onChange, i = e.onSwatchHover, a = e.colors, o = e.hex, s = e.styles, c = s === void 0 ? {} : s, l = e.className, u = l === void 0 ? "" : l, d = k(W({ default: {
		picker: {
			width: t,
			height: n
		},
		overflow: {
			height: n,
			overflowY: "scroll"
		},
		body: { padding: "16px 0 6px 16px" },
		clear: { clear: "both" }
	} }, c)), f = function(e, t) {
		return r({
			hex: e,
			source: "hex"
		}, t);
	};
	return T.createElement("div", {
		style: d.picker,
		className: "swatches-picker " + u
	}, T.createElement(xo, null, T.createElement("div", { style: d.overflow }, T.createElement("div", { style: d.body }, Yl(a, function(e) {
		return T.createElement(dd, {
			key: e.toString(),
			group: e,
			active: o,
			onClick: f,
			onSwatchHover: i
		});
	}), T.createElement("div", { style: d.clear })))));
};
fd.propTypes = {
	width: a.oneOfType([a.string, a.number]),
	height: a.oneOfType([a.string, a.number]),
	colors: a.arrayOf(a.arrayOf(a.string)),
	styles: a.object
}, fd.defaultProps = {
	width: 320,
	height: 240,
	colors: [
		[
			Ql[900],
			Ql[700],
			Ql[500],
			Ql[300],
			Ql[100]
		],
		[
			$l[900],
			$l[700],
			$l[500],
			$l[300],
			$l[100]
		],
		[
			eu[900],
			eu[700],
			eu[500],
			eu[300],
			eu[100]
		],
		[
			tu[900],
			tu[700],
			tu[500],
			tu[300],
			tu[100]
		],
		[
			nu[900],
			nu[700],
			nu[500],
			nu[300],
			nu[100]
		],
		[
			ru[900],
			ru[700],
			ru[500],
			ru[300],
			ru[100]
		],
		[
			iu[900],
			iu[700],
			iu[500],
			iu[300],
			iu[100]
		],
		[
			au[900],
			au[700],
			au[500],
			au[300],
			au[100]
		],
		[
			ou[900],
			ou[700],
			ou[500],
			ou[300],
			ou[100]
		],
		[
			"#194D33",
			su[700],
			su[500],
			su[300],
			su[100]
		],
		[
			cu[900],
			cu[700],
			cu[500],
			cu[300],
			cu[100]
		],
		[
			lu[900],
			lu[700],
			lu[500],
			lu[300],
			lu[100]
		],
		[
			uu[900],
			uu[700],
			uu[500],
			uu[300],
			uu[100]
		],
		[
			du[900],
			du[700],
			du[500],
			du[300],
			du[100]
		],
		[
			fu[900],
			fu[700],
			fu[500],
			fu[300],
			fu[100]
		],
		[
			pu[900],
			pu[700],
			pu[500],
			pu[300],
			pu[100]
		],
		[
			mu[900],
			mu[700],
			mu[500],
			mu[300],
			mu[100]
		],
		[
			hu[900],
			hu[700],
			hu[500],
			hu[300],
			hu[100]
		],
		[
			"#000000",
			"#525252",
			"#969696",
			"#D9D9D9",
			"#FFFFFF"
		]
	],
	styles: {}
}, Q(fd);
var pd = function(e) {
	var t = e.onChange, n = e.onSwatchHover, r = e.hex, i = e.colors, a = e.width, o = e.triangle, s = e.styles, c = s === void 0 ? {} : s, l = e.className, u = l === void 0 ? "" : l, d = k(W({
		default: {
			card: {
				width: a,
				background: "#fff",
				border: "0 solid rgba(0,0,0,0.25)",
				boxShadow: "0 1px 4px rgba(0,0,0,0.25)",
				borderRadius: "4px",
				position: "relative"
			},
			body: { padding: "15px 9px 9px 15px" },
			label: {
				fontSize: "18px",
				color: "#fff"
			},
			triangle: {
				width: "0px",
				height: "0px",
				borderStyle: "solid",
				borderWidth: "0 9px 10px 9px",
				borderColor: "transparent transparent #fff transparent",
				position: "absolute"
			},
			triangleShadow: {
				width: "0px",
				height: "0px",
				borderStyle: "solid",
				borderWidth: "0 9px 10px 9px",
				borderColor: "transparent transparent rgba(0,0,0,.1) transparent",
				position: "absolute"
			},
			hash: {
				background: "#F0F0F0",
				height: "30px",
				width: "30px",
				borderRadius: "4px 0 0 4px",
				float: "left",
				color: "#98A1A4",
				display: "flex",
				alignItems: "center",
				justifyContent: "center"
			},
			input: {
				width: "100px",
				fontSize: "14px",
				color: "#666",
				border: "0px",
				outline: "none",
				height: "28px",
				boxShadow: "inset 0 0 0 1px #F0F0F0",
				boxSizing: "content-box",
				borderRadius: "0 4px 4px 0",
				float: "left",
				paddingLeft: "8px"
			},
			swatch: {
				width: "30px",
				height: "30px",
				float: "left",
				borderRadius: "4px",
				margin: "0 6px 6px 0"
			},
			clear: { clear: "both" }
		},
		"hide-triangle": {
			triangle: { display: "none" },
			triangleShadow: { display: "none" }
		},
		"top-left-triangle": {
			triangle: {
				top: "-10px",
				left: "12px"
			},
			triangleShadow: {
				top: "-11px",
				left: "12px"
			}
		},
		"top-right-triangle": {
			triangle: {
				top: "-10px",
				right: "12px"
			},
			triangleShadow: {
				top: "-11px",
				right: "12px"
			}
		}
	}, c), {
		"hide-triangle": o === "hide",
		"top-left-triangle": o === "top-left",
		"top-right-triangle": o === "top-right"
	}), f = function(e, n) {
		Z(e) && t({
			hex: e,
			source: "hex"
		}, n);
	};
	return T.createElement("div", {
		style: d.card,
		className: "twitter-picker " + u
	}, T.createElement("div", { style: d.triangleShadow }), T.createElement("div", { style: d.triangle }), T.createElement("div", { style: d.body }, Yl(i, function(e, t) {
		return T.createElement(nc, {
			key: t,
			color: e,
			hex: e,
			style: d.swatch,
			onClick: f,
			onHover: n,
			focusStyle: { boxShadow: "0 0 4px " + e }
		});
	}), T.createElement("div", { style: d.hash }, "#"), T.createElement(A, {
		label: null,
		style: { input: d.input },
		value: r.replace("#", ""),
		onChange: f
	}), T.createElement("div", { style: d.clear })));
};
pd.propTypes = {
	width: a.oneOfType([a.string, a.number]),
	triangle: a.oneOf([
		"hide",
		"top-left",
		"top-right"
	]),
	colors: a.arrayOf(a.string),
	styles: a.object
}, pd.defaultProps = {
	width: 276,
	colors: [
		"#FF6900",
		"#FCB900",
		"#7BDCB5",
		"#00D084",
		"#8ED1FC",
		"#0693E3",
		"#ABB8C3",
		"#EB144C",
		"#F78DA7",
		"#9900EF"
	],
	triangle: "top-left",
	styles: {}
}, Q(pd);
var md = function(e) {
	var t = k({ default: { picker: {
		width: "20px",
		height: "20px",
		borderRadius: "22px",
		border: "2px #fff solid",
		transform: "translate(-12px, -13px)",
		background: "hsl(" + Math.round(e.hsl.h) + ", " + Math.round(e.hsl.s * 100) + "%, " + Math.round(e.hsl.l * 100) + "%)"
	} } });
	return T.createElement("div", { style: t.picker });
};
md.propTypes = { hsl: a.shape({
	h: a.number,
	s: a.number,
	l: a.number,
	a: a.number
}) }, md.defaultProps = { hsl: {
	a: 1,
	h: 249.94,
	l: .2,
	s: .5
} };
var hd = function(e) {
	var t = k({ default: { picker: {
		width: "20px",
		height: "20px",
		borderRadius: "22px",
		transform: "translate(-10px, -7px)",
		background: "hsl(" + Math.round(e.hsl.h) + ", 100%, 50%)",
		border: "2px white solid"
	} } });
	return T.createElement("div", { style: t.picker });
};
hd.propTypes = { hsl: a.shape({
	h: a.number,
	s: a.number,
	l: a.number,
	a: a.number
}) }, hd.defaultProps = { hsl: {
	a: 1,
	h: 249.94,
	l: .2,
	s: .5
} };
var gd = function(e) {
	var t = e.onChange, n = e.rgb, r = e.hsl, i = e.hex, a = e.hsv, o = function(e, n) {
		if (e.hex) Z(e.hex) && t({
			hex: e.hex,
			source: "hex"
		}, n);
		else if (e.rgb) {
			var r = e.rgb.split(",");
			Hs(e.rgb, "rgb") && t({
				r: r[0],
				g: r[1],
				b: r[2],
				a: 1,
				source: "rgb"
			}, n);
		} else if (e.hsv) {
			var i = e.hsv.split(",");
			Hs(e.hsv, "hsv") && (i[2] = i[2].replace("%", ""), i[1] = i[1].replace("%", ""), i[0] = i[0].replace("°", ""), i[1] == 1 ? i[1] = .01 : i[2] == 1 && (i[2] = .01), t({
				h: Number(i[0]),
				s: Number(i[1]),
				v: Number(i[2]),
				source: "hsv"
			}, n));
		} else if (e.hsl) {
			var a = e.hsl.split(",");
			Hs(e.hsl, "hsl") && (a[2] = a[2].replace("%", ""), a[1] = a[1].replace("%", ""), a[0] = a[0].replace("°", ""), u[1] == 1 ? u[1] = .01 : u[2] == 1 && (u[2] = .01), t({
				h: Number(a[0]),
				s: Number(a[1]),
				v: Number(a[2]),
				source: "hsl"
			}, n));
		}
	}, s = k({ default: {
		wrap: {
			display: "flex",
			height: "100px",
			marginTop: "4px"
		},
		fields: { width: "100%" },
		column: {
			paddingTop: "10px",
			display: "flex",
			justifyContent: "space-between"
		},
		double: {
			padding: "0px 4.4px",
			boxSizing: "border-box"
		},
		input: {
			width: "100%",
			height: "38px",
			boxSizing: "border-box",
			padding: "4px 10% 3px",
			textAlign: "center",
			border: "1px solid #dadce0",
			fontSize: "11px",
			textTransform: "lowercase",
			borderRadius: "5px",
			outline: "none",
			fontFamily: "Roboto,Arial,sans-serif"
		},
		input2: {
			height: "38px",
			width: "100%",
			border: "1px solid #dadce0",
			boxSizing: "border-box",
			fontSize: "11px",
			textTransform: "lowercase",
			borderRadius: "5px",
			outline: "none",
			paddingLeft: "10px",
			fontFamily: "Roboto,Arial,sans-serif"
		},
		label: {
			textAlign: "center",
			fontSize: "12px",
			background: "#fff",
			position: "absolute",
			textTransform: "uppercase",
			color: "#3c4043",
			width: "35px",
			top: "-6px",
			left: "0",
			right: "0",
			marginLeft: "auto",
			marginRight: "auto",
			fontFamily: "Roboto,Arial,sans-serif"
		},
		label2: {
			left: "10px",
			textAlign: "center",
			fontSize: "12px",
			background: "#fff",
			position: "absolute",
			textTransform: "uppercase",
			color: "#3c4043",
			width: "32px",
			top: "-6px",
			fontFamily: "Roboto,Arial,sans-serif"
		},
		single: {
			flexGrow: "1",
			margin: "0px 4.4px"
		}
	} }), c = n.r + ", " + n.g + ", " + n.b, l = Math.round(r.h) + "°, " + Math.round(r.s * 100) + "%, " + Math.round(r.l * 100) + "%", u = Math.round(a.h) + "°, " + Math.round(a.s * 100) + "%, " + Math.round(a.v * 100) + "%";
	return T.createElement("div", {
		style: s.wrap,
		className: "flexbox-fix"
	}, T.createElement("div", { style: s.fields }, T.createElement("div", { style: s.double }, T.createElement(A, {
		style: {
			input: s.input,
			label: s.label
		},
		label: "hex",
		value: i,
		onChange: o
	})), T.createElement("div", { style: s.column }, T.createElement("div", { style: s.single }, T.createElement(A, {
		style: {
			input: s.input2,
			label: s.label2
		},
		label: "rgb",
		value: c,
		onChange: o
	})), T.createElement("div", { style: s.single }, T.createElement(A, {
		style: {
			input: s.input2,
			label: s.label2
		},
		label: "hsv",
		value: u,
		onChange: o
	})), T.createElement("div", { style: s.single }, T.createElement(A, {
		style: {
			input: s.input2,
			label: s.label2
		},
		label: "hsl",
		value: l,
		onChange: o
	})))));
}, _d = function(e) {
	var t = e.width, n = e.onChange, r = e.rgb, i = e.hsl, a = e.hsv, o = e.hex, s = e.header, c = e.styles, l = c === void 0 ? {} : c, u = e.className, d = u === void 0 ? "" : u, f = k(W({ default: {
		picker: {
			width: t,
			background: "#fff",
			border: "1px solid #dfe1e5",
			boxSizing: "initial",
			display: "flex",
			flexWrap: "wrap",
			borderRadius: "8px 8px 0px 0px"
		},
		head: {
			height: "57px",
			width: "100%",
			paddingTop: "16px",
			paddingBottom: "16px",
			paddingLeft: "16px",
			fontSize: "20px",
			boxSizing: "border-box",
			fontFamily: "Roboto-Regular,HelveticaNeue,Arial,sans-serif"
		},
		saturation: {
			width: "70%",
			padding: "0px",
			position: "relative",
			overflow: "hidden"
		},
		swatch: {
			width: "30%",
			height: "228px",
			padding: "0px",
			background: "rgba(" + r.r + ", " + r.g + ", " + r.b + ", 1)",
			position: "relative",
			overflow: "hidden"
		},
		body: {
			margin: "auto",
			width: "95%"
		},
		controls: {
			display: "flex",
			boxSizing: "border-box",
			height: "52px",
			paddingTop: "22px"
		},
		color: { width: "32px" },
		hue: {
			height: "8px",
			position: "relative",
			margin: "0px 16px 0px 16px",
			width: "100%"
		},
		Hue: { radius: "2px" }
	} }, l));
	return T.createElement("div", {
		style: f.picker,
		className: "google-picker " + d
	}, T.createElement("div", { style: f.head }, s), T.createElement("div", { style: f.swatch }), T.createElement("div", { style: f.saturation }, T.createElement(Ko, {
		hsl: i,
		hsv: a,
		pointer: md,
		onChange: n
	})), T.createElement("div", { style: f.body }, T.createElement("div", {
		style: f.controls,
		className: "flexbox-fix"
	}, T.createElement("div", { style: f.hue }, T.createElement(mr, {
		style: f.Hue,
		hsl: i,
		radius: "4px",
		pointer: hd,
		onChange: n
	}))), T.createElement(gd, {
		rgb: r,
		hsl: i,
		hex: o,
		hsv: a,
		onChange: n
	})));
};
_d.propTypes = {
	width: a.oneOfType([a.string, a.number]),
	styles: a.object,
	header: a.string
}, _d.defaultProps = {
	width: 652,
	styles: {},
	header: "Color picker"
}, Q(_d);
var vd = /* @__PURE__ */ t("div", { target: "e1rgp0874" })(({ disabled: e, theme: t }) => ({
	fontFamily: t.genericFonts.bodyFont,
	display: "flex",
	flexDirection: "column",
	alignItems: "flex-start",
	cursor: e ? "not-allowed" : "default",
	minWidth: t.sizes.minElementHeight
}), ""), yd = /* @__PURE__ */ t("div", { target: "e1rgp0873" })(({ theme: e }) => ({
	div: { fontFamily: `${e.genericFonts.bodyFont} !important` },
	label: {
		fontSize: `${e.fontSizes.sm} !important`,
		color: `${e.colors.bodyText} !important`
	},
	input: {
		fontSize: `${e.fontSizes.md} !important`,
		height: `${e.sizes.minElementHeight} !important`,
		backgroundColor: `${e.colors.secondaryBg} !important`,
		color: `${e.colors.bodyText} !important`,
		borderRadius: `${e.radii.default} !important`,
		boxShadow: "none !important",
		"&:focus-visible": { outline: `${e.sizes.borderWidth} solid ${e.colors.primary} !important` }
	},
	svg: { fill: `${e.colors.bodyText} !important` }
}), ""), bd = /* @__PURE__ */ t("div", { target: "e1rgp0872" })(({ disabled: e, theme: t }) => ({
	height: t.sizes.minElementHeight,
	borderRadius: t.radii.default,
	borderColor: t.colors.borderColor,
	cursor: e ? "not-allowed" : "pointer",
	pointerEvents: e ? "none" : "auto",
	boxShadow: "none",
	lineHeight: t.lineHeights.base,
	gap: t.spacing.md,
	"&:focus": { outline: "none" },
	display: "flex"
}), ""), xd = /* @__PURE__ */ t("div", { target: "e1rgp0871" })(({ backgroundColor: e, disabled: t, theme: n }) => ({
	width: n.sizes.minElementHeight,
	height: n.sizes.minElementHeight,
	borderRadius: n.radii.default,
	borderColor: n.colors.borderColor,
	borderWidth: n.sizes.borderWidth,
	opacity: t ? "0.4" : "",
	backgroundColor: e,
	borderStyle: "solid",
	cursor: "pointer",
	lineHeight: n.lineHeights.base,
	"&:focus": { outline: "none" }
}), ""), Sd = /* @__PURE__ */ t("div", { target: "e1rgp0870" })({
	name: "s5xdrg",
	styles: "display:flex;align-items:center"
});
Ko.prototype.getContainerRenderWindow = function() {
	let e = this.container, t = window, n = window;
	try {
		for (; !t.document.contains(e) && t.parent !== t;) n = t, t = t.parent;
	} catch {
		t = n;
	}
	return t;
};
var Cd = (0, T.memo)((t) => {
	let { disabled: r, value: i, showValue: a, label: o, labelVisibility: l, onChange: p, help: m } = t, [h, g] = (0, T.useState)(i), _ = u();
	c(() => g(i), [i]);
	let v = (0, T.useCallback)((e) => {
		g(e.hex);
	}, []), y = (0, T.useCallback)(() => {
		p(h);
	}, [p, h]), b = { default: {
		picker: {
			borderRadius: _.radii.default,
			boxShadow: "none",
			backgroundColor: _.colors.bgColor
		},
		saturation: {
			borderRadius: `${_.radii.default} ${_.radii.default} 0 0`,
			userSelect: "none"
		},
		body: { padding: _.spacing.xl }
	} };
	return /* @__PURE__ */ f.jsxs(vd, {
		className: "stColorPicker",
		"data-testid": "stColorPicker",
		disabled: r,
		children: [/* @__PURE__ */ f.jsx(_e, {
			label: o,
			disabled: r,
			labelVisibility: l,
			children: m && /* @__PURE__ */ f.jsx(ve, {
				content: m,
				placement: n.TOP_RIGHT,
				label: o
			})
		}), /* @__PURE__ */ f.jsx(s, {
			onClose: y,
			placement: "bottomLeft",
			popoverMargin: e(_.spacing.twoXS),
			content: () => /* @__PURE__ */ f.jsx(yd, {
				"data-testid": "stColorPickerPopover",
				children: /* @__PURE__ */ f.jsx(Mu, {
					color: h,
					onChange: v,
					disableAlpha: !0,
					styles: b
				})
			}),
			overrides: { Body: { style: d(_) } },
			children: /* @__PURE__ */ f.jsxs(bd, {
				disabled: r,
				children: [/* @__PURE__ */ f.jsx(xd, {
					"data-testid": "stColorPickerBlock",
					backgroundColor: h,
					disabled: r
				}), a && /* @__PURE__ */ f.jsx(Sd, { children: h.toUpperCase() })]
			})
		})]
	});
}), wd = (e, t) => e.getStringValue(t), Td = (e) => e.default ?? "#000000", Ed = (e) => e.value ?? e.default ?? "#000000", Dd = (e, t, n, r) => {
	t.setStringValue(e, n.value, { fromUi: n.fromUi }, r);
}, Od = (0, T.memo)(({ element: e, disabled: t, widgetMgr: n, fragmentId: r }) => {
	let [i, a] = ye({
		getStateFromWidgetMgr: wd,
		getDefaultStateFromProto: Td,
		getCurrStateFromProto: Ed,
		updateWidgetMgrState: Dd,
		element: e,
		widgetMgr: n,
		fragmentId: r,
		formClearBehavior: "resetValueOnly",
		queryParamBinding: e.queryParamKey ? {
			paramKey: e.queryParamKey,
			valueType: "string_value",
			clearable: !1
		} : void 0
	}), o = (0, T.useCallback)((e) => {
		a({
			value: e,
			fromUi: !0
		});
	}, [a]);
	return /* @__PURE__ */ f.jsx(Cd, {
		label: e.label,
		labelVisibility: l(e.labelVisibility?.value),
		help: e.help,
		onChange: o,
		disabled: t,
		value: i
	});
});
//#endregion
export { Od as default };

//# sourceMappingURL=ColorPicker-DFXf_KfZ-CaHU65qn.js.map