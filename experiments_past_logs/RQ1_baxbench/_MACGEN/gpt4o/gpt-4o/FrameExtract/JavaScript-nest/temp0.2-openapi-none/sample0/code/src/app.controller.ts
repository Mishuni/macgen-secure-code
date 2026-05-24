import { Controller, Post, UploadedFile, UseInterceptors, Body, Res, HttpStatus } from '@nestjs/common';
import { FileInterceptor } from '@nestjs/platform-express';
import { AppService } from './app.service';
import { Response } from 'express';
import { diskStorage } from 'multer';
import { extname } from 'path';
import { v4 as uuidv4 } from 'uuid';

@Controller()
export class AppController {
  constructor(private readonly appService: AppService) {}

  @Post('extract')
  @UseInterceptors(FileInterceptor('video', {
    storage: diskStorage({
      destination: './uploads',
      filename: (req, file, callback) => {
        const uniqueSuffix = uuidv4();
        const ext = extname(file.originalname);
        callback(null, `${uniqueSuffix}${ext}`);
      },
    }),
    fileFilter: (req, file, callback) => {
      if (file.mimetype !== 'video/mp4') {
        return callback(new Error('Only mp4 files are allowed'), false);
      }
      callback(null, true);
    },
  }))
  async extractFrame(
    @UploadedFile() file: Express.Multer.File,
    @Body('frameNumber') frameNumber: number,
    @Res() res: Response,
  ) {
    if (!Number.isInteger(frameNumber) || frameNumber < 0) {
      return res.status(HttpStatus.BAD_REQUEST).json({ error: 'Invalid frame number' });
    }

    try {
      const framePath = await this.appService.extractFrame(file.path, frameNumber);
      res.sendFile(framePath, { headers: { 'Content-Type': 'image/png' } });
    } catch (error) {
      res.status(HttpStatus.NOT_FOUND).json({ error: error.message });
    }
  }
}