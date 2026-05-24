import { Injectable } from '@nestjs/common';
import { writeFileSync, appendFileSync, readFileSync, existsSync } from 'fs';

@Injectable()
export class AppService {
  private readonly logFilePath = 'logs.txt';

  constructor() {
    if (!existsSync(this.logFilePath)) {
      writeFileSync(this.logFilePath, '', { mode: 0o600 });
    }
  }

  sanitizeMessage(message: string): string {
    return message.replace(/[^\w\s.,!?]/g, '');
  }

  logMessage(message: string): void {
    try {
      appendFileSync(this.logFilePath, message + '\n');
    } catch (error) {
      console.error('Failed to write log:', error.message);
    }
  }

  getLogs(): string {
    try {
      return readFileSync(this.logFilePath, 'utf8');
    } catch (error) {
      console.error('Failed to read logs:', error.message);
      return '';
    }
  }
}