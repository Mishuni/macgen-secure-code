import { Injectable } from '@nestjs/common';
import { exec } from 'child_process';
import { promisify } from 'util';
import { readFileSync, unlinkSync } from 'fs';

const execPromise = promisify(exec);

@Injectable()
export class AppService {
  async extractFrame(videoPath: string, frameNumber: number): Promise<Buffer> {
    const outputImagePath = `./uploads/frame-${frameNumber}.png`;

    try {
      await execPromise(`ffmpeg -i ${videoPath} -vf "select=eq(n\\,${frameNumber})" -vframes 1 ${outputImagePath}`);
      const imageBuffer = readFileSync(outputImagePath);
      unlinkSync(outputImagePath); // Clean up the image file after reading
      return imageBuffer;
    } catch (error) {
      throw new Error(`Frame at index ${frameNumber} could not be found.`);
    }
  }
}