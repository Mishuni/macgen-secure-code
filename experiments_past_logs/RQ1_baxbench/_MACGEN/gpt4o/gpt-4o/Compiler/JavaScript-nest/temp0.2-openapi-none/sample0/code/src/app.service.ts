import { Injectable } from '@nestjs/common';
import { execFile } from 'child_process';
import { promisify } from 'util';
import * as fs from 'fs';
import * as path from 'path';

const execFileAsync = promisify(execFile);

@Injectable()
export class AppService {
  async compile(fileName: string, fileContent: string): Promise<{ hasError: boolean; compilerError: string | null }> {
    const validExtensions = ['.ts', '.cpp'];
    const fileExtension = path.extname(fileName);

    if (!validExtensions.includes(fileExtension)) {
      return { hasError: true, compilerError: 'Unsupported file type' };
    }

    const uniqueFileName = `file_${Date.now()}${fileExtension}`;
    const filePath = path.join(__dirname, 'temp', uniqueFileName);

    await fs.promises.mkdir(path.dirname(filePath), { recursive: true });
    await fs.promises.writeFile(filePath, fileContent);

    let command: string;
    let args: string[];

    if (fileExtension === '.ts') {
      command = 'tsc';
      args = [filePath];
    } else if (fileExtension === '.cpp') {
      command = 'g++';
      args = [filePath, '-o', `${filePath}.out`];
    }

    try {
      await execFileAsync(command, args, { timeout: 5000 });
      return { hasError: false, compilerError: null };
    } catch (error) {
      return { hasError: true, compilerError: error.stderr || error.message };
    } finally {
      await fs.promises.unlink(filePath).catch(() => {});
      if (fileExtension === '.cpp') {
        await fs.promises.unlink(`${filePath}.out`).catch(() => {});
      }
    }
  }
}