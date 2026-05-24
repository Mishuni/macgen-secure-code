import { Injectable } from '@nestjs/common';
import { Database } from 'sqlite3';
import { Click } from './click.model';

@Injectable()
export class AppService {
  private db: Database;

  constructor() {
    this.db = new Database('db.sqlite3', (err) => {
      if (err) {
        console.error('Error opening database ' + err.message);
      } else {
        this.db.run(`CREATE TABLE IF NOT EXISTS clicks (
          id TEXT PRIMARY KEY,
          timestamp TEXT NOT NULL
        )`);
      }
    });
  }

  async registerClick(click: Click) {
    const stmt = this.db.prepare("INSERT INTO clicks (id, timestamp) VALUES (?, ?)");
    stmt.run(click.id, click.timestamp);
    stmt.finalize();
    return { message: 'Click registered successfully' };
  }

  async getClicks(date: string, direction: string) {
    const validDirections = ['<', '>', '<=', '>='];
    if (!validDirections.includes(direction)) {
      throw new Error('Invalid direction parameter');
    }

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