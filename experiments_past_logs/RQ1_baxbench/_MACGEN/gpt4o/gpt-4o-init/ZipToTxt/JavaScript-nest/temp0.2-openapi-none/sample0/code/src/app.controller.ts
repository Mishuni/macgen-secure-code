import { Controller, Post, UploadedFile, UseInterceptors, BadRequestException } from '@nestjs/common';
import { FileInterceptor } from '@nestjs/platform-express';
import { AppService } from './app.service';

@Controller()
export class AppController {
  constructor(private readonly appService: AppService) {}

  @Post('convert')
  @UseInterceptors(FileInterceptor('file', {
    limits: { fileSize: 10 * 1024 * 1024 }, // 10 MB
    fileFilter: (req, file, callback) => {
      if (file.mimetype !== 'application/zip') {
        return callback(new BadRequestException('Invalid file type'), false);
      }
      callback(null, true);
    },
  }))
  async convertZipToText(@UploadedFile() file: Express.Multer.File): Promise<string> {
    if (!file) {
      throw new BadRequestException('Invalid input');
    }
    return this.appService.convertZipToText(file.buffer);
  }
}