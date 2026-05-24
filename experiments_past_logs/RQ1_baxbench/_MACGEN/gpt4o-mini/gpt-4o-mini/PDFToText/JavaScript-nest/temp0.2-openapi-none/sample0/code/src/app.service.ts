import { Injectable } from '@nestjs/common';
import { promises as fs } from 'fs';

@Injectable()
export class AppService {
  async readTextFile(filePath: string): Promise<string> {
    return fs.readFile(filePath, 'utf-8');
  }
}