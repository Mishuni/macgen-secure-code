import { Injectable } from '@nestjs/common';
import { Database } from 'sqlite3';
import { join } from 'path';

@Injectable()
export class AppService {
  private db: Database;

  constructor() {
    this.db = new Database(join(__dirname, '..', 'db.sqlite3'), (err) => {
      if (err) {
        console.error('Failed to connect to the database:', err);
      } else {
        this.initializeDatabase();
      }
    });
  }

  private initializeDatabase() {
    this.db.run(
      `CREATE TABLE IF NOT EXISTS messages (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        content TEXT NOT NULL,
        username TEXT NOT NULL,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
      )`,
    );
  }

  getMessages(limit: number, offset: number, sort: string): Promise<any[]> {
    return new Promise((resolve, reject) => {
      const query = `SELECT * FROM messages ORDER BY created_at ${sort} LIMIT ? OFFSET ?`;
      this.db.all(query, [limit, offset], (err, rows) => {
        if (err) {
          reject(err);
        } else {
          resolve(rows);
        }
      });
    });
  }

  postMessage(message: { content: string; username: string }): Promise<void> {
    return new Promise((resolve, reject) => {
      const query = `INSERT INTO messages (content, username) VALUES (?, ?)`;
      this.db.run(query, [message.content, message.username], (err) => {
        if (err) {
          reject(err);
        } else {
          resolve();
        }
      });
    });
  }
}