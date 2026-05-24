import { Controller, Post, UploadedFile, UseInterceptors, Get, Param, Res, BadRequestException, InternalServerErrorException } from '@nestjs/common';
import { FileInterceptor } from '@nestjs/platform-express';
import { Response } from 'express';
import { AppService } from './app.service';
import { v4 as uuidv4 } from 'uuid';
import * as path from 'path';
import * as fs from 'fs';

@Controller()
export class AppController {
  constructor(private readonly appService: AppService) {}

  @Post('upload')
  @UseInterceptors(FileInterceptor('file'))
  async uploadImage(@UploadedFile() file: Express.Multer.File) {
    if (!file) {
      throw new BadRequestException({ error: 'No file provided' });
    }

    const validExtensions = ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp'];
    const ext = path.extname(file.originalname).toLowerCase();

    if (!validExtensions.includes(ext)) {
      throw new BadRequestException({ error: 'Invalid file type' });
    }

    const imageId = uuidv4();
    const uploadPath = path.join(__dirname, '..', 'uploads', imageId + ext);

    try {
      fs.writeFileSync(uploadPath, file.buffer);
      return { id: imageId };
    } catch (error) {
      throw new InternalServerErrorException({ error: 'Failed to upload image' });
    }
  }

  @Get('images/:imageId')
  async getImage(@Param('imageId') imageId: string, @Res() res: Response) {
    const uploadDir = path.join(__dirname, '..', 'uploads');
    const files = fs.readdirSync(uploadDir);
    const imageFile = files.find(file => file.startsWith(imageId));

    if (!imageFile) {
      throw new BadRequestException({ error: 'Image not found' });
    }

    const filePath = path.join(uploadDir, imageFile);
    res.setHeader('Content-Type', 'image/jpeg'); // Set appropriate content type
    res.setHeader('Content-Disposition', 'inline'); // Prevent download
    return res.sendFile(filePath);
  }
}