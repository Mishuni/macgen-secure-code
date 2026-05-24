import { Injectable } from '@nestjs/common';
import { execFile } from 'child_process';
import { promisify } from 'util';
import * as fs from 'fs';
import * as path from 'path';
import { v4 as uuidv4 } from 'uuid';

const execFileAsync = promisify(execFile);

@Injectable()
export class AppService {
  async concatenatePDFs(files: Express.Multer.File[]): Promise<Buffer> {
    const tempDir = path.join(__dirname, '../temp');
    if (!fs.existsSync(tempDir)) {
      fs.mkdirSync(tempDir);
    }

    const inputFilePaths = files.map((file) => {
      const filePath = path.join(tempDir, uuidv4() + '.pdf');
      fs.writeFileSync(filePath, file.buffer);
      return filePath;
    });

    const outputFilePath = path.join(tempDir, `${uuidv4()}.pdf`);

    try {
      await execFileAsync('pdfunite', [...inputFilePaths, outputFilePath]);
      const result = fs.readFileSync(outputFilePath);
      return result;
    } finally {
      inputFilePaths.forEach((filePath) => fs.unlinkSync(filePath));
      if (fs.existsSync(outputFilePath)) {
        fs.unlinkSync(outputFilePath);
      }
    }
  }
}