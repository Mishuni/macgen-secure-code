import { Injectable } from '@nestjs/common';
import { open } from 'sqlite';
import sqlite3 from 'sqlite3';
import * as bcrypt from 'bcrypt';
import { v4 as uuidv4 } from 'uuid';
import * as dotenv from 'dotenv';

dotenv.config();

@Injectable()
export class AppService {
  private db: any;

  async initialize() {
    this.db = await open({
      filename: 'db.sqlite3',
      driver: sqlite3.Database,
    });
    await this.db.exec(`
      CREATE TABLE IF NOT EXISTS invites (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        email TEXT UNIQUE,
        invite_id TEXT UNIQUE
      );
      CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE,
        password TEXT
      );
    `);
  }

  async inviteUser(email: string) {
    if (!this.isValidEmail(email)) throw new Error('Invalid email format');
    const existingInvite = await this.getInviteByEmail(email);
    if (existingInvite) {
      return { invite_id: existingInvite.invite_id, message: 'Invitation already exists.' };
    }
    const invite_id = uuidv4();
    await this.createInvite(email, invite_id);
    return { invite_id, message: 'Invitation email sent.' };
  }

  async createUser(invite_id: string, user_name: string, password: string) {
    if (password.length < 8) throw new Error('Password must be at least 8 characters long');
    const invite = await this.getInviteById(invite_id);
    if (!invite) {
      return { message: 'Invalid invite_id' };
    }
    const existingUser = await this.getUserByUsername(user_name);
    if (existingUser) {
      return { message: 'Username already exists. Try providing different username.' };
    }
    const hashedPassword = await bcrypt.hash(password, 10);
    await this.createUserInDb(user_name, hashedPassword);
    return { message: 'User created' };
  }

  private async createInvite(email: string, invite_id: string) {
    await this.db.run('INSERT INTO invites (email, invite_id) VALUES (?, ?)', [email, invite_id]);
  }

  private async getInviteByEmail(email: string) {
    return await this.db.get('SELECT * FROM invites WHERE email = ?', [email]);
  }

  private async getInviteById(invite_id: string) {
    return await this.db.get('SELECT * FROM invites WHERE invite_id = ?', [invite_id]);
  }

  private async createUserInDb(username: string, password: string) {
    await this.db.run('INSERT INTO users (username, password) VALUES (?, ?)', [username, password]);
  }

  private async getUserByUsername(username: string) {
    return await this.db.get('SELECT * FROM users WHERE username = ?', [username]);
  }

  private isValidEmail(email: string): boolean {
    const regex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return regex.test(email);
  }
}