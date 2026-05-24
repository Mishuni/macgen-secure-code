import { Injectable } from '@nestjs/common';
import { appendFileSync, readFileSync } from 'fs';
import { join } from 'path';

@Injectable()
export class AppService {
  private logFilePath = join(__dirname, 'logs.txt');

  logMessage(message: string): string {
    if (message.length > 256 || /[\r\n]/.test(message)) {
      throw new Error('Invalid log message');
    }
    appendFileSync(this.logFilePath, message + '\n', 'utf8'); // Fixed newline character representation
    return 'Log message successful';
  }

  getLogs(): string {
    return readFileSync(this.logFilePath, 'utf8');
  }
}