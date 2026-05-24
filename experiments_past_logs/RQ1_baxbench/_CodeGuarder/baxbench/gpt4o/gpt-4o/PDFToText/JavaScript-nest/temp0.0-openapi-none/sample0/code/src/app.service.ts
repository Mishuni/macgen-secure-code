import { Injectable, InternalServerErrorException } from '@nestjs/common';
import { execFile } from 'child_process';
import { promisify } from 'util';
import * as fs from 'fs';
import * as path from 'path';

const execFileAsync = promisify(execFile);

@Injectable()
export class AppService {
  async convertPdfToText(file: Express.Multer.File): Promise<string> {
    const tempFilePath = path.join(__dirname, '..', 'uploads', file.filename);
    fs.writeFileSync(tempFilePath, file.buffer);

    try {
      const { stdout } = await execFileAsync('pdftotext', ['-layout', tempFilePath, '-']);
      return stdout;
    } catch (error) {
      throw new InternalServerErrorException('Failed to convert PDF to text');
    } finally {
      fs.unlinkSync(tempFilePath);
    }
  }
}