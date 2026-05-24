import { Injectable, HttpException, HttpStatus } from '@nestjs/common';
import { v4 as uuidv4 } from 'uuid';
import * as bcrypt from 'bcrypt';
import * as sqlite3 from 'sqlite3';
import { open } from 'sqlite';

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
    try {
      const existingInvitation = await this.db.get(
        'SELECT invite_id FROM invitations WHERE email = ?',
        email,
      );

      if (existingInvitation) {
        return {
          message: 'Invitation already exists for this email.',
        };
      }

      const inviteId = uuidv4();
      await this.db.run(
        'INSERT INTO invitations (email, invite_id) VALUES (?, ?)',
        email,
        inviteId,
      );

      return {
        invite_id: inviteId,
        message: 'Invitation created successfully.',
      };
    } catch (error) {
      throw new HttpException('Database error', HttpStatus.INTERNAL_SERVER_ERROR);
    }
  }

  async createUser(inviteId: string, userName: string, password: string) {
    try {
      const invitation = await this.db.get(
        'SELECT email FROM invitations WHERE invite_id = ?',
        inviteId,
      );

      if (!invitation) {
        throw new HttpException('Invalid invite_id', HttpStatus.UNAUTHORIZED);
      }

      const existingUser = await this.db.get(
        'SELECT user_name FROM users WHERE user_name = ?',
        userName,
      );

      if (existingUser) {
        throw new HttpException('Username already exists. Try providing different username.', HttpStatus.BAD_REQUEST);
      }

      const hashedPassword = await bcrypt.hash(password, 12);
      await this.db.run(
        'INSERT INTO users (user_name, password) VALUES (?, ?)',
        userName,
        hashedPassword,
      );

      return {
        message: 'User created successfully.',
      };
    } catch (error) {
      if (error instanceof HttpException) {
        throw error;
      }
      throw new HttpException('Database error', HttpStatus.INTERNAL_SERVER_ERROR);
    }
  }
}