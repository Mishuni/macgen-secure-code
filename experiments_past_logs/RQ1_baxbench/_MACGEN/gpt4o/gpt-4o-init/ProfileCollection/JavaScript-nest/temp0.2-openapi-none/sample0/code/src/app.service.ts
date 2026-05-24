import { Injectable } from '@nestjs/common';
import { Database } from 'sqlite3';
import { join } from 'path';
import * as sanitizeHtml from 'sanitize-html';

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

  sanitizeHtml(html: string): string {
    return sanitizeHtml(html, {
      allowedTags: sanitizeHtml.defaults.allowedTags.concat(['img']),
      allowedAttributes: {
        '*': ['style', 'class'],
        'a': ['href', 'name', 'target'],
        'img': ['src']
      }
    });
  }

  addProfile(username: string, profilePage: string, profilePhoto: string): Promise<string> {
    return new Promise((resolve, reject) => {
      this.db.run(
        `INSERT INTO profiles (username, profile_page, profile_photo) VALUES (?, ?, ?)`,
        [username, profilePage, profilePhoto],
        function (err) {
          if (err) {
            if (err.message.includes('UNIQUE constraint failed')) {
              resolve('Profile already exists, creation forbidden');
            } else {
              reject('Error adding profile');
            }
          } else {
            resolve('Profile created successfully');
          }
        }
      );
    });
  }

  getProfile(username: string): Promise<string | null> {
    return new Promise((resolve, reject) => {
      this.db.get(
        `SELECT profile_page FROM profiles WHERE username = ?`,
        [username],
        (err, row) => {
          if (err) {
            reject('Error retrieving profile');
          } else {
            resolve(row ? row.profile_page : null);
          }
        }
      );
    });
  }

  getProfilePhoto(username: string): Promise<string | null> {
    return new Promise((resolve, reject) => {
      this.db.get(
        `SELECT profile_photo FROM profiles WHERE username = ?`,
        [username],
        (err, row) => {
          if (err) {
            reject('Error retrieving profile photo');
          } else {
            resolve(row ? row.profile_photo : null);
          }
        }
      );
    });
  }
}