import { Injectable } from '@nestjs/common';
import { exec } from 'child_process';
import { promisify } from 'util';
import * as fs from 'fs';
import * as path from 'path';

const execPromise = promisify(exec);

@Injectable()
export class AppService {
  async convertPdfToText(fileBuffer: Buffer): Promise<string> {
    const tempFilePath = path.join(__dirname, 'temp.pdf');
    const outputFilePath = path.join(__dirname, 'output.txt');

    // Write the buffer to a temporary PDF file
    await fs.promises.writeFile(tempFilePath, fileBuffer);

    try {
      // Use pdftotext to convert PDF to text
      await execPromise(`pdftotext ${tempFilePath} ${outputFilePath}`);

      // Read the output text file
      const text = await fs.promises.readFile(outputFilePath, 'utf-8');
      return text;
    } catch (error) {
      throw new Error('Conversion failed');
    } finally {
      // Clean up temporary files
      try {
        await fs.promises.unlink(tempFilePath);
        await fs.promises.unlink(outputFilePath);
      } catch (cleanupError) {
        console.error('Error cleaning up temporary files:', cleanupError);
      }
    }
  }
}