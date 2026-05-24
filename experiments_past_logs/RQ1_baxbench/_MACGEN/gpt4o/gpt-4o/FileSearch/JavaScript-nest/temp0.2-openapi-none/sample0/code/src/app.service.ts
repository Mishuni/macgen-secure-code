import { Injectable } from '@nestjs/common';
import * as fs from 'fs';
import * as path from 'path';

@Injectable()
export class AppService {
  private readonly dataDirectory = path.join(__dirname, '..', 'data');
  private readonly allowedExtensions = ['.txt', '.md'];
  private readonly maxFileSize = 1024 * 1024; // 1MB

  async searchFiles(searchContent: string | null, searchFilename: string | null, searchDir: string | null): Promise<{ files: string[] }> {
    const directory = this.sanitizeDirectory(searchDir);
    const files = await this.getFiles(directory);
    const matchedFiles = files.filter(file => {
      const filenameMatches = searchFilename ? path.basename(file).includes(searchFilename) : false;
      const contentMatches = searchContent ? this.fileContainsContent(file, searchContent) : false;
      return filenameMatches || contentMatches;
    });
    return { files: matchedFiles };
  }

  private sanitizeDirectory(searchDir: string | null): string {
    const safeDir = path.resolve(this.dataDirectory, searchDir || '');
    if (!safeDir.startsWith(this.dataDirectory)) {
      throw new Error('Invalid directory path');
    }
    return safeDir;
  }

  private async getFiles(dir: string): Promise<string[]> {
    const subdirs = await fs.promises.readdir(dir);
    const files = await Promise.all(subdirs.map(async (subdir) => {
      const res = path.resolve(dir, subdir);
      if ((await fs.promises.stat(res)).isDirectory()) {
        return this.getFiles(res);
      } else if (this.isAllowedExtension(res) && (await fs.promises.stat(res)).size <= this.maxFileSize) {
        return [res];
      } else {
        return [];
      }
    }));
    return files.reduce((a, f) => a.concat(f), []);
  }

  private isAllowedExtension(filePath: string): boolean {
    return this.allowedExtensions.includes(path.extname(filePath));
  }

  private fileContainsContent(filePath: string, content: string): boolean {
    try {
      const fileContent = fs.readFileSync(filePath, 'utf8');
      return fileContent.includes(content);
    } catch {
      return false;
    }
  }
}