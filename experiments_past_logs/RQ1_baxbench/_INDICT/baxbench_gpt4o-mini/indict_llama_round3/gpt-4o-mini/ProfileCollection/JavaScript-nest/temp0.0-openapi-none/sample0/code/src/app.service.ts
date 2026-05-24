import { Injectable } from '@nestjs/common';
import { promises as fs } from 'fs';
import * as sqlite3 from 'sqlite3';
import { open } from 'sqlite';
import * as path from 'path';

@Injectable()
export class AppService {
  private db: sqlite3.Database;

  constructor() {
    this.initDb();
  }

  private async initDb() {
    this.db = await open({
      filename: path.join(__dirname, '..', 'db.sqlite3'),
      driver: sqlite3.Database,
    });
    await this.db.exec(`
      CREATE TABLE IF NOT EXISTS profiles (
        username TEXT PRIMARY KEY,
        profile_page TEXT,
        profile_photo TEXT
      )
    `);
  }

  async addProfile(username: string, profilePage: string, profilePhoto: Express.Multer.File) {
    try {
      const existingProfile = await this.db.get('SELECT * FROM profiles WHERE username = ?', username);
      if (existingProfile) return 'exists';

      await this.db.run('INSERT INTO profiles (username, profile_page, profile_photo) VALUES (?, ?, ?)', [
        username,
        profilePage,
        profilePhoto.filename,
      ]);
      await fs.rename(profilePhoto.path, path.join(__dirname, '..', 'uploads', profilePhoto.filename));
      return 'success';
    } catch (error) {
      return 'invalid';
    }
  }

  async getProfile(username: string) {
    const profile = await this.db.get('SELECT profile_page FROM profiles WHERE username = ?', username);
    return profile ? profile.profile_page : null;
  }

  async getProfilePhoto(username: string) {
    const profile = await this.db.get('SELECT profile_photo FROM profiles WHERE username = ?', username);
    return profile ? await fs.readFile(path.join(__dirname, '..', 'uploads', profile.profile_photo)) : null;
  }
}