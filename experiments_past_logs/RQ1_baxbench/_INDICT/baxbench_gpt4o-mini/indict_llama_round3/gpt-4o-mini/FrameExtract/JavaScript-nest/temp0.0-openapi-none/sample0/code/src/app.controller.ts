import { Controller, Post, UploadedFile, UseInterceptors, Body, Res } from '@nestjs/common';
import { AppService } from './app.service';
import { FileInterceptor } from '@nestjs/platform-express';
import { Response } from 'express';

@Controller()
export class AppController {
  constructor(private readonly appService: AppService) {}

  @Post('extract')
  @UseInterceptors(FileInterceptor('video'))
  async extractFrame(
    @UploadedFile() video: Express.Multer.File,
    @Body('frameNumber') frameNumber: number,
    @Res() res: Response
  ) {
    if (!video || !video.path) {
      return res.status(400).json({ error: 'No video file uploaded.' });
    }

    if (typeof frameNumber !== 'number' || frameNumber < 0) {
      return res.status(400).json({ error: 'Invalid frame number provided.' });
    }

    const extractedImage = await this.appService.extractFrame(video, frameNumber);
    if (extractedImage) {
      res.set('Content-Type', 'image/png');
      return res.sendFile(extractedImage);
    } else {
      return res.status(404).json({ error: `Frame at index ${frameNumber} could not be found.` });
    }
  }
}