import { Controller, Post, Get, Body, Param, Res, HttpStatus } from '@nestjs/common';
import { AppService } from './app.service';
import { Response } from 'express';
import { ProfileDto } from './profile.dto';

@Controller()
export class AppController {
  constructor(private readonly appService: AppService) {}

  @Post('add_profile')
  async addProfile(@Body() profileDto: ProfileDto, @Res() res: Response) {
    try {
      const profile = await this.appService.addProfile(profileDto);
      return res.status(HttpStatus.CREATED).json(profile);
    } catch (error) {
      if (error.message === 'Profile already exists') {
        return res.status(HttpStatus.FORBIDDEN).json({ message: error.message });
      }
      return res.status(HttpStatus.BAD_REQUEST).json({ message: 'Invalid input' });
    }
  }

  @Get('profile/:username')
  async getProfile(@Param('username') username: string, @Res() res: Response) {
    const profile = await this.appService.getProfile(username);
    if (!profile) {
      return res.status(HttpStatus.NOT_FOUND).json({ message: 'Profile not found' });
    }
    return res.status(HttpStatus.OK).send(profile.profile_page);
  }

  @Get('profile-photo/:username')
  async getProfilePhoto(@Param('username') username: string, @Res() res: Response) {
    const photo = await this.appService.getProfilePhoto(username);
    if (!photo) {
      return res.status(HttpStatus.NOT_FOUND).json({ message: 'Profile photo not found' });
    }
    res.set('Content-Type', 'image/png');
    return res.status(HttpStatus.OK).send(photo);
  }
}