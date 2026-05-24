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
      filename: (req, file, cb) => {
        const uniqueSuffix = Date.now() + '-' + Math.round(Math.random() * 1E9);
        cb(null, `${file.fieldname}-${uniqueSuffix}${extname(file.originalname)}`);
      }
    }),
    fileFilter: (req, file, cb) => {
      if (file.mimetype !== 'image/png') {
        return cb(new Error('Only PNG files are allowed!'), false);
      }
      cb(null, true);
    }
  }))
  async addProfile(
    @Body('username') username: string,
    @Body('profile_page') profilePage: string,
    @UploadedFile() profilePhoto: Express.Multer.File,
    @Res() res: Response
  ) {
    try {
      await this.appService.addProfile(username, profilePage, profilePhoto.filename);
      return res.status(HttpStatus.CREATED).send('Profile created successfully');
    } catch (error) {
      if (error.message === 'Profile already exists') {
        return res.status(HttpStatus.FORBIDDEN).send('Profile already exists, creation forbidden');
      }
      return res.status(HttpStatus.BAD_REQUEST).send('Invalid input');
    }
  }

  @Get('profile/:username')
  async getProfile(@Param('username') username: string, @Res() res: Response) {
    try {
      const profilePage = await this.appService.getProfile(username);
      return res.status(HttpStatus.OK).send(profilePage);
    } catch (error) {
      return res.status(HttpStatus.NOT_FOUND).send('Profile not found');
    }
  }

  @Get('profile-photo/:username')
  async getProfilePhoto(@Param('username') username: string, @Res() res: Response) {
    try {
      const profilePhotoPath = await this.appService.getProfilePhoto(username);
      return res.status(HttpStatus.OK).sendFile(profilePhotoPath, { root: './uploads' });
    } catch (error) {
      return res.status(HttpStatus.NOT_FOUND).send('Profile photo not found');
    }
  }
}