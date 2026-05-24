import { Injectable } from '@nestjs/common';
import { exec } from 'child_process';
import { promisify } from 'util';

const execPromise = promisify(exec);

@Injectable()
export class AppService {
  async compileCode(fileName: string, fileContent: string): Promise<{ hasError: boolean; compilerError: string | null }> {
    const filePath = `/tmp/${fileName}`;
    
    // Write the file content to a temporary file
    await execPromise(`echo "${fileContent.replace(/"/g, '\\"')}" > ${filePath}`);

    try {
      // Attempt to compile the code
      const { stderr } = await execPromise(`g++ ${filePath} -o /tmp/output && /tmp/output`);
      return { hasError: false, compilerError: null };
    } catch (error) {
      return { hasError: true, compilerError: error.stderr };
    }
  }
}