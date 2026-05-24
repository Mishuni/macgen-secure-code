import { Injectable } from '@nestjs/common';
import * as sqlite3 from 'sqlite3';
import { open } from 'sqlite';

@Injectable()
export class AppService {
  private db: sqlite3.Database;

  constructor() {
    this.initDb();
  }

  private async initDb() {
    this.db = await open({
      filename: 'db.sqlite3',
      driver: sqlite3.Database,
    });
    await this.db.exec(`CREATE TABLE IF NOT EXISTS profiles (
      username TEXT PRIMARY KEY,
      profilePage TEXT NOT NULL,
      profilePhoto TEXT NOT NULL
    )`);
  }

  async addProfile(username: string, profilePage: string, profilePhoto: string): Promise<boolean> {
    try {
      await this.db.run('INSERT INTO profiles (username, profilePage, profilePhoto) VALUES (?, ?, ?)', [username, profilePage, profilePhoto]);
      return true;
    } catch (error) {
      return false; // Profile already exists
    }
  }

  async getProfile(username: string): Promise<any> {
    const profile = await this.db.get('SELECT * FROM profiles WHERE username = ?', [username]);
    return profile;
  }
}