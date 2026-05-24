import { Injectable } from '@nestjs/common';
import { promises as fs } from 'fs';
import { join } from 'path';

@Injectable()
export class AppService {
  private readonly uploadDir = './uploads';

  async saveFile(filename: string): Promise<string> {
    // In a real application, you would save the file metadata to a database
    return filename;
  }

  async getFilePath(imageId: string): Promise<string | null> {
    const filePath = join(this.uploadDir, imageId);
    try {
      await fs.access(filePath);
      return filePath;
    } catch {
      return null;
    }
  }
}