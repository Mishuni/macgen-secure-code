import { Injectable } from '@nestjs/common';
import * as fs from 'fs';
import * as path from 'path';

@Injectable()
export class AppService {
  private logFilePath = path.join(__dirname, '..', 'logs.txt');

  logMessage(message: string): void {
    try {
      fs.appendFileSync(this.logFilePath, message + '\n', 'utf8');
    } catch (error) {
      console.error('Error writing to log file:', error);
    }
  }

  getLogs(): string {
    try {
      if (fs.existsSync(this.logFilePath)) {
        return fs.readFileSync(this.logFilePath, 'utf8');
      }
      return 'No logs found';
    } catch (error) {
      console.error('Error reading log file:', error);
      return 'Error retrieving logs';
    }
  }
}