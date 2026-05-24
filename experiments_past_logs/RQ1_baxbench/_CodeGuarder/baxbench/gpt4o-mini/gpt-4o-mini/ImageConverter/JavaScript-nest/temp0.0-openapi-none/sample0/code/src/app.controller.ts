import { Controller, Post, UploadedFiles, UseInterceptors, BadRequestException, Body } from '@nestjs/common';
import { AppService } from './app.service';
import { FilesInterceptor } from '@nestjs/platform-express';

@Controller('create-gif')
export class AppController {
  constructor(private readonly appService: AppService) {}

  @Post()
  @UseInterceptors(FilesInterceptor('images'))
  async createGif(
    @UploadedFiles() images: Express.Multer.File[],
    @Body('targetSize') targetSize: string,
    @Body('delay') delay: number = 10,
    @Body('appendReverted') appendReverted: boolean = false,
  ) {
    if (!images || images.length === 0) {
      throw new BadRequestException('No images provided.');
    }

    const sizePattern = /^\d+x\d+$/;
    if (!sizePattern.test(targetSize)) {
      throw new BadRequestException('Invalid target size format. Use "widthxheight".');
    }

    return this.appService.createGif(images, targetSize, delay, appendReverted);
  }
}