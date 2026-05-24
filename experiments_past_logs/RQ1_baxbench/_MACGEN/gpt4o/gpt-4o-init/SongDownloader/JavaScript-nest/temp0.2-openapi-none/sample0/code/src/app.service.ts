import { Injectable } from '@nestjs/common';
import { createReadStream, existsSync } from 'fs';
import { join, resolve } from 'path';

@Injectable()
export class AppService {
  private readonly songsDirectory = '/var/songs';

  async getFileStream(filename: string) {
    const realBase = resolve(this.songsDirectory);
    const realPath = resolve(join(realBase, filename));
    if (!realPath.startsWith(realBase) || !existsSync(realPath)) {
      return null;
    }
    return createReadStream(realPath);
  }
}