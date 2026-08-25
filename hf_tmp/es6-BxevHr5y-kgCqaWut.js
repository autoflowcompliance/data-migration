//#region ../react/build/es6-BxevHr5y.js
var e = globalThis.showDirectoryPicker;
async function t(t = {}) {
	if (e && !t._preferPolyfill) return e(t);
	let n = document.createElement("input");
	n.type = "file", n.webkitdirectory = !0, n.multiple = !0, n.style.position = "fixed", n.style.top = "-100000px", n.style.left = "-100000px", document.body.appendChild(n);
	let r = Promise.resolve().then(() => v);
	return await new Promise((e) => {
		n.addEventListener("change", e), n.click();
	}), r.then((e) => e.getDirHandlesFromInput(n));
}
var n = { accepts: [] }, r = globalThis.showOpenFilePicker;
async function i(e = {}) {
	let t = {
		...n,
		...e
	};
	if (r && !e._preferPolyfill) return r(t);
	let i = document.createElement("input");
	i.type = "file", i.multiple = t.multiple, i.accept = (t.accepts || []).map((e) => [...(e.extensions || []).map((e) => "." + e), ...e.mimeTypes || []]).flat().join(","), Object.assign(i.style, {
		position: "fixed",
		top: "-100000px",
		left: "-100000px"
	}), document.body.appendChild(i);
	let a = Promise.resolve().then(() => v);
	return await new Promise((e) => {
		i.addEventListener("change", e, { once: !0 }), i.click();
	}), i.remove(), a.then((e) => e.getFileHandlesFromInput(i));
}
var a = globalThis.showSaveFilePicker;
async function o(e = {}) {
	if (a && !e._preferPolyfill) return a(e);
	e._name && (console.warn("deprecated _name, spec now have `suggestedName`"), e.suggestedName = e._name);
	let { FileSystemFileHandle: t } = await Promise.resolve().then(() => k), { FileHandle: n } = await import("./downloader-CZ7qD7NY-hiBe8Fyp.js");
	return new t(new n(e.suggestedName));
}
globalThis.DataTransferItem && !DataTransferItem.prototype.getAsFileSystemHandle && (DataTransferItem.prototype.getAsFileSystemHandle = async function() {
	let e = this.webkitGetAsEntry(), [{ FileHandle: t, FolderHandle: n }, { FileSystemDirectoryHandle: r }, { FileSystemFileHandle: i }] = await Promise.all([
		import("./sandbox-DbnteG5V-BgYxqH9y.js"),
		Promise.resolve().then(() => C),
		Promise.resolve().then(() => k)
	]);
	return e.isFile ? new i(new t(e, !1)) : new r(new n(e, !1));
});
async function s(e, t = {}) {
	if (!e) return globalThis.navigator?.storage?.getDirectory() || globalThis.getOriginPrivateDirectory();
	let { FileSystemDirectoryHandle: n } = await Promise.resolve().then(() => C), r = await e;
	return new n(await (r.default ? r.default(t) : r(t)));
}
var c = {
	WritableStream: globalThis.WritableStream,
	TransformStream: globalThis.TransformStream,
	DOMException: globalThis.DOMException,
	Blob: globalThis.Blob,
	File: globalThis.File
}, { WritableStream: l } = c, u = class e extends l {
	#e;
	constructor(t) {
		super(t), this.#e = t, Object.setPrototypeOf(this, e.prototype), this._closed = !1;
	}
	async close() {
		this._closed = !0;
		let e = this.getWriter(), t = e.close();
		return e.releaseLock(), t;
	}
	seek(e) {
		return this.write({
			type: "seek",
			position: e
		});
	}
	truncate(e) {
		return this.write({
			type: "truncate",
			size: e
		});
	}
	write(e) {
		if (this._closed) return Promise.reject(/* @__PURE__ */ TypeError("Cannot write to a CLOSED writable stream"));
		let t = this.getWriter(), n = t.write(e);
		return t.releaseLock(), n;
	}
};
Object.defineProperty(u.prototype, Symbol.toStringTag, {
	value: "FileSystemWritableFileStream",
	writable: !1,
	enumerable: !1,
	configurable: !0
}), Object.defineProperties(u.prototype, {
	close: { enumerable: !0 },
	seek: { enumerable: !0 },
	truncate: { enumerable: !0 },
	write: { enumerable: !0 }
}), globalThis.FileSystemFileHandle && !globalThis.FileSystemFileHandle.prototype.createWritable && !globalThis.FileSystemWritableFileStream && (globalThis.FileSystemWritableFileStream = u);
var d = /* @__PURE__ */ Symbol("adapter"), f = class {
	[d];
	name;
	kind;
	constructor(e) {
		this.kind = e.kind, this.name = e.name, this[d] = e;
	}
	async queryPermission(e = {}) {
		let { mode: t = "read" } = e, n = this[d];
		if (n.queryPermission) return n.queryPermission({ mode: t });
		if (t === "read") return "granted";
		if (t === "readwrite") return n.writable ? "granted" : "denied";
		throw TypeError(`Mode ${t} must be 'read' or 'readwrite'`);
	}
	async requestPermission({ mode: e = "read" } = {}) {
		let t = this[d];
		if (t.requestPermission) return t.requestPermission({ mode: e });
		if (e === "read") return "granted";
		if (e === "readwrite") return t.writable ? "granted" : "denied";
		throw TypeError(`Mode ${e} must be 'read' or 'readwrite'`);
	}
	async remove(e = {}) {
		await this[d].remove(e);
	}
	async isSameEntry(e) {
		return this === e ? !0 : !e || typeof e != "object" || this.kind !== e.kind || !e[d] ? !1 : this[d].isSameEntry(e[d]);
	}
};
Object.defineProperty(f.prototype, Symbol.toStringTag, {
	value: "FileSystemHandle",
	writable: !1,
	enumerable: !1,
	configurable: !0
}), globalThis.FileSystemHandle && (globalThis.FileSystemHandle.prototype.queryPermission ??= function(e) {
	return "granted";
});
var p = {
	INVALID: ["seeking position failed.", "InvalidStateError"],
	GONE: ["A requested file or directory could not be found at the time an operation was processed.", "NotFoundError"],
	MISMATCH: ["The path supplied exists, but was not an entry of requested type.", "TypeMismatchError"],
	MOD_ERR: ["The object can not be modified in this way.", "InvalidModificationError"],
	SYNTAX: (e) => [`Failed to execute 'write' on 'UnderlyingSinkBase': Invalid params passed. ${e}`, "SyntaxError"],
	SECURITY: ["It was determined that certain files are unsafe for access within a Web application, or that too many calls are being made on file resources.", "SecurityError"],
	DISALLOWED: ["The request is not allowed by the user agent or the platform in the current context.", "NotAllowedError"]
}, m = { writable: globalThis.WritableStream };
async function h(e) {
	console.warn("deprecated fromDataTransfer - use `dt.items[0].getAsFileSystemHandle()` instead");
	let [t, n, r] = await Promise.all([
		import("./memory-C-LDMFc2-uqYtP5J5.js"),
		import("./sandbox-DbnteG5V-BgYxqH9y.js"),
		Promise.resolve().then(() => C)
	]), i = new t.FolderHandle("", !1);
	return i._entries = e.map((e) => e.isFile ? new n.FileHandle(e, !1) : new n.FolderHandle(e, !1)), new r.FileSystemDirectoryHandle(i);
}
async function g(e) {
	let { FolderHandle: t, FileHandle: n } = await import("./memory-C-LDMFc2-uqYtP5J5.js"), { FileSystemDirectoryHandle: r } = await Promise.resolve().then(() => C), i = Array.from(e.files), a = i[0].webkitRelativePath.split("/", 1)[0], o = new t(a, !1);
	return i.forEach((e) => {
		let r = e.webkitRelativePath.split("/");
		r.shift();
		let i = r.pop(), a = r.reduce((e, n) => (e._entries[n] || (e._entries[n] = new t(n, !1)), e._entries[n]), o);
		a._entries[i] = new n(e.name, e, !1);
	}), new r(o);
}
async function _(e) {
	let { FileHandle: t } = await import("./memory-C-LDMFc2-uqYtP5J5.js"), { FileSystemFileHandle: n } = await Promise.resolve().then(() => k);
	return Array.from(e.files).map((e) => new n(new t(e.name, e, !1)));
}
var v = /* @__PURE__ */ Object.freeze(/* @__PURE__ */ Object.defineProperty({
	__proto__: null,
	config: m,
	errors: p,
	fromDataTransfer: h,
	getDirHandlesFromInput: g,
	getFileHandlesFromInput: _
}, Symbol.toStringTag, { value: "Module" })), { GONE: y, MOD_ERR: b } = p, x = /* @__PURE__ */ Symbol("adapter"), S = class e extends f {
	[x];
	constructor(e) {
		super(e), this[x] = e;
	}
	async getDirectoryHandle(t, n = {}) {
		if (t === "") throw TypeError("Name can't be an empty string.");
		if (t === "." || t === ".." || t.includes("/")) throw TypeError("Name contains invalid characters.");
		return n.create = !!n.create, new e(await this[x].getDirectoryHandle(t, n));
	}
	async *entries() {
		let { FileSystemFileHandle: t } = await Promise.resolve().then(() => k);
		for await (let [n, r] of this[x].entries()) yield [r.name, r.kind === "file" ? new t(r) : new e(r)];
	}
	async *getEntries() {
		let { FileSystemFileHandle: t } = await Promise.resolve().then(() => k);
		console.warn("deprecated, use .entries() instead");
		for await (let n of this[x].entries()) yield n.kind === "file" ? new t(n) : new e(n);
	}
	async getFileHandle(e, t = {}) {
		let { FileSystemFileHandle: n } = await Promise.resolve().then(() => k);
		if (e === "") throw TypeError("Name can't be an empty string.");
		if (e === "." || e === ".." || e.includes("/")) throw TypeError("Name contains invalid characters.");
		return t.create = !!t.create, new n(await this[x].getFileHandle(e, t));
	}
	async removeEntry(e, t = {}) {
		if (e === "") throw TypeError("Name can't be an empty string.");
		if (e === "." || e === ".." || e.includes("/")) throw TypeError("Name contains invalid characters.");
		return t.recursive = !!t.recursive, this[x].removeEntry(e, t);
	}
	async resolve(e) {
		if (await e.isSameEntry(this)) return [];
		let t = [{
			handle: this,
			path: []
		}];
		for (; t.length;) {
			let { handle: n, path: r } = t.pop();
			for await (let i of n.values()) {
				if (await i.isSameEntry(e)) return [...r, i.name];
				i.kind === "directory" && t.push({
					handle: i,
					path: [...r, i.name]
				});
			}
		}
		return null;
	}
	async *keys() {
		for await (let [e] of this[x].entries()) yield e;
	}
	async *values() {
		for await (let [e, t] of this) yield t;
	}
	[Symbol.asyncIterator]() {
		return this.entries();
	}
};
if (Object.defineProperty(S.prototype, Symbol.toStringTag, {
	value: "FileSystemDirectoryHandle",
	writable: !1,
	enumerable: !1,
	configurable: !0
}), Object.defineProperties(S.prototype, {
	getDirectoryHandle: { enumerable: !0 },
	entries: { enumerable: !0 },
	getFileHandle: { enumerable: !0 },
	removeEntry: { enumerable: !0 }
}), globalThis.FileSystemDirectoryHandle) {
	let e = globalThis.FileSystemDirectoryHandle.prototype;
	e.resolve = async function(e) {
		if (await e.isSameEntry(this)) return [];
		let t = [{
			handle: this,
			path: []
		}];
		for (; t.length;) {
			let { handle: n, path: r } = t.pop();
			for await (let i of n.values()) {
				if (await i.isSameEntry(e)) return [...r, i.name];
				i.kind === "directory" && t.push({
					handle: i,
					path: [...r, i.name]
				});
			}
		}
		return null;
	};
	async function t(e) {
		if (await (await navigator.storage.getDirectory()).resolve(e) === null) throw new DOMException(...y);
	}
	let n = e.entries;
	e.entries = async function* () {
		await t(this), yield* n.call(this);
	}, e[Symbol.asyncIterator] = async function* () {
		yield* this.entries();
	};
	let r = e.removeEntry;
	e.removeEntry = async function(e, t = {}) {
		return r.call(this, e, t).catch(async (e) => {
			throw e instanceof DOMException && e.name === "UnknownError" && !t.recursive && !(await n.call(this).next()).done ? new DOMException(...b) : e;
		});
	};
}
var C = /* @__PURE__ */ Object.freeze(/* @__PURE__ */ Object.defineProperty({
	__proto__: null,
	FileSystemDirectoryHandle: S,
	default: S
}, Symbol.toStringTag, { value: "Module" })), { INVALID: w, SYNTAX: T, GONE: E } = p, D = /* @__PURE__ */ Symbol("adapter"), O = class extends f {
	[D];
	constructor(e) {
		super(e), this[D] = e;
	}
	async createWritable(e = {}) {
		return new u(await this[D].createWritable(e));
	}
	async getFile() {
		return this[D].getFile();
	}
};
if (Object.defineProperty(O.prototype, Symbol.toStringTag, {
	value: "FileSystemFileHandle",
	writable: !1,
	enumerable: !1,
	configurable: !0
}), Object.defineProperties(O.prototype, {
	createWritable: { enumerable: !0 },
	getFile: { enumerable: !0 }
}), globalThis.FileSystemFileHandle && !globalThis.FileSystemFileHandle.prototype.createWritable) {
	let e = /* @__PURE__ */ new WeakMap(), t, n = () => {
		let e, t;
		onmessage = async (n) => {
			let r = n.ports[0], i = n.data;
			switch (i.type) {
				case "open":
					let n = i.name, r = await navigator.storage.getDirectory();
					for (let e of i.path) r = await r.getDirectoryHandle(e);
					e = await r.getFileHandle(n), t = await e.createSyncAccessHandle();
					break;
				case "write":
					t.write(i.data, { at: i.position }), t.flush();
					break;
				case "truncate":
					t.truncate(i.size);
					break;
				case "abort":
				case "close":
					t.close();
					break;
			}
			r.postMessage(0);
		};
	};
	globalThis.FileSystemFileHandle.prototype.createWritable = async function(r) {
		if (!t) {
			let e = `(${n.toString()})()`, r = new Blob([e], { type: "text/javascript" });
			t = URL.createObjectURL(r);
		}
		let i = new Worker(t, { type: "module" }), a = 0, o = new TextEncoder(), s = await this.getFile().then((e) => e.size), c = (e) => new Promise((t, n) => {
			let r = new MessageChannel();
			r.port1.onmessage = (e) => {
				e.data instanceof Error ? n(e.data) : t(e.data), r.port1.close(), r.port2.close(), r.port1.onmessage = null;
			}, i.postMessage(e, [r.port2]);
		}), l = await navigator.storage.getDirectory(), d = await e.get(this), f = await l.resolve(d);
		if (f === null) throw new DOMException(...E);
		return await c({
			type: "open",
			path: f,
			name: this.name
		}), r?.keepExistingData === !1 && (await c({
			type: "truncate",
			size: 0
		}), s = 0), new u({
			start: (e) => {},
			async write(e) {
				if (e = e?.constructor === Object ? { ...e } : {
					type: "write",
					data: e,
					position: a
				}, e.type === "write") {
					if (!("data" in e)) throw await c({ type: "close" }), new DOMException(...T("write requires a data argument"));
					if (e.position ??= a, typeof e.data == "string") e.data = o.encode(e.data);
					else if (e.data instanceof ArrayBuffer) e.data = new Uint8Array(e.data);
					else if (!(e.data instanceof Uint8Array) && ArrayBuffer.isView(e.data)) e.data = new Uint8Array(e.data.buffer, e.data.byteOffset, e.data.byteLength);
					else if (!(e.data instanceof Uint8Array)) {
						let t = await new Response(e.data).arrayBuffer();
						e.data = new Uint8Array(t);
					}
					Number.isInteger(e.position) && e.position >= 0 && (a = e.position), a += e.data.byteLength, s += e.data.byteLength;
				} else if (e.type === "seek") if (Number.isInteger(e.position) && e.position >= 0) {
					if (s < e.position) throw new DOMException(...w);
					console.log("seeking", e), a = e.position;
					return;
				} else throw await c({ type: "close" }), new DOMException(...T("seek requires a position argument"));
				else if (e.type === "truncate") if (Number.isInteger(e.size) && e.size >= 0) s = e.size, a > s && (a = s);
				else throw await c({ type: "close" }), new DOMException(...T("truncate requires a size argument"));
				await c(e);
			},
			async close() {
				await c({ type: "close" }), i.terminate();
			},
			async abort(e) {
				await c({
					type: "abort",
					reason: e
				}), i.terminate();
			}
		});
	};
	let r = FileSystemDirectoryHandle.prototype.getFileHandle;
	FileSystemDirectoryHandle.prototype.getFileHandle = async function(...t) {
		let n = await r.call(this, ...t);
		return e.set(n, this), n;
	};
}
var k = /* @__PURE__ */ Object.freeze(/* @__PURE__ */ Object.defineProperty({
	__proto__: null,
	FileSystemFileHandle: O,
	default: O
}, Symbol.toStringTag, { value: "Module" })), A = /* @__PURE__ */ Object.freeze(/* @__PURE__ */ Object.defineProperty({
	__proto__: null,
	FileSystemDirectoryHandle: S,
	FileSystemFileHandle: O,
	FileSystemHandle: f,
	FileSystemWritableFileStream: u,
	getOriginPrivateDirectory: s,
	showDirectoryPicker: t,
	showOpenFilePicker: i,
	showSaveFilePicker: o
}, Symbol.toStringTag, { value: "Module" }));
//#endregion
export { A as a, c, p as e };

//# sourceMappingURL=es6-BxevHr5y-kgCqaWut.js.map