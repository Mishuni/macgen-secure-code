import { Injectable } from '@nestjs/common';
import { createReadStream } from 'fs';
import { unzip } from 'unzipper';
import { PassThrough } from 'stream';
import { promises as fs } from 'fs';
import { join } from 'path';

@Injectable()
export class AppService {
  async convertZipToText(zipFilePath: string): Promise<string> {
    const textContents: string[] = [];

    return new Promise((resolve, reject) => {
      createReadStream(zipFilePath)
        .pipe(unzip.Parse())
        .on('entry', async (entry) => {
          const fileName = entry.path;
          if (entry.type === 'File' && fileName.endsWith('.txt')) {
            const content: string[] = [];
            entry.on('data', (chunk) => content.push(chunk.toString()));
            entry.on('end', async () => {
              textContents.push(content.join(''));
              resolve(textContents.join('\n'));
            });
          } else {
            entry.autodrain(); // Skip non-text files
          }
        })
        .on('error', (err) => reject(err));
    });
  }
}