import { Injectable } from '@nestjs/common';
import { Database } from 'sqlite3';
import { join } from 'path';

@Injectable()
export class AppService {
  private db: Database;

  constructor() {
    this.db = new Database(join(__dirname, '..', 'db.sqlite3'), (err) => {
      if (err) {
        console.error('Error opening database', err.message);
      } else {
        this.db.run(`CREATE TABLE IF NOT EXISTS profiles (
          username TEXT PRIMARY KEY,
          profile_page TEXT,
          profile_photo TEXT
        )`);
      }
    });
  }

  addProfile(username: string, profilePage: string, profilePhoto: string): Promise<void> {
    return new Promise((resolve, reject) => {
      this.db.run(
        `INSERT INTO profiles (username, profile_page, profile_photo) VALUES (?, ?, ?)`,
        [username, profilePage, profilePhoto],
        function (err) {
          if (err) {
            if (err.message.includes('UNIQUE constraint failed')) {
              reject(new Error('Profile already exists'));
            } else {
              reject(err);
            }
          } else {
            resolve();
          }
        }
      );
    });
  }

  getProfile(username: string): Promise<string> {
    return new Promise((resolve, reject) => {
      this.db.get(
        `SELECT profile_page FROM profiles WHERE username = ?`,
        [username],
        (err, row) => {
          if (err) {
            reject(err);
          } else if (row) {
            resolve(row.profile_page);
          } else {
            reject(new Error('Profile not found'));
          }
        }
      );
    });
  }

  getProfilePhoto(username: string): Promise<string> {
    return new Promise((resolve, reject) => {
      this.db.get(
        `SELECT profile_photo FROM profiles WHERE username = ?`,
        [username],
        (err, row) => {
          if (err) {
            reject(err);
          } else if (row) {
            resolve(row.profile_photo);
          } else {
            reject(new Error('Profile photo not found'));
          }
        }
      );
    });
  }
}