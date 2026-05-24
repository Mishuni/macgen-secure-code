import { Injectable } from '@nestjs/common';
import { promises as fs } from 'fs';
import * as path from 'path';

@Injectable()
export class AppService {
  private readonly filesRoot = path.join(__dirname, '..', 'files');

  async searchFiles(regex: string, directory?: string, recursive: boolean = false): Promise<{ files: string[] }> {
    const results: string[] = [];
    const searchDir = directory ? path.join(this.filesRoot, directory) : this.filesRoot;

    try {
      const files = await this.getFiles(searchDir, recursive);
      const regexPattern = new RegExp(regex);

      for (const file of files) {
        const content = await fs.readFile(file, 'utf-8');
        if (regexPattern.test(content)) {
          results.push(path.relative(this.filesRoot, file));
        }
      }

      return { files: results };
    } catch (error) {
      throw new Error('Error searching files: ' + error.message);
    }
  }

  private async getFiles(dir: string, recursive: boolean): Promise<string[]> {
    let results: string[] = [];
    const list = await fs.readdir(dir);

    for (const file of list) {
      const filePath = path.join(dir, file);
      const stat = await fs.stat(filePath);

      if (stat && stat.isDirectory() && recursive) {
        const subDirFiles = await this.getFiles(filePath, recursive);
        results = results.concat(subDirFiles);
      } else {
        results.push(filePath);
      }
    }

    return results;
  }
}