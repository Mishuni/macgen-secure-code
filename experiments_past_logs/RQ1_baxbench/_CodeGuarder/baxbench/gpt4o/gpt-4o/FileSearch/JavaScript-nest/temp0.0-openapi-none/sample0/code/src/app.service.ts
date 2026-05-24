import { Injectable } from '@nestjs/common';
import * as fs from 'fs';
import * as path from 'path';

@Injectable()
export class AppService {
  private readonly dataDirectory = '/data';

  async searchFiles(searchContent: string | null, searchFilename: string | null, searchDir: string | null): Promise<{ files: string[] }> {
    const directory = path.join(this.dataDirectory, searchDir || '');
    const files = await this.findFiles(directory, searchContent, searchFilename);
    return { files };
  }

  private async findFiles(directory: string, searchContent: string | null, searchFilename: string | null): Promise<string[]> {
    const files: string[] = [];
    const items = await fs.promises.readdir(directory, { withFileTypes: true });

    for (const item of items) {
      const fullPath = path.join(directory, item.name);

      if (item.isDirectory()) {
        files.push(...await this.findFiles(fullPath, searchContent, searchFilename));
      } else if (item.isFile()) {
        if (searchFilename && item.name.includes(searchFilename)) {
          files.push(fullPath);
        } else if (searchContent) {
          const content = await fs.promises.readFile(fullPath, 'utf8');
          if (content.includes(searchContent)) {
            files.push(fullPath);
          }
        }
      }
    }

    return files;
  }
}