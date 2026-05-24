import { Injectable } from '@nestjs/common';
import { exec } from 'child_process';
import { promisify } from 'util';
import * as fs from 'fs';
import * as path from 'path';

const execAsync = promisify(exec);

@Injectable()
export class AppService {
  async compileCode(fileName: string, fileContent: string): Promise<{ hasError: boolean; compilerError: string | null }> {
    const tempDir = path.join(__dirname, 'temp');
    if (!fs.existsSync(tempDir)) {
      fs.mkdirSync(tempDir);
    }

    const filePath = path.join(tempDir, fileName);
    fs.writeFileSync(filePath, fileContent);

    try {
      let command = '';
      if (fileName.endsWith('.ts')) {
        command = `tsc ${filePath}`;
      } else if (fileName.endsWith('.cpp')) {
        command = `g++ ${filePath} -o ${filePath}.out`;
      } else {
        throw new Error('Unsupported file type');
      }

      await execAsync(command);
      return { hasError: false, compilerError: null };
    } catch (error) {
      return { hasError: true, compilerError: error.stderr || error.message };
    } finally {
      fs.unlinkSync(filePath);
      if (fileName.endsWith('.cpp')) {
        fs.unlinkSync(`${filePath}.out`);
      }
    }
  }
}