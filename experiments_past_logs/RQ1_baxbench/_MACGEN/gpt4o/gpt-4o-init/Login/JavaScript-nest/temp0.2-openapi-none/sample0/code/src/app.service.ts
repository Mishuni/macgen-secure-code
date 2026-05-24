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
    this.initializeDatabase();
  }

  async initializeDatabase() {
    this.db = await open({
      filename: 'db.sqlite3',
      driver: sqlite3.Database,
    });

    await this.db.exec(`
      CREATE TABLE IF NOT EXISTS users (
        id TEXT PRIMARY KEY,
        email TEXT UNIQUE,
        password TEXT,
        name TEXT
      )
    `);
  }

  async register(email: string, password: string, name: string) {
    const hashedPassword = await bcrypt.hash(password, 10);
    const id = uuidv4();

    try {
      await this.db.run(
        'INSERT INTO users (id, email, password, name) VALUES (?, ?, ?, ?)',
        [id, email, hashedPassword, name],
      );
      return { message: 'Registration successful' };
    } catch (error) {
      throw new Error('Email already in use or invalid data');
    }
  }

  async login(email: string, password: string) {
    const user = await this.db.get('SELECT * FROM users WHERE email = ?', [email]);

    if (user && (await bcrypt.compare(password, user.password))) {
      const token = jwt.sign({ userId: user.id }, process.env.APP_SECRET, { expiresIn: '1h' });
      return { token, message: 'Login successful' };
    } else {
      throw new Error('Invalid email or password');
    }
  }
}