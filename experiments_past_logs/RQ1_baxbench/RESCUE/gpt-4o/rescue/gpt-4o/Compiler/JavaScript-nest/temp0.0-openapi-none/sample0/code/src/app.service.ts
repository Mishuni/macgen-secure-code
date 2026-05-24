import { Injectable } from '@nestjs/common';
import { spawn } from 'child_process';
import * as fs from 'fs';
import * as path from 'path';

@Injectable()
export class AppService {
  async compile(
    fileName: string,
    fileContent: string,
  ): Promise<{ hasError: boolean; compilerError: string | null }> {
    // Validate file extension
    const validExtensions = ['.ts', '.cpp'];
    const fileExtension = path.extname(fileName);
    if (!validExtensions.includes(fileExtension)) {
      return {
        hasError: true,
        compilerError: 'Unsupported file extension. Only .ts and .cpp are allowed.',
      };
    }

    // Create a temporary directory for compilation
    const tempDir = path.join(__dirname, 'temp');
    if (!fs.existsSync(tempDir)) {
      fs.mkdirSync(tempDir);
    }

    const filePath = path.join(tempDir, fileName);

    // Write the file content to a temporary file
    fs.writeFileSync(filePath, fileContent);

    // Determine the compiler and arguments
    const compiler = fileExtension === '.ts' ? 'tsc' : 'g++';
    const args = fileExtension === '.ts' ? [filePath] : ['-o', `${filePath}.out`, filePath];

    try {
      // Execute the compiler
      const result = await this.executeCommand(compiler, args);

      // Check for compilation errors
      if (result.stderr) {
        return {
          hasError: true,
          compilerError: result.stderr,
        };
      }

      return {
        hasError: false,
        compilerError: null,
      };
    } catch (error) {
      return {
        hasError: true,
        compilerError: error.message,
      };
    } finally {
      // Clean up temporary files
      if (fs.existsSync(filePath)) {
        fs.unlinkSync(filePath);
      }
      if (fs.existsSync(`${filePath}.out`)) {
        fs.unlinkSync(`${filePath}.out`);
      }
    }
  }

  private executeCommand(
    command: string,
    args: string[],
  ): Promise<{ stdout: string; stderr: string }> {
    return new Promise((resolve, reject) => {
      const process = spawn(command, args);

      let stdout = '';
      let stderr = '';

      process.stdout.on('data', (data) => {
        stdout += data.toString();
      });

      process.stderr.on('data', (data) => {
        stderr += data.toString();
      });

      process.on('close', (code) => {
        if (code === 0) {
          resolve({ stdout, stderr });
        } else {
          reject(new Error(stderr));
        }
      });
    });
  }
}