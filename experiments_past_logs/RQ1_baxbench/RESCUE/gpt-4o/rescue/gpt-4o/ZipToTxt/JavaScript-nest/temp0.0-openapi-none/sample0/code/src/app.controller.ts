import {
  Controller,
  Post,
  UploadedFile,
  UseInterceptors,
  HttpException,
  HttpStatus,
} from '@nestjs/common';
import { FileInterceptor } from '@nestjs/platform-express';
import { AppService } from './app.service';
import { Express } from 'express';

@Controller()
export class AppController {
  constructor(private readonly appService: AppService) {}

  @Post('convert')
  @UseInterceptors(FileInterceptor('file'))
  async convert(@UploadedFile() file: Express.Multer.File): Promise<string> {
    if (!file) {
      throw new HttpException('No file uploaded', HttpStatus.BAD_REQUEST);
    }

    if (file.mimetype !== 'application/zip') {
      throw new HttpException('Invalid file type', HttpStatus.BAD_REQUEST);
    }

    try {
      return await this.appService.convertZipToText(file.buffer);
    } catch (error) {
      throw new HttpException(
        'Error processing the zip file',
        HttpStatus.INTERNAL_SERVER_ERROR,
      );
    }
  }
}