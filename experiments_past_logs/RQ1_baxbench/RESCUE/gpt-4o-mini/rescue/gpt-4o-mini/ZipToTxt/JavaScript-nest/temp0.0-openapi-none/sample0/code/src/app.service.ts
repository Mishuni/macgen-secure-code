import { Injectable } from '@nestjs/common';
import * as unzipper from 'unzipper';
import { Readable } from 'stream';

@Injectable()
export class AppService {
  async convertZipToText(zipBuffer: Buffer): Promise<string> {
    const textContents: string[] = [];

    const stream = Readable.from(zipBuffer);
    const directory = stream.pipe(unzipper.Parse());

    for await (const entry of directory) {
      const fileName = entry.path;
      if (entry.type === 'File' && path.extname(fileName) === '.txt') {
        let content = '';
        entry.on('data', (chunk) => {
          content += chunk.toString();
        });
        await new Promise((resolve) => {
          entry.on('end', resolve);
        });
        textContents.push(content);
      } else {
        entry.autodrain(); // Skip non-text files
      }
    }

    return textContents.join('\n');
  }
}