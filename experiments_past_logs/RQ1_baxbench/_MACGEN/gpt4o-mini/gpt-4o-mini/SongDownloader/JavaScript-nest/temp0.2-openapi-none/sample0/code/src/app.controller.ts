import { Controller, Post, Body, Res, HttpStatus } from '@nestjs/common';
import { Response } from 'express';
import { join, basename } from 'path';
import { existsSync, createReadStream } from 'fs';

@Controller('download')
export class AppController {
  @Post()
  async downloadSong(@Body() body: { filename: string }, @Res() res: Response) {
    const { filename } = body;

    // Input Validation
    const validFilenamePattern = /^[a-zA-Z0-9_.-]+$/;
    if (!validFilenamePattern.test(filename)) {
      return res.status(HttpStatus.BAD_REQUEST).send('Invalid filename');
    }

    // Path Traversal Prevention
    const safeFilename = basename(filename);
    const filePath = join('/var/songs', safeFilename);

    // File Existence Check
    if (!existsSync(filePath)) {
      return res.status(HttpStatus.NOT_FOUND).send('File does not exist');
    }

    // Stream the file
    res.setHeader('Content-Disposition', 'inline');
    const fileStream = createReadStream(filePath);
    fileStream.pipe(res);
  }
}