import { Injectable } from '@nestjs/common';
import { open } from 'sqlite';
import sqlite3 from 'sqlite3';

@Injectable()
export class DatabaseService {
  private db;

  constructor() {
    this.init();
  }

  async init() {
    this.db = await open({
      filename: 'db.sqlite3',
      driver: sqlite3.Database,
    });
    await this.db.exec(`CREATE TABLE IF NOT EXISTS users (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      email TEXT UNIQUE,
      password TEXT,
      name TEXT
    )`);
  }

  async createUser(email: string, password: string, name: string) {
    try {
      await this.db.run('INSERT INTO users (email, password, name) VALUES (?, ?, ?)', [email, password, name]);
    } catch (error) {
      throw new Error('Email already in use or invalid data');
    }
  }

  async findUserByEmail(email: string) {
    return await this.db.get('SELECT * FROM users WHERE email = ?', [email]);
  }
}