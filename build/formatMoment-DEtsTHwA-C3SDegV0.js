//#region ../react/build/formatMoment-DEtsTHwA.js
function e(e, t, n = "datetime") {
	if (t === "localized") {
		let t = navigator.languages, r = n === "time" ? void 0 : "medium", i = n === "date" ? void 0 : "medium";
		try {
			return new Intl.DateTimeFormat(t, {
				dateStyle: r,
				timeStyle: i
			}).format(e.toDate());
		} catch (t) {
			if (t instanceof RangeError) return new Intl.DateTimeFormat(void 0, {
				dateStyle: r,
				timeStyle: i
			}).format(e.toDate());
			throw t;
		}
	} else {
		if (t === "distance") return e.fromNow();
		if (t === "calendar") return e.calendar();
		if (t === "iso8601") return n === "date" ? e.format("YYYY-MM-DD") : n === "time" ? e.format("HH:mm:ss.SSS[Z]") : e.toISOString();
	}
	return e.format(t);
}
//#endregion
export { e as t };

//# sourceMappingURL=formatMoment-DEtsTHwA-C3SDegV0.js.map