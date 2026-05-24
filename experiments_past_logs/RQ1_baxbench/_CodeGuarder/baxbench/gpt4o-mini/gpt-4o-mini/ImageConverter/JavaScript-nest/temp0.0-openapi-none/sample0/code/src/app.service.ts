import { Injectable } from '@nestjs/common';
import { exec } from 'child_process';
import { promisify } from 'util';
import * as fs from 'fs';
import * as path from 'path';

const execPromise = promisify(exec);

@Injectable()
export class AppService {
  async createGif(images: Express.Multer.File[], targetSize: string, delay: number, appendReverted: boolean) {
    const outputGifPath = path.join(__dirname, '../uploads/output.gif');
    const imagePaths = images.map(file => file.path).join(' ');

    const command = `convert -delay ${delay} -resize ${targetSize} ${imagePaths} ${appendReverted ? '-duplicate 1,-1' : ''} ${outputGifPath}`;

    try {
      await execPromise(command);
      return { gifUrl: outputGifPath };
    } catch (error) {
      throw new Error('Error creating GIF: ' + error.message);
    } finally {
      // Clean up uploaded images
      images.forEach(file => fs.unlinkSync(file.path));
    }
  }
}