import {
  Controller,
  Post,
  Get,
  Param,
  Body,
  UploadedFile,
  UseInterceptors,
  HttpException,
  HttpStatus,
} from '@nestjs/common';
import { AppService } from './app.service';
import { FileInterceptor } from '@nestjs/platform-express';
import { diskStorage } from 'multer';
import { extname } from 'path';
import { escape } from 'querystring';

@Controller()
export class AppController {
  constructor(private readonly appService: AppService) {}

  @Post('add_profile')
  @UseInterceptors(
    FileInterceptor('profile_photo', {
      storage: diskStorage({
        destination: './uploads',
        filename: (req, file, callback) => {
          const uniqueSuffix = Date.now() + '-' + Math.round(Math.random() * 1e9);
          const ext = extname(file.originalname);
          callback(null, `${uniqueSuffix}${ext}`);
        },
      }),
      fileFilter: (req, file, callback) => {
        if (file.mimetype !== 'image/png') {
          return callback(
            new HttpException('Only PNG files are allowed', HttpStatus.BAD_REQUEST),
            false,
          );
        }
        callback(null, true);
      },
    }),
  )
  async addProfile(
    @Body('username') username: string,
    @Body('profile_page') profilePage: string,
    @UploadedFile() profilePhoto: Express.Multer.File,
  ) {
    if (!username || !profilePage || !profilePhoto) {
      throw new HttpException('Invalid input', HttpStatus.BAD_REQUEST);
    }

    // Sanitize inputs
    const sanitizedUsername = escape(username);
    const sanitizedProfilePage = escape(profilePage);

    const result = await this.appService.addProfile(
      sanitizedUsername,
      sanitizedProfilePage,
      profilePhoto.filename,
    );

    if (!result) {
      throw new HttpException('Profile already exists', HttpStatus.FORBIDDEN);
    }

    return { message: 'Profile created successfully' };
  }

  @Get('profile/:username')
  async getProfile(@Param('username') username: string) {
    const sanitizedUsername = escape(username);
    const profile = await this.appService.getProfile(sanitizedUsername);

    if (!profile) {
      throw new HttpException('Profile not found', HttpStatus.NOT_FOUND);
    }

    return profile.profilePage;
  }

  @Get('profile-photo/:username')
  async getProfilePhoto(@Param('username') username: string) {
    const sanitizedUsername = escape(username);
    const profilePhoto = await this.appService.getProfilePhoto(sanitizedUsername);

    if (!profilePhoto) {
      throw new HttpException('Profile photo not found', HttpStatus.NOT_FOUND);
    }

    return { path: `uploads/${profilePhoto}` };
  }
}