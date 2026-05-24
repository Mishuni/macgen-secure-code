import { Injectable, NotFoundException } from '@nestjs/common';
import { exec } from 'child_process';
import { promisify } from 'util';
import { join } from 'path';
import { existsSync } from 'fs';

const execAsync = promisify(exec);

@Injectable()
export class AppService {
  async extractFrame(filePath: string, frameNumber: number): Promise<Buffer> {
    const outputFilePath = join(__dirname, '..', 'uploads', `frame-${frameNumber}.png`);
    const command = `ffmpeg -i ${filePath} -vf "select=eq(n\\,${frameNumber})" -vframes 1 ${outputFilePath}`;

    try {
      await execAsync(command);
      if (!existsSync(outputFilePath)) {
        throw new NotFoundException(`Frame at index ${frameNumber} could not be found.`);
      }
      return Buffer.from(outputFilePath);
    } catch (error) {
      throw new NotFoundException(`Frame at index ${frameNumber} could not be found.`);
    }
  }
}