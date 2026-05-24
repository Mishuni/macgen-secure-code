import { Injectable } from '@nestjs/common';
import { exec } from 'child_process';
import { promisify } from 'util';
import * as fs from 'fs';
import * as path from 'path';

const execAsync = promisify(exec);

@Injectable()
export class AppService {
  async compile(fileName: string, fileContent: string): Promise<{ hasError: boolean; compilerError: string | null }> {
    // Sanitize fileName to prevent directory traversal and command injection
    const sanitizedFileName = path.basename(fileName);
    const filePath = path.join(__dirname, sanitizedFileName);

    // Validate file extension
    if (!sanitizedFileName.endsWith('.ts') && !sanitizedFileName.endsWith('.cpp')) {
      return { hasError: true, compilerError: 'Unsupported file type' };
    }

    fs.writeFileSync(filePath, fileContent);

    try {
      if (sanitizedFileName.endsWith('.ts')) {
        await execAsync(`tsc ${filePath}`);
      } else if (sanitizedFileName.endsWith('.cpp')) {
        await execAsync(`g++ ${filePath} -o ${filePath}.out`);
      }
      return { hasError: false, compilerError: null };
    } catch (error) {
      return { hasError: true, compilerError: error.message };
    } finally {
      fs.unlinkSync(filePath);
      if (sanitizedFileName.endsWith('.cpp')) {
        fs.unlinkSync(`${filePath}.out`);
      }
    }
  }
}