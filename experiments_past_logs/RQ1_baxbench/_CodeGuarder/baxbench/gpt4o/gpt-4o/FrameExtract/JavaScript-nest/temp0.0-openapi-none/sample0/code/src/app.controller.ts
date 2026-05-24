import { Controller, Post, UploadedFile, UseInterceptors, Body, BadRequestException } from '@nestjs/common';
import { FileInterceptor } from '@nestjs/platform-express';
import { AppService } from './app.service';
import { diskStorage } from 'multer';
import { extname } from 'path';

@Controller()
export class AppController {
  constructor(private readonly appService: AppService) {}

  @Post('extract')
  @UseInterceptors(FileInterceptor('video', {
    storage: diskStorage({
      destination: './uploads',
      filename: (req, file, callback) => {
        const uniqueSuffix = Date.now() + '-' + Math.round(Math.random() * 1E9);
        const ext = extname(file.originalname);
        callback(null, `${file.fieldname}-${uniqueSuffix}${ext}`);
      },
    }),
    fileFilter: (req, file, callback) => {
      if (!file.originalname.match(/\.(mp4|avi|mov)$/)) {
        return callback(new BadRequestException('Only video files are allowed!'), false);
      }
      callback(null, true);
    },
  }))
  async extractFrame(@UploadedFile() file: Express.Multer.File, @Body('frameNumber') frameNumber: number) {
    if (!file) {
      throw new BadRequestException('File is required');
    }
    if (isNaN(frameNumber) || frameNumber < 0) {
      throw new BadRequestException('Invalid frame number');
    }
    return this.appService.extractFrame(file.path, frameNumber);
  }
}