import {
  Controller,
  Post,
  Get,
  Param,
  UploadedFile,
  UseInterceptors,
  Res,
  HttpException,
  HttpStatus,
} from '@nestjs/common';
import { AppService } from './app.service';
import { FileInterceptor } from '@nestjs/platform-express';
import { Response } from 'express';

@Controller()
export class AppController {
  constructor(private readonly appService: AppService) {}

  @Post('upload')
  @UseInterceptors(FileInterceptor('file'))
  uploadImage(@UploadedFile() file: Express.Multer.File) {
    if (!file) {
      throw new HttpException(
        { error: 'No file uploaded' },
        HttpStatus.BAD_REQUEST,
      );
    }

    // Save the image and return the ID
    const imageId = this.appService.saveImage(file);
    return { id: imageId };
  }

  @Get('images/:imageId')
  viewImage(@Param('imageId') imageId: string, @Res() res: Response) {
    const filePath = this.appService.getImagePath(imageId);

    if (!filePath) {
      throw new HttpException(
        { error: 'Image not found' },
        HttpStatus.NOT_FOUND,
      );
    }

    // Stream the image file to the browser
    res.sendFile(filePath, { headers: { 'Content-Disposition': 'inline' } });
  }
}