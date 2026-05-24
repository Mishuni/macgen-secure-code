import { Injectable } from '@nestjs/common';
import { ProfileDto } from './profile.dto';
import { DatabaseService } from './database.service';

@Injectable()
export class AppService {
  constructor(private readonly databaseService: DatabaseService) {}

  async addProfile(profileDto: ProfileDto) {
    const existingProfile = await this.databaseService.getProfileByUsername(profileDto.username);
    if (existingProfile) {
      throw new Error('Profile already exists');
    }
    return this.databaseService.createProfile(profileDto);
  }

  async getProfile(username: string) {
    return this.databaseService.getProfileByUsername(username);
  }

  async getProfilePhoto(username: string) {
    const profile = await this.databaseService.getProfileByUsername(username);
    return profile ? profile.profile_photo : null;
  }
}