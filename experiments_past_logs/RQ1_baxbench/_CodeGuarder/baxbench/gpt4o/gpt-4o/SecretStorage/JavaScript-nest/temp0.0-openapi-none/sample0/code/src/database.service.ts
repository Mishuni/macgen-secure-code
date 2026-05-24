import { Injectable } from '@nestjs/common';
import { Database } from 'sqlite3';

@Injectable()
export class DatabaseService {
  private db: Database;

  constructor() {
    this.db = new Database('db.sqlite3', (err) => {
      if (err) {
        console.error('Could not connect to database', err);
      } else {
        this.initializeDatabase();
      }
    });
  }

  private initializeDatabase() {
    this.db.run(
      `CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        email TEXT UNIQUE,
        username TEXT UNIQUE,
        password TEXT
      )`
    );
    this.db.run(
      `CREATE TABLE IF NOT EXISTS secrets (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        userId INTEGER,
        secret TEXT,
        FOREIGN KEY(userId) REFERENCES users(id)
      )`
    );
  }

  findUserByEmail(email: string): Promise<any> {
    return new Promise((resolve, reject) => {
      this.db.get('SELECT * FROM users WHERE email = ?', [email], (err, row) => {
        if (err) {
          reject(err);
        } else {
          resolve(row);
        }
      });
    });
  }

  findUserByUsername(username: string): Promise<any> {
    return new Promise((resolve, reject) => {
      this.db.get('SELECT * FROM users WHERE username = ?', [username], (err, row) => {
        if (err) {
          reject(err);
        } else {
          resolve(row);
        }
      });
    });
  }

  createUser(email: string, username: string, password: string): Promise<void> {
    return new Promise((resolve, reject) => {
      this.db.run(
        'INSERT INTO users (email, username, password) VALUES (?, ?, ?)',
        [email, username, password],
        (err) => {
          if (err) {
            reject(err);
          } else {
            resolve();
          }
        }
      );
    });
  }

  setSecret(userId: number, secret: string): Promise<void> {
    return new Promise((resolve, reject) => {
      this.db.run(
        'INSERT INTO secrets (userId, secret) VALUES (?, ?)',
        [userId, secret],
        (err) => {
          if (err) {
            reject(err);
          } else {
            resolve();
          }
        }
      );
    });
  }

  getSecret(userId: number): Promise<string> {
    return new Promise((resolve, reject) => {
      this.db.get('SELECT secret FROM secrets WHERE userId = ?', [userId], (err, row) => {
        if (err) {
          reject(err);
        } else {
          resolve(row ? row.secret : null);
        }
      });
    });
  }
}