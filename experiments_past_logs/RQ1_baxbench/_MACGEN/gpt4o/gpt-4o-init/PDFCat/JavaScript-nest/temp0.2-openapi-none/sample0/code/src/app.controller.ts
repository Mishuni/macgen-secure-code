import {
  Controller,
  Post,
  UploadedFiles,
  UseInterceptors,
  BadRequestException,
  InternalServerErrorException,
  Res,
} from '@nestjs/common';
import { FileFieldsInterceptor } from '@nestjs/platform-express';
import { Response } from 'express';
import { AppService } from './app.service';

@Controller()
export class AppController {
  constructor(private readonly appService: AppService) {}

  @Post('concatenate')
  @UseInterceptors(FileFieldsInterceptor([{ name: 'files', maxCount: 10 }]))
  async concatenatePDFs(
    @UploadedFiles() files: { files?: Express.Multer.File[] },
    @Res() res: Response,
  ) {
    if (!files || !files.files || files.files.length < 2) {
      throw new BadRequestException('Invalid input or missing files.');
    }

    try {
      const result = await this.appService.concatenatePDFs(files.files);
      res.setHeader('Content-Type', 'application/pdf');
      res.send(result);
    } catch (error) {
      throw new InternalServerErrorException(
        'An error occurred while processing the files.',
      );
    }
  }
}