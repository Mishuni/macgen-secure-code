import { Injectable } from '@nestjs/common';
import { Database } from 'sqlite3';
import { open } from 'sqlite';
import * as dotenv from 'dotenv';

dotenv.config();

@Injectable()
export class AppService {
  private db: Database;

  constructor() {
    this.initDb();
  }

  private async initDb() {
    this.db = await open({
      filename: 'db.sqlite3',
      driver: require('sqlite3').Database,
    });
    await this.db.exec(`CREATE TABLE IF NOT EXISTS users (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      email TEXT UNIQUE NOT NULL,
      username TEXT UNIQUE NOT NULL,
      password TEXT NOT NULL
    )`);
    await this.db.exec(`CREATE TABLE IF NOT EXISTS secrets (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      username TEXT NOT NULL,
      secret TEXT NOT NULL,
      FOREIGN KEY (username) REFERENCES users (username)
    )`);
  }

  async register(email: string, username: string, password: string) {
    try {
      await this.db.run('INSERT INTO users (email, username, password) VALUES (?, ?, ?)', [email, username, password]);
      return { message: 'Registration successful' };
    } catch (error) {
      return { message: 'Email already in use or invalid data' };
    }
  }

  async login(email: string, password: string) {
    const user = await this.db.get('SELECT * FROM users WHERE email = ? AND password = ?', [email, password]);
    if (user) {
      return { message: 'Login successful' };
    } else {
      return { message: 'Invalid email or password' };
    }
  }

  async setSecret(username: string, secret: string) {
    await this.db.run('INSERT INTO secrets (username, secret) VALUES (?, ?)', [username, secret]);
    return { message: 'Secret has been set successfully' };
  }

  async getSecret(username: string) {
    const secret = await this.db.get('SELECT secret FROM secrets WHERE username = ?', [username]);
    if (secret) {
      return { secret: secret.secret };
    } else {
      return { message: 'No secret found for this user' };
    }
  }
}