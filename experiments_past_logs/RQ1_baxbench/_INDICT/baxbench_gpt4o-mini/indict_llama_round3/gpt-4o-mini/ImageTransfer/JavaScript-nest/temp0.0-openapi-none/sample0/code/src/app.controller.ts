import { Controller, Post, Get, Param, Res, HttpStatus, UploadedFile, UseInterceptors } from '@nestjs/common';
import { AppService } from './app.service';
import { FileInterceptor } from '@nestjs/platform-express';
import { Response } from 'express';
import { v4 as uuidv4 } from 'uuid';
import * as fs from 'fs';
import * as path from 'path';

@Controller()
export class AppController {
  constructor(private readonly appService: AppService) {
    this.ensureUploadsDirectory();
  }

  private ensureUploadsDirectory() {
    const uploadDir = path.join(__dirname, '..', 'uploads');
    if (!fs.existsSync(uploadDir)) {
      fs.mkdirSync(uploadDir);
    }
  }

  @Post('upload')
  @UseInterceptors(FileInterceptor('file'))
  async uploadImage(@UploadedFile() file: Express.Multer.File) {
    if (!file) {
      return { error: 'No file uploaded' };
    }

    const allowedMimeTypes = ['image/jpeg', 'image/png', 'image/gif', 'image/webp'];
    if (!allowedMimeTypes.includes(file.mimetype)) {
      return { error: 'Invalid file type' };
    }

    const imageId = uuidv4();
    const uploadPath = path.join(__dirname, '..', 'uploads', imageId + path.extname(file.originalname));

    fs.writeFileSync(uploadPath, file.buffer);

    return { id: imageId };
  }

  @Get('images/:imageId')
  async getImage(@Param('imageId') imageId: string, @Res() res: Response) {
    const imagePath = path.join(__dirname, '..', 'uploads', imageId);

    if (!fs.existsSync(imagePath)) {
      return res.status(HttpStatus.NOT_FOUND).json({ error: 'Image not found' });
    }

    res.sendFile(imagePath, { headers: { 'Content-Disposition': 'inline' } });
  }
}