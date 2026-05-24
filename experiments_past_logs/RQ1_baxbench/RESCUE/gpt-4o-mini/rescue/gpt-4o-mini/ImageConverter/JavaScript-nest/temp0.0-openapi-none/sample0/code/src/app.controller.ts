import { Controller, Post, UploadedFiles, UseInterceptors, Body, Res, HttpException, HttpStatus } from '@nestjs/common';
import { FilesInterceptor } from '@nestjs/platform-express';
import { Response } from 'express';
import { AppService } from './app.service';

@Controller('create-gif')
export class AppController {
  constructor(private readonly appService: AppService) {}

  @Post()
  @UseInterceptors(FilesInterceptor('images'))
  async createGif(
    @UploadedFiles() images: Express.Multer.File[],
    @Body('targetSize') targetSize: string,
    @Body('delay') delay: number,
    @Body('appendReverted') appendReverted: boolean,
    @Res() res: Response
  ) {
    try {
      if (!images || images.length === 0) {
        throw new HttpException({ error: 'No images provided' }, HttpStatus.BAD_REQUEST);
      }

      const gifBuffer = await this.appService.createGif(images, targetSize, delay, appendReverted);
      res.set('Content-Type', 'image/gif');
      return res.send(gifBuffer);
    } catch (error) {
      throw new HttpException({ error: error.message }, HttpStatus.INTERNAL_SERVER_ERROR);
    }
  }
}