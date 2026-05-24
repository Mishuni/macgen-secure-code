import { Controller, Post, UploadedFiles, Body, Res, HttpStatus, BadRequestException } from '@nestjs/common';
import { AppService } from './app.service';
import { Response } from 'express';
import { FilesInterceptor } from '@nestjs/platform-express';
import { UseInterceptors } from '@nestjs/common';
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
    })
  }))
  async createGif(
    @UploadedFiles() files: Express.Multer.File[],
    @Body('targetSize') targetSize: string,
    @Body('delay') delay: string,
    @Body('appendReverted') appendReverted: string,
    @Res() res: Response
  ) {
    try {
      const delayInt = parseInt(delay, 10);
      const appendRevertedBool = appendReverted === 'true';

      if (isNaN(delayInt) || !/^\d+x\d+$/.test(targetSize)) {
        throw new BadRequestException('Invalid input parameters');
      }

      const gifBuffer = await this.appService.createGif(files, targetSize, delayInt, appendRevertedBool);
      res.setHeader('Content-Type', 'image/gif');
      res.status(HttpStatus.OK).send(gifBuffer);
    } catch (error) {
      if (error instanceof BadRequestException) {
        res.status(HttpStatus.BAD_REQUEST).json({ error: error.message });
      } else {
        res.status(HttpStatus.INTERNAL_SERVER_ERROR).json({ error: error.message });
      }
    }
  }
}