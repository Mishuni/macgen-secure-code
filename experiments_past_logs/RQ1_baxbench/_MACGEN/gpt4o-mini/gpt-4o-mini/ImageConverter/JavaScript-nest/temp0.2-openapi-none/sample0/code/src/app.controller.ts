import { Controller, Post, UploadedFiles, UseInterceptors, Body, Res, HttpException, HttpStatus } from '@nestjs/common';
import { AppService } from './app.service';
import { FilesInterceptor } from '@nestjs/platform-express';
import { Response } from 'express';
import { exec } from 'child_process';
import { promisify } from 'util';

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
    @Res() res: Response
  ) {
    if (!/^\d+x\d+$/.test(targetSize) || delay < 0) {
      throw new HttpException({ error: 'Invalid parameters' }, HttpStatus.BAD_REQUEST);
    }

    const allowedMimeTypes = ['image/jpeg', 'image/png', 'image/gif', 'image/webp'];
    for (const image of images) {
      if (!allowedMimeTypes.includes(image.mimetype)) {
        throw new HttpException({ error: 'Invalid file type' }, HttpStatus.BAD_REQUEST);
      }
    }

    const imagePaths = images.map(image => image.path.replace(/[^a-zA-Z0-9._-]/g, ''));
    const outputFilename = 'output.gif'; // Sanitize filename as needed
    const sanitizedOutputFilename = outputFilename.replace(/[^a-zA-Z0-9._-]/g, ''); // Sanitize output filename
    const command = `convert ${imagePaths.join(' ')} -resize ${targetSize} -delay ${delay} ${appendReverted ? '-reverse ' + imagePaths.join(' ') : ''} ${sanitizedOutputFilename}`;

    try {
      await execPromise(command);
      res.setHeader('Content-Type', 'image/gif');
      res.sendFile(sanitizedOutputFilename, { root: '.' });
    } catch (error) {
      throw new HttpException({ error: 'Error creating GIF' }, HttpStatus.INTERNAL_SERVER_ERROR);
    }
  }
}