import { Injectable, BadRequestException } from '@nestjs/common';
import * as fs from 'fs/promises';
import * as path from 'path';

@Injectable()
export class AppService {
  private readonly dataDirectory = path.join(__dirname, '..', 'data');

  async searchFiles({ search_content, search_filename, search_dir }: { search_content?: string; search_filename?: string; search_dir?: string }) {
    const results: string[] = [];
    const searchPath = search_dir ? path.join(this.dataDirectory, search_dir) : this.dataDirectory;

    try {
      const files = await fs.readdir(searchPath);

      for (const file of files) {
        const filePath = path.join(searchPath, file);
        const stats = await fs.stat(filePath);

        if (stats.isFile()) {
          let contentMatches = true;
          let filenameMatches = true;

          if (search_content) {
            const fileContent = await fs.readFile(filePath, 'utf-8');
            contentMatches = fileContent.includes(search_content);
          }

          if (search_filename) {
            filenameMatches = file.startsWith(search_filename);
          }

          if (contentMatches || filenameMatches) {
            results.push(filePath);
          }
        }
      }
    } catch (error) {
      console.error('Error reading files:', error);
      throw new BadRequestException('Invalid input or directory does not exist');
    }

    return { files: results };
  }
}