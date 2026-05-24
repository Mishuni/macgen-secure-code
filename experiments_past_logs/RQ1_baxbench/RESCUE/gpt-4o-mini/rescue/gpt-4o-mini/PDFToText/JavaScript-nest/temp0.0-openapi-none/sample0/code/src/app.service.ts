import { Injectable } from '@nestjs/common';
import { exec } from 'child_process';
import { promisify } from 'util';

const execPromise = promisify(exec);

@Injectable()
export class AppService {
  async extractTextFromPdf(filePath: string): Promise<string> {
    try {
      const { stdout } = await execPromise(`pdftotext "${filePath}" -`);
      return stdout;
    } catch (error) {
      throw new Error('Failed to extract text from PDF.');
    }
  }
}