import { $i as e, At as t, Ei as n, En as r, Ka as i, Ln as a, Rn as o, Ua as s, Zt as c, dt as l, ha as u, ii as d, jr as f, ma as p, st as m, ti as h, tr as g } from "./index-Dl4ETd_L-D2oMd1k2.js";
import { n as _ } from "./moment-C29_LcvN-Dw52XTOQ.js";
import { t as v } from "./formatNumber-B9NmJPl4-CfTaoV6j.js";
import { t as y } from "./formatMoment-DEtsTHwA-C3SDegV0.js";
import { t as b } from "./WidgetLabel-CQfHGtry-udktvHE5.js";
import { t as x } from "./WidgetLabelHelpIcon-C6IRqJ_I-BBI6AbZ-.js";
import { n as S } from "./useBasicWidgetState-D3zHnRUK-Dsaz4YO6.js";
import { t as C } from "./withCalculatedWidth-DwrWHMUR-BEQsmBif.js";
//#region ../react/build/Slider-DMZ19nRR.js
var w = /* @__PURE__ */ i(s(), 1), T = {}, E = {}, D = {}, O = {}, k;
function A() {
	if (k) return O;
	k = 1, Object.defineProperty(O, "__esModule", { value: !0 }), O.Direction = void 0;
	var e;
	return function(e) {
		e.Right = "to right", e.Left = "to left", e.Down = "to bottom", e.Up = "to top";
	}(e || (O.Direction = e = {})), O;
}
var j;
function M() {
	return j || (j = 1, function(e) {
		var t = D && D.__spreadArray || function(e, t, n) {
			if (n || arguments.length === 2) for (var r = 0, i = t.length, a; r < i; r++) (a || !(r in t)) && (a ||= Array.prototype.slice.call(t, 0, r), a[r] = t[r]);
			return e.concat(a || Array.prototype.slice.call(t));
		};
		Object.defineProperty(e, "__esModule", { value: !0 }), e.isIOS = e.useThumbOverlap = e.assertUnreachable = e.voidFn = e.getTrackBackground = e.replaceAt = e.schd = e.translate = e.getClosestThumbIndex = e.translateThumbs = e.getPaddingAndBorder = e.getMargin = e.checkInitialOverlap = e.checkValuesAgainstBoundaries = e.checkBoundaries = e.isVertical = e.relativeValue = e.normalizeValue = e.isStepDivisible = e.isTouchEvent = e.getStepDecimals = void 0;
		var n = w.default, r = /* @__PURE__ */ A();
		e.getStepDecimals = function(e) {
			var t = e.toString().split(".")[1];
			return t ? t.length : 0;
		};
		function i(e) {
			return e.touches && e.touches.length || e.changedTouches && e.changedTouches.length;
		}
		e.isTouchEvent = i;
		function a(e, t, n) {
			var r = (t - e) / n, i = Number(r.toFixed(8));
			return parseInt(i.toString(), 10) === i;
		}
		e.isStepDivisible = a;
		function o(t, n, r, i, a, o, s) {
			var c = 1e11;
			if (t = Math.round(t * c) / c, !o) {
				var l = s[n - 1], u = s[n + 1];
				if (l && l > t) return l;
				if (u && u < t) return u;
			}
			if (t > i) return i;
			if (t < r) return r;
			var d = Math.floor(t * c - r * c) % Math.floor(a * c), f = Math.floor(t * c - Math.abs(d)), p = d === 0 ? t : f / c, m = Math.abs(d / c) < a / 2 ? p : p + a, h = (0, e.getStepDecimals)(a);
			return parseFloat(m.toFixed(h));
		}
		e.normalizeValue = o;
		function s(e, t, n) {
			return (e - t) / (n - t);
		}
		e.relativeValue = s;
		function c(e) {
			return e === r.Direction.Up || e === r.Direction.Down;
		}
		e.isVertical = c;
		function l(e, t, n) {
			if (t >= n) throw RangeError(`min (${t}) is equal/bigger than max (${n})`);
			if (e < t) throw RangeError(`value (${e}) is smaller than min (${t})`);
			if (e > n) throw RangeError(`value (${e}) is bigger than max (${n})`);
		}
		e.checkBoundaries = l;
		function u(e, t, n) {
			return e < t ? t : e > n ? n : e;
		}
		e.checkValuesAgainstBoundaries = u;
		function d(e) {
			if (!(e.length < 2) && !e.slice(1).every(function(t, n) {
				return e[n] <= t;
			})) throw RangeError(`values={[${e}]} needs to be sorted when allowOverlap={false}`);
		}
		e.checkInitialOverlap = d;
		function f(e) {
			var t = window.getComputedStyle(e);
			return {
				top: parseInt(t["margin-top"], 10),
				bottom: parseInt(t["margin-bottom"], 10),
				left: parseInt(t["margin-left"], 10),
				right: parseInt(t["margin-right"], 10)
			};
		}
		e.getMargin = f;
		function p(e) {
			var t = window.getComputedStyle(e);
			return {
				top: parseInt(t["padding-top"], 10) + parseInt(t["border-top-width"], 10),
				bottom: parseInt(t["padding-bottom"], 10) + parseInt(t["border-bottom-width"], 10),
				left: parseInt(t["padding-left"], 10) + parseInt(t["border-left-width"], 10),
				right: parseInt(t["padding-right"], 10) + parseInt(t["border-right-width"], 10)
			};
		}
		e.getPaddingAndBorder = p;
		function m(e, t, n) {
			var r = n ? -1 : 1;
			e.forEach(function(e, n) {
				return g(e, r * t[n].x, t[n].y);
			});
		}
		e.translateThumbs = m;
		function h(e, t, n, r) {
			for (var i = 0, a = C(e[0], t, n, r), o = 1; o < e.length; o++) {
				var s = C(e[o], t, n, r);
				s < a && (a = s, i = o);
			}
			return i;
		}
		e.getClosestThumbIndex = h;
		function g(e, t, n) {
			e.style.transform = `translate(${t}px, ${n}px)`;
		}
		e.translate = g, e.schd = function(e) {
			var t = [], n = null;
			return function() {
				t = [...arguments], !n && (n = requestAnimationFrame(function() {
					n = null, e.apply(void 0, t);
				}));
			};
		};
		function _(e, t, n) {
			var r = e.slice(0);
			return r[t] = n, r;
		}
		e.replaceAt = _;
		function v(e) {
			var t = e.values, n = e.colors, i = e.min, a = e.max, o = e.direction, s = o === void 0 ? r.Direction.Right : o, c = e.rtl, l = c === void 0 ? !1 : c;
			l && s === r.Direction.Right ? s = r.Direction.Left : l && r.Direction.Left && (s = r.Direction.Right);
			var u = t.slice(0).sort(function(e, t) {
				return e - t;
			}).map(function(e) {
				return (e - i) / (a - i) * 100;
			}).reduce(function(e, t, r) {
				return `${e}, ${n[r]} ${t}%, ${n[r + 1]} ${t}%`;
			}, "");
			return `linear-gradient(${s}, ${n[0]} 0%${u}, ${n[n.length - 1]} 100%)`;
		}
		e.getTrackBackground = v;
		function y() {}
		e.voidFn = y;
		function b(e) {
			throw Error("Didn't expect to get here");
		}
		e.assertUnreachable = b;
		var x = function(e, n, r, i, a) {
			return a === void 0 && (a = function(e) {
				return e;
			}), Math.ceil(t([e], Array.from(e.children), !0).reduce(function(e, t) {
				var o = Math.ceil(t.getBoundingClientRect().width);
				if (t.innerText && t.innerText.includes(r) && t.childElementCount === 0) {
					var s = t.cloneNode(!0);
					s.innerHTML = a(n.toFixed(i)), s.style.visibility = "hidden", document.body.appendChild(s), o = Math.ceil(s.getBoundingClientRect().width), document.body.removeChild(s);
				}
				return o > e ? o : e;
			}, e.getBoundingClientRect().width));
		}, S = function(e, n, r, i, a, o, s) {
			s === void 0 && (s = function(e) {
				return e;
			});
			var c = [], l = function(e) {
				var u = x(r[e], i[e], a, o, s), d = n[e].x;
				n.forEach(function(n, f) {
					var p = n.x, m = x(r[f], i[f], a, o, s);
					e !== f && (d >= p && d <= p + m || d + u >= p && d + u <= p + m) && (c.includes(f) || (c.push(e), c.push(f), c = t(t([], c, !0), [e, f], !1), l(f)));
				});
			};
			return l(e), Array.from(new Set(c.sort()));
		};
		e.useThumbOverlap = function(r, i, a, o, s, c) {
			o === void 0 && (o = .1), s === void 0 && (s = " - "), c === void 0 && (c = function(e) {
				return e;
			});
			var l = (0, e.getStepDecimals)(o), u = (0, n.useState)({}), d = u[0], f = u[1], p = (0, n.useState)(c(i[a].toFixed(l))), m = p[0], h = p[1];
			return (0, n.useEffect)(function() {
				if (r) {
					var e = r.getThumbs();
					if (e.length < 1) return;
					var n = {}, o = r.getOffsets(), u = S(a, o, e, i, s, l, c), d = c(i[a].toFixed(l));
					if (u.length) {
						var p = u.reduce(function(e, n, r, i) {
							return e.length ? t(t([], e, !0), [o[i[r]].x], !1) : [o[i[r]].x];
						}, []);
						if (Math.min.apply(Math, p) === o[a].x) {
							var m = [];
							u.forEach(function(e) {
								m.push(i[e].toFixed(l));
							}), d = Array.from(new Set(m.sort(function(e, t) {
								return parseFloat(e) - parseFloat(t);
							}))).map(c).join(s);
							var g = Math.min.apply(Math, p), _ = Math.max.apply(Math, p), v = e[u[p.indexOf(_)]].getBoundingClientRect().width;
							n.left = `${Math.abs(g - (_ + v)) / 2}px`, n.transform = "translate(-50%, 0)";
						} else n.visibility = "hidden";
					}
					h(d), f(n);
				}
			}, [r, i]), [m, d];
		};
		function C(e, t, n, r) {
			var i = e.getBoundingClientRect(), a = i.left, o = i.top, s = i.width, l = i.height;
			return c(r) ? Math.abs(n - (o + l / 2)) : Math.abs(t - (a + s / 2));
		}
		e.isIOS = function() {
			var e = navigator.userAgentData?.platform || navigator.platform;
			return [
				"iPad Simulator",
				"iPhone Simulator",
				"iPod Simulator",
				"iPad",
				"iPhone",
				"iPod"
			].includes(e) || navigator.userAgent.includes("Mac") && "ontouchend" in document;
		};
	}(D)), D;
}
var N;
function ee() {
	if (N) return E;
	N = 1;
	var e = E && E.__extends || /* @__PURE__ */ function() {
		var e = function(t, n) {
			return e = Object.setPrototypeOf || { __proto__: [] } instanceof Array && function(e, t) {
				e.__proto__ = t;
			} || function(e, t) {
				for (var n in t) Object.prototype.hasOwnProperty.call(t, n) && (e[n] = t[n]);
			}, e(t, n);
		};
		return function(t, n) {
			if (typeof n != "function" && n !== null) throw TypeError("Class extends value " + String(n) + " is not a constructor or null");
			e(t, n);
			function r() {
				this.constructor = t;
			}
			t.prototype = n === null ? Object.create(n) : (r.prototype = n.prototype, new r());
		};
	}(), t = E && E.__createBinding || (Object.create ? function(e, t, n, r) {
		r === void 0 && (r = n);
		var i = Object.getOwnPropertyDescriptor(t, n);
		(!i || ("get" in i ? !t.__esModule : i.writable || i.configurable)) && (i = {
			enumerable: !0,
			get: function() {
				return t[n];
			}
		}), Object.defineProperty(e, r, i);
	} : function(e, t, n, r) {
		r === void 0 && (r = n), e[r] = t[n];
	}), n = E && E.__setModuleDefault || (Object.create ? function(e, t) {
		Object.defineProperty(e, "default", {
			enumerable: !0,
			value: t
		});
	} : function(e, t) {
		e.default = t;
	}), r = E && E.__importStar || function(e) {
		if (e && e.__esModule) return e;
		var r = {};
		if (e != null) for (var i in e) i !== "default" && Object.prototype.hasOwnProperty.call(e, i) && t(r, e, i);
		return n(r, e), r;
	}, i = E && E.__spreadArray || function(e, t, n) {
		if (n || arguments.length === 2) for (var r = 0, i = t.length, a; r < i; r++) (a || !(r in t)) && (a ||= Array.prototype.slice.call(t, 0, r), a[r] = t[r]);
		return e.concat(a || Array.prototype.slice.call(t));
	};
	Object.defineProperty(E, "__esModule", { value: !0 });
	var a = r(w.default), o = /* @__PURE__ */ M(), s = /* @__PURE__ */ A(), c = [
		"ArrowRight",
		"ArrowUp",
		"k",
		"PageUp"
	], l = [
		"ArrowLeft",
		"ArrowDown",
		"j",
		"PageDown"
	];
	return E.default = function(t) {
		e(n, t);
		function n(e) {
			var n = t.call(this, e) || this;
			if (n.trackRef = a.createRef(), n.thumbRefs = [], n.state = {
				draggedTrackPos: [-1, -1],
				draggedThumbIndex: -1,
				thumbZIndexes: Array(n.props.values.length).fill(0).map(function(e, t) {
					return t;
				}),
				isChanged: !1,
				markOffsets: []
			}, n.getOffsets = function() {
				var e = n.props, t = e.direction, r = e.values, i = e.min, a = e.max, c = n.trackRef.current;
				if (!c) return console.warn("No track element found."), [];
				var l = c.getBoundingClientRect(), u = (0, o.getPaddingAndBorder)(c);
				return n.getThumbs().map(function(e, n) {
					var c = {
						x: 0,
						y: 0
					}, d = e.getBoundingClientRect(), f = (0, o.getMargin)(e);
					switch (t) {
						case s.Direction.Right: return c.x = (f.left + u.left) * -1, c.y = ((d.height - l.height) / 2 + u.top) * -1, c.x += l.width * (0, o.relativeValue)(r[n], i, a) - d.width / 2, c;
						case s.Direction.Left: return c.x = (f.right + u.right) * -1, c.y = ((d.height - l.height) / 2 + u.top) * -1, c.x += l.width - l.width * (0, o.relativeValue)(r[n], i, a) - d.width / 2, c;
						case s.Direction.Up: return c.x = ((d.width - l.width) / 2 + f.left + u.left) * -1, c.y = -u.left, c.y += l.height - l.height * (0, o.relativeValue)(r[n], i, a) - d.height / 2, c;
						case s.Direction.Down: return c.x = ((d.width - l.width) / 2 + f.left + u.left) * -1, c.y = -u.left, c.y += l.height * (0, o.relativeValue)(r[n], i, a) - d.height / 2, c;
						default: return (0, o.assertUnreachable)(t);
					}
				});
			}, n.getThumbs = function() {
				return n.trackRef && n.trackRef.current ? Array.from(n.trackRef.current.children).filter(function(e) {
					return e.hasAttribute("aria-valuenow");
				}) : (console.warn("No thumbs found in the track container. Did you forget to pass & spread the `props` param in renderTrack?"), []);
			}, n.getTargetIndex = function(e) {
				return n.getThumbs().findIndex(function(t) {
					return t === e.target || t.contains(e.target);
				});
			}, n.addTouchEvents = function(e) {
				document.addEventListener("touchmove", n.schdOnTouchMove, { passive: !1 }), document.addEventListener("touchend", n.schdOnEnd, { passive: !1 }), document.addEventListener("touchcancel", n.schdOnEnd, { passive: !1 });
			}, n.addMouseEvents = function(e) {
				document.addEventListener("mousemove", n.schdOnMouseMove), document.addEventListener("mouseup", n.schdOnEnd);
			}, n.onMouseDownTrack = function(e) {
				var t;
				if (!(e.button !== 0 || (0, o.isIOS)())) if (e.persist(), e.preventDefault(), n.addMouseEvents(e.nativeEvent), n.props.values.length > 1 && n.props.draggableTrack) {
					if (n.thumbRefs.some(function(t) {
						return t.current?.contains(e.target);
					})) return;
					n.setState({ draggedTrackPos: [e.clientX, e.clientY] }, function() {
						return n.onMove(e.clientX, e.clientY);
					});
				} else {
					var r = (0, o.getClosestThumbIndex)(n.thumbRefs.map(function(e) {
						return e.current;
					}), e.clientX, e.clientY, n.props.direction);
					(t = n.thumbRefs[r].current) == null || t.focus(), n.setState({ draggedThumbIndex: r }, function() {
						return n.onMove(e.clientX, e.clientY);
					});
				}
			}, n.onResize = function() {
				(0, o.translateThumbs)(n.getThumbs(), n.getOffsets(), n.props.rtl), n.calculateMarkOffsets();
			}, n.onTouchStartTrack = function(e) {
				var t;
				if (e.persist(), n.addTouchEvents(e.nativeEvent), n.props.values.length > 1 && n.props.draggableTrack) {
					if (n.thumbRefs.some(function(t) {
						return t.current?.contains(e.target);
					})) return;
					n.setState({ draggedTrackPos: [e.touches[0].clientX, e.touches[0].clientY] }, function() {
						return n.onMove(e.touches[0].clientX, e.touches[0].clientY);
					});
				} else {
					var r = (0, o.getClosestThumbIndex)(n.thumbRefs.map(function(e) {
						return e.current;
					}), e.touches[0].clientX, e.touches[0].clientY, n.props.direction);
					(t = n.thumbRefs[r].current) == null || t.focus(), n.setState({ draggedThumbIndex: r }, function() {
						return n.onMove(e.touches[0].clientX, e.touches[0].clientY);
					});
				}
			}, n.onMouseOrTouchStart = function(e) {
				if (!n.props.disabled) {
					var t = (0, o.isTouchEvent)(e);
					if (!(!t && e.button !== 0)) {
						var r = n.getTargetIndex(e);
						r !== -1 && (t ? n.addTouchEvents(e) : n.addMouseEvents(e), n.setState({
							draggedThumbIndex: r,
							thumbZIndexes: n.state.thumbZIndexes.map(function(e, t) {
								return t === r ? Math.max.apply(Math, n.state.thumbZIndexes) : e <= n.state.thumbZIndexes[r] ? e : e - 1;
							})
						}));
					}
				}
			}, n.onMouseMove = function(e) {
				e.preventDefault(), n.onMove(e.clientX, e.clientY);
			}, n.onTouchMove = function(e) {
				e.preventDefault(), n.onMove(e.touches[0].clientX, e.touches[0].clientY);
			}, n.onKeyDown = function(e) {
				var t = n.props, r = t.values, i = t.onChange, a = t.step, u = t.rtl, d = t.direction, f = n.state.isChanged, p = n.getTargetIndex(e.nativeEvent), m = u || d === s.Direction.Left || d === s.Direction.Down ? -1 : 1;
				p !== -1 && (c.includes(e.key) ? (e.preventDefault(), n.setState({
					draggedThumbIndex: p,
					isChanged: !0
				}), i((0, o.replaceAt)(r, p, n.normalizeValue(r[p] + m * (e.key === "PageUp" ? a * 10 : a), p)))) : l.includes(e.key) ? (e.preventDefault(), n.setState({
					draggedThumbIndex: p,
					isChanged: !0
				}), i((0, o.replaceAt)(r, p, n.normalizeValue(r[p] - m * (e.key === "PageDown" ? a * 10 : a), p)))) : e.key === "Tab" ? n.setState({ draggedThumbIndex: -1 }, function() {
					f && n.fireOnFinalChange();
				}) : f && n.fireOnFinalChange());
			}, n.onKeyUp = function(e) {
				var t = n.state.isChanged;
				n.setState({ draggedThumbIndex: -1 }, function() {
					t && n.fireOnFinalChange();
				});
			}, n.onMove = function(e, t) {
				var r = n.state, i = r.draggedThumbIndex, a = r.draggedTrackPos, c = n.props, l = c.direction, u = c.min, d = c.max, f = c.onChange, p = c.values, m = c.step, h = c.rtl;
				if (i === -1 && a[0] === -1 && a[1] === -1) return null;
				var g = n.trackRef.current;
				if (!g) return null;
				var _ = g.getBoundingClientRect(), v = (0, o.isVertical)(l) ? _.height : _.width;
				if (a[0] !== -1 && a[1] !== -1) {
					var y = e - a[0], b = t - a[1], x = 0;
					switch (l) {
						case s.Direction.Right:
						case s.Direction.Left:
							x = y / v * (d - u);
							break;
						case s.Direction.Down:
						case s.Direction.Up:
							x = b / v * (d - u);
							break;
						default: (0, o.assertUnreachable)(l);
					}
					if (h && (x *= -1), Math.abs(x) >= m / 2) {
						for (var S = 0; S < n.thumbRefs.length; S++) {
							if (p[S] === d && Math.sign(x) === 1 || p[S] === u && Math.sign(x) === -1) return;
							var C = p[S] + x;
							C > d ? x = d - p[S] : C < u && (x = u - p[S]);
						}
						for (var w = p.slice(0), S = 0; S < n.thumbRefs.length; S++) w = (0, o.replaceAt)(w, S, n.normalizeValue(p[S] + x, S));
						n.setState({ draggedTrackPos: [e, t] }), f(w);
					}
				} else {
					var T = 0;
					switch (l) {
						case s.Direction.Right:
							T = (e - _.left) / v * (d - u) + u;
							break;
						case s.Direction.Left:
							T = (v - (e - _.left)) / v * (d - u) + u;
							break;
						case s.Direction.Down:
							T = (t - _.top) / v * (d - u) + u;
							break;
						case s.Direction.Up:
							T = (v - (t - _.top)) / v * (d - u) + u;
							break;
						default: (0, o.assertUnreachable)(l);
					}
					h && (T = d + u - T), Math.abs(p[i] - T) >= m / 2 && f((0, o.replaceAt)(p, i, n.normalizeValue(T, i)));
				}
			}, n.normalizeValue = function(e, t) {
				var r = n.props, i = r.min, a = r.max, s = r.step, c = r.allowOverlap, l = r.values;
				return (0, o.normalizeValue)(e, t, i, a, s, c, l);
			}, n.onEnd = function(e) {
				if (e.preventDefault(), document.removeEventListener("mousemove", n.schdOnMouseMove), document.removeEventListener("touchmove", n.schdOnTouchMove), document.removeEventListener("mouseup", n.schdOnEnd), document.removeEventListener("touchend", n.schdOnEnd), document.removeEventListener("touchcancel", n.schdOnEnd), n.state.draggedThumbIndex === -1 && n.state.draggedTrackPos[0] === -1 && n.state.draggedTrackPos[1] === -1) return null;
				n.setState({
					draggedThumbIndex: -1,
					draggedTrackPos: [-1, -1]
				}, function() {
					n.fireOnFinalChange();
				});
			}, n.fireOnFinalChange = function() {
				n.setState({ isChanged: !1 });
				var e = n.props, t = e.onFinalChange, r = e.values;
				t && t(r);
			}, n.updateMarkRefs = function(e) {
				if (!e.renderMark) {
					n.numOfMarks = void 0, n.markRefs = void 0;
					return;
				}
				n.numOfMarks = (e.max - e.min) / n.props.step, n.markRefs = [];
				for (var t = 0; t < n.numOfMarks + 1; t++) n.markRefs[t] = a.createRef();
			}, n.calculateMarkOffsets = function() {
				if (!(!n.props.renderMark || !n.trackRef || !n.numOfMarks || !n.markRefs || n.trackRef.current === null)) {
					for (var e = window.getComputedStyle(n.trackRef.current), t = parseInt(e.width, 10), r = parseInt(e.height, 10), i = parseInt(e.paddingLeft, 10), a = parseInt(e.paddingTop, 10), o = [], c = 0; c < n.numOfMarks + 1; c++) {
						var l = 9999, u = 9999;
						if (n.markRefs[c].current) {
							var d = n.markRefs[c].current.getBoundingClientRect();
							l = d.height, u = d.width;
						}
						n.props.direction === s.Direction.Left || n.props.direction === s.Direction.Right ? o.push([Math.round(t / n.numOfMarks * c + i - u / 2), -Math.round((l - r) / 2)]) : o.push([Math.round(r / n.numOfMarks * c + a - l / 2), -Math.round((u - t) / 2)]);
					}
					n.setState({ markOffsets: o });
				}
			}, e.step === 0) throw Error("\"step\" property should be a positive number");
			return n.schdOnMouseMove = (0, o.schd)(n.onMouseMove), n.schdOnTouchMove = (0, o.schd)(n.onTouchMove), n.schdOnEnd = (0, o.schd)(n.onEnd), n.thumbRefs = e.values.map(function() {
				return a.createRef();
			}), n.updateMarkRefs(e), n;
		}
		return n.prototype.componentDidMount = function() {
			var e = this, t = this.props, n = t.values, r = t.min, i = t.step;
			this.resizeObserver = window.ResizeObserver ? new window.ResizeObserver(this.onResize) : {
				observe: function() {
					return window.addEventListener("resize", e.onResize);
				},
				unobserve: function() {
					return window.removeEventListener("resize", e.onResize);
				}
			}, document.addEventListener("touchstart", this.onMouseOrTouchStart, { passive: !1 }), document.addEventListener("mousedown", this.onMouseOrTouchStart, { passive: !1 }), !this.props.allowOverlap && (0, o.checkInitialOverlap)(this.props.values), this.props.values.forEach(function(t) {
				return (0, o.checkBoundaries)(t, e.props.min, e.props.max);
			}), this.resizeObserver.observe(this.trackRef.current), (0, o.translateThumbs)(this.getThumbs(), this.getOffsets(), this.props.rtl), this.calculateMarkOffsets(), n.forEach(function(e) {
				(0, o.isStepDivisible)(r, e, i) || console.warn("The `values` property is in conflict with the current `step`, `min`, and `max` properties. Please provide values that are accessible using the min, max, and step values.");
			});
		}, n.prototype.componentDidUpdate = function(e, t) {
			var n = this.props, r = n.max, i = n.min, a = n.step, s = n.values, c = n.rtl;
			(e.max !== r || e.min !== i || e.step !== a) && this.updateMarkRefs(this.props), (0, o.translateThumbs)(this.getThumbs(), this.getOffsets(), c), (e.max !== r || e.min !== i || e.step !== a || t.markOffsets.length !== this.state.markOffsets.length) && (this.calculateMarkOffsets(), s.forEach(function(e) {
				(0, o.isStepDivisible)(i, e, a) || console.warn("The `values` property is in conflict with the current `step`, `min`, and `max` properties. Please provide values that are accessible using the min, max, and step values.");
			}));
		}, n.prototype.componentWillUnmount = function() {
			document.removeEventListener("mousedown", this.onMouseOrTouchStart, { passive: !1 }), document.removeEventListener("mousemove", this.schdOnMouseMove), document.removeEventListener("touchmove", this.schdOnTouchMove), document.removeEventListener("touchstart", this.onMouseOrTouchStart), document.removeEventListener("mouseup", this.schdOnEnd), document.removeEventListener("touchend", this.schdOnEnd), this.resizeObserver.unobserve(this.trackRef.current);
		}, n.prototype.render = function() {
			var e = this, t = this.props, n = t.label, r = t.labelledBy, a = t.renderTrack, c = t.renderThumb, l = t.renderMark, u = l === void 0 ? function() {
				return null;
			} : l, d = t.values, f = t.min, p = t.max, m = t.allowOverlap, h = t.disabled, g = this.state, _ = g.draggedThumbIndex, v = g.thumbZIndexes, y = g.markOffsets;
			return a({
				props: {
					style: {
						transform: "scale(1)",
						cursor: _ > -1 ? "grabbing" : this.props.draggableTrack ? (0, o.isVertical)(this.props.direction) ? "ns-resize" : "ew-resize" : d.length === 1 && !h ? "pointer" : "inherit"
					},
					onMouseDown: h ? o.voidFn : this.onMouseDownTrack,
					onTouchStart: h ? o.voidFn : this.onTouchStartTrack,
					ref: this.trackRef
				},
				isDragged: this.state.draggedThumbIndex > -1,
				disabled: h,
				children: i(i([], y.map(function(t, n, r) {
					return u({
						props: {
							style: e.props.direction === s.Direction.Left || e.props.direction === s.Direction.Right ? {
								position: "absolute",
								left: `${t[0]}px`,
								marginTop: `${t[1]}px`
							} : {
								position: "absolute",
								top: `${t[0]}px`,
								marginLeft: `${t[1]}px`
							},
							key: `mark${n}`,
							ref: e.markRefs[n]
						},
						index: n
					});
				}), !0), d.map(function(t, i) {
					var a = e.state.draggedThumbIndex === i;
					return c({
						index: i,
						value: t,
						isDragged: a,
						props: {
							style: {
								position: "absolute",
								zIndex: v[i],
								cursor: h ? "inherit" : a ? "grabbing" : "grab",
								userSelect: "none",
								touchAction: "none",
								WebkitUserSelect: "none",
								MozUserSelect: "none",
								msUserSelect: "none"
							},
							key: i,
							tabIndex: h ? void 0 : 0,
							"aria-valuemax": m ? p : d[i + 1] || p,
							"aria-valuemin": m ? f : d[i - 1] || f,
							"aria-valuenow": t,
							draggable: !1,
							ref: e.thumbRefs[i],
							"aria-label": n,
							"aria-labelledby": r,
							role: "slider",
							onKeyDown: h ? o.voidFn : e.onKeyDown,
							onKeyUp: h ? o.voidFn : e.onKeyUp
						}
					});
				}), !0)
			});
		}, n.defaultProps = {
			label: "Accessibility label",
			labelledBy: null,
			step: 1,
			direction: s.Direction.Right,
			rtl: !1,
			disabled: !1,
			allowOverlap: !1,
			draggableTrack: !1,
			min: 0,
			max: 100
		}, n;
	}(a.Component), E;
}
var P;
function F() {
	return P || (P = 1, function(e) {
		var t = T && T.__importDefault || function(e) {
			return e && e.__esModule ? e : { default: e };
		};
		Object.defineProperty(e, "__esModule", { value: !0 }), e.checkValuesAgainstBoundaries = e.relativeValue = e.useThumbOverlap = e.Direction = e.getTrackBackground = e.Range = void 0, e.Range = t(/* @__PURE__ */ ee()).default;
		var n = /* @__PURE__ */ M();
		Object.defineProperty(e, "getTrackBackground", {
			enumerable: !0,
			get: function() {
				return n.getTrackBackground;
			}
		}), Object.defineProperty(e, "useThumbOverlap", {
			enumerable: !0,
			get: function() {
				return n.useThumbOverlap;
			}
		}), Object.defineProperty(e, "relativeValue", {
			enumerable: !0,
			get: function() {
				return n.relativeValue;
			}
		}), Object.defineProperty(e, "checkValuesAgainstBoundaries", {
			enumerable: !0,
			get: function() {
				return n.checkValuesAgainstBoundaries;
			}
		});
		var r = /* @__PURE__ */ A();
		Object.defineProperty(e, "Direction", {
			enumerable: !0,
			get: function() {
				return r.Direction;
			}
		});
	}(T)), T;
}
var te = /* @__PURE__ */ F();
function I(e, t) {
	var n = Object.keys(e);
	if (Object.getOwnPropertySymbols) {
		var r = Object.getOwnPropertySymbols(e);
		t && (r = r.filter(function(t) {
			return Object.getOwnPropertyDescriptor(e, t).enumerable;
		})), n.push.apply(n, r);
	}
	return n;
}
function L(e) {
	for (var t = 1; t < arguments.length; t++) {
		var n = arguments[t] == null ? {} : arguments[t];
		t % 2 ? I(Object(n), !0).forEach(function(t) {
			ne(e, t, n[t]);
		}) : Object.getOwnPropertyDescriptors ? Object.defineProperties(e, Object.getOwnPropertyDescriptors(n)) : I(Object(n)).forEach(function(t) {
			Object.defineProperty(e, t, Object.getOwnPropertyDescriptor(n, t));
		});
	}
	return e;
}
function ne(e, t, n) {
	return t in e ? Object.defineProperty(e, t, {
		value: n,
		enumerable: !0,
		configurable: !0,
		writable: !0
	}) : e[t] = n, e;
}
var re = e("div", {
	position: "relative",
	width: "100%"
});
re.displayName = "Root", re.displayName = "Root", re.displayName = "StyledRoot";
var ie = e("div", function(e) {
	var t = e.$theme, n = e.$value, r = n === void 0 ? [] : n, i = e.$disabled, a = e.$isDragged, o = t.sizing, s = "inherit";
	return i ? s = "not-allowed" : a ? s = "grabbing" : r.length === 1 && (s = "pointer"), {
		paddingTop: o.scale600,
		paddingBottom: o.scale600,
		paddingRight: o.scale600,
		paddingLeft: o.scale600,
		display: "flex",
		cursor: s,
		backgroundColor: t.colors.sliderTrackFill
	};
});
ie.displayName = "Track", ie.displayName = "Track", ie.displayName = "StyledTrack";
var R = e("div", function(e) {
	var t = e.$theme, n = e.$value, r = n === void 0 ? [] : n, i = e.$min, a = e.$max, o = e.$disabled, s = t.colors, c = t.borders, l = t.direction, u = t.borders.useRoundedCorners ? c.radius100 : 0;
	return {
		borderTopLeftRadius: u,
		borderTopRightRadius: u,
		borderBottomRightRadius: u,
		borderBottomLeftRadius: u,
		background: te.getTrackBackground({
			values: r,
			colors: r.length === 1 ? [o ? s.borderOpaque : s.primary, o ? s.backgroundSecondary : s.borderOpaque] : [
				o ? s.backgroundSecondary : s.borderOpaque,
				o ? s.borderOpaque : s.primary,
				o ? s.backgroundSecondary : s.borderOpaque
			],
			min: i || 0,
			max: a || 0,
			rtl: l === "rtl"
		}),
		height: "2px",
		width: "100%",
		alignSelf: "center",
		cursor: o ? "not-allowed" : "inherit"
	};
});
R.displayName = "InnerTrack", R.displayName = "InnerTrack", R.displayName = "StyledInnerTrack";
var ae = e("div", function(e) {
	return {
		width: "4px",
		height: "2px",
		backgroundColor: e.$theme.colors.backgroundPrimary,
		marginLeft: "16px"
	};
});
ae.displayName = "Mark", ae.displayName = "Mark", ae.displayName = "StyledMark";
var z = e("div", function(e) {
	return L(L({}, e.$theme.typography.font200), {}, { color: e.$theme.colors.contentPrimary });
});
z.displayName = "Tick", z.displayName = "Tick", z.displayName = "StyledTick";
var B = e("div", function(e) {
	var t = e.$theme.sizing;
	return {
		display: "flex",
		justifyContent: "space-between",
		alignItems: "center",
		paddingRight: t.scale600,
		paddingLeft: t.scale600,
		paddingBottom: t.scale400
	};
});
B.displayName = "TickBar", B.displayName = "TickBar", B.displayName = "StyledTickBar";
var V = e("div", function(e) {
	var t = e.$theme, n = e.$value, r = n === void 0 ? [] : n, i = e.$thumbIndex, a = e.$disabled, o = r.length === 2 && i === 0, s = r.length === 2 && i === 1;
	return t.direction === "rtl" && (s || o) && (o = !o, s = !s), {
		height: "24px",
		width: "24px",
		borderTopLeftRadius: "24px",
		borderTopRightRadius: "24px",
		borderBottomLeftRadius: "24px",
		borderBottomRightRadius: "24px",
		display: "flex",
		justifyContent: "center",
		alignItems: "center",
		backgroundColor: a ? t.colors.sliderHandleFillDisabled : t.colors.sliderHandleFill,
		outline: "none",
		boxShadow: e.$isFocusVisible ? `0 0 0 3px ${t.colors.accent}` : "0 1px 4px rgba(0, 0, 0, 0.12)",
		cursor: a ? "not-allowed" : "inherit"
	};
});
V.displayName = "Thumb", V.displayName = "Thumb", V.displayName = "StyledThumb";
var H = e("div", function(e) {
	var t = e.$disabled, n = e.$theme;
	return {
		position: "absolute",
		top: "-16px",
		width: "4px",
		height: "20px",
		backgroundColor: t ? n.colors.sliderHandleFillDisabled : n.colors.sliderHandleInnerFill
	};
});
H.displayName = "InnerThumb", H.displayName = "InnerThumb", H.displayName = "StyledInnerThumb";
var U = e("div", function(e) {
	var t = e.$disabled, n = e.$theme;
	return L(L({
		position: "absolute",
		top: `-${n.sizing.scale1400}`
	}, n.typography.font200), {}, {
		backgroundColor: t ? n.colors.sliderHandleFillDisabled : n.colors.sliderHandleInnerFill,
		color: n.colors.contentInversePrimary,
		paddingLeft: n.sizing.scale600,
		paddingRight: n.sizing.scale600,
		paddingTop: n.sizing.scale500,
		paddingBottom: n.sizing.scale500,
		borderBottomLeftRadius: "48px",
		borderBottomRightRadius: "48px",
		borderTopLeftRadius: "48px",
		borderTopRightRadius: "48px",
		whiteSpace: "nowrap"
	});
});
U.displayName = "ThumbValue", U.displayName = "ThumbValue", U.displayName = "StyledThumbValue";
function W(e, t) {
	var n = Object.keys(e);
	if (Object.getOwnPropertySymbols) {
		var r = Object.getOwnPropertySymbols(e);
		t && (r = r.filter(function(t) {
			return Object.getOwnPropertyDescriptor(e, t).enumerable;
		})), n.push.apply(n, r);
	}
	return n;
}
function oe(e) {
	for (var t = 1; t < arguments.length; t++) {
		var n = arguments[t] == null ? {} : arguments[t];
		t % 2 ? W(Object(n), !0).forEach(function(t) {
			se(e, t, n[t]);
		}) : Object.getOwnPropertyDescriptors ? Object.defineProperties(e, Object.getOwnPropertyDescriptors(n)) : W(Object(n)).forEach(function(t) {
			Object.defineProperty(e, t, Object.getOwnPropertyDescriptor(n, t));
		});
	}
	return e;
}
function se(e, t, n) {
	return t in e ? Object.defineProperty(e, t, {
		value: n,
		enumerable: !0,
		configurable: !0,
		writable: !0
	}) : e[t] = n, e;
}
function G() {
	return G = Object.assign ? Object.assign.bind() : function(e) {
		for (var t = 1; t < arguments.length; t++) {
			var n = arguments[t];
			for (var r in n) Object.prototype.hasOwnProperty.call(n, r) && (e[r] = n[r]);
		}
		return e;
	}, G.apply(this, arguments);
}
function K(e, t) {
	return ue(e) || le(e, t) || q(e, t) || ce();
}
function ce() {
	throw TypeError("Invalid attempt to destructure non-iterable instance.\nIn order to be iterable, non-array objects must have a [Symbol.iterator]() method.");
}
function q(e, t) {
	if (e) {
		if (typeof e == "string") return J(e, t);
		var n = Object.prototype.toString.call(e).slice(8, -1);
		if (n === "Object" && e.constructor && (n = e.constructor.name), n === "Map" || n === "Set") return Array.from(e);
		if (n === "Arguments" || /^(?:Ui|I)nt(?:8|16|32)(?:Clamped)?Array$/.test(n)) return J(e, t);
	}
}
function J(e, t) {
	(t == null || t > e.length) && (t = e.length);
	for (var n = 0, r = Array(t); n < t; n++) r[n] = e[n];
	return r;
}
function le(e, t) {
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
function ue(e) {
	if (Array.isArray(e)) return e;
}
var de = function(e) {
	if (e.length > 2 || e.length === 0) throw Error("the value prop represents positions of thumbs, so its length can be only one or two");
	return e;
};
function Y(e) {
	var n = e.overrides, r = n === void 0 ? {} : n, i = e.disabled, s = i === void 0 ? !1 : i, c = e.marks, l = c === void 0 ? !1 : c, u = e.onChange, d = u === void 0 ? function() {} : u, p = e.onFinalChange, m = p === void 0 ? function() {} : p, h = e.min, _ = h === void 0 ? 0 : h, v = e.max, y = v === void 0 ? 100 : v, b = e.step, x = b === void 0 ? 1 : b, S = e.persistentThumb, C = S === void 0 ? !1 : S, T = e.valueToLabel, E = T === void 0 ? function(e) {
		return e;
	} : T, D = e.value, O = w.useContext(t), k = K(w.useState(!1), 2), A = k[0], j = k[1], M = K(w.useState(!1), 2), N = M[0], ee = M[1], P = K(w.useState(!1), 2), F = P[0], I = P[1], L = K(w.useState(-1), 2), ne = L[0], W = L[1], se = w.useCallback(function(e) {
		f(e) && I(!0), W(e.target.parentNode.firstChild === e.target ? 0 : 1);
	}, []), ce = w.useCallback(function(e) {
		F !== !1 && I(!1), W(-1);
	}, []), q = de(D), J = {
		$disabled: s,
		$step: x,
		$min: _,
		$max: y,
		$marks: l,
		$value: q,
		$isFocusVisible: F
	}, le = K(g(r.Root, re), 2), ue = le[0], Y = le[1], fe = K(g(r.Track, ie), 2), pe = fe[0], me = fe[1], he = K(g(r.InnerTrack, R), 2), ge = he[0], _e = he[1], ve = K(g(r.Thumb, V), 2), X = ve[0], Z = ve[1], ye = K(g(r.InnerThumb, H), 2), be = ye[0], xe = ye[1], Se = K(g(r.ThumbValue, U), 2), Ce = Se[0], we = Se[1], Te = K(g(r.Tick, z), 2), Ee = Te[0], Q = Te[1], De = K(g(r.TickBar, B), 2), Oe = De[0], $ = De[1], ke = K(g(r.Mark, ae), 2), Ae = ke[0], je = ke[1];
	return /* @__PURE__ */ w.createElement(ue, G({ "data-baseweb": "slider" }, J, Y, {
		onFocus: o(Y, se),
		onBlur: a(Y, ce)
	}), /* @__PURE__ */ w.createElement(te.Range, G({
		step: x,
		min: _,
		max: y,
		values: q,
		disabled: s,
		onChange: function(e) {
			return d({ value: e });
		},
		onFinalChange: function(e) {
			return m({ value: e });
		},
		rtl: O.direction === "rtl",
		renderTrack: function(e) {
			var t = e.props, n = e.children, r = e.isDragged;
			return /* @__PURE__ */ w.createElement(pe, G({
				onMouseDown: t.onMouseDown,
				onTouchStart: t.onTouchStart,
				$isDragged: r
			}, J, me), /* @__PURE__ */ w.createElement(ge, G({
				$isDragged: r,
				ref: t.ref
			}, J, _e), n));
		},
		renderThumb: function(e) {
			var t = e.props, n = e.index, r = e.isDragged, i = C || (!!n && N || !n && A || r) && !s;
			return /* @__PURE__ */ w.createElement(X, G({}, t, {
				onMouseEnter: function() {
					n === 0 ? j(!0) : ee(!0);
				},
				onMouseLeave: function() {
					n === 0 ? j(!1) : ee(!1);
				},
				$thumbIndex: n,
				$isDragged: r,
				style: oe({}, t.style)
			}, J, Z, { $isFocusVisible: F && ne === n }), i && /* @__PURE__ */ w.createElement(Ce, G({
				$thumbIndex: n,
				$isDragged: r
			}, J, we), E(q[n])), i && /* @__PURE__ */ w.createElement(be, G({
				$thumbIndex: n,
				$isDragged: r
			}, J, xe)));
		}
	}, l ? { renderMark: function(e) {
		var t = e.props, n = e.index;
		return /* @__PURE__ */ w.createElement(Ae, G({ $markIndex: n }, t, J, je));
	} } : {})), /* @__PURE__ */ w.createElement(Oe, G({}, J, $), /* @__PURE__ */ w.createElement(Ee, G({}, J, Q), E(_)), /* @__PURE__ */ w.createElement(Ee, G({}, J, Q), E(y))));
}
var fe = /* @__PURE__ */ r("div", { target: "ew7r33m5" })({
	name: "igqoeg",
	styles: "position:relative;:focus-within:has(:focus-visible){--slider-focused:1;}"
}), pe = /* @__PURE__ */ r("div", { target: "ew7r33m4" })(({ disabled: e, theme: t, isDragged: n }) => ({
	alignItems: "center",
	backgroundColor: e ? t.colors.gray60 : t.colors.primary,
	borderTopLeftRadius: "100%",
	borderTopRightRadius: "100%",
	borderBottomLeftRadius: "100%",
	borderBottomRightRadius: "100%",
	borderTopStyle: "none",
	borderBottomStyle: "none",
	borderRightStyle: "none",
	borderLeftStyle: "none",
	display: "flex",
	justifyContent: "center",
	height: t.sizes.sliderThumb,
	width: t.sizes.sliderThumb,
	boxShadow: n ? t.shadows.focusRing : t.shadows.none,
	":focus": { outline: "none" },
	":focus-visible": { boxShadow: t.shadows.focusRing }
}), ""), me = /* @__PURE__ */ r("div", { target: "ew7r33m3" })(({ disabled: e, theme: t }) => ({
	fontFamily: t.genericFonts.bodyFont,
	fontSize: t.fontSizes.sm,
	color: e ? t.colors.gray60 : t.colors.primary,
	top: "-1.6em",
	position: "absolute",
	whiteSpace: "nowrap",
	backgroundColor: t.colors.transparent,
	lineHeight: t.lineHeights.base,
	fontWeight: t.fontWeights.normal,
	pointerEvents: "none"
}), ""), he = /* @__PURE__ */ r("div", { target: "ew7r33m2" })({
	name: "82a6rk",
	styles: "flex:1"
}), ge = /* @__PURE__ */ r("div", { target: "ew7r33m1" })(({ theme: e }) => ({
	position: "absolute",
	height: e.spacing.twoXS,
	left: `calc(${e.sizes.sliderThumb} / 2)`,
	right: `calc(${e.sizes.sliderThumb} / 2)`
}), ""), _e = /* @__PURE__ */ r("div", { target: "ew7r33m0" })(({ theme: e, isHovered: t, isDisabled: n }) => ({
	position: "absolute",
	left: 0,
	right: 0,
	top: "100%",
	display: "flex",
	justifyContent: "space-between",
	pointerEvents: "none",
	marginTop: `-${e.spacing.md}`,
	fontSize: e.fontSizes.sm,
	lineHeight: e.lineHeights.base,
	fontWeight: e.fontWeights.normal,
	color: n ? e.colors.fadedText40 : e.colors.fadedText60,
	opacity: t ? 1 : "var(--slider-focused, 0)",
	transition: t ? "none" : "opacity 300ms 200ms"
}), "");
function ve({ minLabel: e, maxLabel: t, isHovered: n, isDisabled: r }) {
	return /* @__PURE__ */ h.jsxs(_e, {
		"data-testid": "stSliderTickBar",
		isHovered: n,
		isDisabled: r,
		children: [/* @__PURE__ */ h.jsx(l, {
			source: e,
			allowHTML: !1,
			inheritFont: !0,
			isLabel: !0
		}), /* @__PURE__ */ h.jsx(l, {
			source: t,
			allowHTML: !1,
			inheritFont: !0,
			isLabel: !0
		})]
	});
}
function X(e) {
	return e.type === m.Type.SELECT_SLIDER;
}
function Z(e, t, n) {
	return e.map((e, r) => {
		let i = t.indexOf(e);
		return i >= 0 ? i : n[r] ?? 0;
	});
}
function ye(e, t) {
	return e.map((e) => t[e] ?? "");
}
function be({ disabled: e, element: t, widgetMgr: r, fragmentId: i }) {
	let [a, o] = S({
		getStateFromWidgetMgr: xe,
		getDefaultStateFromProto: Se,
		getCurrStateFromProto: Ce,
		updateWidgetMgrState: we,
		element: t,
		widgetMgr: r,
		fragmentId: i,
		formClearBehavior: "resetValueOnly",
		queryParamBinding: t.queryParamKey ? {
			paramKey: t.queryParamKey,
			valueType: X(t) ? "string_array_value" : "double_array_value",
			clearable: !1,
			urlFormat: "repeated",
			urlDefault: X(t) ? ye(t.default, t.options) : void 0,
			dateType: Te(t) ? Ee(t) : void 0
		} : void 0
	}), [s, f] = (0, w.useState)(a), [m, g] = (0, w.useState)(!1), [_, v] = (0, w.useState)(!1), y = (0, w.useCallback)(() => g(!0), []), C = (0, w.useCallback)(() => g(!1), []), T = (0, w.useRef)(null), [E] = (0, w.useState)([]), [D] = (0, w.useState)([]), O = p(), k = (0, w.useRef)(t);
	k.current = t;
	let A = s.map((e) => Q(e, t)), j = Q(t.min, t), M = Q(t.max, t);
	(0, w.useEffect)(() => {
		f(a);
	}, [a]), u(() => {
		if (!X(t)) return;
		let e = r.getStringArrayValue(t);
		e !== void 0 && f(Z(e, t.options, t.default));
	}, [t.options], (e, t) => c(e[0], t[0]));
	let N = (0, w.useCallback)(({ value: e }) => {
		o({
			value: e,
			fromUi: !0
		}), v(!1);
	}, [o]), ee = (0, w.useCallback)(({ value: e }) => {
		f(e), v(!0);
	}, []), P = (0, w.useCallback)((0, w.forwardRef)(function(e, t) {
		let { $thumbIndex: r, $value: i } = e, a = r || 0;
		E[a] = t, D[a] ||= (0, w.createRef)();
		let o = n(e, [
			"role",
			"style",
			"aria-valuemax",
			"aria-valuemin",
			"aria-valuenow",
			"tabIndex",
			"onKeyUp",
			"onKeyDown",
			"onMouseEnter",
			"onMouseLeave",
			"draggable"
		]), s = k.current, c = Q((i ?? [s.min])[a] ?? s.min, s);
		return /* @__PURE__ */ h.jsx(pe, {
			...o,
			disabled: e.$disabled === !0,
			isDragged: e.$isDragged === !0,
			ref: E[a],
			"aria-valuetext": c,
			"aria-label": s.label,
			children: /* @__PURE__ */ h.jsx(me, {
				"data-testid": "stSliderThumbValue",
				disabled: e.$disabled === !0,
				ref: D[a],
				children: /* @__PURE__ */ h.jsx(l, {
					source: c,
					allowHTML: !1,
					inheritFont: !0,
					isLabel: !0
				})
			})
		});
	}), []);
	(0, w.useLayoutEffect)(() => {
		E.forEach((e, t) => {
			e.current && e.current.setAttribute("aria-valuetext", A[t]);
		});
		let e = T.current ?? null, t = E[0].current, n = E[1]?.current, r = D[0].current, i = D[1]?.current;
		Oe(e, t, n, r, i);
	});
	let F = (0, w.useCallback)(({ $disabled: e }) => ({
		height: O.spacing.twoXS,
		...e ? { background: O.colors.darkenedBgMix25 } : {}
	}), [O.colors.darkenedBgMix25, O.spacing.twoXS]), te = (0, w.useCallback)((0, w.forwardRef)(function(e, t) {
		let { children: n, ...r } = e;
		return /* @__PURE__ */ h.jsxs(he, { children: [/* @__PURE__ */ h.jsx(ge, {
			ref: t,
			children: n
		}), /* @__PURE__ */ h.jsx(R, {
			...r,
			style: F({ $disabled: e.$disabled })
		})] });
	}), []);
	return /* @__PURE__ */ h.jsxs(fe, {
		ref: T,
		className: "stSlider",
		"data-testid": "stSlider",
		onMouseEnter: y,
		onMouseLeave: C,
		children: [/* @__PURE__ */ h.jsx(b, {
			label: t.label,
			disabled: e,
			labelVisibility: d(t.labelVisibility?.value),
			children: t.help && /* @__PURE__ */ h.jsx(x, {
				content: t.help,
				label: t.label
			})
		}), /* @__PURE__ */ h.jsx(Y, {
			min: t.min,
			max: t.max,
			step: t.step,
			value: De(s, t),
			onChange: ee,
			onFinalChange: N,
			disabled: e,
			overrides: {
				Thumb: P,
				Track: { style: {
					backgroundColor: "none !important",
					paddingLeft: O.spacing.none,
					paddingRight: O.spacing.none,
					paddingTop: `calc((${O.sizes.minElementHeight} - ${O.spacing.twoXS}) / 2)`,
					paddingBottom: `calc((${O.sizes.minElementHeight} - ${O.spacing.twoXS}) / 2)`
				} },
				InnerTrack: te,
				TickBar: {
					component: ve,
					props: {
						minLabel: j,
						maxLabel: M,
						isHovered: m || _,
						isDisabled: e
					}
				}
			}
		})]
	});
}
function xe(e, t) {
	if (X(t)) {
		let n = e.getStringArrayValue(t);
		return n === void 0 ? void 0 : Z(n, t.options, t.default);
	}
	return e.getDoubleArrayValue(t);
}
function Se(e) {
	return e.default;
}
function Ce(e) {
	if (X(e)) {
		let t = e.rawValue;
		return t && t.length > 0 ? Z(t, e.options, e.default) : e.default;
	}
	return e.value;
}
function we(e, t, n, r) {
	if (X(e)) {
		let i = ye(n.value, e.options);
		t.setStringArrayValue(e, i, { fromUi: n.fromUi }, r);
	} else t.setDoubleArrayValue(e, n.value, { fromUi: n.fromUi }, r);
}
function Te(e) {
	let { dataType: t } = e;
	return t === m.DataType.DATETIME || t === m.DataType.DATE || t === m.DataType.TIME;
}
function Ee(e) {
	let { dataType: t } = e;
	return t === m.DataType.DATE ? "date" : t === m.DataType.TIME ? "time" : "datetime";
}
function Q(e, t) {
	let { format: n, options: r } = t;
	return r.length > 0 ? r[e] ?? "" : Te(t) ? y(_.utc(e / 1e3), n, Ee(t)) : v(e, n);
}
function De(e, t) {
	let { min: n, max: r } = t, i = e[0], a = e.length > 1 ? e[1] : e[0];
	return i > a && (i = a), i < n && (i = n), i > r && (i = r), a < n && (a = n), a > r && (a = r), e.length > 1 ? [i, a] : [i];
}
function Oe(e, t, n, r, i) {
	!e || !t || !r || ($(e, t, r), n && i && ($(e, n, i), ke(e, t, n, r, i)));
}
function $(e, t, n) {
	let r = e.getBoundingClientRect(), i = t.getBoundingClientRect(), a = n.getBoundingClientRect(), o = i.left + i.width / 2, s = o - a.width / 2 < r.left, c = o + a.width / 2 > r.right;
	n.style.left = s ? "0" : "", n.style.right = c ? "0" : "";
}
function ke(e, t, n, r, i) {
	let a = e.getBoundingClientRect(), o = t.getBoundingClientRect(), s = n.getBoundingClientRect(), c = r.getBoundingClientRect(), l = i.getBoundingClientRect(), u = a.left + a.width / 2, d = o.left + o.width / 2, f = s.left + s.width / 2, p = d - c.width / 2 >= a.left, m = f + l.width / 2 <= a.right, h = o.left - c.width >= a.left, g = s.right + l.width <= a.right, _ = p ? c.width / 2 : c.width, v = m ? l.width / 2 : l.width, y = d + _;
	if (f - v - y > 24) {
		$(e, t, r), $(e, n, i);
		return;
	}
	if (h && g) {
		r.style.left = "", r.style.right = `${Math.round(o.width)}px`, i.style.left = `${Math.round(s.width)}px`, i.style.right = "";
		return;
	}
	d < u ? ($(e, t, r), i.style.left = `${Math.round(d + _ + 24 - f)}px`, i.style.right = "") : ($(e, n, i), r.style.left = "", r.style.right = `${-Math.round(f - v - 24 - d)}px`);
}
var Ae = C((0, w.memo)(be));
//#endregion
export { Ae as default };

//# sourceMappingURL=Slider-DMZ19nRR-thfD0SWh.js.map