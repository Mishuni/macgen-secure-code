import { Module } from '@nestjs/common';
import { DatabaseService } from './database.service';
import { sqlite3 } from 'sqlite3';
import { open } from 'sqlite';

@Module({
  providers: [DatabaseService],
  exports: [DatabaseService],
})
export class DatabaseModule {
  static async initializeDatabase() {
    const db = await open({
      filename: 'db.sqlite3',
      driver: sqlite3.Database,
    });

    await db.exec(`CREATE TABLE IF NOT EXISTS invites (
      invite_id TEXT PRIMARY KEY,
      email TEXT UNIQUE NOT NULL
    )`);

    await db.exec(`CREATE TABLE IF NOT EXISTS users (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      user_name TEXT UNIQUE NOT NULL,
      password TEXT NOT NULL,
      invite_id TEXT NOT NULL,
      FOREIGN KEY (invite_id) REFERENCES invites(invite_id)
    )`);

    return db;
  }
}