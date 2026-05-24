import { Injectable } from '@nestjs/common';
import { createReadStream, promises as fsPromises } from 'fs';
import { join, resolve } from 'path';

@Injectable()
export class AppService {
  private readonly songsDirectory = '/var/songs';

  async getSongStream(filename: string) {
    const filePath = resolve(this.songsDirectory, filename);
    if (!filePath.startsWith(this.songsDirectory)) {
      throw new Error('Invalid file path');
    }
    await fsPromises.access(filePath); // Check if file exists
    return createReadStream(filePath);
  }
}