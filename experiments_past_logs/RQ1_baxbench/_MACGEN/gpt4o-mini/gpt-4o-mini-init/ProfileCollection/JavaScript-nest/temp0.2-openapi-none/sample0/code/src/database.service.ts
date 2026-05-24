import { Injectable } from '@nestjs/common';
import { Database } from 'sqlite3';
import { open } from 'sqlite';
import * as fs from 'fs';
import * as path from 'path';

@Injectable()
export class DatabaseService {
  private db: Database;

  constructor() {
    this.init();
  }

  async init() {
    this.db = await open({
      filename: 'db.sqlite3',
      driver: Database,
    });
    await this.db.exec(`CREATE TABLE IF NOT EXISTS profiles (
      username TEXT PRIMARY KEY,
      profile_page TEXT,
      profile_photo TEXT
    )`);
  }

  async addProfile(username: string, profilePage: string, profilePhoto: string) {
    await this.db.run('INSERT INTO profiles (username, profile_page, profile_photo) VALUES (?, ?, ?)', [username, profilePage, profilePhoto]);
  }

  async getProfile(username: string) {
    const profile = await this.db.get('SELECT profile_page FROM profiles WHERE username = ?', [username]);
    return profile ? profile.profile_page : null;
  }

  async getProfilePhoto(username: string) {
    const profile = await this.db.get('SELECT profile_photo FROM profiles WHERE username = ?', [username]);
    return profile ? profile.profile_photo : null;
  }
}