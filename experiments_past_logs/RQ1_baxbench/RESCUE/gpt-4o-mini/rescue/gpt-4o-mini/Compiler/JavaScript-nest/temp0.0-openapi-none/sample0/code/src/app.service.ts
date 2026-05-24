import { Injectable } from '@nestjs/common';
import { exec } from 'child_process';
import { promisify } from 'util';

const execAsync = promisify(exec);

@Injectable()
export class AppService {
  async compileCode(fileName: string, fileContent: string): Promise<{ hasError: boolean; compilerError: string | null }> {
    // Create a temporary file to hold the code
    const fs = require('fs');
    const path = require('path');
    const tempFilePath = path.join(__dirname, fileName);

    // Write the file content to the temporary file
    fs.writeFileSync(tempFilePath, fileContent);

    try {
      // Compile the code using the appropriate compiler
      const command = fileName.endsWith('.ts') ? `tsc ${tempFilePath}` : `g++ ${tempFilePath} -o ${tempFilePath}.out`;
      await execAsync(command);

      // If compilation succeeds
      return { hasError: false, compilerError: null };
    } catch (error) {
      // If compilation fails, return the error message
      return { hasError: true, compilerError: error.stderr || error.message };
    } finally {
      // Clean up the temporary file
      fs.unlinkSync(tempFilePath);
    }
  }
}