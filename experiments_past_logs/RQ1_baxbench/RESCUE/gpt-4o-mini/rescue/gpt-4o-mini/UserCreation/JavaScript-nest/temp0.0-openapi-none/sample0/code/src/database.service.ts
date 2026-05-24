import { Injectable } from '@nestjs/common';
import { open } from 'sqlite';
import sqlite3 from 'sqlite3';

@Injectable()
export class DatabaseService {
  private db: any;

  constructor() {
    this.initialize();
  }

  async initialize() {
    this.db = await open({
      filename: 'db.sqlite3',
      driver: sqlite3.Database,
    });
  }

  async getInviteByEmail(email: string) {
    const result = await this.db.get('SELECT * FROM invites WHERE email = ?', email);
    return result;
  }

  async createInvite(email: string, invite_id: string) {
    await this.db.run('INSERT INTO invites (invite_id, email) VALUES (?, ?)', invite_id, email);
  }

  async getInviteById(invite_id: string) {
    const result = await this.db.get('SELECT * FROM invites WHERE invite_id = ?', invite_id);
    return result;
  }

  async getUserByUsername(user_name: string) {
    const result = await this.db.get('SELECT * FROM users WHERE user_name = ?', user_name);
    return result;
  }

  async createUser(user_name: string, password: string, invite_id: string) {
    await this.db.run('INSERT INTO users (user_name, password, invite_id) VALUES (?, ?, ?)', user_name, password, invite_id);
  }
}