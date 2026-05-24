import { Controller, Post, UploadedFile, UseInterceptors, Res, HttpException, HttpStatus } from '@nestjs/common';
import { FileInterceptor } from 'multer';
import { AppService } from './app.service';
import { Response } from 'express';
import { exec } from 'child_process';
import { promisify } from 'util';
import { v4 as uuidv4 } from 'uuid';
import * as fs from 'fs';
import * as path from 'path';

const execPromise = promisify(exec);

@Controller()
export class AppController {
  constructor(private readonly appService: AppService) {}

  @Post('convert')
  @UseInterceptors(FileInterceptor('file'))
  async convertPdfToText(@UploadedFile() file: Express.Multer.File, @Res() res: Response) {
    if (!file || !file.mimetype.includes('pdf')) {
      throw new HttpException('Bad Request - Invalid input or missing file', HttpStatus.BAD_REQUEST);
    }

    const safeFileName = `${uuidv4()}.pdf`;
    const tempFilePath = path.join('/tmp', safeFileName);
    const outputFilePath = path.join('/tmp', `${uuidv4()}.txt`).replace(/[^a-zA-Z0-9_.-]/g, ''); // Sanitized output file path

    try {
      fs.writeFileSync(tempFilePath, file.buffer);
      await execPromise(`pdftotext ${tempFilePath} ${outputFilePath}`);
      const text = await this.appService.readTextFile(outputFilePath);
      res.type('text/plain').send(text);
    } catch (error) {
      throw new HttpException('Internal Server Error - Conversion failed', HttpStatus.INTERNAL_SERVER_ERROR);
    } finally {
      // Clean up temporary files
      fs.unlinkSync(tempFilePath);
      fs.unlinkSync(outputFilePath);
    }
  }
}