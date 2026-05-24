import { Injectable } from '@nestjs/common';
import * as fs from 'fs';
import * as path from 'path';

@Injectable()
export class AppService {
  searchFiles(searchContent?: string, searchFilename?: string, searchDir?: string) {
    if (searchDir && (!/^[a-zA-Z0-9/_-]*$/.test(searchDir) || searchDir.includes('..'))) {
      throw new Error('Invalid directory');
    }

    const directoryPath = path.resolve('/data', searchDir || '');
    const files: string[] = [];

    try {
      const fileList = fs.readdirSync(directoryPath);
      fileList.forEach(file => {
        const filePath = path.join(directoryPath, file);
        if (searchFilename && file.includes(searchFilename)) {
          files.push(filePath);
        } else if (searchContent) {
          const content = fs.readFileSync(filePath, 'utf8');
          if (content.includes(searchContent)) {
            files.push(filePath);
          }
        }
      });
    } catch (error) {
      throw new Error('Error reading files');
    }

    return { files };
  }
}