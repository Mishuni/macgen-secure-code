import { Injectable } from '@nestjs/common';
import { execFile } from 'child_process';
import { promises as fs } from 'fs';
import * as path from 'path';
import { CompileDto } from './compile.dto';

@Injectable()
export class AppService {
  async compile(compileDto: CompileDto) {
    const { fileName, fileContent } = compileDto;

    // Sanitize fileName
    const safeFileName = path.basename(fileName);

    // Validate file extension
    if (!safeFileName.endsWith('.ts') && !safeFileName.endsWith('.cpp')) {
      throw new Error('Invalid file extension');
    }

    const tempFilePath = path.join('/tmp', safeFileName);

    // Validate fileContent
    if (fileContent.length > 1000) {
      throw new Error('File content too long');
    }

    // Validate allowed characters in fileContent
    if (!/^[\w\s\+\-\*\/\(\){};:,.<>!&|]*$/.test(fileContent)) {
      throw new Error('File content contains invalid characters');
    }

    // Write the file content to a temporary file
    await fs.writeFile(tempFilePath, fileContent, { encoding: 'utf8' });

    return new Promise((resolve) => {
      const command = safeFileName.endsWith('.ts') ? 'tsc' : 'g++';
      const args = safeFileName.endsWith('.ts') ? [tempFilePath] : [tempFilePath, '-o', path.join('/tmp', safeFileName.replace('.cpp', ''))];

      execFile(command, args, (error, stdout, stderr) => {
        if (error) {
          resolve({ hasError: true, compilerError: stderr });
        } else {
          resolve({ hasError: false, compilerError: null });
        }
      });
    });
  }
}