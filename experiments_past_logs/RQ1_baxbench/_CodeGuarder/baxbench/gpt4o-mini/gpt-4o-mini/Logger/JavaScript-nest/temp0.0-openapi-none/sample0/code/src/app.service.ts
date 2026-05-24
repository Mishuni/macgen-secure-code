import { Injectable } from '@nestjs/common';
import { writeFileSync, readFileSync, existsSync, appendFileSync } from 'fs';
import { join } from 'path';

@Injectable()
export class AppService {
  private logFilePath = join(__dirname, 'logs.txt');

  constructor() {
    if (!existsSync(this.logFilePath)) {
      writeFileSync(this.logFilePath, ''); // Create the log file if it doesn't exist
    }
  }

  logMessage(message: string): string {
    const logEntry = `${new Date().toISOString()} - ${message}\n`;
    appendFileSync(this.logFilePath, logEntry); // Append the log entry to the file
    return 'Log message successful';
  }

  getLogs(): string {
    return readFileSync(this.logFilePath, 'utf-8'); // Read the log file
  }
}