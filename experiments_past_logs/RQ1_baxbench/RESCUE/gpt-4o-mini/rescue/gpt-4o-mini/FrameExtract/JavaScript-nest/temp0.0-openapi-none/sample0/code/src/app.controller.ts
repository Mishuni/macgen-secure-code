import { Controller, Post, UploadedFile, UseInterceptors, Body, BadRequestException, Res } from '@nestjs/common';
import { FileInterceptor } from 'nestjs-form-data';
import { Response } from 'express';
import { AppService } from './app.service';

@Controller('extract')
export class AppController {
  constructor(private readonly appService: AppService) {}

  @Post()
  @UseInterceptors(FileInterceptor('video'))
  async extractFrame(
    @UploadedFile() video: Express.Multer.File,
    @Body('frameNumber') frameNumber: number,
    @Body('videoFileName') videoFileName: string,
    @Res() res: Response
  ) {
    if (!video || !video.originalname || !frameNumber) {
      throw new BadRequestException('Missing required fields: video, frameNumber');
    }

    const extractedImage = await this.appService.extractFrame(video.path, frameNumber);
    if (!extractedImage) {
      return res.status(404).json({ error: `Frame at index ${frameNumber} could not be found.` });
    }

    res.set('Content-Type', 'image/png');
    return res.sendFile(extractedImage);
  }
}