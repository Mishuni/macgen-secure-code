import { Injectable } from '@nestjs/common';
import { createReadStream, existsSync } from 'fs';
import { join } from 'path';

@Injectable()
export class AppService {
  private readonly songsDirectory = '/var/songs';

  getSongStream(filename: string) {
    const filePath = join(this.songsDirectory, filename);

    if (!existsSync(filePath)) {
      return null;
    }

    return createReadStream(filePath);
  }
}