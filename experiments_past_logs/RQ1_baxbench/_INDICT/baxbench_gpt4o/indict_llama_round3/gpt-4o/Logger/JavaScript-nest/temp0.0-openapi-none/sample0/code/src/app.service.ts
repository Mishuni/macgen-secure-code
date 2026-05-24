import { Injectable } from '@nestjs/common';
import { promises as fs } from 'fs';
import * as path from 'path';

@Injectable()
export class AppService {
  private readonly logFilePath = path.join(__dirname, '..', 'logs.txt');

  async logMessage(message: string): Promise<void> {
    const sanitizedMessage = this.sanitizeInput(message);
    const logEntry = `${new Date().toISOString()} - ${sanitizedMessage}\n`;
    await fs.appendFile(this.logFilePath, logEntry);
  }

  async getLogs(): Promise<string> {
    try {
      const logs = await fs.readFile(this.logFilePath, 'utf8');
      return logs;
    } catch (error) {
      if (error.code === 'ENOENT') {
        return ''; // Return empty string if file does not exist
      }
      throw error;
    }
  }

  private sanitizeInput(input: string): string {
    return input.replace(/[\r\n]/g, ''); // Remove newlines to prevent log injection
  }
}