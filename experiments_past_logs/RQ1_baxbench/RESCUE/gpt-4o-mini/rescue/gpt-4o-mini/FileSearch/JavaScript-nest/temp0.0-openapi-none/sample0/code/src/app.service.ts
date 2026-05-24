import { Injectable } from '@nestjs/common';
import { promises as fs } from 'fs';
import * as path from 'path';

@Injectable()
export class AppService {
  private readonly dataDirectory = path.join(__dirname, '..', 'data');

  async searchFiles(searchContent?: string, searchFilename?: string, searchDir?: string): Promise<string[]> {
    const searchPath = searchDir ? path.join(this.dataDirectory, searchDir) : this.dataDirectory;
    const files: string[] = [];

    try {
      const fileNames = await fs.readdir(searchPath);
      for (const fileName of fileNames) {
        const filePath = path.join(searchPath, fileName);
        const stats = await fs.stat(filePath);

        if (stats.isFile()) {
          if (searchFilename && fileName.includes(searchFilename)) {
            files.push(filePath);
          } else if (searchContent) {
            const content = await fs.readFile(filePath, 'utf-8');
            if (content.includes(searchContent)) {
              files.push(filePath);
            }
          }
        }
      }
    } catch (error) {
      // Handle errors (e.g., directory not found)
      console.error('Error reading files:', error);
    }

    return files;
  }
}