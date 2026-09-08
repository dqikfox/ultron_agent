"use strict";
var __createBinding = (this && this.__createBinding) || (Object.create ? (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    var desc = Object.getOwnPropertyDescriptor(m, k);
    if (!desc || ("get" in desc ? !m.__esModule : desc.writable || desc.configurable)) {
      desc = { enumerable: true, get: function() { return m[k]; } };
    }
    Object.defineProperty(o, k2, desc);
}) : (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    o[k2] = m[k];
}));
var __setModuleDefault = (this && this.__setModuleDefault) || (Object.create ? (function(o, v) {
    Object.defineProperty(o, "default", { enumerable: true, value: v });
}) : function(o, v) {
    o["default"] = v;
});
var __importStar = (this && this.__importStar) || (function () {
    var ownKeys = function(o) {
        ownKeys = Object.getOwnPropertyNames || function (o) {
            var ar = [];
            for (var k in o) if (Object.prototype.hasOwnProperty.call(o, k)) ar[ar.length] = k;
            return ar;
        };
        return ownKeys(o);
    };
    return function (mod) {
        if (mod && mod.__esModule) return mod;
        var result = {};
        if (mod != null) for (var k = ownKeys(mod), i = 0; i < k.length; i++) if (k[i] !== "default") __createBinding(result, mod, k[i]);
        __setModuleDefault(result, mod);
        return result;
    };
})();
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
exports.ToolService = void 0;
const child_process_1 = require("child_process");
const fs = __importStar(require("fs"));
const path = __importStar(require("path"));
const axios_1 = __importDefault(require("axios"));
class ToolService {
    constructor() {
        this.safeMode = true;
    }
    async executeTool(toolName, params) {
        try {
            switch (toolName) {
                case 'web-fetch':
                    return await this.webFetch(params.url);
                case 'python-exec':
                    return await this.executePython(params.code);
                case 'file-read':
                    return await this.readFile(params.path);
                case 'file-write':
                    return await this.writeFile(params.path, params.content);
                case 'shell-exec':
                    return await this.executeShell(params.command);
                default:
                    return {
                        success: false,
                        error: `Unknown tool: ${toolName}`
                    };
            }
        }
        catch (error) {
            return {
                success: false,
                error: error instanceof Error ? error.message : 'Unknown error'
            };
        }
    }
    async webFetch(url) {
        try {
            const response = await axios_1.default.get(url, {
                timeout: 10000,
                headers: {
                    'User-Agent': 'Ultron-Agent-Command-Center/1.0'
                }
            });
            return {
                success: true,
                result: {
                    data: response.data,
                    status: response.status,
                    headers: response.headers
                }
            };
        }
        catch (error) {
            return {
                success: false,
                error: error instanceof Error ? error.message : 'Web fetch failed'
            };
        }
    }
    async executePython(code) {
        return new Promise((resolve) => {
            if (this.safeMode && this.containsDangerousCode(code)) {
                resolve({
                    success: false,
                    error: 'Code contains potentially dangerous operations'
                });
                return;
            }
            const tempFile = path.join(__dirname, `temp_${Date.now()}.py`);
            fs.writeFileSync(tempFile, code);
            (0, child_process_1.exec)(`python ${tempFile}`, { timeout: 30000 }, (error, stdout, stderr) => {
                // Clean up temp file
                try {
                    fs.unlinkSync(tempFile);
                }
                catch (cleanupError) {
                    console.warn('Failed to clean up temp file:', cleanupError);
                }
                if (error) {
                    resolve({
                        success: false,
                        error: error.message,
                        output: stderr
                    });
                }
                else {
                    resolve({
                        success: true,
                        output: stdout,
                        result: stdout
                    });
                }
            });
        });
    }
    async readFile(filePath) {
        try {
            if (this.safeMode && !this.isPathSafe(filePath)) {
                return {
                    success: false,
                    error: 'File path not allowed in safe mode'
                };
            }
            const content = fs.readFileSync(filePath, 'utf8');
            return {
                success: true,
                result: content
            };
        }
        catch (error) {
            return {
                success: false,
                error: error instanceof Error ? error.message : 'File read failed'
            };
        }
    }
    async writeFile(filePath, content) {
        try {
            if (this.safeMode && !this.isPathSafe(filePath)) {
                return {
                    success: false,
                    error: 'File path not allowed in safe mode'
                };
            }
            fs.writeFileSync(filePath, content, 'utf8');
            return {
                success: true,
                result: 'File written successfully'
            };
        }
        catch (error) {
            return {
                success: false,
                error: error instanceof Error ? error.message : 'File write failed'
            };
        }
    }
    async executeShell(command) {
        return new Promise((resolve) => {
            if (this.safeMode && this.containsDangerousShellCommand(command)) {
                resolve({
                    success: false,
                    error: 'Command contains potentially dangerous operations'
                });
                return;
            }
            (0, child_process_1.exec)(command, { timeout: 30000 }, (error, stdout, stderr) => {
                if (error) {
                    resolve({
                        success: false,
                        error: error.message,
                        output: stderr
                    });
                }
                else {
                    resolve({
                        success: true,
                        output: stdout,
                        result: stdout
                    });
                }
            });
        });
    }
    containsDangerousCode(code) {
        const dangerousPatterns = [
            /import\s+os/,
            /import\s+subprocess/,
            /import\s+sys/,
            /exec\(/,
            /eval\(/,
            /__import__/,
            /open\(/,
            /file\(/
        ];
        return dangerousPatterns.some(pattern => pattern.test(code));
    }
    containsDangerousShellCommand(command) {
        const dangerousPatterns = [
            /rm\s+-rf/,
            /del\s+\/s/,
            /format\s+c:/,
            /shutdown/,
            /reboot/,
            /sudo/,
            /passwd/,
            /chmod\s+777/,
            /\|\|/,
            /&&/,
            /;/
        ];
        return dangerousPatterns.some(pattern => pattern.test(command.toLowerCase()));
    }
    isPathSafe(filePath) {
        // Only allow paths within the app's data directory
        const normalizedPath = path.normalize(filePath);
        return !normalizedPath.includes('..') &&
            !normalizedPath.startsWith('/') &&
            !normalizedPath.includes('system32') &&
            !normalizedPath.includes('windows');
    }
    setSafeMode(enabled) {
        this.safeMode = enabled;
    }
    isSafeMode() {
        return this.safeMode;
    }
}
exports.ToolService = ToolService;
//# sourceMappingURL=tool-service.js.map