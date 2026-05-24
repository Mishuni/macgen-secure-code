import { Injectable } from '@nestjs/common';
import * as sqlite3 from 'sqlite3';
import { open } from 'sqlite';
import { v4 as uuidv4 } from 'uuid';

@Injectable()
export class AppService {
  private db: sqlite3.Database;

  constructor() {
    this.initializeDatabase();
  }

  private async initializeDatabase() {
    const db = await open({
      filename: './db.sqlite3',
      driver: sqlite3.Database,
    });

    await db.exec(`
      CREATE TABLE IF NOT EXISTS invitations (
        id TEXT PRIMARY KEY,
        email TEXT UNIQUE NOT NULL
      );
    `);

    await db.exec(`
      CREATE TABLE IF NOT EXISTS users (
        id TEXT PRIMARY KEY,
        user_name TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL
      );
    `);

    this.db = db;
  }

  async createInvitation(email: string): Promise<{ invite_id: string; message: string }> {
    const existingInvitation = await this.db.get('SELECT id FROM invitations WHERE email = ?', [email]);

    if (existingInvitation) {
      return { invite_id: existingInvitation.id, message: 'Invitation already exists for this email.' };
    }

    const inviteId = uuidv4();
    await this.db.run('INSERT INTO invitations (id, email) VALUES (?, ?)', [inviteId, email]);

    return { invite_id: inviteId, message: 'Invitation created successfully.' };
  }

  async createUser(inviteId: string, userName: string, password: string): Promise<{ message: string }> {
    const invitation = await this.db.get('SELECT id FROM invitations WHERE id = ?', [inviteId]);

    if (!invitation) {
      return { message: 'Invalid invite_id' };
    }

    try {
      await this.db.run('INSERT INTO users (id, user_name, password) VALUES (?, ?, ?)', [
        uuidv4(),
        userName,
        password,
      ]);
      return { message: 'User created successfully.' };
    } catch (error) {
      if (error.message.includes('UNIQUE constraint failed: users.user_name')) {
        return { message: 'Username already exists. Try providing a different username.' };
      }
      throw error;
    }
  }
}