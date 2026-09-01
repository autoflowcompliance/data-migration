import { Kn as e } from "./index-Dl4ETd_L-D2oMd1k2.js";
//#region ../react/build/iframeResizer.contentWindow-CaUMNiuy.js
var t = { exports: {} }, n;
function r() {
	return n || (n = 1, function(e) {
		(function(t) {
			if (typeof window > "u") return;
			var n = !0, r = 10, i = "", a = 0, o = "", s = null, c = "", l = !1, u = {
				resize: 1,
				click: 1
			}, d = 128, f = !0, p = 1, m = "bodyOffset", h = m, ee = !0, te = "", g = {}, _ = 32, v = null, y = !1, b = !1, x = "[iFrameSizer]", ne = x.length, S = "", re = {
				max: 1,
				min: 1,
				bodyScroll: 1,
				documentElementScroll: 1
			}, C = "child", w = window.parent, T = "*", E = 0, D = !1, ie = null, O = 16, k = 1, A = "scroll", j = A, ae = window, M = function() {
				V("onMessage function not defined");
			}, N = function() {}, P = function() {}, F = {
				height: function() {
					return V("Custom height calculation function not defined"), document.documentElement.offsetHeight;
				},
				width: function() {
					return V("Custom width calculation function not defined"), document.body.scrollWidth;
				}
			}, I = {}, oe = !1;
			function se() {}
			try {
				var ce = Object.create({}, { passive: { get: function() {
					oe = !0;
				} } });
				window.addEventListener("test", se, ce), window.removeEventListener("test", se, ce);
			} catch {}
			function L(e, t, n, r) {
				e.addEventListener(t, n, oe ? r || {} : !1);
			}
			function le(e, t, n) {
				e.removeEventListener(t, n, !1);
			}
			function R(e) {
				return e.charAt(0).toUpperCase() + e.slice(1);
			}
			function ue(e) {
				var t, n, r, i = null, a = 0, o = function() {
					a = Date.now(), i = null, r = e.apply(t, n), i || (t = n = null);
				};
				return function() {
					var s = Date.now();
					a ||= s;
					var c = O - (s - a);
					return t = this, n = arguments, c <= 0 || c > O ? (i &&= (clearTimeout(i), null), a = s, r = e.apply(t, n), i || (t = n = null)) : i ||= setTimeout(o, c), r;
				};
			}
			function z(e) {
				return x + "[" + S + "] " + e;
			}
			function B(e) {
				y && typeof window.console == "object" && console.log(z(e));
			}
			function V(e) {
				typeof window.console == "object" && console.warn(z(e));
			}
			function de() {
				fe(), B("Initialising iFrame (" + window.location.href + ")"), me(), ge(), H("background", i), H("padding", c), Ce(), ve(), ye(), _e(), Ee(), Te(), be(), g = we(), Q("init", "Init message from host page"), N();
			}
			function fe() {
				function e(e) {
					return e === "true";
				}
				var r = te.slice(ne).split(":");
				S = r[0], a = t === r[1] ? a : Number(r[1]), l = t === r[2] ? l : e(r[2]), y = t === r[3] ? y : e(r[3]), _ = t === r[4] ? _ : Number(r[4]), n = t === r[6] ? n : e(r[6]), o = r[7], h = t === r[8] ? h : r[8], i = r[9], c = r[10], E = t === r[11] ? E : Number(r[11]), g.enable = t === r[12] ? !1 : e(r[12]), C = t === r[13] ? C : r[13], j = t === r[14] ? j : r[14], b = t === r[15] ? b : e(r[15]);
			}
			function pe(e) {
				var t = e.split("Callback");
				if (t.length === 2) {
					var n = "on" + t[0].charAt(0).toUpperCase() + t[0].slice(1);
					this[n] = this[e], delete this[e], V("Deprecated: '" + e + "' has been renamed '" + n + "'. The old method will be removed in the next major version.");
				}
			}
			function me() {
				function e() {
					var e = window.iFrameResizer;
					B("Reading data from page: " + JSON.stringify(e)), Object.keys(e).forEach(pe, e), M = "onMessage" in e ? e.onMessage : M, N = "onReady" in e ? e.onReady : N, T = "targetOrigin" in e ? e.targetOrigin : T, h = "heightCalculationMethod" in e ? e.heightCalculationMethod : h, j = "widthCalculationMethod" in e ? e.widthCalculationMethod : j;
				}
				function t(e, t) {
					return typeof e == "function" && (B("Setup custom " + t + "CalcMethod"), F[t] = e, e = "custom"), e;
				}
				"iFrameResizer" in window && Object === window.iFrameResizer.constructor && (e(), h = t(h, "height"), j = t(j, "width")), B("TargetOrigin for parent set to: " + T);
			}
			function he(e, t) {
				return t.indexOf("-") !== -1 && (V("Negative CSS value ignored for " + e), t = ""), t;
			}
			function H(e, n) {
				t !== n && n !== "" && n !== "null" && (document.body.style[e] = n, B("Body " + e + " set to \"" + n + "\""));
			}
			function ge() {
				t === o && (o = a + "px"), H("margin", he("margin", o));
			}
			function _e() {
				document.documentElement.style.height = "", document.body.style.height = "", B("HTML & body height set to \"auto\"");
			}
			function U(e) {
				var t = {
					add: function(t) {
						function n() {
							Q(e.eventName, e.eventType);
						}
						I[t] = n, L(window, t, n, { passive: !0 });
					},
					remove: function(e) {
						var t = I[e];
						delete I[e], le(window, e, t);
					}
				};
				e.eventNames && Array.prototype.map ? (e.eventName = e.eventNames[0], e.eventNames.map(t[e.method])) : t[e.method](e.eventName), B(R(e.method) + " event listener: " + e.eventType);
			}
			function W(e) {
				U({
					method: e,
					eventType: "Animation Start",
					eventNames: ["animationstart", "webkitAnimationStart"]
				}), U({
					method: e,
					eventType: "Animation Iteration",
					eventNames: ["animationiteration", "webkitAnimationIteration"]
				}), U({
					method: e,
					eventType: "Animation End",
					eventNames: ["animationend", "webkitAnimationEnd"]
				}), U({
					method: e,
					eventType: "Input",
					eventName: "input"
				}), U({
					method: e,
					eventType: "Mouse Up",
					eventName: "mouseup"
				}), U({
					method: e,
					eventType: "Mouse Down",
					eventName: "mousedown"
				}), U({
					method: e,
					eventType: "Orientation Change",
					eventName: "orientationchange"
				}), U({
					method: e,
					eventType: "Print",
					eventNames: ["afterprint", "beforeprint"]
				}), U({
					method: e,
					eventType: "Ready State Change",
					eventName: "readystatechange"
				}), U({
					method: e,
					eventType: "Touch Start",
					eventName: "touchstart"
				}), U({
					method: e,
					eventType: "Touch End",
					eventName: "touchend"
				}), U({
					method: e,
					eventType: "Touch Cancel",
					eventName: "touchcancel"
				}), U({
					method: e,
					eventType: "Transition Start",
					eventNames: [
						"transitionstart",
						"webkitTransitionStart",
						"MSTransitionStart",
						"oTransitionStart",
						"otransitionstart"
					]
				}), U({
					method: e,
					eventType: "Transition Iteration",
					eventNames: [
						"transitioniteration",
						"webkitTransitionIteration",
						"MSTransitionIteration",
						"oTransitionIteration",
						"otransitioniteration"
					]
				}), U({
					method: e,
					eventType: "Transition End",
					eventNames: [
						"transitionend",
						"webkitTransitionEnd",
						"MSTransitionEnd",
						"oTransitionEnd",
						"otransitionend"
					]
				}), C === "child" && U({
					method: e,
					eventType: "IFrame Resized",
					eventName: "resize"
				});
			}
			function G(e, t, n, r) {
				return t !== e && (e in n || (V(e + " is not a valid option for " + r + "CalculationMethod."), e = t), B(r + " calculation method set to \"" + e + "\"")), e;
			}
			function ve() {
				h = G(h, m, X, "height");
			}
			function ye() {
				j = G(j, A, Z, "width");
			}
			function be() {
				n === !0 ? (W("add"), ke()) : B("Auto Resize disabled");
			}
			function xe() {
				s !== null && s.disconnect();
			}
			function Se() {
				W("remove"), xe(), clearInterval(v);
			}
			function Ce() {
				var e = document.createElement("div");
				e.style.clear = "both", e.style.display = "block", e.style.height = "0", document.body.appendChild(e);
			}
			function we() {
				function e() {
					return {
						x: window.pageXOffset === t ? document.documentElement.scrollLeft : window.pageXOffset,
						y: window.pageYOffset === t ? document.documentElement.scrollTop : window.pageYOffset
					};
				}
				function n(t) {
					var n = t.getBoundingClientRect(), r = e();
					return {
						x: parseInt(n.left, 10) + parseInt(r.x, 10),
						y: parseInt(n.top, 10) + parseInt(r.y, 10)
					};
				}
				function r(e) {
					function r(e) {
						var t = n(e);
						B("Moving to in page link (#" + i + ") at x: " + t.x + " y: " + t.y), $(t.y, t.x, "scrollToOffset");
					}
					var i = e.split("#")[1] || e, a = decodeURIComponent(i), o = document.getElementById(a) || document.getElementsByName(a)[0];
					t === o ? (B("In page link (#" + i + ") not found in iFrame, so sending to parent"), $(0, 0, "inPageLink", "#" + i)) : r(o);
				}
				function i() {
					var e = window.location.hash, t = window.location.href;
					e !== "" && e !== "#" && r(t);
				}
				function a() {
					function e(e) {
						function t(e) {
							e.preventDefault(), r(this.getAttribute("href"));
						}
						e.getAttribute("href") !== "#" && L(e, "click", t);
					}
					Array.prototype.forEach.call(document.querySelectorAll("a[href^=\"#\"]"), e);
				}
				function o() {
					L(window, "hashchange", i);
				}
				function s() {
					setTimeout(i, d);
				}
				function c() {
					Array.prototype.forEach && document.querySelectorAll ? (B("Setting up location.hash handlers"), a(), o(), s()) : V("In page linking not fully supported in this browser! (See README.md for IE8 workaround)");
				}
				return g.enable ? c() : B("In page linking not enabled"), { findTarget: r };
			}
			function Te() {
				if (b !== !0) return;
				function e(e) {
					$(0, 0, e.type, e.screenY + ":" + e.screenX);
				}
				function t(t, n) {
					B("Add event listener: " + n), L(window.document, t, e);
				}
				t("mouseenter", "Mouse Enter"), t("mouseleave", "Mouse Leave");
			}
			function Ee() {
				B("Enable public methods"), ae.parentIFrame = {
					autoResize: function(e) {
						return e === !0 && n === !1 ? (n = !0, be()) : e === !1 && n === !0 && (n = !1, Se()), $(0, 0, "autoResize", JSON.stringify(n)), n;
					},
					close: function() {
						$(0, 0, "close");
					},
					getId: function() {
						return S;
					},
					getPageInfo: function(e) {
						typeof e == "function" ? (P = e, $(0, 0, "pageInfo")) : (P = function() {}, $(0, 0, "pageInfoStop"));
					},
					moveToAnchor: function(e) {
						g.findTarget(e);
					},
					reset: function() {
						Ie("parentIFrame.reset");
					},
					scrollTo: function(e, t) {
						$(t, e, "scrollTo");
					},
					scrollToOffset: function(e, t) {
						$(t, e, "scrollToOffset");
					},
					sendMessage: function(e, t) {
						$(0, 0, "message", JSON.stringify(e), t);
					},
					setHeightCalculationMethod: function(e) {
						h = e, ve();
					},
					setWidthCalculationMethod: function(e) {
						j = e, ye();
					},
					setTargetOrigin: function(e) {
						B("Set targetOrigin: " + e), T = e;
					},
					size: function(e, t) {
						Q("size", "parentIFrame.size(" + ("" + (e || "") + (t ? "," + t : "")) + ")", e, t);
					}
				};
			}
			function De() {
				_ !== 0 && (B("setInterval: " + _ + "ms"), v = setInterval(function() {
					Q("interval", "setInterval: " + _);
				}, Math.abs(_)));
			}
			function Oe() {
				function e(e) {
					function t(e) {
						e.complete === !1 && (B("Attach listeners to " + e.src), e.addEventListener("load", i, !1), e.addEventListener("error", a, !1), c.push(e));
					}
					e.type === "attributes" && e.attributeName === "src" ? t(e.target) : e.type === "childList" && Array.prototype.forEach.call(e.target.querySelectorAll("img"), t);
				}
				function t(e) {
					c.splice(c.indexOf(e), 1);
				}
				function n(e) {
					B("Remove listeners from " + e.src), e.removeEventListener("load", i, !1), e.removeEventListener("error", a, !1), t(e);
				}
				function r(e, t, r) {
					n(e.target), Q(t, r + ": " + e.target.src);
				}
				function i(e) {
					r(e, "imageLoad", "Image loaded");
				}
				function a(e) {
					r(e, "imageLoadFailed", "Image load failed");
				}
				function o(t) {
					Q("mutationObserver", "mutationObserver: " + t[0].target + " " + t[0].type), t.forEach(e);
				}
				function s() {
					var e = document.querySelector("body");
					return u = new l(o), B("Create body MutationObserver"), u.observe(e, {
						attributes: !0,
						attributeOldValue: !1,
						characterData: !0,
						characterDataOldValue: !1,
						childList: !0,
						subtree: !0
					}), u;
				}
				var c = [], l = window.MutationObserver || window.WebKitMutationObserver, u = s();
				return { disconnect: function() {
					"disconnect" in u && (B("Disconnect body MutationObserver"), u.disconnect(), c.forEach(n));
				} };
			}
			function ke() {
				var e = 0 > _;
				window.MutationObserver || window.WebKitMutationObserver ? e ? De() : s = Oe() : (B("MutationObserver not supported in this browser!"), De());
			}
			function K(e, t) {
				var n = 0;
				return t ||= document.body, n = document.defaultView.getComputedStyle(t, null), n = n === null ? 0 : n[e], parseInt(n, r);
			}
			function Ae(e) {
				e > O / 2 && (O = 2 * e, B("Event throttle increased to " + O + "ms"));
			}
			function q(e, t) {
				for (var n = t.length, r = 0, i = 0, a = R(e), o = Date.now(), s = 0; s < n; s++) r = t[s].getBoundingClientRect()[e] + K("margin" + a, t[s]), r > i && (i = r);
				return o = Date.now() - o, B("Parsed " + n + " HTML elements"), B("Element position calculated in " + o + "ms"), Ae(o), i;
			}
			function J(e) {
				return [
					e.bodyOffset(),
					e.bodyScroll(),
					e.documentElementOffset(),
					e.documentElementScroll()
				];
			}
			function je(e, t) {
				function n() {
					return V("No tagged elements (" + t + ") found on page"), document.querySelectorAll("body *");
				}
				var r = document.querySelectorAll("[" + t + "]");
				return r.length === 0 && n(), q(e, r);
			}
			function Y() {
				return document.querySelectorAll("body *");
			}
			var X = {
				bodyOffset: function() {
					return document.body.offsetHeight + K("marginTop") + K("marginBottom");
				},
				offset: function() {
					return X.bodyOffset();
				},
				bodyScroll: function() {
					return document.body.scrollHeight;
				},
				custom: function() {
					return F.height();
				},
				documentElementOffset: function() {
					return document.documentElement.offsetHeight;
				},
				documentElementScroll: function() {
					return document.documentElement.scrollHeight;
				},
				max: function() {
					return Math.max.apply(null, J(X));
				},
				min: function() {
					return Math.min.apply(null, J(X));
				},
				grow: function() {
					return X.max();
				},
				lowestElement: function() {
					return Math.max(X.bodyOffset() || X.documentElementOffset(), q("bottom", Y()));
				},
				taggedElement: function() {
					return je("bottom", "data-iframe-height");
				}
			}, Z = {
				bodyScroll: function() {
					return document.body.scrollWidth;
				},
				bodyOffset: function() {
					return document.body.offsetWidth;
				},
				custom: function() {
					return F.width();
				},
				documentElementScroll: function() {
					return document.documentElement.scrollWidth;
				},
				documentElementOffset: function() {
					return document.documentElement.offsetWidth;
				},
				scroll: function() {
					return Math.max(Z.bodyScroll(), Z.documentElementScroll());
				},
				max: function() {
					return Math.max.apply(null, J(Z));
				},
				min: function() {
					return Math.min.apply(null, J(Z));
				},
				rightMostElement: function() {
					return q("right", Y());
				},
				taggedElement: function() {
					return je("right", "data-iframe-width");
				}
			};
			function Me(e, n, r, i) {
				function a() {
					p = f, k = m, $(p, k, e);
				}
				function o() {
					function e(e, t) {
						return !(Math.abs(e - t) <= E);
					}
					return f = t === r ? X[h]() : r, m = t === i ? Z[j]() : i, e(p, f) || l && e(k, m);
				}
				function s() {
					return !(e in {
						init: 1,
						interval: 1,
						size: 1
					});
				}
				function c() {
					return h in re || l && j in re;
				}
				function u() {
					B("No change in size detected");
				}
				function d() {
					s() && c() ? Ie(n) : e in { interval: 1 } || u();
				}
				var f, m;
				o() || e === "init" ? (Pe(), a()) : d();
			}
			var Ne = ue(Me);
			function Q(e, t, n, r) {
				function i() {
					e in {
						reset: 1,
						resetPage: 1,
						init: 1
					} || B("Trigger event: " + t);
				}
				function a() {
					return D && e in u;
				}
				a() ? B("Trigger event cancelled: " + e) : (i(), e === "init" ? Me(e, t, n, r) : Ne(e, t, n, r));
			}
			function Pe() {
				D || (D = !0, B("Trigger event lock on")), clearTimeout(ie), ie = setTimeout(function() {
					D = !1, B("Trigger event lock off"), B("--");
				}, d);
			}
			function Fe(e) {
				p = X[h](), k = Z[j](), $(p, k, e);
			}
			function Ie(e) {
				var t = h;
				h = m, B("Reset trigger event: " + e), Pe(), Fe("reset"), h = t;
			}
			function $(e, n, r, i, a) {
				function o() {
					t === a ? a = T : B("Message targetOrigin: " + a);
				}
				function s() {
					var o = e + ":" + n, s = S + ":" + o + ":" + r + (t === i ? "" : ":" + i);
					B("Sending message to host page (" + s + ")"), w.postMessage(x + s, a);
				}
				o(), s();
			}
			function Le(n) {
				var r = {
					init: function() {
						te = n.data, w = n.source, de(), f = !1, setTimeout(function() {
							ee = !1;
						}, d);
					},
					reset: function() {
						ee ? B("Page reset ignored by init") : (B("Page size reset by host page"), Fe("resetPage"));
					},
					resize: function() {
						Q("resizeParent", "Parent window requested size check");
					},
					moveToAnchor: function() {
						g.findTarget(o());
					},
					inPageLink: function() {
						this.moveToAnchor();
					},
					pageInfo: function() {
						var e = o();
						B("PageInfoFromParent called from parent: " + e), P(JSON.parse(e)), B(" --");
					},
					message: function() {
						var e = o();
						B("onMessage called from parent: " + e), M(JSON.parse(e)), B(" --");
					}
				};
				function i() {
					return x === ("" + n.data).slice(0, ne);
				}
				function a() {
					return n.data.split("]")[1].split(":")[0];
				}
				function o() {
					return n.data.slice(n.data.indexOf(":") + 1);
				}
				function s() {
					return !e.exports && "iFrameResize" in window || window.jQuery !== t && "iFrameResize" in window.jQuery.prototype;
				}
				function c() {
					return n.data.split(":")[2] in {
						true: 1,
						false: 1
					};
				}
				function l() {
					var e = a();
					e in r ? r[e]() : !s() && !c() && V("Unexpected message (" + n.data + ")");
				}
				function u() {
					f === !1 ? l() : c() ? r.init() : B("Ignored message of type \"" + a() + "\". Received before initialization.");
				}
				i() && u();
			}
			function Re() {
				document.readyState !== "loading" && window.parent.postMessage("[iFrameResizerChild]Ready", "*");
			}
			"iframeResizer" in window || (window.iframeChildListener = function(e) {
				Le({ data: e });
			}, L(window, "message", Le), L(window, "readystatechange", Re), Re());
		})();
	}(t)), t.exports;
}
var i = /* @__PURE__ */ e(r()), a = /* @__PURE__ */ Object.freeze(/* @__PURE__ */ Object.defineProperty({
	__proto__: null,
	default: i
}, Symbol.toStringTag, { value: "Module" }));
//#endregion
export { a as i };

//# sourceMappingURL=iframeResizer.contentWindow-CaUMNiuy-DNwceofi.js.map