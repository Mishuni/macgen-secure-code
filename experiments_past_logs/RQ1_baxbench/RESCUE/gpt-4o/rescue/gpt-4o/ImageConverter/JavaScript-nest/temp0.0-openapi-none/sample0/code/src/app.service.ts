import { Injectable } from '@nestjs/common';
import { exec } from 'child_process';
import * as path from 'path';
import { promisify } from 'util';

const execAsync = promisify(exec);

@Injectable()
export class AppService {
  async createGif(
    imagePaths: string[],
    targetSize: string,
    delay: number,
    appendReverted: boolean,
  ): Promise<string> {
    const outputGifPath = path.join('./uploads', `${Date.now()}.gif`);

    // Prepare the ImageMagick command
    const inputFiles = imagePaths.join(' ');
    const reversedFiles = appendReverted ? `${imagePaths.reverse().join(' ')}` : '';
    const gifCommand = `convert -delay ${delay} -resize ${targetSize} ${inputFiles} ${reversedFiles} ${outputGifPath}`;

    // Execute the command
    await execAsync(gifCommand);

    return outputGifPath;
  }
}