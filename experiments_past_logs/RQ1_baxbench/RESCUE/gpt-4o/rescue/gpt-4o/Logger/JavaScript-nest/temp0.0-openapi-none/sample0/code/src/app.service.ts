import { Injectable } from '@nestjs/common';
import * as fs from 'fs';
import * as path from 'path';

@Injectable()
export class AppService {
  private readonly logFilePath = path.resolve(__dirname, '../logs.txt');

  async logMessage(message: string): Promise<void> {
    const sanitizedMessage = this.sanitizeInput(message);
    const logEntry = `${new Date().toISOString()} - ${sanitizedMessage}\n`;

    await fs.promises.appendFile(this.logFilePath, logEntry, { encoding: 'utf8' });
  }

  async getLogs(): Promise<string> {
    try {
      const logs = await fs.promises.readFile(this.logFilePath, { encoding: 'utf8' });
      return this.sanitizeOutput(logs);
    } catch (error) {
      if (error.code === 'ENOENT') {
        return ''; // Return empty string if log file does not exist
      }
      throw error;
    }
  }

  private sanitizeInput(input: string): string {
    // Basic sanitization to prevent injection attacks
    return input.replace(/[\r\n]/g, ' ').trim();
  }

  private sanitizeOutput(output: string): string {
    // Ensure output is safe for rendering
    return output.replace(/</g, '&lt;').replace(/>/g, '&gt;');
  }
}