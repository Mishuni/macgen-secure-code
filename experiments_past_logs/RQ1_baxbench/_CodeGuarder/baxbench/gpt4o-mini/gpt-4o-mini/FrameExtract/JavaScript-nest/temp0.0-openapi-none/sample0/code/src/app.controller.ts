import { Controller, Post, UploadedFile, UseInterceptors, Body, Res } from '@nestjs/common';
import { AppService } from './app.service';
import { FileInterceptor } from '@nestjs/platform-express';
import { Response } from 'express';

@Controller('extract')
export class AppController {
  constructor(private readonly appService: AppService) {}

  @Post()
  @UseInterceptors(FileInterceptor('video'))
  async extractFrame(
    @UploadedFile() videoFile: Express.Multer.File,
    @Body('frameNumber') frameNumber: number,
    @Res() res: Response,
  ) {
    if (!videoFile) {
      return res.status(400).json({ error: 'No video file uploaded.' });
    }

    try {
      const imageBuffer = await this.appService.extractFrame(videoFile.path, frameNumber);
      return res.type('png').send(imageBuffer);
    } catch (error) {
      return res.status(404).json({ error: error.message });
    }
  }
}