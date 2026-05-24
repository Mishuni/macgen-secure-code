import { Controller, Post, UseInterceptors, UploadedFile, BadRequestException } from '@nestjs/common';
import { AppService } from './app.service';
import { FileInterceptor } from '@nestjs/platform-express';

@Controller()
export class AppController {
  constructor(private readonly appService: AppService) {}

  @Post('convert')
  @UseInterceptors(FileInterceptor('file', {
    limits: { fileSize: 5 * 1024 * 1024 }, // 5 MB limit
    fileFilter: (req, file, cb) => {
      if (file.mimetype !== 'application/zip') {
        return cb(new BadRequestException('Only zip files are allowed!'), false);
      }
      cb(null, true);
    },
  }))
  async convert(@UploadedFile() file: Express.Multer.File): Promise<string> {
    return this.appService.convertZipToText(file);
  }
}