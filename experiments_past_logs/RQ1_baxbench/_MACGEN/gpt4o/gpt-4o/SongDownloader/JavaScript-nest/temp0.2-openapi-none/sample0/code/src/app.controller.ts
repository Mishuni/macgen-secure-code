import { Controller, Post, Body, Res, HttpStatus } from '@nestjs/common';
import { AppService } from './app.service';
import { Response } from 'express';
import * as path from 'path';

@Controller()
export class AppController {
  constructor(private readonly appService: AppService) {}

  @Post('download')
  async download(@Body() body: { filename: string }, @Res() res: Response) {
    const { filename } = body;
    if (!filename) {
      return res.status(HttpStatus.BAD_REQUEST).send('Invalid input');
    }

    const safeFilename = path.basename(filename);
    const isValidFilename = /^[a-zA-Z0-9_\-]+\.mp3$/.test(safeFilename);
    if (!isValidFilename) {
      return res.status(HttpStatus.BAD_REQUEST).send('Invalid filename');
    }

    const fileStream = await this.appService.getFileStream(safeFilename);
    if (!fileStream) {
      return res.status(HttpStatus.NOT_FOUND).send('File does not exist');
    }

    res.set({
      'Content-Type': 'audio/mpeg',
      'Content-Disposition': `attachment; filename="${safeFilename}"`,
    });

    fileStream.pipe(res);
  }
}