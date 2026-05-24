import { Injectable } from '@nestjs/common';
import { v4 as uuidv4 } from 'uuid';
import * as bcrypt from 'bcrypt';
import * as sqlite3 from 'sqlite3';
import { open } from 'sqlite';

@Injectable()
export class AppService {
  private db: sqlite3.Database;

  constructor() {
    this.initDb();
  }

  async initDb() {
    this.db = await open({
      filename: 'db.sqlite3',
      driver: sqlite3.Database
    });

    await this.db.exec(`
      CREATE TABLE IF NOT EXISTS invitations (
        email TEXT PRIMARY KEY,
        invite_id TEXT NOT NULL
      );
    `);

    await this.db.exec(`
      CREATE TABLE IF NOT EXISTS users (
        user_name TEXT PRIMARY KEY,
        password TEXT NOT NULL
      );
    `);
  }

  async createInvitation(email: string) {
    const existingInvite = await this.db.get('SELECT invite_id FROM invitations WHERE email = ?', email);
    if (existingInvite) {
      return { invite_id: existingInvite.invite_id, message: 'Invitation already exists' };
    }

    const invite_id = uuidv4();
    await this.db.run('INSERT INTO invitations (email, invite_id) VALUES (?, ?)', email, invite_id);
    return { invite_id, message: 'Invitation created' };
  }

  async createUser(invite_id: string, user_name: string, password: string) {
    const invite = await this.db.get('SELECT email FROM invitations WHERE invite_id = ?', invite_id);
    if (!invite) {
      return { message: 'Invalid invite_id' };
    }

    const existingUser = await this.db.get('SELECT user_name FROM users WHERE user_name = ?', user_name);
    if (existingUser) {
      return { message: 'Username already exists. Try providing different username.' };
    }

    const hashedPassword = await bcrypt.hash(password, 12);
    await this.db.run('INSERT INTO users (user_name, password) VALUES (?, ?)', user_name, hashedPassword);
    return { message: 'User created successfully' };
  }
}