import { Controller, Post, UploadedFile, UseInterceptors, BadRequestException, InternalServerErrorException, Res } from '@nestjs/common';
import { FileInterceptor } from '@nestjs/platform-express';
import { AppService } from './app.service';
import { Response } from 'express';

@Controller('convert')
export class AppController {
  constructor(private readonly appService: AppService) {}

  @Post()
  @UseInterceptors(FileInterceptor('file'))
  async convertPdfToText(@UploadedFile() file: Express.Multer.File, @Res() res: Response) {
    if (!file) {
      throw new BadRequestException('No file uploaded or invalid file.');
    }

    try {
      const text = await this.appService.extractTextFromPdf(file.path);
      res.type('text/plain').send(text);
    } catch (error) {
      throw new InternalServerErrorException('Conversion failed.');
    }
  }
}