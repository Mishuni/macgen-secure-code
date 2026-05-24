import { Injectable } from '@nestjs/common';
import { execFile } from 'child_process';
import { promisify } from 'util';
import { readFile, unlink } from 'fs/promises';

const execFileAsync = promisify(execFile);

@Injectable()
export class AppService {
  async convertPdfToText(filePath: string): Promise<string> {
    const outputFilePath = filePath.replace(/\.pdf$/, '.txt');

    try {
      await execFileAsync('pdftotext', [filePath, outputFilePath]);
      const text = await readFile(outputFilePath, 'utf8');
      await unlink(filePath);
      await unlink(outputFilePath);
      return text;
    } catch (error) {
      throw new Error('Error during PDF to text conversion');
    }
  }
}