import { Controller, Post, Body, Res, HttpStatus } from '@nestjs/common';
import { AppService } from './app.service';
import { Response } from 'express';

@Controller()
export class AppController {
  constructor(private readonly appService: AppService) {}

  @Post('download')
  async downloadSong(@Body('filename') filename: string, @Res() res: Response) {
    if (!filename || typeof filename !== 'string') {
      return res.status(HttpStatus.BAD_REQUEST).send('Invalid input');
    }

    try {
      const fileStream = await this.appService.getSongStream(filename);
      if (!fileStream) {
        return res.status(HttpStatus.NOT_FOUND).send('File does not exist');
      }

      res.set({
        'Content-Type': 'audio/mpeg',
        'Content-Disposition': `attachment; filename="${filename}"`,
      });

      fileStream.pipe(res);
    } catch (error) {
      return res.status(HttpStatus.INTERNAL_SERVER_ERROR).send('Error streaming file');
    }
  }
}