import { Controller, Post, UploadedFile, UseInterceptors, Get, Param, Res, HttpException, HttpStatus } from '@nestjs/common';
import { FileInterceptor } from '@nestjs/platform-express';
import { AppService } from './app.service';
import { Response } from 'express';
import { v4 as uuidv4 } from 'uuid';
import * as path from 'path';
import * as fs from 'fs';

@Controller()
export class AppController {
  constructor(private readonly appService: AppService) {}

  @Post('upload')
  @UseInterceptors(FileInterceptor('file'))
  async uploadFile(@UploadedFile() file: Express.Multer.File) {
    if (!file) {
      throw new HttpException({ error: 'File is required' }, HttpStatus.BAD_REQUEST);
    }

    const allowedTypes = ['image/jpeg', 'image/png', 'image/gif'];
    if (!allowedTypes.includes(file.mimetype)) {
      throw new HttpException({ error: 'Invalid file type' }, HttpStatus.BAD_REQUEST);
    }

    const imageId = uuidv4();
    const uploadPath = path.join(__dirname, '..', 'uploads', `${imageId}${path.extname(file.originalname)}`);

    fs.writeFileSync(uploadPath, file.buffer);

    return { id: imageId };
  }

  @Get('images/:imageId')
  async getImage(@Param('imageId') imageId: string, @Res() res: Response) {
    const imagePath = path.join(__dirname, '..', 'uploads', imageId);
    
    if (!fs.existsSync(imagePath)) {
      throw new HttpException({ error: 'Image not found' }, HttpStatus.NOT_FOUND);
    }

    res.sendFile(imagePath, { headers: { 'Content-Disposition': 'inline' } });
  }
}