import { Injectable, HttpException, HttpStatus } from '@nestjs/common';
import { Express } from 'express';
import { v4 as uuidv4 } from 'uuid';
import * as fs from 'fs';
import * as path from 'path';
import * as mime from 'mime-types';

@Injectable()
export class AppService {
  private readonly uploadDir = path.join(__dirname, '..', 'uploads');

  constructor() {
    if (!fs.existsSync(this.uploadDir)) {
      fs.mkdirSync(this.uploadDir);
    }
  }

  async saveImage(file: Express.Multer.File): Promise<string> {
    const imageId = uuidv4();
    const filePath = path.join(this.uploadDir, imageId);
    await fs.promises.writeFile(filePath, file.buffer);
    return imageId;
  }

  async getImage(imageId: string): Promise<{ buffer: Buffer; mimetype: string }> {
    const filePath = path.join(this.uploadDir, imageId);
    if (!fs.existsSync(filePath)) {
      throw new HttpException('Image not found', HttpStatus.NOT_FOUND);
    }
    const buffer = await fs.promises.readFile(filePath);
    const mimetype = mime.lookup(buffer) || 'application/octet-stream';
    return { buffer, mimetype };
  }
}