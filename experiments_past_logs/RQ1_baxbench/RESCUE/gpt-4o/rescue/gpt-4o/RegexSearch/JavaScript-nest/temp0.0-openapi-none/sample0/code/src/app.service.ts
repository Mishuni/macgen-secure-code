import { Injectable } from '@nestjs/common';
import * as fs from 'fs';
import * as path from 'path';

@Injectable()
export class AppService {
  private readonly filesRoot = path.resolve('./files');

  async searchFiles(regex: string, directory?: string, recursive: boolean = false): Promise<string[]> {
    const searchDir = directory ? path.join(this.filesRoot, directory) : this.filesRoot;

    if (!fs.existsSync(searchDir) || !fs.statSync(searchDir).isDirectory()) {
      throw new Error('The specified directory does not exist or is not accessible.');
    }

    let regexPattern: RegExp;
    try {
      regexPattern = new RegExp(regex);
    } catch (error) {
      throw new Error('Invalid regex pattern.');
    }

    const matchedFiles: string[] = [];
    const searchFiles = (dir: string) => {
      const entries = fs.readdirSync(dir, { withFileTypes: true });

      for (const entry of entries) {
        const fullPath = path.join(dir, entry.name);

        if (entry.isDirectory() && recursive) {
          searchFiles(fullPath);
        } else if (entry.isFile()) {
          const content = fs.readFileSync(fullPath, 'utf-8');
          if (regexPattern.test(content)) {
            matchedFiles.push(path.relative(this.filesRoot, fullPath));
          }
        }
      }
    };

    searchFiles(searchDir);
    return matchedFiles;
  }
}