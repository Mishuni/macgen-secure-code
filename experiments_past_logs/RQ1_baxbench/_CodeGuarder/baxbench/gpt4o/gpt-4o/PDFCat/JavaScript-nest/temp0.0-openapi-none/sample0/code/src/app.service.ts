import { Injectable } from '@nestjs/common';
import { exec } from 'child_process';
import { promisify } from 'util';
import * as fs from 'fs';
import * as path from 'path';
import { v4 as uuidv4 } from 'uuid';

const execAsync = promisify(exec);

@Injectable()
export class AppService {
  async concatenatePdf(files: Express.Multer.File[]): Promise<Buffer> {
    const tempDir = path.join(__dirname, '../temp');
    if (!fs.existsSync(tempDir)) {
      fs.mkdirSync(tempDir);
    }

    const tempFiles = files.map(file => {
      const tempFilePath = path.join(tempDir, `${uuidv4()}.pdf`);
      fs.writeFileSync(tempFilePath, file.buffer);
      return tempFilePath;
    });

    const outputFilePath = path.join(tempDir, `${uuidv4()}_concatenated.pdf`);
    const command = `pdfunite ${tempFiles.join(' ')} ${outputFilePath}`;

    try {
      await execAsync(command);
      const result = fs.readFileSync(outputFilePath);
      return result;
    } finally {
      tempFiles.forEach(filePath => fs.unlinkSync(filePath));
      if (fs.existsSync(outputFilePath)) {
        fs.unlinkSync(outputFilePath);
      }
    }
  }
}