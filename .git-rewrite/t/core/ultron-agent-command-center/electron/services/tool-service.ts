import { exec } from 'child_process'
import * as fs from 'fs'
import * as path from 'path'
import axios from 'axios'

export interface ToolResult {
  success: boolean
  result?: any
  error?: string
  output?: string
}

export class ToolService {
  private safeMode = true

  async executeTool(toolName: string, params: any): Promise<ToolResult> {
    try {
      switch (toolName) {
        case 'web-fetch':
          return await this.webFetch(params.url)
        case 'python-exec':
          return await this.executePython(params.code)
        case 'file-read':
          return await this.readFile(params.path)
        case 'file-write':
          return await this.writeFile(params.path, params.content)
        case 'shell-exec':
          return await this.executeShell(params.command)
        default:
          return {
            success: false,
            error: `Unknown tool: ${toolName}`
          }
      }
    } catch (error) {
      return {
        success: false,
        error: error instanceof Error ? error.message : 'Unknown error'
      }
    }
  }

  private async webFetch(url: string): Promise<ToolResult> {
    try {
      const response = await axios.get(url, {
        timeout: 10000,
        headers: {
          'User-Agent': 'Ultron-Agent-Command-Center/1.0'
        }
      })
      
      return {
        success: true,
        result: {
          data: response.data,
          status: response.status,
          headers: response.headers
        }
      }
    } catch (error) {
      return {
        success: false,
        error: error instanceof Error ? error.message : 'Web fetch failed'
      }
    }
  }

  private async executePython(code: string): Promise<ToolResult> {
    return new Promise((resolve) => {
      if (this.safeMode && this.containsDangerousCode(code)) {
        resolve({
          success: false,
          error: 'Code contains potentially dangerous operations'
        })
        return
      }

      const tempFile = path.join(__dirname, `temp_${Date.now()}.py`)
      
      fs.writeFileSync(tempFile, code)
      
      exec(`python ${tempFile}`, { timeout: 30000 }, (error, stdout, stderr) => {
        // Clean up temp file
        try {
          fs.unlinkSync(tempFile)
        } catch (cleanupError) {
          console.warn('Failed to clean up temp file:', cleanupError)
        }
        
        if (error) {
          resolve({
            success: false,
            error: error.message,
            output: stderr
          })
        } else {
          resolve({
            success: true,
            output: stdout,
            result: stdout
          })
        }
      })
    })
  }

  private async readFile(filePath: string): Promise<ToolResult> {
    try {
      if (this.safeMode && !this.isPathSafe(filePath)) {
        return {
          success: false,
          error: 'File path not allowed in safe mode'
        }
      }
      
      const content = fs.readFileSync(filePath, 'utf8')
      return {
        success: true,
        result: content
      }
    } catch (error) {
      return {
        success: false,
        error: error instanceof Error ? error.message : 'File read failed'
      }
    }
  }

  private async writeFile(filePath: string, content: string): Promise<ToolResult> {
    try {
      if (this.safeMode && !this.isPathSafe(filePath)) {
        return {
          success: false,
          error: 'File path not allowed in safe mode'
        }
      }
      
      fs.writeFileSync(filePath, content, 'utf8')
      return {
        success: true,
        result: 'File written successfully'
      }
    } catch (error) {
      return {
        success: false,
        error: error instanceof Error ? error.message : 'File write failed'
      }
    }
  }

  private async executeShell(command: string): Promise<ToolResult> {
    return new Promise((resolve) => {
      if (this.safeMode && this.containsDangerousShellCommand(command)) {
        resolve({
          success: false,
          error: 'Command contains potentially dangerous operations'
        })
        return
      }

      exec(command, { timeout: 30000 }, (error, stdout, stderr) => {
        if (error) {
          resolve({
            success: false,
            error: error.message,
            output: stderr
          })
        } else {
          resolve({
            success: true,
            output: stdout,
            result: stdout
          })
        }
      })
    })
  }

  private containsDangerousCode(code: string): boolean {
    const dangerousPatterns = [
      /import\s+os/,
      /import\s+subprocess/,
      /import\s+sys/,
      /exec\(/,
      /eval\(/,
      /__import__/,
      /open\(/,
      /file\(/
    ]
    
    return dangerousPatterns.some(pattern => pattern.test(code))
  }

  private containsDangerousShellCommand(command: string): boolean {
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
    ]
    
    return dangerousPatterns.some(pattern => pattern.test(command.toLowerCase()))
  }

  private isPathSafe(filePath: string): boolean {
    // Only allow paths within the app's data directory
    const normalizedPath = path.normalize(filePath)
    return !normalizedPath.includes('..') && 
           !normalizedPath.startsWith('/') && 
           !normalizedPath.includes('system32') &&
           !normalizedPath.includes('windows')
  }

  setSafeMode(enabled: boolean): void {
    this.safeMode = enabled
  }

  isSafeMode(): boolean {
    return this.safeMode
  }
}
