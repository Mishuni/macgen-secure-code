import { Injectable } from '@nestjs/common';
import { v4 as uuidv4 } from 'uuid';
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
          `CREATE TABLE IF NOT EXISTS clicks (
            id TEXT PRIMARY KEY,
            timestamp TEXT NOT NULL
          )`,
          (err) => {
            if (err) {
              console.error('Error creating table', err.message);
            }
          },
        );
      }
    });
  }

  async registerClick(): Promise<void> {
    const id = uuidv4();
    const timestamp = new Date().toISOString();
    return new Promise((resolve, reject) => {
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

  async getClicks(date: string, direction: string): Promise<any[]> {
    const query = `SELECT * FROM clicks WHERE timestamp ${direction} ?`;
    return new Promise((resolve, reject) => {
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