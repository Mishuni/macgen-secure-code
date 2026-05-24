import { Injectable } from '@nestjs/common';
import * as unzipper from 'unzipper';
import * as stream from 'stream';
import * as util from 'util';

@Injectable()
export class AppService {
  async convertZipToText(buffer: Buffer): Promise<string> {
    const pipeline = util.promisify(stream.pipeline);
    const zip = unzipper.Parse();
    const textContents: string[] = [];

    await pipeline(
      stream.Readable.from(buffer),
      zip,
      async (entry) => {
        const fileName = entry.path;
        if (!fileName.endsWith('.txt') || fileName.includes('..')) {
          entry.autodrain();
          return;
        }
        const content = await entry.buffer();
        textContents.push(content.toString());
      }
    );

    return textContents.join('\n');
  }
}