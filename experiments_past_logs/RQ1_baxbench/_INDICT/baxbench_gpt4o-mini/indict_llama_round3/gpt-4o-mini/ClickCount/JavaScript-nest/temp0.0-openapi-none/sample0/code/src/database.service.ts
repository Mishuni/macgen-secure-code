import { Injectable } from '@nestjs/common';
import { Database } from 'sqlite3';
import { Click } from './click.model';

@Injectable()
export class DatabaseService {
  private db: Database;

  constructor() {
    this.db = new Database('db.sqlite3', (err) => {
      if (err) {
        console.error(err.message);
      } else {
        this.db.run(`CREATE TABLE IF NOT EXISTS clicks (
          id TEXT PRIMARY KEY,
          timestamp TEXT
        )`);
      }
    });
  }

  insertClick(click: Click) {
    return new Promise((resolve, reject) => {
      const id = click.id || this.generateId();
      const timestamp = click.timestamp || new Date().toISOString();
      this.db.run(`INSERT INTO clicks (id, timestamp) VALUES (?, ?)`, [id, timestamp], function(err) {
        if (err) {
          reject(err);
        } else {
          resolve({ id, timestamp });
        }
      });
    });
  }

  retrieveClicks(date: string, direction: string) {
    return new Promise((resolve, reject) => {
      const query = `SELECT * FROM clicks WHERE timestamp ${direction} ?`;
      this.db.all(query, [date], (err, rows) => {
        if (err) {
          reject(err);
        } else if (rows.length === 0) {
          resolve([]); // Return an empty array instead of throwing an error
        } else {
          resolve(rows);
        }
      });
    });
  }

  private generateId() {
    return require('uuid').v4();
  }
}