import { Injectable } from '@nestjs/common';
import * as unzipper from 'unzipper';
import * as stream from 'stream';
import { promisify } from 'util';

const pipeline = promisify(stream.pipeline);

@Injectable()
export class AppService {
  async convertZipToText(zipBuffer: Buffer): Promise<string> {
    const textFilesContent: string[] = [];

    const zipStream = stream.Readable.from(zipBuffer);

    await pipeline(
      zipStream.pipe(unzipper.Parse()),
      new stream.Writable({
        objectMode: true,
        write: async (entry, _, callback) => {
          const { path: filePath, type } = entry;

          if (type === 'File' && filePath.endsWith('.txt')) {
            const chunks: Buffer[] = [];
            entry.on('data', (chunk) => chunks.push(chunk));
            entry.on('end', () => {
              textFilesContent.push(Buffer.concat(chunks).toString('utf-8'));
              callback();
            });
          } else {
            entry.autodrain();
            callback();
          }
        },
      }),
    );

    return textFilesContent.join('\n');
  }
}