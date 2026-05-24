import { Injectable, BadRequestException } from '@nestjs/common';
import * as unzipper from 'unzipper';
import * as stream from 'stream';
import { promisify } from 'util';

const pipeline = promisify(stream.pipeline);

@Injectable()
export class AppService {
  async convertZipToText(zipBuffer: Buffer): Promise<string> {
    const textContents: string[] = [];

    const zipStream = stream.Readable.from(zipBuffer).pipe(unzipper.Parse({ forceStream: true }));

    for await (const entry of zipStream) {
      const fileName = entry.path;
      if (entry.type === 'File' && fileName.endsWith('.txt')) {
        const content = await this.streamToString(entry);
        textContents.push(content);
      } else {
        entry.autodrain();
      }
    }

    if (textContents.length === 0) {
      throw new BadRequestException('No text files found in the zip');
    }

    return textContents.join('\n');
  }

  private async streamToString(stream: stream.Readable): Promise<string> {
    const chunks: Buffer[] = [];
    for await (const chunk of stream) {
      chunks.push(chunk);
    }
    return Buffer.concat(chunks).toString('utf-8');
  }
}