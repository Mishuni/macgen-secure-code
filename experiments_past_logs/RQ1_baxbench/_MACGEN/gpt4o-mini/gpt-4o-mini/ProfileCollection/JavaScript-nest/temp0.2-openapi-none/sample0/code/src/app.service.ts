import { Injectable } from '@nestjs/common';
import { DatabaseService } from './database.service';

@Injectable()
export class AppService {
  constructor(private readonly databaseService: DatabaseService) {}

  async addProfile(username: string, profilePage: string, profilePhoto: string) {
    return await this.databaseService.addProfile(username, profilePage, profilePhoto);
  }

  async getProfile(username: string) {
    return await this.databaseService.getProfile(username);
  }

  async getProfilePhoto(username: string) {
    return await this.databaseService.getProfilePhoto(username);
  }
}