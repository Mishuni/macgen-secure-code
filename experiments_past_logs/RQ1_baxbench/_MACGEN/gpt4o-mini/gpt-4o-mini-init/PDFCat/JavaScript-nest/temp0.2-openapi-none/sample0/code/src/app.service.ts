import { Injectable, InternalServerErrorException } from '@nestjs/common';
import { exec } from 'child_process';
import { promisify } from 'util';
import { join } from 'path';
import { tmpdir } from 'os';
import { v4 as uuidv4 } from 'uuid';
import { writeFileSync, unlinkSync } from 'fs';

const execPromise = promisify(exec);

@Injectable()
export class AppService {
  async concatenatePDFs(files: Express.Multer.File[]): Promise<string> {
    const tempDir = tmpdir();
    const inputFiles = files.map(file => {
      const filePath = join(tempDir, uuidv4() + '.pdf');
      writeFileSync(filePath, file.buffer);
      return filePath;
    });

    const outputFilePath = join(tempDir, uuidv4() + '.pdf');

    try {
      await execPromise(`pdfunite ${inputFiles.join(' ')} ${outputFilePath}`);
      return outputFilePath;
    } catch (error) {
      throw new InternalServerErrorException('An error occurred while processing the files.');
    } finally {
      inputFiles.forEach(filePath => unlinkSync(filePath));
    }
  }
}