import { Injectable } from '@nestjs/common';
import { Database } from 'sqlite3';
import { join } from 'path';
import { existsSync, mkdirSync } from 'fs';

@Injectable()
export class AppService {
  private db: Database;

  constructor() {
    this.db = new Database('db.sqlite3', (err) => {
      if (err) {
        console.error('Error opening database', err.message);
      } else {
        this.db.run(`CREATE TABLE IF NOT EXISTS profiles (
          username TEXT PRIMARY KEY,
          profile_page TEXT NOT NULL,
          profile_photo TEXT NOT NULL
        )`);
      }
    });

    if (!existsSync('./uploads')) {
      mkdirSync('./uploads');
    }
  }

  async addProfile(username: string, profilePage: string, profilePhoto: string): Promise<void> {
    return new Promise((resolve, reject) => {
      this.db.run(
        `INSERT INTO profiles (username, profile_page, profile_photo) VALUES (?, ?, ?)`,
        [username, profilePage, profilePhoto],
        function (err) {
          if (err) {
            if (err.message.includes('UNIQUE constraint failed')) {
              return reject(new Error('Profile already exists'));
            }
            return reject(err);
          }
          resolve();
        }
      );
    });
  }

  async getProfile(username: string): Promise<string> {
    return new Promise((resolve, reject) => {
      this.db.get(
        `SELECT profile_page FROM profiles WHERE username = ?`,
        [username],
        (err, row) => {
          if (err) {
            return reject(err);
          }
          if (!row) {
            return reject(new Error('Profile not found'));
          }
          resolve(row.profile_page);
        }
      );
    });
  }

  async getProfilePhoto(username: string): Promise<string> {
    return new Promise((resolve, reject) => {
      this.db.get(
        `SELECT profile_photo FROM profiles WHERE username = ?`,
        [username],
        (err, row) => {
          if (err) {
            return reject(err);
          }
          if (!row) {
            return reject(new Error('Profile photo not found'));
          }
          resolve(row.profile_photo);
        }
      );
    });
  }
}