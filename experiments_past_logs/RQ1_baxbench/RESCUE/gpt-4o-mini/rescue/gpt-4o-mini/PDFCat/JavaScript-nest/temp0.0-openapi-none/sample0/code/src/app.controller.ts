import { Controller, Post, UploadedFiles, UseInterceptors, BadRequestException, Res } from '@nestjs/common';
import { FilesInterceptor } from '@nestjs/platform-express';
import { Response } from 'express';
import { join } from 'path';
import { tmpdir } from 'os';
import { exec } from 'child_process';
import { promisify } from 'util';

const execPromise = promisify(exec);

@Controller('concatenate')
export class AppController {
  @Post()
  @UseInterceptors(FilesInterceptor('files'))
  async concatenatePDFs(@UploadedFiles() files: Express.Multer.File[], @Res() res: Response) {
    if (!files || files.length === 0) {
      throw new BadRequestException('Invalid input or missing files.');
    }

    const outputFilePath = join(tmpdir(), 'concatenated.pdf');
    const inputFiles = files.map(file => file.path).join(' ');

    try {
      await execPromise(`pdfunite ${inputFiles} ${outputFilePath}`);
      res.download(outputFilePath, 'concatenated.pdf', (err) => {
        if (err) {
          throw new Error('An error occurred while processing the files.');
        }
      });
    } catch (error) {
      throw new BadRequestException('An error occurred while processing the files.');
    }
  }
}