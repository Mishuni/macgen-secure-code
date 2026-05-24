import { Controller, Post, UploadedFile, Body, Res, HttpStatus, BadRequestException } from '@nestjs/common';
import { AppService } from './app.service';
import { Response } from 'express';
import { FileInterceptor } from '@nestjs/platform-express';
import { UseInterceptors } from '@nestjs/common';
import { diskStorage } from 'multer';
import { extname } from 'path';
import * as mime from 'mime-types';

@Controller()
export class AppController {
  constructor(private readonly appService: AppService) {}

  @Post('extract')
  @UseInterceptors(
    FileInterceptor('video', {
      storage: diskStorage({
        destination: './uploads',
        filename: (req, file, callback) => {
          const uniqueSuffix = Date.now() + '-' + Math.round(Math.random() * 1e9);
          const ext = extname(file.originalname);
          callback(null, `${file.fieldname}-${uniqueSuffix}${ext}`);
        },
      }),
      limits: { fileSize: 50 * 1024 * 1024 }, // Limit file size to 50MB
      fileFilter: (req, file, callback) => {
        const mimeType = mime.lookup(file.originalname);
        if (mimeType && mimeType.startsWith('video/')) {
          callback(null, true);
        } else {
          callback(new BadRequestException('Invalid file type. Only video files are allowed.'), false);
        }
      },
    }),
  )
  async extractFrame(
    @UploadedFile() file: Express.Multer.File,
    @Body('frameNumber') frameNumber: string,
    @Res() res: Response,
  ) {
    if (!file) {
      throw new BadRequestException('Video file is required.');
    }

    const frameNum = parseInt(frameNumber, 10);
    if (isNaN(frameNum) || frameNum < 0) {
      throw new BadRequestException('Invalid frame number.');
    }

    try {
      const framePath = await this.appService.extractFrame(file.path, frameNum);
      res.sendFile(framePath, { headers: { 'Content-Type': 'image/png' } });
    } catch (error) {
      res.status(HttpStatus.NOT_FOUND).json({ error: error.message });
    }
  }
}