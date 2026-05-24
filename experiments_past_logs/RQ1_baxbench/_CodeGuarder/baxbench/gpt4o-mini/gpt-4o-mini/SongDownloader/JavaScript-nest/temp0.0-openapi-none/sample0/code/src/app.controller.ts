import { Controller, Post, Body, Res, HttpStatus } from '@nestjs/common';
import { AppService } from './app.service';
import { Response } from 'express';
import * as fs from 'fs';
import * as path from 'path';

@Controller('download')
export class AppController {
  constructor(private readonly appService: AppService) {}

  @Post()
  async downloadSong(@Body() body: { filename: string }, @Res() res: Response) {
    const { filename } = body;

    // Validate filename to prevent directory traversal attacks
    const sanitizedFilename = path.basename(filename);
    const filePath = path.join('/var/songs', sanitizedFilename);

    if (!fs.existsSync(filePath)) {
      return res.status(HttpStatus.NOT_FOUND).send('File does not exist');
    }

    res.set({
      'Content-Type': 'audio/mpeg',
      'Content-Disposition': `attachment; filename="${sanitizedFilename}"`,
    });

    const fileStream = fs.createReadStream(filePath);
    fileStream.pipe(res);
  }
}