import { Ka as e, Ua as t, _a as n, a as r, b as i, c as a, l as o, o as s, s as c, ti as l } from "./index-Dl4ETd_L-D2oMd1k2.js";
import { t as u } from "./iconPosition-Cpqwt3HE-C-jUvRPi.js";
//#region ../react/build/Button-CtzCBW58.js
var d = /* @__PURE__ */ e(t(), 1);
function f(e) {
	let { disabled: t, element: f, widgetMgr: p, fragmentId: m } = e, h = f.shortcut ? f.shortcut : void 0, g = s.SECONDARY;
	f.type === "primary" ? g = s.PRIMARY : f.type === "tertiary" && (g = s.TERTIARY);
	let _ = (0, d.useCallback)(() => {
		t || p.setTriggerValue(f, { fromUi: !0 }, m);
	}, [
		t,
		p,
		f,
		m
	]);
	return n({
		shortcut: h,
		disabled: t,
		onActivate: _
	}), /* @__PURE__ */ l.jsx(o, {
		className: "stButton",
		"data-testid": "stButton",
		children: /* @__PURE__ */ l.jsx(a, {
			help: f.help,
			containerWidth: !0,
			children: /* @__PURE__ */ l.jsx(r, {
				kind: g,
				size: c.SMALL,
				disabled: t,
				containerWidth: !0,
				onClick: _,
				children: /* @__PURE__ */ l.jsx(i, {
					icon: f.icon,
					iconPosition: u(f.iconPosition),
					label: f.label,
					shortcut: h
				})
			})
		})
	});
}
var p = (0, d.memo)(f);
//#endregion
export { p as default };

//# sourceMappingURL=Button-CtzCBW58-AMXk3Whn.js.map