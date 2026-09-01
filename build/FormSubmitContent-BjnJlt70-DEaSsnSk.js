import { A as e, Ka as t, Ua as n, _a as r, a as i, b as a, c as o, l as s, o as c, s as l, ti as u, va as d, yt as f } from "./index-Dl4ETd_L-D2oMd1k2.js";
import { t as p } from "./iconPosition-Cpqwt3HE-C-jUvRPi.js";
//#region ../react/build/FormSubmitContent-BjnJlt70.js
var m = /* @__PURE__ */ t(n(), 1);
function h(t) {
	let { disabled: n, element: f, widgetMgr: h, fragmentId: g } = t, { formId: _ } = f, v = f.shortcut ? f.shortcut : void 0, { formsData: y } = d(e), b = y.formsWithUploads.has(_), x = c.SECONDARY_FORM_SUBMIT;
	f.type === "primary" ? x = c.PRIMARY_FORM_SUBMIT : f.type === "tertiary" && (x = c.TERTIARY_FORM_SUBMIT);
	let S = n || b;
	(0, m.useEffect)(() => (h.addSubmitButton(_, f), () => h.removeSubmitButton(_, f)), [
		h,
		_,
		f
	]);
	let C = (0, m.useCallback)(() => {
		S || h.submitForm(f.formId, g, f);
	}, [
		S,
		h,
		f,
		g
	]);
	return r({
		shortcut: v,
		disabled: S,
		onActivate: C
	}), /* @__PURE__ */ u.jsx(s, {
		className: "stFormSubmitButton",
		"data-testid": "stFormSubmitButton",
		children: /* @__PURE__ */ u.jsx(o, {
			help: f.help,
			containerWidth: !0,
			children: /* @__PURE__ */ u.jsx(i, {
				kind: x,
				size: l.SMALL,
				containerWidth: !0,
				disabled: S,
				onClick: C,
				children: /* @__PURE__ */ u.jsx(a, {
					icon: f.icon,
					iconPosition: p(f.iconPosition),
					label: f.label,
					shortcut: v
				})
			})
		})
	});
}
function g(e) {
	return /* @__PURE__ */ u.jsx(f, { children: /* @__PURE__ */ u.jsx(h, { ...e }) });
}
//#endregion
export { g as FormSubmitContent };

//# sourceMappingURL=FormSubmitContent-BjnJlt70-DEaSsnSk.js.map