import { Controller, Post, UploadedFiles, Body, Res, HttpStatus } from '@nestjs/common';
import { AppService } from './app.service';
import { Response } from 'express';
import { FileFieldsInterceptor } from '@nestjs/platform-express';
import { UseInterceptors } from '@nestjs/common';

@Controller()
export class AppController {
  constructor(private readonly appService: AppService) {}

  @Post('/create-gif')
  @UseInterceptors(FileFieldsInterceptor([{ name: 'images', maxCount: 10 }]))
  async createGif(
    @UploadedFiles() files: { images?: Express.Multer.File[] },
    @Body('targetSize') targetSize: string,
    @Body('delay') delay: string,
    @Body('appendReverted') appendReverted: string,
    @Res() res: Response,
  ) {
    if (!files || !files.images || !targetSize || !/^\d+x\d+$/.test(targetSize)) {
      return res.status(HttpStatus.BAD_REQUEST).json({ error: 'Invalid input' });
    }

    const delayValue = parseInt(delay, 10);
    if (isNaN(delayValue) || delayValue < 10 || delayValue > 1000) {
      return res.status(HttpStatus.BAD_REQUEST).json({ error: 'Invalid delay value' });
    }

    try {
      const gifBuffer = await this.appService.createGif(
        files.images,
        targetSize,
        delayValue,
        appendReverted === 'true',
      );
      res.setHeader('Content-Type', 'image/gif');
      res.send(gifBuffer);
    } catch (error) {
      res.status(HttpStatus.INTERNAL_SERVER_ERROR).json({ error: error.message });
    }
  }
}