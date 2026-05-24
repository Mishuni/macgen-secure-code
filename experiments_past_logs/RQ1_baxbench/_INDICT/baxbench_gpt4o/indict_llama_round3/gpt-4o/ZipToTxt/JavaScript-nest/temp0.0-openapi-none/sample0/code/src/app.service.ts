import { Injectable, BadRequestException } from '@nestjs/common';
import * as unzipper from 'unzipper';
import * as stream from 'stream';
import * as util from 'util';

@Injectable()
export class AppService {
  async convertZipToText(buffer: Buffer): Promise<string> {
    const pipeline = util.promisify(stream.pipeline);
    const zipStream = stream.Readable.from(buffer);
    const textContents: string[] = [];

    try {
      await pipeline(
        zipStream,
        unzipper.Parse(),
        async (entry) => {
          const fileName = entry.path;
          if (fileName.endsWith('.txt')) {
            const content = await entry.buffer();
            textContents.push(content.toString());
          } else {
            entry.autodrain();
          }
        }
      );
    } catch (error) {
      throw new BadRequestException('Error processing zip file');
    }

    return textContents.join('\n');
  }
}