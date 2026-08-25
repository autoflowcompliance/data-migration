import { En as e, Mr as t, ni as n, ti as r } from "./index-Dl4ETd_L-D2oMd1k2.js";
import { r as i } from "./styled-components-BDZ1Vzrp-C65H8d9R.js";
//#region ../react/build/InputInstructions-BQBBgzXB.js
var a = n`
  50% {
    color: rgba(0, 0, 0, 0);
  }
`, o = /* @__PURE__ */ e("span", { target: "edlqvik0" })(({ includeDot: e, shouldBlink: t, theme: n }) => ({
	...e ? { "&::before": {
		opacity: 1,
		content: "\"•\"",
		animation: "none",
		color: n.colors.grayTextColor,
		margin: `0 ${n.spacing.twoXS}`
	} } : {},
	...t ? {
		color: n.colors.redTextColor,
		animationName: `${a}`,
		animationDuration: "0.5s",
		animationIterationCount: 5
	} : {}
}), ""), s = ({ dirty: e, value: n, inForm: a, maxLength: s, className: c, type: l = "single", allowEnterToSubmit: u = !0 }) => {
	let d = [], f = (e, t = !1) => {
		d.push(/* @__PURE__ */ r.jsx(o, {
			includeDot: d.length > 0,
			shouldBlink: t,
			children: e
		}, d.length));
	};
	if (u) {
		let e = a ? "submit form" : "apply";
		l === "multiline" ? f(`Press ${t() ? "⌘" : "Ctrl"}+Enter to ${e}`) : l === "single" && f(`Press Enter to ${e}`);
	}
	return s && (l !== "chat" || e) && f(`${n.length}/${s}`, e && n.length >= s), /* @__PURE__ */ r.jsx(i, {
		"data-testid": "InputInstructions",
		className: c,
		children: d
	});
};
//#endregion
export { s as t };

//# sourceMappingURL=InputInstructions-BQBBgzXB-ClQbP4Gu.js.map