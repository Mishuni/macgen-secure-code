import { Injectable, HttpException, HttpStatus } from '@nestjs/common';
import * as fs from 'fs';
import * as path from 'path';
import { v4 as uuidv4 } from 'uuid';

@Injectable()
export class AppService {
  private readonly uploadDir = path.resolve('./uploads');

  constructor() {
    if (!fs.existsSync(this.uploadDir)) {
      fs.mkdirSync(this.uploadDir);
    }
  }

  async saveImage(file: Express.Multer.File): Promise<string> {
    const imageId = uuidv4();
    const filePath = path.join(this.uploadDir, imageId + path.extname(file.originalname));
    await fs.promises.writeFile(filePath, file.buffer);
    return imageId;
  }

  async getImagePath(imageId: string): Promise<string> {
    const files = await fs.promises.readdir(this.uploadDir);
    const file = files.find(f => f.startsWith(imageId));
    if (!file) {
      throw new HttpException('Image not found', HttpStatus.NOT_FOUND);
    }
    return file;
  }
}