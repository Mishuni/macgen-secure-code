import { Injectable } from '@nestjs/common';
import { v4 as uuidv4 } from 'uuid';
import * as fs from 'fs';
import * as path from 'path';

@Injectable()
export class AppService {
  private readonly uploadDir = path.join(__dirname, '..', 'uploads');

  constructor() {
    // Ensure the upload directory exists
    if (!fs.existsSync(this.uploadDir)) {
      fs.mkdirSync(this.uploadDir, { recursive: true });
    }
  }

  saveImage(file: Express.Multer.File): string {
    const imageId = uuidv4();
    const filePath = path.join(this.uploadDir, imageId);

    // Save the file securely
    fs.writeFileSync(filePath, file.buffer);

    return imageId;
  }

  getImagePath(imageId: string): string | null {
    const filePath = path.join(this.uploadDir, imageId);

    // Check if the file exists
    if (fs.existsSync(filePath)) {
      return filePath;
    }

    return null;
  }
}