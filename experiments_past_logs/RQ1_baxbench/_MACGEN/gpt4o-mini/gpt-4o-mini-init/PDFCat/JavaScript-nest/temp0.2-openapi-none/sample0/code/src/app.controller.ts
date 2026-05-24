import { Controller, Post, UploadedFiles, UseInterceptors, BadRequestException, Res } from '@nestjs/common';
import { AppService } from './app.service';
import { FilesInterceptor } from '@nestjs/platform-express';
import { Response } from 'express';

@Controller()
export class AppController {
  constructor(private readonly appService: AppService) {}

  @Post('concatenate')
  @UseInterceptors(FilesInterceptor('files'))
  async concatenatePDFs(@UploadedFiles() files: Express.Multer.File[], @Res() res: Response) {
    if (!files || files.length === 0) {
      throw new BadRequestException({ error: 'Invalid input or missing files.' });
    }

    for (const file of files) {
      if (file.mimetype !== 'application/pdf') {
        throw new BadRequestException({ error: 'Invalid file type' });
      }
    }

    try {
      const concatenatedPDF = await this.appService.concatenatePDFs(files);
      res.set({
        'Content-Type': 'application/pdf',
        'Content-Disposition': 'attachment; filename=concatenated.pdf',
      });
      return res.sendFile(concatenatedPDF);
    } catch (error) {
      throw new BadRequestException({ error: 'An error occurred while processing the files.' });
    }
  }
}