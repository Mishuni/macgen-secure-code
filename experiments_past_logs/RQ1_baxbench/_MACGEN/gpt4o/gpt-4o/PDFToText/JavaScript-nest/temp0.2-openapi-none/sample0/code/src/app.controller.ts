import { Controller, Post, UploadedFile, UseInterceptors, BadRequestException, InternalServerErrorException } from '@nestjs/common';
import { FileInterceptor } from '@nestjs/platform-express';
import { AppService } from './app.service';
import { diskStorage } from 'multer';
import { extname } from 'path';
import { v4 as uuidv4 } from 'uuid';

@Controller()
export class AppController {
  constructor(private readonly appService: AppService) {}

  @Post('convert')
  @UseInterceptors(FileInterceptor('file', {
    storage: diskStorage({
      destination: './uploads',
      filename: (req, file, callback) => {
        const uniqueSuffix = uuidv4() + extname(file.originalname);
        callback(null, uniqueSuffix);
      },
    }),
    fileFilter: (req, file, callback) => {
      if (!file.originalname.match(/\.pdf$/)) {
        return callback(new BadRequestException('Only PDF files are allowed!'), false);
      }
      callback(null, true);
    },
  }))
  async convertPdfToText(@UploadedFile() file: Express.Multer.File): Promise<string> {
    if (!file) {
      throw new BadRequestException('File is required');
    }

    try {
      const text = await this.appService.convertPdfToText(file.path);
      return text;
    } catch (error) {
      throw new InternalServerErrorException('Failed to convert PDF to text');
    }
  }
}