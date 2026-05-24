import { Injectable } from '@nestjs/common';
import { createReadStream, existsSync } from 'fs';
import { join } from 'path';

@Injectable()
export class AppService {
  private readonly songsDirectory = '/var/songs';

  getSongStream(filename: string) {
    const filePath = join(this.songsDirectory, filename);

    // Check if the file exists
    if (!existsSync(filePath)) {
      throw new Error('File does not exist');
    }

    return createReadStream(filePath);
  }
}