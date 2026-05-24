import { Injectable } from '@nestjs/common';
import { exec } from 'child_process';
import { promisify } from 'util';
import { join } from 'path';
import { existsSync } from 'fs';

const execPromise = promisify(exec);

@Injectable()
export class AppService {
  async extractFrame(videoPath: string, frameNumber: number): Promise<string | null> {
    const outputImagePath = join(__dirname, `../output/frame-${frameNumber}.png`);

    try {
      const command = `ffmpeg -i ${videoPath} -vf "select=eq(n\\,${frameNumber})" -vframes 1 ${outputImagePath}`;
      await execPromise(command);

      if (existsSync(outputImagePath)) {
        return outputImagePath;
      }
    } catch (error) {
      console.error('Error extracting frame:', error);
    }

    return null;
  }
}