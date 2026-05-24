import { Controller, Post, UploadedFile, UseInterceptors, Body, BadRequestException } from '@nestjs/common';
import { FileInterceptor } from '@nestjs/platform-express';
import { AppService } from './app.service';

@Controller()
export class AppController {
  constructor(private readonly appService: AppService) {}

  @Post('extract')
  @UseInterceptors(FileInterceptor('video'))
  async extractFrame(
    @UploadedFile() video: Express.Multer.File,
    @Body('frameNumber') frameNumber: number,
  ) {
    if (frameNumber < 0) {
      throw new BadRequestException('Invalid frame number');
    }

    const validMimeTypes = ['video/mp4', 'video/x-msvideo', 'video/x-matroska'];
    if (!validMimeTypes.includes(video.mimetype)) {
      throw new BadRequestException('Invalid file type');
    }

    return await this.appService.extractFrame(video, frameNumber);
  }
}