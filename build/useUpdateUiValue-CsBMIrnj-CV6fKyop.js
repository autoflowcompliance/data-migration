import { Ka as e, Pr as t, Ua as n } from "./index-Dl4ETd_L-D2oMd1k2.js";
import { t as r } from "./inputUtils-DCYiajnz-DpM8zsby.js";
//#region ../react/build/useUpdateUiValue-CsBMIrnj.js
var i = /* @__PURE__ */ e(n(), 1);
function a({ formId: e, maxChars: n, setDirty: r, setUiValue: a, setValueWithSource: o, additionalAction: s }) {
	return (0, i.useCallback)((i) => {
		let { value: c } = i.target;
		n !== 0 && c.length > n || (r(!0), a(c), t({ formId: e }) && o({
			value: c,
			fromUi: !0
		}), s && s());
	}, [
		e,
		n,
		r,
		a,
		o,
		s
	]);
}
function o(e, t, n, a, o, s = !1) {
	return (0, i.useCallback)((i) => {
		let c = s ? i.metaKey || i.ctrlKey : !0;
		!r(i) || !c || (i.preventDefault(), n && t(), a.allowFormEnterToSubmit(e) && a.submitForm(e, o));
	}, [
		e,
		o,
		n,
		t,
		a,
		s
	]);
}
function s(e, t, n, r) {
	(0, i.useEffect)(() => {
		r || e !== t && n(e);
	}, [
		e,
		t,
		r,
		n
	]);
}
//#endregion
export { s as n, o as r, a as t };

//# sourceMappingURL=useUpdateUiValue-CsBMIrnj-CV6fKyop.js.map