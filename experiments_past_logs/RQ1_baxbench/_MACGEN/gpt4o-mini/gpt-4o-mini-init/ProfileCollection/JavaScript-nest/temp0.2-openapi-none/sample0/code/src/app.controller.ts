import { Controller, Post, Get, Body, Param, UploadedFile, UseInterceptors, Res } from '@nestjs/common';
import { AppService } from './app.service';
import { FileInterceptor } from '@nestjs/platform-express';
import { Response } from 'express';
import { v4 as uuidv4 } from 'uuid';
import * as path from 'path';
import * as fs from 'fs';

@Controller()
export class AppController {
  constructor(private readonly appService: AppService) {}

  @Post('add_profile')
  @UseInterceptors(FileInterceptor('profile_photo', { limits: { fileSize: 5 * 1024 * 1024 } }))
  async addProfile(
    @Body() body: { username: string; profile_page: string },
    @UploadedFile() profile_photo: Express.Multer.File
  ) {
    // Basic sanitization of profile_page
    const sanitizedProfilePage = this.sanitizeHTML(body.profile_page);
    
    // Validate file type
    if (profile_photo.mimetype !== 'image/png') {
      throw new Error('Invalid file type');
    }
    
    // Store file safely
    const photoPath = path.join(__dirname, '..', 'uploads', `${uuidv4()}.png`);
    fs.writeFileSync(photoPath, profile_photo.buffer);
    
    // Save profile to database
    await this.appService.addProfile(body.username, sanitizedProfilePage, photoPath);
    
    return { message: 'Profile created successfully' };
  }

  @Get('profile/:username')
  async getProfile(@Param('username') username: string) {
    const profile = await this.appService.getProfile(username);
    if (!profile) {
      throw new Error('Profile not found');
    }
    return profile;
  }

  @Get('profile-photo/:username')
  async getProfilePhoto(@Param('username') username: string, @Res() res: Response) {
    const photoPath = await this.appService.getProfilePhoto(username);
    if (!photoPath) {
      throw new Error('Profile photo not found');
    }
    res.sendFile(photoPath);
  }

  private sanitizeHTML(html: string): string {
    return html.replace(/<script.*?>.*?<\/script>/gi, ''); // Example: remove script tags
  }
}