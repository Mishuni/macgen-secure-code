import { Controller, Post, Get, Param, UploadedFile, UseInterceptors, Res, HttpException, HttpStatus } from '@nestjs/common';
import { FileInterceptor } from '@nestjs/platform-express';
import { AppService } from './app.service';
import { Express, Response } from 'express';

@Controller()
export class AppController {
  constructor(private readonly appService: AppService) {}

  @Post('upload')
  @UseInterceptors(FileInterceptor('file'))
  async uploadImage(@UploadedFile() file: Express.Multer.File) {
    if (!file || !this.isValidMimeType(file.mimetype)) {
      throw new HttpException('Invalid input', HttpStatus.BAD_REQUEST);
    }
    const imageId = await this.appService.saveImage(file);
    return { id: imageId };
  }

  @Get('images/:imageId')
  async getImage(@Param('imageId') imageId: string, @Res() res: Response) {
    try {
      const { buffer, mimetype } = await this.appService.getImage(imageId);
      res.setHeader('Content-Type', mimetype);
      res.send(buffer);
    } catch (error) {
      throw new HttpException('Image not found', HttpStatus.NOT_FOUND);
    }
  }

  private isValidMimeType(mimetype: string): boolean {
    const allowedMimeTypes = ['image/jpeg', 'image/png', 'image/gif', 'image/webp'];
    return allowedMimeTypes.includes(mimetype);
  }
}