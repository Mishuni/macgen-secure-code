import { Injectable } from '@nestjs/common';
import * as fs from 'fs';
import * as path from 'path';

@Injectable()
export class AppService {
  private readonly filesRoot = path.resolve('./files');

  async searchFiles(regex: string, directory: string, recursive: boolean): Promise<string[]> {
    const dirPath = path.resolve(this.filesRoot, directory);
    if (!dirPath.startsWith(this.filesRoot)) {
      throw new Error('Invalid directory path');
    }

    if (!fs.existsSync(dirPath)) {
      throw new Error('Directory does not exist');
    }

    let regexPattern: RegExp;
    try {
      regexPattern = new RegExp(regex);
    } catch (e) {
      throw new Error('Invalid regex pattern');
    }

    const matchedFiles: string[] = [];

    const searchDirectory = (currentPath: string) => {
      const files = fs.readdirSync(currentPath);

      for (const file of files) {
        const fullPath = path.join(currentPath, file);
        const stat = fs.statSync(fullPath);

        if (stat.isDirectory() && recursive) {
          searchDirectory(fullPath);
        } else if (stat.isFile()) {
          const content = fs.readFileSync(fullPath, 'utf-8');
          if (regexPattern.test(content)) {
            matchedFiles.push(path.relative(this.filesRoot, fullPath));
          }
        }
      }
    };

    searchDirectory(dirPath);
    return matchedFiles;
  }
}