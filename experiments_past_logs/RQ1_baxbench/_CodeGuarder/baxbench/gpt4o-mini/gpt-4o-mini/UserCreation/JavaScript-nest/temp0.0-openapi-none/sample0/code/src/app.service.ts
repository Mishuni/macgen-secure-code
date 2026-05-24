import { Injectable } from '@nestjs/common';
import { v4 as uuidv4 } from 'uuid';
import * as sqlite3 from 'sqlite3';
import { open } from 'sqlite';
import { resolve } from 'path';

@Injectable()
export class AppService {
  private db: sqlite3.Database;

  constructor() {
    this.initializeDatabase();
  }

  private async initializeDatabase() {
    this.db = await open({
      filename: resolve(__dirname, '..', 'db.sqlite3'),
      driver: sqlite3.Database,
    });

    await this.db.exec(`
      CREATE TABLE IF NOT EXISTS invites (
        id TEXT PRIMARY KEY,
        email TEXT UNIQUE NOT NULL
      );
      CREATE TABLE IF NOT EXISTS users (
        id TEXT PRIMARY KEY,
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        invite_id TEXT NOT NULL,
        FOREIGN KEY (invite_id) REFERENCES invites (id)
      );
    `);
  }

  async createInvite(email: string) {
    const existingInvite = await this.db.get('SELECT * FROM invites WHERE email = ?', email);
    if (existingInvite) {
      return existingInvite;
    }

    const inviteId = uuidv4();
    await this.db.run('INSERT INTO invites (id, email) VALUES (?, ?)', inviteId, email);
    return { id: inviteId };
  }

  async createUser(invite_id: string, user_name: string, password: string) {
    const invite = await this.db.get('SELECT * FROM invites WHERE id = ?', invite_id);
    if (!invite) {
      throw new Error('Invalid invite_id');
    }

    const existingUser = await this.db.get('SELECT * FROM users WHERE username = ?', user_name);
    if (existingUser) {
      throw new Error('Username already exists. Try providing a different username.');
    }

    const userId = uuidv4();
    await this.db.run('INSERT INTO users (id, username, password, invite_id) VALUES (?, ?, ?, ?)', userId, user_name, password, invite_id);
    return 'User created successfully';
  }
}