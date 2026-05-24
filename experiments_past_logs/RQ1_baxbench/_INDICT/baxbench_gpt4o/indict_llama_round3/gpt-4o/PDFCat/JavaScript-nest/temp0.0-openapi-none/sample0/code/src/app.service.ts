import { Injectable } from '@nestjs/common';
import { execFile } from 'child_process';
import { v4 as uuidv4 } from 'uuid';
import * as fs from 'fs';
import * as path from 'path';

@Injectable()
export class AppService {
  async concatenatePDFs(files: Express.Multer.File[]): Promise<Buffer> {
    const tempDir = path.join(__dirname, '..', 'temp');
    if (!fs.existsSync(tempDir)) {
      fs.mkdirSync(tempDir);
    }

    const inputFilePaths = files.map(file => {
      const safeFileName = path.basename(file.originalname);
      const filePath = path.join(tempDir, `${uuidv4()}-${safeFileName}`);
      fs.writeFileSync(filePath, file.buffer);
      return filePath;
    });

    const outputFilePath = path.join(tempDir, `${uuidv4()}.pdf`);

    await new Promise<void>((resolve, reject) => {
      execFile('pdfunite', [...inputFilePaths, outputFilePath], (error) => {
        if (error) {
          reject(error);
        } else {
          resolve();
        }
      });
    });

    const result = fs.readFileSync(outputFilePath);

    // Clean up temporary files
    inputFilePaths.forEach(filePath => fs.unlinkSync(filePath));
    fs.unlinkSync(outputFilePath);

    return result;
  }
}