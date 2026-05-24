import { Injectable } from '@nestjs/common';
import { basename } from 'path';

@Injectable()
export class AppService {
  /**
   * Sanitizes the filename by removing any directory traversal attempts
   * and ensuring only the base filename is returned.
   * @param filename The input filename
   * @returns The sanitized filename
   */
  sanitizeFilename(filename: string): string {
    return basename(filename);
  }
}