import { Injectable } from '@nestjs/common';
import { exec } from 'child_process';
import { promisify } from 'util';
import * as fs from 'fs';
import * as path from 'path';

const execAsync = promisify(exec);

@Injectable()
export class AppService {
  async extractFrame(videoPath: string, frameNumber: number): Promise<string> {
    const outputDir = path.join(__dirname, '..', 'output');
    const outputFile = path.join(outputDir, `frame_${frameNumber}.png`);

    // Ensure the output directory exists
    if (!fs.existsSync(outputDir)) {
      fs.mkdirSync(outputDir, { recursive: true });
    }

    // Construct the ffmpeg command
    const command = `ffmpeg -i "${videoPath}" -vf "select=eq(n\\,${frameNumber})" -vframes 1 "${outputFile}"`;

    try {
      // Execute the ffmpeg command
      await execAsync(command);

      // Check if the output file was created
      if (!fs.existsSync(outputFile)) {
        throw new Error('Frame not found');
      }

      return outputFile;
    } catch (error) {
      throw new Error('Failed to extract frame: ' + error.message);
    }
  }
}