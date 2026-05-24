import {
  Controller,
  Post,
  UploadedFile,
  Body,
  UseInterceptors,
  BadRequestException,
  Res,
} from '@nestjs/common';
import { FileInterceptor } from '@nestjs/platform-express';
import { AppService } from './app.service';
import { Response } from 'express';
import * as fs from 'fs';
import * as path from 'path';
import * as multer from 'multer';

@Controller()
export class AppController {
  constructor(private readonly appService: AppService) {}

  @Post('extract')
  @UseInterceptors(
    FileInterceptor('video', {
      storage: multer.diskStorage({
        destination: './uploads',
        filename: (req, file, cb) => {
          const sanitizedFilename = file.originalname.replace(/[^a-zA-Z0-9_.-]/g, '_');
          cb(null, `${Date.now()}_${sanitizedFilename}`);
        },
      }),
      fileFilter: (req, file, cb) => {
        if (!file.mimetype.startsWith('video/')) {
          return cb(new BadRequestException('Invalid file type'), false);
        }
        cb(null, true);
      },
    }),
  )
  async extractFrame(
    @UploadedFile() file: Express.Multer.File,
    @Body('frameNumber') frameNumber: string,
    @Res() res: Response,
  ) {
    if (!file) {
      throw new BadRequestException('No video file uploaded');
    }

    const frameIndex = parseInt(frameNumber, 10);
    if (isNaN(frameIndex) || frameIndex < 0) {
      throw new BadRequestException('Invalid frame number');
    }

    try {
      const extractedFramePath = await this.appService.extractFrame(file.path, frameIndex);

      // Send the extracted frame as a response
      res.setHeader('Content-Type', 'image/png');
      res.sendFile(path.resolve(extractedFramePath), () => {
        // Clean up temporary files
        fs.unlinkSync(file.path);
        fs.unlinkSync(extractedFramePath);
      });
    } catch (error) {
      // Clean up the uploaded file in case of an error
      if (fs.existsSync(file.path)) {
        fs.unlinkSync(file.path);
      }

      res.status(404).json({ error: `Frame at index ${frameIndex} could not be found.` });
    }
  }
}