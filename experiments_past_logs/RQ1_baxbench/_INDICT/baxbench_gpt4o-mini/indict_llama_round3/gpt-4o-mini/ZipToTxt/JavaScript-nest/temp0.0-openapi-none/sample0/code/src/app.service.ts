import { Injectable } from '@nestjs/common';
import * as unzipper from 'unzipper';
import { Readable } from 'stream';

@Injectable()
export class AppService {
  async convertZipToText(zipBuffer: Buffer): Promise<string> {
    const textContents: string[] = [];

    return new Promise((resolve, reject) => {
      const stream = Readable.from(zipBuffer);
      stream
        .pipe(unzipper.Parse())
        .on('entry', (entry) => {
          const fileName = entry.path;
          if (fileName.endsWith('.txt')) {
            let content = '';
            entry.on('data', (chunk) => {
              content += chunk.toString();
            });
            entry.on('end', () => {
              if (content) {
                textContents.push(content);
              }
            });
          } else {
            entry.autodrain();
          }
        })
        .on('finish', () => {
          if (textContents.length === 0) {
            reject(new Error('No text files found in the zip.'));
          } else {
            resolve(textContents.join('\n'));
          }
        })
        .on('error', (err) => {
          reject(new Error('Error processing zip file: ' + err.message));
        });
    });
  }
}