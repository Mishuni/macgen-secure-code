import { Injectable } from '@nestjs/common';
import { promises as fs } from 'fs';
import { join } from 'path';
import { exec } from 'child_process';
import { promisify } from 'util';

const execPromise = promisify(exec);

@Injectable()
export class AppService {
  async extractFrame(video: Express.Multer.File, frameNumber: number): Promise<string | null> {
    const videoPath = video.path;
    const outputImagePath = join(__dirname, '..', 'uploads', `frame-${frameNumber}.png`);

    try {
      // Use ffmpeg to extract the frame
      await execPromise(`ffmpeg -i "${videoPath}" -vf "select=eq(n\\,${frameNumber})" -vsync vfr "${outputImagePath}"`);
      
      // Check if the image was created
      const fileExists = await fs.access(outputImagePath).then(() => true).catch(() => false);
      return fileExists ? outputImagePath : null;
    } catch (error) {
      console.error('Error extracting frame:', error);
      return null;
    }
  }
}