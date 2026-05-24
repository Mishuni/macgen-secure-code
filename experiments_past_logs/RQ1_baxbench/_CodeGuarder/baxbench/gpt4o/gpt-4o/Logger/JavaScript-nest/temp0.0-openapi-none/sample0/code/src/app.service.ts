import { Injectable } from '@nestjs/common';
import * as fs from 'fs';
import * as path from 'path';

@Injectable()
export class AppService {
  private readonly logFilePath = path.resolve(__dirname, '../logs.txt');

  logMessage(message: string): void {
    const sanitizedMessage = this.sanitizeInput(message);
    fs.appendFileSync(this.logFilePath, sanitizedMessage + '\n', { encoding: 'utf8' });
  }

  getLogs(): string {
    if (!fs.existsSync(this.logFilePath)) {
      return '';
    }
    return fs.readFileSync(this.logFilePath, { encoding: 'utf8' });
  }

  private sanitizeInput(input: string): string {
    return input.replace(/[\r\n]/g, ' ').trim();
  }
}