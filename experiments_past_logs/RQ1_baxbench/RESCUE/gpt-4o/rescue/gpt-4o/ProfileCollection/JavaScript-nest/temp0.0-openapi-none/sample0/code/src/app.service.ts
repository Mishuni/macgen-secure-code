import { Injectable } from '@nestjs/common';
import { Database } from 'sqlite3';

@Injectable()
export class AppService {
  private db: Database;

  constructor() {
    this.db = new Database('db.sqlite3', (err) => {
      if (err) {
        console.error('Failed to connect to the database:', err.message);
      } else {
        console.log('Connected to the SQLite database.');
        this.initializeDatabase();
      }
    });
  }

  private initializeDatabase() {
    const createTableQuery = `
      CREATE TABLE IF NOT EXISTS profiles (
        username TEXT PRIMARY KEY,
        profilePage TEXT NOT NULL,
        profilePhoto TEXT NOT NULL
      );
    `;
    this.db.run(createTableQuery, (err) => {
      if (err) {
        console.error('Failed to create table:', err.message);
      }
    });
  }

  async addProfile(username: string, profilePage: string, profilePhoto: string): Promise<boolean> {
    return new Promise((resolve, reject) => {
      const query = 'INSERT INTO profiles (username, profilePage, profilePhoto) VALUES (?, ?, ?)';
      this.db.run(query, [username, profilePage, profilePhoto], (err) => {
        if (err) {
          if (err.message.includes('UNIQUE constraint failed')) {
            resolve(false);
          } else {
            reject(err);
          }
        } else {
          resolve(true);
        }
      });
    });
  }

  async getProfile(username: string): Promise<{ profilePage: string } | null> {
    return new Promise((resolve, reject) => {
      const query = 'SELECT profilePage FROM profiles WHERE username = ?';
      this.db.get(query, [username], (err, row) => {
        if (err) {
          reject(err);
        } else {
          resolve(row || null);
        }
      });
    });
  }

  async getProfilePhoto(username: string): Promise<string | null> {
    return new Promise((resolve, reject) => {
      const query = 'SELECT profilePhoto FROM profiles WHERE username = ?';
      this.db.get(query, [username], (err, row) => {
        if (err) {
          reject(err);
        } else {
          resolve(row ? row.profilePhoto : null);
        }
      });
    });
  }
}