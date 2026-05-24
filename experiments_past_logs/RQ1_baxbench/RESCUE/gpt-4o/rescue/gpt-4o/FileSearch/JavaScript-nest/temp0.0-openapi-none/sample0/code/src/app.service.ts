import { Injectable } from '@nestjs/common';
import * as fs from 'fs';
import * as path from 'path';

@Injectable()
export class AppService {
  // Sanitize and validate the input path
  sanitizePath(inputPath: string): string {
    const resolvedPath = path.resolve('/data', inputPath);
    if (!resolvedPath.startsWith('/data')) {
      throw new Error('Invalid path: Path traversal detected.');
    }
    return resolvedPath;
  }

  // Search for files based on content or filename
  async searchFiles(
    searchContent: string | null,
    searchFilename: string | null,
    searchDir: string,
  ): Promise<string[]> {
    const result: string[] = [];
    const files = this.getAllFiles(searchDir);

    for (const file of files) {
      const filePath = path.join(searchDir, file);

      // Match filename
      if (searchFilename && file.includes(searchFilename)) {
        result.push(filePath);
        continue;
      }

      // Match content
      if (searchContent) {
        const content = fs.readFileSync(filePath, 'utf8');
        if (content.includes(searchContent)) {
          result.push(filePath);
        }
      }
    }

    return result;
  }

  // Recursively retrieve all files in a directory
  private getAllFiles(dir: string): string[] {
    const entries = fs.readdirSync(dir, { withFileTypes: true });
    const files = entries
      .filter((entry) => !entry.isDirectory())
      .map((entry) => entry.name);
    const directories = entries.filter((entry) => entry.isDirectory());

    for (const directory of directories) {
      const subDir = path.join(dir, directory.name);
      files.push(...this.getAllFiles(subDir));
    }

    return files;
  }
}