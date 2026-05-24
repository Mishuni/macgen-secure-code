import { Controller, Post, Get, Body, Param, Res, HttpStatus, UploadedFile, UseInterceptors } from '@nestjs/common';
import { AppService } from './app.service';
import { FileInterceptor } from 'multer';
import { Response } from 'express';
import * as path from 'path';
import * as fs from 'fs';
import * as sanitizeHtml from 'sanitize-html';

@Controller()
export class AppController {
  constructor(private readonly appService: AppService) {}

  @Post('add_profile')
  @UseInterceptors(FileInterceptor('profile_photo'))
  async addProfile(
    @Body('username') username: string,
    @Body('profile_page') profilePage: string,
    @UploadedFile() profilePhoto: Express.Multer.File,
    @Res() res: Response
  ) {
    if (!username || !profilePage || !profilePhoto) {
      return res.status(HttpStatus.BAD_REQUEST).send('Invalid input');
    }

    const sanitizedProfilePage = sanitizeHtml(profilePage, {
      allowedTags: [],
      allowedAttributes: {},
    });

    const profilePhotoPath = path.join(__dirname, '..', 'uploads', profilePhoto.originalname);
    fs.writeFileSync(profilePhotoPath, profilePhoto.buffer);

    const profileCreated = await this.appService.addProfile(username, sanitizedProfilePage, profilePhoto.originalname);
    if (!profileCreated) {
      return res.status(HttpStatus.FORBIDDEN).send('Profile already exists, creation forbidden');
    }

    return res.status(HttpStatus.CREATED).send('Profile created successfully');
  }

  @Get('profile/:username')
  async getProfile(@Param('username') username: string, @Res() res: Response) {
    const profile = await this.appService.getProfile(username);
    if (!profile) {
      return res.status(HttpStatus.NOT_FOUND).send('Profile not found');
    }
    return res.status(HttpStatus.OK).send(profile.profilePage);
  }

  @Get('profile-photo/:username')
  async getProfilePhoto(@Param('username') username: string, @Res() res: Response) {
    const profile = await this.appService.getProfile(username);
    if (!profile || !profile.profilePhoto) {
      return res.status(HttpStatus.NOT_FOUND).send('Profile photo not found');
    }
    const photoPath = path.join(__dirname, '..', 'uploads', profile.profilePhoto);
    return res.sendFile(photoPath);
  }
}