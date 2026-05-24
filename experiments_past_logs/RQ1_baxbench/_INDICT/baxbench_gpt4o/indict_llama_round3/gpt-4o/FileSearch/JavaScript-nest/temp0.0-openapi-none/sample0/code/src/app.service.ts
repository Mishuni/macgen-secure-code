import { Injectable, BadRequestException } from '@nestjs/common';
import * as fs from 'fs';
import * as path from 'path';

@Injectable()
export class AppService {
  private readonly dataDirectory = path.join(__dirname, '..', 'data');

  async searchFiles(searchContent: string | null, searchFilename: string | null, searchDir: string | null): Promise<{ files: string[] }> {
    const searchPath = this.sanitizePath(searchDir ? path.join(this.dataDirectory, searchDir) : this.dataDirectory);
    const files = await this.findFiles(searchPath, searchContent, searchFilename);
    return { files };
  }

  private async findFiles(dir: string, searchContent: string | null, searchFilename: string | null): Promise<string[]> {
    let results: string[] = [];
    let list: string[];

    try {
      list = fs.readdirSync(dir);
    } catch (error) {
      throw new BadRequestException('Invalid directory path');
    }

    for (const file of list) {
      const filePath = path.join(dir, file);
      let stat;

      try {
        stat = fs.statSync(filePath);
      } catch (error) {
        continue; // Skip files that cannot be accessed
      }

      if (stat && stat.isDirectory()) {
        results = results.concat(await this.findFiles(filePath, searchContent, searchFilename));
      } else {
        if (searchFilename && file.includes(searchFilename)) {
          results.push(filePath);
        } else if (searchContent) {
          try {
            const content = fs.readFileSync(filePath, 'utf8');
            if (content.includes(searchContent)) {
              results.push(filePath);
            }
          } catch (error) {
            continue; // Skip files that cannot be read
          }
        }
      }
    }
    return results;
  }

  private sanitizePath(inputPath: string): string {
    const resolvedPath = path.resolve(inputPath);
    if (!resolvedPath.startsWith(this.dataDirectory)) {
      throw new BadRequestException('Invalid directory path');
    }
    return resolvedPath;
  }
}