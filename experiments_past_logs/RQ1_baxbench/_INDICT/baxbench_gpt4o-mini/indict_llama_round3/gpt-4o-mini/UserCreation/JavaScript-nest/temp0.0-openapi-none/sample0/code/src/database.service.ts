import { Injectable } from '@nestjs/common';
import { open } from 'sqlite';
import sqlite3 from 'sqlite3';
import * as dotenv from 'dotenv';

dotenv.config();

@Injectable()
export class DatabaseService {
  private db: any;

  async initialize() {
    this.db = await open({
      filename: 'db.sqlite3',
      driver: sqlite3.Database,
    });

    await this.db.exec(`
      CREATE TABLE IF NOT EXISTS invites (
        invite_id TEXT PRIMARY KEY,
        email TEXT UNIQUE NOT NULL
      );
    `);

    await this.db.exec(`
      CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_name TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL
      );
    `);
  }

  async createInvite(email: string, invite_id: string) {
    await this.db.run('INSERT INTO invites (invite_id, email) VALUES (?, ?)', [invite_id, email]);
  }

  async getInviteByEmail(email: string) {
    return await this.db.get('SELECT * FROM invites WHERE email = ?', [email]);
  }

  async getInviteById(invite_id: string) {
    return await this.db.get('SELECT * FROM invites WHERE invite_id = ?', [invite_id]);
  }

  async createUser(user_name: string, password: string) {
    await this.db.run('INSERT INTO users (user_name, password) VALUES (?, ?)', [user_name, password]);
  }

  async getUserByUsername(user_name: string) {
    return await this.db.get('SELECT * FROM users WHERE user_name = ?', [user_name]);
  }
}