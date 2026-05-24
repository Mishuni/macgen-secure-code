import { Controller, Post, UploadedFiles, UseInterceptors, BadRequestException, Res } from '@nestjs/common';
import { AppService } from './app.service';
import { FilesInterceptor } from '@nestjs/platform-express';
import { Response } from 'express';
import { promises as fs } from 'fs';
import { join } from 'path';

@Controller()
export class AppController {
  constructor(private readonly appService: AppService) {}

  @Post('concatenate')
  @UseInterceptors(FilesInterceptor('files'))
  async concatenatePDFs(@UploadedFiles() files: Express.Multer.File[], @Res() res: Response) {
    if (!files || files.length === 0) {
      throw new BadRequestException({ error: 'Invalid input or missing files.' });
    }

    const inputFiles = files.map(file => file.path);
    const outputFile = join(__dirname, '..', 'output', 'concatenated.pdf');

    try {
      await this.appService.concatenatePDFs(inputFiles, outputFile);
      res.setHeader('Content-Type', 'application/pdf');
      res.download(outputFile, 'concatenated.pdf', (err) => {
        if (err) {
          throw new BadRequestException({ error: 'An error occurred while processing the files.' });
        }
      });
    } catch (error) {
      throw new BadRequestException({ error: 'An error occurred while processing the files.' });
    }
  }
}