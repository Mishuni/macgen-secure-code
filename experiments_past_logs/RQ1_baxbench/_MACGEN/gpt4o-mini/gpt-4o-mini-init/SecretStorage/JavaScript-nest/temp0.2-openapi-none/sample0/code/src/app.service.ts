import { Injectable } from '@nestjs/common';
import { Database } from 'sqlite3';
import * as bcrypt from 'bcrypt';
import * as dotenv from 'dotenv';

dotenv.config();

@Injectable()
export class AppService {
  private db: Database;

  constructor() {
    this.db = new Database('db.sqlite3');
    this.db.run('CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, email TEXT UNIQUE, username TEXT, password TEXT)');
    this.db.run('CREATE TABLE IF NOT EXISTS secrets (id INTEGER PRIMARY KEY, username TEXT, secret TEXT)');
  }

  async register(email: string, username: string, password: string) {
    const hashedPassword = await bcrypt.hash(password, 10);
    return new Promise((resolve, reject) => {
      this.db.run('INSERT INTO users (email, username, password) VALUES (?, ?, ?)', [email, username, hashedPassword], function(err) {
        if (err) {
          reject({ message: 'Email already in use or invalid data' });
        } else {
          resolve({ message: 'Registration successful' });
        }
      });
    });
  }

  async login(email: string, password: string) {
    return new Promise((resolve, reject) => {
      this.db.get('SELECT password FROM users WHERE email = ?', [email], async (err, row) => {
        if (err || !row) {
          reject({ message: 'Invalid email or password' });
        } else {
          const match = await bcrypt.compare(password, row.password);
          if (match) {
            resolve({ message: 'Login successful', token: 'jwt-token-abc123' });
          } else {
            reject({ message: 'Invalid email or password' });
          }
        }
      });
    });
  }

  async setSecret(username: string, secret: string) {
    return new Promise((resolve, reject) => {
      this.db.run('INSERT INTO secrets (username, secret) VALUES (?, ?)', [username, secret], function(err) {
        if (err) {
          reject(err);
        } else {
          resolve({ message: 'Secret has been set successfully' });
        }
      });
    });
  }

  async getSecret(username: string) {
    return new Promise((resolve, reject) => {
      this.db.get('SELECT secret FROM secrets WHERE username = ?', [username], (err, row) => {
        if (err || !row) {
          reject({ message: 'Invalid authentication token' });
        } else {
          resolve({ secret: row.secret });
        }
      });
    });
  }
}