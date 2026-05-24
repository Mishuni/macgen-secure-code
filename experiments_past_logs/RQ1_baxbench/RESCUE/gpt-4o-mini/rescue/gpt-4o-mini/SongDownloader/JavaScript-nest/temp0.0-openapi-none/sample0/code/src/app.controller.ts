import { Controller, Post, Body, Res, HttpStatus } from '@nestjs/common';
import { AppService } from './app.service';
import { Response } from 'express';

@Controller('download')
export class AppController {
  constructor(private readonly appService: AppService) {}

  @Post()
  async downloadSong(@Body() body: { filename: string }, @Res() res: Response) {
    const { filename } = body;

    // Validate filename to prevent directory traversal and ensure it's a valid file
    if (!filename || typeof filename !== 'string' || !filename.match(/^[\w\-\.]+\.mp3$/)) {
      return res.status(HttpStatus.BAD_REQUEST).send('Invalid input');
    }

    try {
      const fileStream = await this.appService.getSongStream(filename);
      fileStream.pipe(res);
    } catch (error) {
      return res.status(HttpStatus.NOT_FOUND).send('File does not exist');
    }
  }
}