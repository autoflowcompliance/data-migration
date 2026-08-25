import { En as e, Ka as t, Ua as n, Ur as r, ti as i, vi as a } from "./index-Dl4ETd_L-D2oMd1k2.js";
import { n as o, t as s } from "./IFrameUtil-BYTcNZ4E-B8B2FnkH.js";
//#region ../react/build/IFrame-DRaylZUz.js
var c = /* @__PURE__ */ t(n(), 1), l = /* @__PURE__ */ e("iframe", { target: "e1u6k47s0" })(({ theme: e, disableScrolling: t, width: n, height: r }) => ({
	width: n ?? "100%",
	height: r ?? "100%",
	colorScheme: "normal",
	border: "none",
	padding: e.spacing.none,
	margin: e.spacing.none,
	overflow: t ? "hidden" : void 0
}), ""), u = "streamlit:iframe:setSize", d = "25rem", f = `<script>
(function() {
  var lastW = 0, lastH = 0;
  function sendSize() {
    // Guard against malformed HTML (e.g., <frameset>) or script running before body init
    if (!document.body) return;
    // Use getBoundingClientRect for accurate fractional pixel measurement,
    // then ceil to avoid scrollbars from sub-pixel rounding
    var rect = document.body.getBoundingClientRect();
    var w = Math.ceil(Math.max(
      rect.width,
      document.body.scrollWidth,
      document.body.offsetWidth,
      document.documentElement.scrollWidth,
      document.documentElement.offsetWidth
    ));
    var h = Math.ceil(Math.max(
      rect.height,
      document.body.scrollHeight,
      document.body.offsetHeight,
      document.documentElement.scrollHeight,
      document.documentElement.offsetHeight
    ));
    if (w !== lastW || h !== lastH) {
      lastW = w; lastH = h;
      // Note: postMessage with '*' broadcasts to any origin, but this is safe because:
      // 1. This script only runs inside srcdoc (same-origin, sandboxed)
      // 2. The payload is just dimension integers
      // 3. The frontend receiver validates event.source === iframe.contentWindow
      window.parent.postMessage({type: '${u}', width: w, height: h}, '*');
    }
  }
  // Send initial size after DOM is ready
  if (document.readyState === 'complete') {
    sendSize();
  } else {
    window.addEventListener('load', sendSize);
  }
  // Re-measure on DOM changes
  if (typeof MutationObserver !== 'undefined') {
    new MutationObserver(sendSize).observe(document.body, {
      childList: true, subtree: true, attributes: true, characterData: true
    });
  }
  // Re-measure on resize and image/font loading
  window.addEventListener('resize', sendSize);
  document.addEventListener('load', sendSize, true);
})();
<\/script>`;
function p(e) {
	return e + f;
}
function m(e) {
	return r(e) || e === "" ? void 0 : e;
}
function h({ element: e, widthConfig: t, heightConfig: n }) {
	let r = m(e.src), f = a(r) ? void 0 : m(e.srcdoc), h = (0, c.useRef)(null), [g, _] = (0, c.useState)({
		width: null,
		height: null
	}), v = t?.useContent ?? !1, y = n?.useContent ?? !1, b = a(f) && (v || y), x = b ? p(f) : f;
	(0, c.useEffect)(() => {
		if (!b) return;
		let e = (e) => {
			if (e.source && e.source === h.current?.contentWindow) {
				let t = e.data;
				if (t?.type === u && typeof t?.width == "number" && typeof t?.height == "number" && Number.isFinite(t.width) && Number.isFinite(t.height) && t.width >= 0 && t.height >= 0) {
					let e = t.width, n = t.height;
					_((t) => t.width === e && t.height === n ? t : {
						width: e,
						height: n
					});
				}
			}
		};
		return window.addEventListener("message", e), () => {
			window.removeEventListener("message", e);
		};
	}, [b]);
	let S = b && v && g.width !== null ? `${g.width}px` : void 0, C;
	return y && (b && g.height !== null ? C = `${g.height}px` : a(r) && (C = d)), /* @__PURE__ */ i.jsx(l, {
		ref: h,
		className: "stIFrame",
		"data-testid": "stIFrame",
		allow: o,
		disableScrolling: !e.scrolling,
		src: r,
		srcDoc: x,
		scrolling: e.scrolling ? "auto" : "no",
		sandbox: s,
		title: "st.iframe",
		tabIndex: e.tabIndex ?? void 0,
		width: S,
		height: C
	});
}
var g = (0, c.memo)(h);
//#endregion
export { g as default };

//# sourceMappingURL=IFrame-DRaylZUz-CTXRbjvJ.js.map