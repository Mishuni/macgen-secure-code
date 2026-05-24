import { Injectable } from '@nestjs/common';
import { Message } from './message.interface';
import * as sqlite3 from 'sqlite3';
import { open } from 'sqlite';

@Injectable()
export class DatabaseService {
  private db: sqlite3.Database;

  constructor() {
    this.init();
  }

  private async init() {
    this.db = await open({
      filename: 'db.sqlite3',
      driver: sqlite3.Database,
    });
    await this.db.exec(`CREATE TABLE IF NOT EXISTS messages (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      content TEXT NOT NULL,
      username TEXT NOT NULL
    )`);
  }

  async getMessages(limit: number, offset: number, sort: 'ASC' | 'DESC') {
    const order = sort === 'ASC' ? 'ASC' : 'DESC';
    const messages = await this.db.all(`SELECT * FROM messages ORDER BY id ${order} LIMIT ? OFFSET ?`, [limit, offset]);
    return messages;
  }

  async saveMessage(message: Message) {
    const { content, username } = message;
    const result = await this.db.run(`INSERT INTO messages (content, username) VALUES (?, ?)`, [content, username]);
    return { id: result.lastID, content, username };
  }
}