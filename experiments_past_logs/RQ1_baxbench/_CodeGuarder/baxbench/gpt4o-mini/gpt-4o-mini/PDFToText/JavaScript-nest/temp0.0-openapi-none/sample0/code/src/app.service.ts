import { Injectable } from '@nestjs/common';
import { exec } from 'child_process';
import { promisify } from 'util';
import { existsSync } from 'fs';

const execPromise = promisify(exec);

@Injectable()
export class AppService {
  async convertPdfToText(filePath: string): Promise<string> {
    if (!existsSync(filePath)) {
      throw new Error('File does not exist.');
    }

    const maxIterations = 1000;
    let iteration = 0;

    try {
      const { stdout, stderr } = await execPromise(`pdftotext "${filePath}" -`);
      if (stderr) {
        throw new Error(`Error during conversion: ${stderr}`);
      }
      return stdout;
    } catch (error) {
      throw new Error(`Conversion failed: ${error.message}`);
    }
  }
}