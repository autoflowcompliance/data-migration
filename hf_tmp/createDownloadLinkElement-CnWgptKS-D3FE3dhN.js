import { ut as e } from "./index-Dl4ETd_L-D2oMd1k2.js";
//#region ../react/build/createDownloadLinkElement-CnWgptKS.js
var t = ({ enforceDownloadInNewTab: t, url: n, filename: r }) => {
	let i = document.createElement("a");
	i.setAttribute("href", n), t ? i.setAttribute("target", "_blank") : i.setAttribute("target", "_self");
	let a = e.DOWNLOAD_ASSETS_BASE_URL;
	return (!a || !n.startsWith(a) || window.navigator.userAgent.includes("Firefox")) && i.setAttribute("download", r), i;
};
//#endregion
export { t };

//# sourceMappingURL=createDownloadLinkElement-CnWgptKS-D3FE3dhN.js.map