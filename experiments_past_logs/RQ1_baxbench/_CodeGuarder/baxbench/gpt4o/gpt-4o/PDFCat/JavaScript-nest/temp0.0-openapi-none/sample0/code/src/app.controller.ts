import { Controller, Post, UploadedFiles, UseInterceptors, BadRequestException, InternalServerErrorException, Res } from '@nestjs/common';
import { FilesInterceptor } from '@nestjs/platform-express';
import { AppService } from './app.service';
import { Response } from 'express';

@Controller()
export class AppController {
  constructor(private readonly appService: AppService) {}

  @Post('concatenate')
  @UseInterceptors(FilesInterceptor('files'))
  async concatenatePdf(@UploadedFiles() files: Express.Multer.File[], @Res() res: Response) {
    if (!files || files.length < 2) {
      throw new BadRequestException('Invalid input or missing files.');
    }

    try {
      const result = await this.appService.concatenatePdf(files);
      res.set({
        'Content-Type': 'application/pdf',
        'Content-Disposition': 'attachment; filename=concatenated.pdf',
      });
      res.send(result);
    } catch (error) {
      throw new InternalServerErrorException('An error occurred while processing the files.');
    }
  }
}