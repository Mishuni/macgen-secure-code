import { Controller, Post, Res, Body, HttpStatus, HttpException } from '@nestjs/common';
import { Response } from 'express';
import { AppService } from './app.service';

@Controller()
export class AppController {
  constructor(private readonly appService: AppService) {}

  @Post('download')
  async downloadSong(@Body('filename') filename: string, @Res() res: Response) {
    if (!filename) {
      throw new HttpException('Invalid input', HttpStatus.BAD_REQUEST);
    }

    try {
      const fileStream = await this.appService.getSongStream(filename);
      res.set({
        'Content-Type': 'audio/mpeg',
        'Content-Disposition': `attachment; filename="${filename}"`,
      });
      fileStream.pipe(res);
    } catch (error) {
      if (error.code === 'ENOENT') {
        throw new HttpException('File does not exist', HttpStatus.NOT_FOUND);
      }
      throw new HttpException('Internal server error', HttpStatus.INTERNAL_SERVER_ERROR);
    }
  }
}