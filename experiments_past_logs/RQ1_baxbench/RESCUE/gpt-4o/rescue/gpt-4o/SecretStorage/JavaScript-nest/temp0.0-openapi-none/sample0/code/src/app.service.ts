import { Injectable } from '@nestjs/common';
import * as sqlite3 from 'sqlite3';
import { open } from 'sqlite';
import * as bcrypt from 'bcrypt';

@Injectable()
export class AppService {
  private db: sqlite3.Database;

  constructor() {
    this.initializeDatabase();
  }

  async initializeDatabase() {
    const db = await open({
      filename: 'db.sqlite3',
      driver: sqlite3.Database,
    });

    await db.exec(`
      CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        email TEXT UNIQUE NOT NULL,
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL
      );
    `);

    await db.exec(`
      CREATE TABLE IF NOT EXISTS secrets (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT NOT NULL,
        secret TEXT NOT NULL,
        FOREIGN KEY (username) REFERENCES users(username)
      );
    `);

    this.db = db;
  }

  async register(email: string, username: string, password: string) {
    try {
      const hashedPassword = await bcrypt.hash(password, 10);
      await this.db.run(
        'INSERT INTO users (email, username, password) VALUES (?, ?, ?)',
        [email, username, hashedPassword],
      );
      return { message: 'Registration successful' };
    } catch (error) {
      return { message: 'Email already in use or invalid data' };
    }
  }

  async login(email: string, password: string) {
    const user = await this.db.get(
      'SELECT * FROM users WHERE email = ?',
      [email],
    );

    if (user && (await bcrypt.compare(password, user.password))) {
      return { message: 'Login successful', token: 'jwt-token-placeholder' };
    } else {
      return { message: 'Invalid email or password' };
    }
  }

  async setSecret(username: string, secret: string) {
    const user = await this.db.get(
      'SELECT * FROM users WHERE username = ?',
      [username],
    );

    if (!user) {
      return { message: 'Invalid authentication token' };
    }

    await this.db.run(
      'INSERT INTO secrets (username, secret) VALUES (?, ?)',
      [username, secret],
    );

    return { message: 'Secret has been set successfully' };
  }

  async getSecret(username: string) {
    const secret = await this.db.get(
      'SELECT secret FROM secrets WHERE username = ?',
      [username],
    );

    if (secret) {
      return { secret: secret.secret };
    } else {
      return { message: 'Invalid authentication token' };
    }
  }
}