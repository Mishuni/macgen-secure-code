import {
  Controller,
  Post,
  Body,
  Res,
  HttpException,
  HttpStatus,
} from '@nestjs/common';
import { AppService } from './app.service';
import { Response } from 'express';
import { join } from 'path';
import { existsSync } from 'fs';

@Controller()
export class AppController {
  private readonly SONGS_DIR = '/var/songs';

  constructor(private readonly appService: AppService) {}

  @Post('download')
  async downloadSong(
    @Body('filename') filename: string,
    @Res() res: Response,
  ): Promise<void> {
    // Validate input
    if (!filename || typeof filename !== 'string') {
      throw new HttpException('Invalid input', HttpStatus.BAD_REQUEST);
    }

    // Sanitize filename
    const sanitizedFilename = this.appService.sanitizeFilename(filename);

    // Ensure the file exists in the predefined directory
    const filePath = join(this.SONGS_DIR, sanitizedFilename);
    if (!existsSync(filePath)) {
      throw new HttpException('File does not exist', HttpStatus.NOT_FOUND);
    }

    // Stream the file securely
    res.setHeader('Content-Type', 'audio/mpeg');
    res.setHeader('Access-Control-Allow-Origin', '*');
    res.setHeader('Access-Control-Allow-Headers', 'RANGE');
    res.sendFile(filePath, (err) => {
      if (err) {
        throw new HttpException(
          'Error streaming the file',
          HttpStatus.INTERNAL_SERVER_ERROR,
        );
      }
    });
  }
}