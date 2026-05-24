import { Injectable } from '@nestjs/common';
import * as fs from 'fs';
import * as path from 'path';
import * as escape from 'escape-html';

@Injectable()
export class AppService {
  private logFilePath = path.join(__dirname, 'logs.txt');

  async logMessage(message: string): Promise<void> {
    fs.appendFileSync(this.logFilePath, message + '\n', { encoding: 'utf8' });
  }

  async getLogs(): Promise<string> {
    if (fs.existsSync(this.logFilePath)) {
      return fs.readFileSync(this.logFilePath, { encoding: 'utf8' });
    }
    return '';
  }

  sanitizeInput(input: string): string {
    return escape(input);
  }
}