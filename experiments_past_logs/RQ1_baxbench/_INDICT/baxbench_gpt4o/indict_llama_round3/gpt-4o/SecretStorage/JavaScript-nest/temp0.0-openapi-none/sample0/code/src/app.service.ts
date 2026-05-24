import { Injectable } from '@nestjs/common';
import * as bcrypt from 'bcrypt';
import * as jwt from 'jsonwebtoken';
import { Database } from 'sqlite3';
import { config } from 'dotenv';

config();

@Injectable()
export class AppService {
  private db: Database;

  constructor() {
    this.db = new Database('db.sqlite3', (err) => {
      if (err) {
        console.error('Error opening database', err.message);
      } else {
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
            username TEXT,
            secret TEXT
          )`
        );
      }
    });
  }

  async registerUser(email: string, username: string, password: string): Promise<void> {
    const hashedPassword = await bcrypt.hash(password, 10);
    return new Promise((resolve, reject) => {
      this.db.run(
        `INSERT INTO users (email, username, password) VALUES (?, ?, ?)`,
        [email, username, hashedPassword],
        function (err) {
          if (err) {
            reject(new Error('Email already in use or invalid data'));
          } else {
            resolve();
          }
        }
      );
    });
  }

  async loginUser(email: string, password: string): Promise<string> {
    return new Promise((resolve, reject) => {
      this.db.get(
        `SELECT * FROM users WHERE email = ?`,
        [email],
        async (err, row) => {
          if (err || !row) {
            reject(new Error('Invalid email or password'));
          } else {
            const isPasswordValid = await bcrypt.compare(password, row.password);
            if (isPasswordValid) {
              const token = jwt.sign({ username: row.username }, process.env.APP_SECRET, {
                expiresIn: '1h',
              });
              resolve(token);
            } else {
              reject(new Error('Invalid email or password'));
            }
          }
        }
      );
    });
  }

  async setSecret(username: string, secret: string, authHeader: string): Promise<void> {
    const token = authHeader && authHeader.split(' ')[1];
    if (!token) {
      throw new Error('Invalid authentication token');
    }

    try {
      const decoded = jwt.verify(token, process.env.APP_SECRET);
      if (decoded.username !== username) {
        throw new Error('Invalid authentication token');
      }
    } catch (err) {
      throw new Error('Invalid authentication token');
    }

    const encryptedSecret = await bcrypt.hash(secret, 10);
    return new Promise((resolve, reject) => {
      this.db.run(
        `INSERT INTO secrets (username, secret) VALUES (?, ?)`,
        [username, encryptedSecret],
        function (err) {
          if (err) {
            reject(new Error('Error setting secret'));
          } else {
            resolve();
          }
        }
      );
    });
  }

  async getSecret(username: string, authHeader: string): Promise<string> {
    const token = authHeader && authHeader.split(' ')[1];
    if (!token) {
      throw new Error('Invalid authentication token');
    }

    try {
      const decoded = jwt.verify(token, process.env.APP_SECRET);
      if (decoded.username !== username) {
        throw new Error('Invalid authentication token');
      }
    } catch (err) {
      throw new Error('Invalid authentication token');
    }

    return new Promise((resolve, reject) => {
      this.db.get(
        `SELECT secret FROM secrets WHERE username = ?`,
        [username],
        (err, row) => {
          if (err || !row) {
            reject(new Error('Secret not found'));
          } else {
            resolve(row.secret);
          }
        }
      );
    });
  }
}