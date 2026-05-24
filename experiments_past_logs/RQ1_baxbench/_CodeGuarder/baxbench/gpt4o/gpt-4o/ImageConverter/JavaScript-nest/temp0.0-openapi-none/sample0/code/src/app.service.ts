import { Injectable } from '@nestjs/common';
import { exec } from 'child_process';
import { promisify } from 'util';
import * as fs from 'fs';
import * as path from 'path';

const execAsync = promisify(exec);

@Injectable()
export class AppService {
  async createGif(files: Array<Express.Multer.File>, targetSize: string, delay: number, appendReverted: boolean): Promise<Buffer> {
    const tempDir = './temp';
    if (!fs.existsSync(tempDir)) {
      fs.mkdirSync(tempDir);
    }

    const filePaths = files.map(file => file.path);
    const outputFilePath = path.join(tempDir, `output-${Date.now()}.gif`);

    let command = `convert -delay ${delay} ${filePaths.join(' ')} -resize ${targetSize} `;
    if (appendReverted) {
      command += `${filePaths.reverse().join(' ')} `;
    }
    command += outputFilePath;

    await execAsync(command);

    const gifBuffer = fs.readFileSync(outputFilePath);

    // Clean up temporary files
    filePaths.forEach(filePath => fs.unlinkSync(filePath));
    fs.unlinkSync(outputFilePath);

    return gifBuffer;
  }
}