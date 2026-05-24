import { Injectable } from '@nestjs/common';
import * as unzipper from 'unzipper';
import { Readable } from 'stream';

@Injectable()
export class AppService {
  async convertZipToText(file: Express.Multer.File): Promise<string> {
    const textContents: string[] = [];

    return new Promise((resolve, reject) => {
      const stream = Readable.from(file.buffer);
      stream
        .pipe(unzipper.Parse())
        .on('entry', (entry) => {
          if (entry.path.endsWith('.txt')) {
            let content = '';
            entry.on('data', (chunk) => {
              content += chunk.toString();
            });
            entry.on('end', () => {
              textContents.push(content);
            });
          } else {
            entry.autodrain(); // Discard unwanted files
          }
        })
        .on('finish', () => {
          resolve(textContents.join('\n'));
        })
        .on('error', (err) => {
          reject(err);
        });
    });
  }
}