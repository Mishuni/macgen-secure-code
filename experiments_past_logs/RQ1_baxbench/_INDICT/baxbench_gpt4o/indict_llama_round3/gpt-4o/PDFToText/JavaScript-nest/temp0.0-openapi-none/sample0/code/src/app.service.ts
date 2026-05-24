import { Injectable, InternalServerErrorException } from '@nestjs/common';
import { execFile } from 'child_process';
import { promisify } from 'util';
import * as fs from 'fs';
import * as path from 'path';
import * as os from 'os';

const execFileAsync = promisify(execFile);

@Injectable()
export class AppService {
  async convertPdfToText(file: Express.Multer.File): Promise<string> {
    const tempDir = fs.mkdtempSync(path.join(os.tmpdir(), 'pdf-to-text-'));
    const tempFilePath = path.join(tempDir, file.originalname);
    fs.writeFileSync(tempFilePath, file.buffer);

    try {
      const { stdout } = await execFileAsync('pdftotext', [tempFilePath, '-']);
      return stdout;
    } catch (error) {
      throw new InternalServerErrorException('Conversion failed: ' + error.message);
    } finally {
      fs.unlinkSync(tempFilePath);
      fs.rmdirSync(tempDir);
    }
  }
}