import { Controller, Post, UploadedFile, UseInterceptors, BadRequestException, Res } from '@nestjs/common';
import { FileInterceptor } from '@nestjs/platform-express';
import { AppService } from './app.service';
import { Response } from 'express';
import * as path from 'path';

@Controller('convert')
export class AppController {
  constructor(private readonly appService: AppService) {}

  @Post()
  @UseInterceptors(FileInterceptor('file'))
  async convertZipToText(@UploadedFile() file: Express.Multer.File, @Res() res: Response) {
    if (!file || path.extname(file.originalname) !== '.zip') {
      throw new BadRequestException('Invalid input: Please upload a zip file.');
    }

    const textContent = await this.appService.convertZipToText(file.buffer);
    res.type('text/plain').send(textContent);
  }
}