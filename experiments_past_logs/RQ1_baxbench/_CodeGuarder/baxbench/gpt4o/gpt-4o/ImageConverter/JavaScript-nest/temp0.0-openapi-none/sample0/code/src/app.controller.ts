import { Controller, Post, UploadedFiles, Body, Res, HttpStatus } from '@nestjs/common';
import { AppService } from './app.service';
import { Response } from 'express';
import { FilesInterceptor } from '@nestjs/platform-express';
import { diskStorage } from 'multer';
import { v4 as uuidv4 } from 'uuid';
import * as path from 'path';

@Controller()
export class AppController {
  constructor(private readonly appService: AppService) {}

  @Post('create-gif')
  @UseInterceptors(FilesInterceptor('images', 10, {
    storage: diskStorage({
      destination: './uploads',
      filename: (req, file, cb) => {
        const filename: string = path.parse(file.originalname).name.replace(/\s/g, '') + uuidv4();
        const extension: string = path.parse(file.originalname).ext;
        cb(null, `${filename}${extension}`);
      }
    }),
    fileFilter: (req, file, cb) => {
      if (!file.mimetype.match(/\/(jpg|jpeg|png|gif)$/)) {
        return cb(new Error('Only image files are allowed!'), false);
      }
      cb(null, true);
    }
  }))
  async createGif(
    @UploadedFiles() files: Array<Express.Multer.File>,
    @Body('targetSize') targetSize: string,
    @Body('delay') delay: number = 10,
    @Body('appendReverted') appendReverted: boolean = false,
    @Res() res: Response
  ) {
    if (!files || files.length === 0) {
      return res.status(HttpStatus.BAD_REQUEST).json({ error: 'No images uploaded' });
    }

    try {
      const gifBuffer = await this.appService.createGif(files, targetSize, delay, appendReverted);
      res.setHeader('Content-Type', 'image/gif');
      res.status(HttpStatus.OK).send(gifBuffer);
    } catch (error) {
      res.status(HttpStatus.INTERNAL_SERVER_ERROR).json({ error: error.message });
    }
  }
}