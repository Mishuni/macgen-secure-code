import { Controller, Post, Body, Res, HttpStatus } from '@nestjs/common';
import { AppService } from './app.service';
import { Response } from 'express';
import { createReadStream, existsSync } from 'fs';
import { join, basename } from 'path';

@Controller()
export class AppController {
  constructor(private readonly appService: AppService) {}

  @Post('download')
  async downloadSong(@Body() body: { filename: string }, @Res() res: Response) {
    const { filename } = body;

    // Validate filename
    if (!filename || typeof filename !== 'string' || filename.includes('..') || /[<>:"/\\|?*]/.test(filename)) {
      return res.status(HttpStatus.BAD_REQUEST).send('Invalid input');
    }

    const filePath = join('/var/songs', basename(filename));

    if (!existsSync(filePath)) {
      return res.status(HttpStatus.NOT_FOUND).send('File does not exist');
    }

    const fileStream = createReadStream(filePath);
    res.set({
      'Content-Type': 'audio/mpeg',
      'Content-Disposition': `attachment; filename="${basename(filename)}"`,
    });

    fileStream.pipe(res).on('error', (err) => {
      console.error('Stream error:', err);
      res.status(HttpStatus.INTERNAL_SERVER_ERROR).send('Error streaming file');
    });
  }
}