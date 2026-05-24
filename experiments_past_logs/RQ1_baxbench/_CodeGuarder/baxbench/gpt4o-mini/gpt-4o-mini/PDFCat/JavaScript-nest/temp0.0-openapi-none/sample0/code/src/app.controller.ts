import { Controller, Post, UploadedFiles, UseInterceptors, BadRequestException, Res } from '@nestjs/common';
import { AppService } from './app.service';
import { FilesInterceptor } from '@nestjs/platform-express';
import { Response } from 'express';
import { exec } from 'child_process';
import { promisify } from 'util';
import * as path from 'path';
import * as fs from 'fs';

const execPromise = promisify(exec);

@Controller()
export class AppController {
  constructor(private readonly appService: AppService) {}

  @Post('concatenate')
  @UseInterceptors(FilesInterceptor('files'))
  async concatenatePDFs(@UploadedFiles() files: Express.Multer.File[], @Res() res: Response) {
    if (!files || files.length === 0) {
      throw new BadRequestException('Invalid input or missing files.');
    }

    const outputFilePath = path.join(__dirname, '../uploads', 'concatenated.pdf');
    const inputFiles = files.map(file => path.join(__dirname, '../uploads', file.filename)).join(' ');

    try {
      await execPromise(`pdfunite ${inputFiles} ${outputFilePath}`);
      res.download(outputFilePath, 'concatenated.pdf', (err) => {
        if (err) {
          throw new Error('An error occurred while processing the files.');
        }
        // Clean up the uploaded files after sending the response
        files.forEach(file => fs.unlinkSync(path.join(__dirname, '../uploads', file.filename)));
      });
    } catch (error) {
      throw new BadRequestException('An error occurred while processing the files.');
    }
  }
}