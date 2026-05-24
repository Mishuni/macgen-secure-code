import { Controller, Post, UploadedFile, UseInterceptors, BadRequestException } from '@nestjs/common';
import { FileInterceptor } from '@nestjs/platform-express';
import { AppService } from './app.service';

@Controller()
export class AppController {
  constructor(private readonly appService: AppService) {}

  @Post('convert')
  @UseInterceptors(FileInterceptor('file'))
  async convertZipToText(@UploadedFile() file: Express.Multer.File): Promise<string> {
    if (!file || file.mimetype !== 'application/zip') {
      throw new BadRequestException('Invalid input: Please upload a valid zip file.');
    }
    return this.appService.convertZipToText(file.buffer);
  }
}