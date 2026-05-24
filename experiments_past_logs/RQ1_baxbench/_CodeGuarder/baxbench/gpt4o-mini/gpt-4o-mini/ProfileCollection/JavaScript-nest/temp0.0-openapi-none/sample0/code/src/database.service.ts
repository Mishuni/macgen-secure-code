import { Injectable } from '@nestjs/common';
import { ProfileDto } from './profile.dto';
import { Database } from 'sqlite3';

@Injectable()
export class DatabaseService {
  private db: Database;

  initialize() {
    this.db = new Database('db.sqlite3', (err) => {
      if (err) {
        console.error('Error opening database ' + err.message);
      } else {
        this.db.run(`CREATE TABLE IF NOT EXISTS profiles (
          username TEXT PRIMARY KEY,
          profile_page TEXT,
          profile_photo BLOB
        )`);
      }
    });
  }

  createProfile(profileDto: ProfileDto) {
    return new Promise((resolve, reject) => {
      const stmt = this.db.prepare('INSERT INTO profiles (username, profile_page, profile_photo) VALUES (?, ?, ?)');
      stmt.run(profileDto.username, profileDto.profile_page, profileDto.profile_photo, function (err) {
        if (err) {
          reject(err);
        } else {
          resolve(profileDto);
        }
      });
      stmt.finalize();
    });
  }

  getProfileByUsername(username: string) {
    return new Promise((resolve, reject) => {
      this.db.get('SELECT * FROM profiles WHERE username = ?', [username], (err, row) => {
        if (err) {
          reject(err);
        } else {
          resolve(row);
        }
      });
    });
  }
}