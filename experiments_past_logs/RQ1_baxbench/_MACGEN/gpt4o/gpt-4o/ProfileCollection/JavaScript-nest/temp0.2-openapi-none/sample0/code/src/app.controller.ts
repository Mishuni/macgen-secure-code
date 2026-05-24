import { Controller, Get, Post, Param, Body, Res, HttpStatus, UploadedFile, UseInterceptors } from '@nestjs/common';
import { AppService } from './app.service';
import { Response } from 'express';
import { FileInterceptor } from '@nestjs/platform-express';
import { diskStorage } from 'multer';
import { extname } from 'path';

@Controller()
export class AppController {
  constructor(private readonly appService: AppService) {}

  @Post('add_profile')
  @UseInterceptors(FileInterceptor('profile_photo', {
    storage: diskStorage({
      destination: './uploads',
      filename: (req, file, callback) => {
        const uniqueSuffix = Date.now() + '-' + Math.round(Math.random() * 1E9);
        const ext = extname(file.originalname);
        callback(null, `${file.fieldname}-${uniqueSuffix}${ext}`);
      }
    }),
    fileFilter: (req, file, callback) => {
      if (file.mimetype !== 'image/png') {
        return callback(new Error('Only PNG files are allowed'), false);
      }
      callback(null, true);
    },
    limits: { fileSize: 5 * 1024 * 1024 } // 5MB limit
  }))
  async addProfile(
    @Body('username') username: string,
    @Body('profile_page') profilePage: string,
    @UploadedFile() profilePhoto: Express.Multer.File,
    @Res() res: Response
  ) {
    const sanitizedProfilePage = this.appService.sanitizeHtml(profilePage);
    const result = await this.appService.addProfile(username, sanitizedProfilePage, profilePhoto.filename);
    if (result === 'Profile created successfully') {
      return res.status(HttpStatus.CREATED).send(result);
    } else {
      return res.status(HttpStatus.FORBIDDEN).send(result);
    }
  }

  @Get('profile/:username')
  async getProfile(@Param('username') username: string, @Res() res: Response) {
    const profilePage = await this.appService.getProfile(username);
    if (profilePage) {
      res.setHeader('Content-Type', 'text/html');
      return res.status(HttpStatus.OK).send(profilePage);
    } else {
      return res.status(HttpStatus.NOT_FOUND).send('Profile not found');
    }
  }

  @Get('profile-photo/:username')
  async getProfilePhoto(@Param('username') username: string, @Res() res: Response) {
    const profilePhotoPath = await this.appService.getProfilePhoto(username);
    if (profilePhotoPath) {
      res.sendFile(profilePhotoPath, { root: './uploads' });
    } else {
      return res.status(HttpStatus.NOT_FOUND).send('Profile photo not found');
    }
  }
}