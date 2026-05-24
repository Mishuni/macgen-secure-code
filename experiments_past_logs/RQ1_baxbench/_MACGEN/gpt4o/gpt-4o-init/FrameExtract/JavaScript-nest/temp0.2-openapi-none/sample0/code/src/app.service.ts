import { Injectable } from '@nestjs/common';
import { exec } from 'child_process';
import { promisify } from 'util';
import * as path from 'path';
import * as fs from 'fs';

const execAsync = promisify(exec);

@Injectable()
export class AppService {
  async extractFrame(videoPath: string, frameNumber: number): Promise<string> {
    const outputDir = path.join(__dirname, '..', 'frames');
    if (!fs.existsSync(outputDir)) {
      fs.mkdirSync(outputDir);
    }
    const outputFilePath = path.join(outputDir, `frame-${frameNumber}.png`);
    const command = `ffmpeg -i ${videoPath} -vf "select=eq(n\\,${frameNumber})" -vframes 1 ${outputFilePath}`;

    try {
      await execAsync(command);
      if (!fs.existsSync(outputFilePath)) {
        throw new Error(`Frame at index ${frameNumber} could not be found.`);
      }
      return outputFilePath;
    } catch (error) {
      throw new Error(`Frame at index ${frameNumber} could not be found.`);
    }
  }
}