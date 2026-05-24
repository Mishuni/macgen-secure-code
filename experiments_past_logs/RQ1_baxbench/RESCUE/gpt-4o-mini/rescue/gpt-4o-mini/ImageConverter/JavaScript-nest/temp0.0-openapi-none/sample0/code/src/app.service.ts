import { Injectable } from '@nestjs/common';
import { exec } from 'child_process';
import { promisify } from 'util';

const execPromise = promisify(exec);

@Injectable()
export class AppService {
  async createGif(images: Express.Multer.File[], targetSize: string, delay: number, appendReverted: boolean): Promise<Buffer> {
    const imagePaths = images.map(image => image.path).join(' ');
    const outputGifPath = `output.gif`;
    const command = `convert ${imagePaths} -resize ${targetSize} -delay ${delay} ${appendReverted ? '-reverse' : ''} ${outputGifPath}`;

    await execPromise(command);
    
    return await this.getGifBuffer(outputGifPath);
  }

  private async getGifBuffer(filePath: string): Promise<Buffer> {
    return await promisify(require('fs').readFile)(filePath);
  }
}