import { Injectable } from '@nestjs/common';
import { Database } from 'sqlite3';
import { Message } from './message.entity';
import { open } from 'sqlite';
import { config } from 'dotenv';

config();

@Injectable()
export class AppService {
  private db: Database;

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

  async getMessages(limit: number, offset: number, sort: 'ASC' | 'DESC'): Promise<Message[]> {
    const order = sort === 'ASC' ? 'ASC' : 'DESC';
    return this.db.all(`SELECT * FROM messages ORDER BY id ${order} LIMIT ? OFFSET ?`, [limit, offset]);
  }

  async postMessage(message: Message): Promise<void> {
    await this.db.run(`INSERT INTO messages (content, username) VALUES (?, ?)`, [message.content, message.username]);
  }
}