"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.platform = exports.is = void 0;
exports.is = {
    dev: process.env.NODE_ENV === 'development'
};
exports.platform = {
    isWindows: process.platform === 'win32',
    isMacOS: process.platform === 'darwin',
    isLinux: process.platform === 'linux'
};
//# sourceMappingURL=utils.js.map