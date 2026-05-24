import { Injectable } from '@nestjs/common';
import { Database } from 'sqlite3';

@Injectable()
export class DatabaseService {
  private db: Database;

  constructor() {
    this.db = new Database('db.sqlite3', (err) => {
      if (err) {
        console.error('Error opening database', err.message);
      } else {
        this.db.run(
          `CREATE TABLE IF NOT EXISTS invites (
            email TEXT PRIMARY KEY,
            invite_id TEXT NOT NULL
          )`
        );
        this.db.run(
          `CREATE TABLE IF NOT EXISTS users (
            user_name TEXT PRIMARY KEY,
            password TEXT NOT NULL
          )`
        );
      }
    });
  }

  getInviteByEmail(email: string): Promise<any> {
    return new Promise((resolve, reject) => {
      this.db.get('SELECT * FROM invites WHERE email = ?', [email], (err, row) => {
        if (err) {
          reject(err);
        } else {
          resolve(row);
        }
      });
    });
  }

  createInvite(email: string, invite_id: string): Promise<void> {
    return new Promise((resolve, reject) => {
      this.db.run('INSERT INTO invites (email, invite_id) VALUES (?, ?)', [email, invite_id], (err) => {
        if (err) {
          reject(err);
        } else {
          resolve();
        }
      });
    });
  }

  getInviteById(invite_id: string): Promise<any> {
    return new Promise((resolve, reject) => {
      this.db.get('SELECT * FROM invites WHERE invite_id = ?', [invite_id], (err, row) => {
        if (err) {
          reject(err);
        } else {
          resolve(row);
        }
      });
    });
  }

  getUserByUsername(user_name: string): Promise<any> {
    return new Promise((resolve, reject) => {
      this.db.get('SELECT * FROM users WHERE user_name = ?', [user_name], (err, row) => {
        if (err) {
          reject(err);
        } else {
          resolve(row);
        }
      });
    });
  }

  createUser(user_name: string, password: string): Promise<void> {
    return new Promise((resolve, reject) => {
      this.db.run('INSERT INTO users (user_name, password) VALUES (?, ?)', [user_name, password], (err) => {
        if (err) {
          reject(err);
        } else {
          resolve();
        }
      });
    });
  }
}