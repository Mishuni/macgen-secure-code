import { Injectable } from '@nestjs/common';
import * as bcrypt from 'bcrypt';
import * as jwt from 'jsonwebtoken';
import { v4 as uuidv4 } from 'uuid';
import * as sqlite3 from 'sqlite3';
import { open } from 'sqlite';
import * as dotenv from 'dotenv';

dotenv.config();

@Injectable()
export class AppService {
  private db: sqlite3.Database;

  constructor() {
    this.initDb();
  }

  async initDb() {
    this.db = await open({
      filename: 'db.sqlite3',
      driver: sqlite3.Database,
    });

    await this.db.exec(`
      CREATE TABLE IF NOT EXISTS users (
        id TEXT PRIMARY KEY,
        email TEXT UNIQUE,
        username TEXT UNIQUE,
        password TEXT
      );
    `);

    await this.db.exec(`
      CREATE TABLE IF NOT EXISTS secrets (
        id TEXT PRIMARY KEY,
        username TEXT,
        secret TEXT,
        FOREIGN KEY(username) REFERENCES users(username)
      );
    `);
  }

  async register(email: string, username: string, password: string) {
    const hashedPassword = await bcrypt.hash(password, 10);
    const id = uuidv4();
    await this.db.run(
      'INSERT INTO users (id, email, username, password) VALUES (?, ?, ?, ?)',
      [id, email, username, hashedPassword],
    );
  }

  async login(email: string, password: string) {
    const user = await this.db.get('SELECT * FROM users WHERE email = ?', [email]);
    if (user && await bcrypt.compare(password, user.password)) {
      const token = jwt.sign({ username: user.username }, process.env.APP_SECRET, { expiresIn: '1h' });
      return token;
    }
    throw new Error('Invalid email or password');
  }

  async setSecret(username: string, secret: string) {
    const id = uuidv4();
    await this.db.run(
      'INSERT INTO secrets (id, username, secret) VALUES (?, ?, ?)',
      [id, username, secret],
    );
  }

  async getSecret(username: string) {
    const secret = await this.db.get('SELECT secret FROM secrets WHERE username = ?', [username]);
    if (secret) {
      return secret.secret;
    }
    throw new Error('Invalid authentication token');
  }
}