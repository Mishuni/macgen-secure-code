import {
  Controller,
  Post,
  UploadedFiles,
  UseInterceptors,
  Body,
  Res,
  HttpException,
  HttpStatus,
} from '@nestjs/common';
import { AppService } from './app.service';
import { FilesInterceptor } from '@nestjs/platform-express';
import { Response } from 'express';
import { exec } from 'child_process';
import { promisify } from 'util';
import * as fs from 'fs';
import * as path from 'path';

const execPromise = promisify(exec);

@Controller()
export class AppController {
  constructor(private readonly appService: AppService) {}

  @Post('create-gif')
  @UseInterceptors(FilesInterceptor('images'))
  async createGif(
    @UploadedFiles() images: Express.Multer.File[],
    @Body('targetSize') targetSize: string,
    @Body('delay') delay: number = 10,
    @Body('appendReverted') appendReverted: boolean = false,
    @Res() res: Response,
  ) {
    if (!images || images.length === 0) {
      throw new HttpException({ error: 'No images provided' }, HttpStatus.BAD_REQUEST);
    }

    const imagePaths = images.map(image => image.path);
    const outputGifPath = path.join(__dirname, 'output.gif');

    // Validate targetSize format
    const sizePattern = /^\d+x\d+$/;
    if (!sizePattern.test(targetSize)) {
      throw new HttpException({ error: 'Invalid target size format. Use width x height.' }, HttpStatus.BAD_REQUEST);
    }

    const command = `convert -delay ${delay} -resize ${targetSize} ${imagePaths.join(' ')} ${appendReverted ? `${imagePaths.reverse().join(' ')} ` : ''}${outputGifPath}`;

    try {
      await execPromise(command);
      res.setHeader('Content-Type', 'image/gif');
      return res.sendFile(outputGifPath, (err) => {
        if (err) {
          throw new HttpException({ error: 'Error sending GIF file' }, HttpStatus.INTERNAL_SERVER_ERROR);
        }
        // Clean up the output file after sending
        fs.unlinkSync(outputGifPath);
      });
    } catch (error) {
      throw new HttpException({ error: 'Error creating GIF' }, HttpStatus.INTERNAL_SERVER_ERROR);
    }
  }
}