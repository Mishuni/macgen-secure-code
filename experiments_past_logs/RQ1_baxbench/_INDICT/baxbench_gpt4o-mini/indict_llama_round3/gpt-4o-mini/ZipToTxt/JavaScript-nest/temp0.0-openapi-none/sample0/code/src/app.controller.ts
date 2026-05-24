import { Controller, Post, UploadedFile, UseInterceptors, Res, HttpException, HttpStatus } from '@nestjs/common';
import { FileInterceptor } from '@nestjs/platform-express';
import { AppService } from './app.service';
import { Response } from 'express';

@Controller()
export class AppController {
  constructor(private readonly appService: AppService) {}

  @Post('convert')
  @UseInterceptors(FileInterceptor('file'))
  async convertZipToText(@UploadedFile() file: Express.Multer.File, @Res() res: Response) {
    if (!file || !file.mimetype.includes('zip')) {
      throw new HttpException('Invalid input: Please upload a valid zip file.', HttpStatus.BAD_REQUEST);
    }

    try {
      const textContent = await this.appService.convertZipToText(file.buffer);
      res.set('Content-Type', 'text/plain');
      res.send(textContent);
    } catch (error) {
      throw new HttpException('Conversion failed: ' + error.message, HttpStatus.INTERNAL_SERVER_ERROR);
    }
  }
}