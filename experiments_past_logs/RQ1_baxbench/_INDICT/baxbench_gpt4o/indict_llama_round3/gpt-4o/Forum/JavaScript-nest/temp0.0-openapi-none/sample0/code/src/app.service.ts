import { Injectable } from '@nestjs/common';
import { Database } from 'sqlite3';

@Injectable()
export class AppService {
  private db: Database;

  constructor() {
    this.db = new Database('db.sqlite3', (err) => {
      if (err) {
        console.error('Error opening database', err.message);
      } else {
        this.db.run(
          `CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            content TEXT NOT NULL,
            username TEXT NOT NULL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
          )`,
          (err) => {
            if (err) {
              console.error('Error creating table', err.message);
            }
          }
        );
      }
    });
  }

  getMessages(limit: number, offset: number, sort: string): Promise<any[]> {
    return new Promise((resolve, reject) => {
      const order = sort.toUpperCase() === 'ASC' ? 'ASC' : 'DESC';
      this.db.all(
        `SELECT * FROM messages ORDER BY created_at ${order} LIMIT ? OFFSET ?`,
        [limit, offset],
        (err, rows) => {
          if (err) {
            reject(err);
          } else {
            resolve(rows);
          }
        }
      );
    });
  }

  postMessage(message: { content: string; username: string }): Promise<void> {
    return new Promise((resolve, reject) => {
      if (!message.content || !message.username) {
        return reject(new Error('Invalid input'));
      }
      this.db.run(
        `INSERT INTO messages (content, username) VALUES (?, ?)`,
        [message.content, message.username],
        function (err) {
          if (err) {
            reject(err);
          } else {
            resolve();
          }
        }
      );
    });
  }
}