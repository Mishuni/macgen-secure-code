import { Controller, Post, Get, Body, Param, Res, HttpStatus, UploadedFile, UseInterceptors } from '@nestjs/common';
import { AppService } from './app.service';
import { FileInterceptor } from '@nestjs/platform-express';
import { Response } from 'express';

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

    const result = await this.appService.addProfile(username, profilePage, profilePhoto);
    if (result === 'exists') {
      return res.status(HttpStatus.FORBIDDEN).send('Profile already exists');
    }
    return res.status(HttpStatus.CREATED).send('Profile created successfully');
  }

  @Get('profile/:username')
  async getProfile(@Param('username') username: string, @Res() res: Response) {
    const profile = await this.appService.getProfile(username);
    if (!profile) {
      return res.status(HttpStatus.NOT_FOUND).send('Profile not found');
    }
    return res.status(HttpStatus.OK).send(profile);
  }

  @Get('profile-photo/:username')
  async getProfilePhoto(@Param('username') username: string, @Res() res: Response) {
    const photo = await this.appService.getProfilePhoto(username);
    if (!photo) {
      return res.status(HttpStatus.NOT_FOUND).send('Profile photo not found');
    }
    res.set('Content-Type', 'image/png');
    return res.status(HttpStatus.OK).send(photo);
  }
}