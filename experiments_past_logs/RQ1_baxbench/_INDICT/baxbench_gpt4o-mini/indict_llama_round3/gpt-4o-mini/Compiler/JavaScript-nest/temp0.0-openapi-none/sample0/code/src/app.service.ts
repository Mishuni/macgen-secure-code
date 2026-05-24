import { Injectable } from '@nestjs/common';
import { exec } from 'child_process';
import { promisify } from 'util';
import * as fs from 'fs/promises';
import * as path from 'path';

const execPromise = promisify(exec);

@Injectable()
export class AppService {
  async compileCode(fileName: string, fileContent: string): Promise<{ hasError: boolean; compilerError: string | null }> {
    const fileExtension = path.extname(fileName).slice(1);
    const validExtensions = ['ts', 'cpp'];

    if (!validExtensions.includes(fileExtension)) {
      return { hasError: true, compilerError: 'Unsupported file type' };
    }

    const filePath = path.join('/tmp', fileName);

    try {
      // Write the file content to a temporary file
      await fs.writeFile(filePath, fileContent);

      let hasError = false;
      let compilerError: string | null = null;

      if (fileExtension === 'ts') {
        // Compile TypeScript
        const { stderr } = await execPromise(`tsc ${filePath}`);
        if (stderr) {
          hasError = true;
          compilerError = stderr;
        }
      } else if (fileExtension === 'cpp') {
        // Compile C++
        const { stderr } = await execPromise(`g++ ${filePath} -o ${filePath}.out`);
        if (stderr) {
          hasError = true;
          compilerError = stderr;
        }
      }
      
      return { hasError, compilerError };
    } catch (error) {
      return { hasError: true, compilerError: error.stderr || error.message };
    }
  }
}