import { Controller, Post, Get, Param, Res, UploadedFile, UseInterceptors, HttpException, HttpStatus } from '@nestjs/common';
import { FileInterceptor } from '@nestjs/platform-express';
import { diskStorage } from 'multer';
import { v4 as uuidv4 } from 'uuid';
import { AppService } from './app.service';
import { Response } from 'express';
import { join } from 'path';

@Controller()
export class AppController {
  constructor(private readonly appService: AppService) {}

  @Post('upload')
  @UseInterceptors(FileInterceptor('file', {
    storage: diskStorage({
      destination: './uploads',
      filename: (req, file, cb) => {
        const filename = `${uuidv4()}-${file.originalname}`;
        cb(null, filename);
      }
    }),
    limits: { fileSize: 5 * 1024 * 1024 }, // 5MB file size limit
    fileFilter: (req, file, cb) => {
      if (!file.mimetype.startsWith('image/')) {
        return cb(new HttpException('Invalid file type', HttpStatus.BAD_REQUEST), false);
      }
      cb(null, true);
    }
  }))
  async uploadFile(@UploadedFile() file: Express.Multer.File) {
    if (!file) {
      throw new HttpException('Invalid file', HttpStatus.BAD_REQUEST);
    }
    const id = await this.appService.saveFile(file.filename);
    return { id };
  }

  @Get('images/:imageId')
  async getImage(@Param('imageId') imageId: string, @Res() res: Response) {
    const filePath = await this.appService.getFilePath(imageId);
    if (!filePath) {
      throw new HttpException('Image not found', HttpStatus.NOT_FOUND);
    }
    res.sendFile(join(process.cwd(), filePath));
  }
}