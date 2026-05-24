import { Injectable } from '@nestjs/common';
import { promises as fs } from 'fs';
import * as path from 'path';

@Injectable()
export class AppService {
  private readonly filesRoot = path.join(__dirname, '../files');

  async searchFiles(regex: string, directory: string = '', recursive: boolean = false): Promise<string[]> {
    const dirPath = path.join(this.filesRoot, directory);
    const results: string[] = [];

    const isValidRegex = this.validateRegex(regex);
    if (!isValidRegex) {
      throw { status: 400, message: 'Invalid regex pattern' };
    }

    const files = await this.getFiles(dirPath, recursive);
    for (const file of files) {
      const content = await fs.readFile(file, 'utf-8');
      if (new RegExp(regex).test(content)) {
        results.push(path.relative(this.filesRoot, file));
      }
    }

    return results;
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

  private validateRegex(regex: string): boolean {
    try {
      new RegExp(regex);
      return true;
    } catch {
      return false;
    }
  }
}