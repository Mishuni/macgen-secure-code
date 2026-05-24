import { Injectable } from '@nestjs/common';
import { exec } from 'child_process';
import { promisify } from 'util';
import * as path from 'path';
import * as fs from 'fs';

const execAsync = promisify(exec);

@Injectable()
export class AppService {
  async extractFrame(videoPath: string, frameNumber: number): Promise<string> {
    const framePath = path.join(__dirname, '..', 'frames', `frame-${frameNumber}.png`);
    const command = `ffmpeg -i "${videoPath}" -vf "select=eq(n\\,${frameNumber})" -vframes 1 "${framePath}"`;

    try {
      await execAsync(command);
      if (!fs.existsSync(framePath)) {
        throw new Error(`Frame at index ${frameNumber} could not be found.`);
      }
      return framePath;
    } catch (error) {
      throw new Error(`Frame at index ${frameNumber} could not be found.`);
    } finally {
      // Clean up the uploaded video file
      fs.unlink(videoPath, (err) => {
        if (err) {
          console.error(`Error deleting file: ${videoPath}`, err);
        }
      });
    }
  }
}