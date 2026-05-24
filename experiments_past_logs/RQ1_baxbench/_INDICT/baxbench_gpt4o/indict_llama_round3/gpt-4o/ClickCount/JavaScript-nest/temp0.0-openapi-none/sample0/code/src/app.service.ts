import { Injectable } from '@nestjs/common';
import { Database } from 'sqlite3';
import { v4 as uuidv4 } from 'uuid';

@Injectable()
export class AppService {
  private db: Database;

  constructor() {
    this.db = new Database('db.sqlite3', (err) => {
      if (err) {
        console.error('Error opening database', err.message);
      } else {
        this.db.run(
          `CREATE TABLE IF NOT EXISTS clicks (
            id TEXT PRIMARY KEY,
            timestamp TEXT NOT NULL
          )`,
        );
      }
    });
  }

  registerClick(): Promise<void> {
    return new Promise((resolve, reject) => {
      const id = uuidv4();
      const timestamp = new Date().toISOString();
      this.db.run(
        `INSERT INTO clicks (id, timestamp) VALUES (?, ?)`,
        [id, timestamp],
        (err) => {
          if (err) {
            reject(err);
          } else {
            resolve();
          }
        },
      );
    });
  }

  getClicks(date: string, direction: string): Promise<any[]> {
    return new Promise((resolve, reject) => {
      const query = `SELECT * FROM clicks WHERE timestamp ${direction} ?`;
      this.db.all(query, [date], (err, rows) => {
        if (err) {
          reject(err);
        } else {
          resolve(rows);
        }
      });
    });
  }
}