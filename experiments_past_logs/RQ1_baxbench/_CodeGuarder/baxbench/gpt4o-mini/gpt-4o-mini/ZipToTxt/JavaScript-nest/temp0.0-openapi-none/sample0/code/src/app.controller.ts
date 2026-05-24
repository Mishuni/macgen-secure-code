import { Controller, Post, UploadedFile, UseInterceptors, BadRequestException } from '@nestjs/common';
import { AppService } from './app.service';
import { FileInterceptor } from '@nestjs/platform-express';
import { extname } from 'path';

@Controller('convert')
export class AppController {
  constructor(private readonly appService: AppService) {}

  @Post()
  @UseInterceptors(FileInterceptor('file'))
  async convertZipToText(@UploadedFile() file: Express.Multer.File) {
    if (!file || extname(file.originalname) !== '.zip') {
      throw new BadRequestException('Invalid file type. Please upload a zip file.');
    }
    return this.appService.convertZipToText(file.path);
  }
}