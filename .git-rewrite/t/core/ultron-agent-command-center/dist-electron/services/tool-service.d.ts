export interface ToolResult {
    success: boolean;
    result?: any;
    error?: string;
    output?: string;
}
export declare class ToolService {
    private safeMode;
    executeTool(toolName: string, params: any): Promise<ToolResult>;
    private webFetch;
    private executePython;
    private readFile;
    private writeFile;
    private executeShell;
    private containsDangerousCode;
    private containsDangerousShellCommand;
    private isPathSafe;
    setSafeMode(enabled: boolean): void;
    isSafeMode(): boolean;
}
