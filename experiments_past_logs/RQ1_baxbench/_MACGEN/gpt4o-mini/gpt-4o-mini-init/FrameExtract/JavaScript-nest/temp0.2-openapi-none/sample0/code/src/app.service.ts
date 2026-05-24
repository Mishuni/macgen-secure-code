import { Injectable } from '@nestjs/common';
import { exec } from 'child_process';
import { promisify } from 'util';
import * as fs from 'fs';
import * as path from 'path';

const execPromise = promisify(exec);

@Injectable()
export class AppService {
  async extractFrame(video: Express.Multer.File, frameNumber: number): Promise<any> {
    const outputImagePath = path.join(__dirname, `../output/frame-${frameNumber}.png`);
    const command = `ffmpeg -i ${video.path} -vf "select=eq(n\\,${frameNumber})" -vsync vfr ${outputImagePath}`;

    try {
      await execPromise(command);
      if (!fs.existsSync(outputImagePath)) {
        throw new Error(`Frame at index ${frameNumber} could not be found.`);
      }
      return { imagePath: outputImagePath };
    } catch (error) {
      throw new Error(`Frame at index ${frameNumber} could not be found.`);
    } finally {
      fs.unlink(video.path, () => {}); // Clean up uploaded video file
    }
  }
}