import { Injectable } from '@nestjs/common';
import * as fs from 'fs';
import * as path from 'path';
import { exec } from 'child_process';
import { promisify } from 'util';
import * as os from 'os';

const execAsync = promisify(exec);

@Injectable()
export class AppService {
  async concatenatePDFs(files: Express.Multer.File[]): Promise<string> {
    const tempDir = fs.mkdtempSync(path.join(os.tmpdir(), 'pdf-concat-'));
    const inputFilePaths: string[] = [];

    try {
      // Save uploaded files to temporary directory
      for (const file of files) {
        const tempFilePath = path.join(tempDir, file.originalname);
        fs.writeFileSync(tempFilePath, file.buffer);
        inputFilePaths.push(tempFilePath);
      }

      // Generate a temporary output file
      const outputFilePath = path.join(tempDir, 'output.pdf');

      // Use pdfunite to concatenate the files
      const command = `pdfunite ${inputFilePaths.join(' ')} ${outputFilePath}`;
      await execAsync(command);

      // Ensure the output file exists
      if (!fs.existsSync(outputFilePath)) {
        throw new Error('Failed to generate concatenated PDF.');
      }

      return outputFilePath;
    } catch (error) {
      throw new Error('Error during PDF concatenation: ' + error.message);
    } finally {
      // Cleanup input files
      for (const filePath of inputFilePaths) {
        if (fs.existsSync(filePath)) {
          fs.unlinkSync(filePath);
        }
      }
    }
  }

  cleanupFile(filePath: string): void {
    if (fs.existsSync(filePath)) {
      fs.unlinkSync(filePath);
    }
  }
}