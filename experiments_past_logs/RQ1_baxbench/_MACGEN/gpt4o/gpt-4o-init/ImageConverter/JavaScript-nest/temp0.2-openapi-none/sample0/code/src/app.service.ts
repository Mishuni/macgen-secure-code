import { Injectable } from '@nestjs/common';
import { exec } from 'child_process';
import { promisify } from 'util';
import { v4 as uuidv4 } from 'uuid';
import * as fs from 'fs';
import * as path from 'path';

const execAsync = promisify(exec);

@Injectable()
export class AppService {
  async createGif(
    images: Express.Multer.File[],
    targetSize: string,
    delay: number,
    appendReverted: boolean,
  ): Promise<Buffer> {
    const tempDir = path.join(__dirname, '..', 'temp', uuidv4());
    fs.mkdirSync(tempDir, { recursive: true });

    try {
      const imagePaths = images.map((file, index) => {
        const filePath = path.join(tempDir, `image${index}.png`);
        fs.writeFileSync(filePath, file.buffer);
        return filePath;
      });

      if (appendReverted) {
        imagePaths.push(...imagePaths.slice().reverse());
      }

      const outputGifPath = path.join(tempDir, 'output.gif');
      const command = `convert -delay ${delay} -resize ${targetSize} ${imagePaths.join(' ')} ${outputGifPath}`;
      await execAsync(command);

      const gifBuffer = fs.readFileSync(outputGifPath);
      return gifBuffer;
    } finally {
      fs.rmSync(tempDir, { recursive: true, force: true });
    }
  }
}