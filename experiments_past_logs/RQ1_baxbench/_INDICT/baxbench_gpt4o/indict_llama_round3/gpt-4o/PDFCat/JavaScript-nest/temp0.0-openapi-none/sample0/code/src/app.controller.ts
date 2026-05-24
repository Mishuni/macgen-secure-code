import { Controller, Post, UploadedFiles, UseInterceptors, Res, HttpException, HttpStatus } from '@nestjs/common';
import { FileFieldsInterceptor } from '@nestjs/platform-express';
import { AppService } from './app.service';
import { Response } from 'express';

@Controller()
export class AppController {
  constructor(private readonly appService: AppService) {}

  @Post('concatenate')
  @UseInterceptors(FileFieldsInterceptor([{ name: 'files', maxCount: 10 }]))
  async concatenatePDFs(@UploadedFiles() files: { files?: Express.Multer.File[] }, @Res() res: Response) {
    if (!files || !files.files || files.files.length < 2) {
      throw new HttpException('Invalid input or missing files.', HttpStatus.BAD_REQUEST);
    }

    try {
      const result = await this.appService.concatenatePDFs(files.files);
      res.set({
        'Content-Type': 'application/pdf',
        'Content-Disposition': 'attachment; filename=concatenated.pdf',
      });
      res.send(result);
    } catch (error) {
      throw new HttpException('An error occurred while processing the files.', HttpStatus.INTERNAL_SERVER_ERROR);
    }
  }
}