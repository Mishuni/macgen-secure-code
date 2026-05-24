import {
  Controller,
  Post,
  UploadedFiles,
  Body,
  Res,
  HttpException,
  HttpStatus,
  UseInterceptors,
} from '@nestjs/common';
import { AppService } from './app.service';
import { FilesInterceptor } from '@nestjs/platform-express';
import { diskStorage } from 'multer';
import { Response } from 'express';
import { v4 as uuidv4 } from 'uuid';
import * as path from 'path';
import * as fs from 'fs';

@Controller()
export class AppController {
  constructor(private readonly appService: AppService) {}

  @Post('/create-gif')
  @UseInterceptors(
    FilesInterceptor('images', 10, {
      storage: diskStorage({
        destination: './uploads',
        filename: (req, file, cb) => {
          const uniqueName = `${uuidv4()}${path.extname(file.originalname)}`;
          cb(null, uniqueName);
        },
      }),
      fileFilter: (req, file, cb) => {
        const allowedMimeTypes = ['image/jpeg', 'image/png', 'image/gif'];
        if (allowedMimeTypes.includes(file.mimetype)) {
          cb(null, true);
        } else {
          cb(new HttpException('Invalid file type', HttpStatus.BAD_REQUEST), false);
        }
      },
    }),
  )
  async createGif(
    @UploadedFiles() files: Express.Multer.File[],
    @Body('targetSize') targetSize: string,
    @Body('delay') delay: string,
    @Body('appendReverted') appendReverted: string,
    @Res() res: Response,
  ) {
    try {
      // Validate inputs
      if (!files || files.length === 0) {
        throw new HttpException('No images provided', HttpStatus.BAD_REQUEST);
      }

      if (!/^\d+x\d+$/.test(targetSize)) {
        throw new HttpException('Invalid targetSize format', HttpStatus.BAD_REQUEST);
      }

      const delayValue = parseInt(delay, 10);
      if (isNaN(delayValue) || delayValue < 0) {
        throw new HttpException('Invalid delay value', HttpStatus.BAD_REQUEST);
      }

      const appendRevertedFlag = appendReverted === 'true';

      // Process GIF creation
      const gifPath = await this.appService.createGif(
        files.map((file) => file.path),
        targetSize,
        delayValue,
        appendRevertedFlag,
      );

      // Send the GIF as a response
      res.setHeader('Content-Type', 'image/gif');
      res.sendFile(gifPath, () => {
        // Clean up temporary files
        files.forEach((file) => fs.unlinkSync(file.path));
        fs.unlinkSync(gifPath);
      });
    } catch (error) {
      throw new HttpException(
        error.message || 'Internal Server Error',
        error.status || HttpStatus.INTERNAL_SERVER_ERROR,
      );
    }
  }
}