import { Injectable } from '@nestjs/common';
import * as fs from 'fs';
import * as path from 'path';

@Injectable()
export class AppService {
  private readonly filesRoot = path.join(__dirname, '..', 'files');

  async searchFiles(regex: string, directory: string = '', recursive: boolean = false): Promise<string[]> {
    const fullPath = path.join(this.filesRoot, directory);
    if (!fs.existsSync(fullPath) || !fs.lstatSync(fullPath).isDirectory()) {
      throw new Error('Invalid directory.');
    }

    const pattern = new RegExp(regex);
    const matchingFiles: string[] = [];

    const searchDirectory = (dir: string) => {
      const files = fs.readdirSync(dir);
      for (const file of files) {
        const filePath = path.join(dir, file);
        if (fs.lstatSync(filePath).isDirectory() && recursive) {
          searchDirectory(filePath);
        } else {
          const content = fs.readFileSync(filePath, 'utf-8');
          if (pattern.test(content)) {
            matchingFiles.push(path.relative(this.filesRoot, filePath));
          }
        }
      }
    };

    searchDirectory(fullPath);
    return matchingFiles;
  }
}