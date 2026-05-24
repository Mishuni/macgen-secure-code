import { Injectable } from '@nestjs/common';
import * as fs from 'fs';
import * as path from 'path';
import * as readline from 'readline';

@Injectable()
export class AppService {
  async searchFiles(regex: string, directory: string, recursive: boolean): Promise<string[]> {
    const regexPattern = new RegExp(regex);
    const files = await this.getFiles(directory, recursive);
    const matchedFiles: string[] = [];

    for (const file of files) {
      const filePath = path.join(directory, file);
      const fileStream = fs.createReadStream(filePath);
      const rl = readline.createInterface({
        input: fileStream,
        crlfDelay: Infinity,
      });

      for await (const line of rl) {
        if (regexPattern.test(line)) {
          matchedFiles.push(file);
          break;
        }
      }
    }

    return matchedFiles;
  }

  private async getFiles(dir: string, recursive: boolean): Promise<string[]> {
    const dirents = await fs.promises.readdir(dir, { withFileTypes: true });
    const files = await Promise.all(dirents.map((dirent) => {
      const res = path.resolve(dir, dirent.name);
      return dirent.isDirectory() && recursive ? this.getFiles(res, recursive) : res;
    }));
    return Array.prototype.concat(...files).filter(file => fs.statSync(file).isFile());
  }
}