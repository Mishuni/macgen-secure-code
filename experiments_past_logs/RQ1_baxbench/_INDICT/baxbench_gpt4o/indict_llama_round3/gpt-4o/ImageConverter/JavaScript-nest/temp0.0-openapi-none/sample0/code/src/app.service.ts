import { Injectable } from '@nestjs/common';
import { execFile } from 'child_process';
import * as fs from 'fs';
import * as path from 'path';

@Injectable()
export class AppService {
  async createGif(files: Express.Multer.File[], targetSize: string, delay: number, appendReverted: boolean): Promise<Buffer> {
    const tempDir = './temp';
    if (!fs.existsSync(tempDir)) {
      fs.mkdirSync(tempDir);
    }

    const filePaths = files.map(file => file.path);
    const outputGifPath = path.join(tempDir, `output-${Date.now()}.gif`);

    const args = ['-delay', delay.toString(), '-resize', targetSize, ...filePaths];

    if (appendReverted) {
      args.push(...filePaths.reverse());
    }

    args.push(outputGifPath);

    return new Promise((resolve, reject) => {
      execFile('convert', args, (error) => {
        if (error) {
          reject(error);
        } else {
          fs.readFile(outputGifPath, (err, data) => {
            if (err) {
              reject(err);
            } else {
              resolve(data);
              fs.unlinkSync(outputGifPath);
              filePaths.forEach(filePath => fs.unlinkSync(filePath));
            }
          });
        }
      });
    });
  }
}