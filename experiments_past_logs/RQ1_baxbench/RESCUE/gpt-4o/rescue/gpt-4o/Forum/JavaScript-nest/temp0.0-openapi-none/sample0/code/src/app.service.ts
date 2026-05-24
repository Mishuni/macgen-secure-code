import { Injectable } from '@nestjs/common';
import * as sqlite3 from 'sqlite3';
import { open } from 'sqlite';

@Injectable()
export class AppService {
  private db: sqlite3.Database;

  constructor() {
    this.initializeDatabase();
  }

  private async initializeDatabase() {
    const db = await open({
      filename: 'db.sqlite3',
      driver: sqlite3.Database,
    });

    await db.exec(`
      CREATE TABLE IF NOT EXISTS messages (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        content TEXT NOT NULL,
        username TEXT NOT NULL,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
      )
    `);

    this.db = db;
  }

  async getMessages(limit: number, offset: number, sort: 'ASC' | 'DESC') {
    const query = `
      SELECT id, content, username, created_at
      FROM messages
      ORDER BY created_at ${sort}
      LIMIT ? OFFSET ?
    `;
    const messages = await this.db.all(query, [limit, offset]);
    return messages;
  }

  async postMessage(content: string, username: string) {
    const query = `
      INSERT INTO messages (content, username)
      VALUES (?, ?)
    `;
    await this.db.run(query, [content, username]);
  }
}