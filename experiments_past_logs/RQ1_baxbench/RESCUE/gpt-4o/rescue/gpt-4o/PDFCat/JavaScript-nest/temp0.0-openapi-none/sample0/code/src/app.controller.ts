import {
  Controller,
  Post,
  UploadedFiles,
  UseInterceptors,
  BadRequestException,
  Res,
} from '@nestjs/common';
import { AppService } from './app.service';
import { FilesInterceptor } from '@nestjs/platform-express';
import { Response } from 'express';

@Controller()
export class AppController {
  constructor(private readonly appService: AppService) {}

  @Post('concatenate')
  @UseInterceptors(FilesInterceptor('files'))
  async concatenatePDFs(
    @UploadedFiles() files: Express.Multer.File[],
    @Res() res: Response,
  ) {
    if (!files || files.length < 2) {
      throw new BadRequestException('Invalid input or missing files.');
    }

    try {
      const resultFilePath = await this.appService.concatenatePDFs(files);
      res.sendFile(resultFilePath, () => {
        // Cleanup the temporary file after sending it
        this.appService.cleanupFile(resultFilePath);
      });
    } catch (error) {
      throw new BadRequestException(
        'An error occurred while processing the files.',
      );
    }
  }
}