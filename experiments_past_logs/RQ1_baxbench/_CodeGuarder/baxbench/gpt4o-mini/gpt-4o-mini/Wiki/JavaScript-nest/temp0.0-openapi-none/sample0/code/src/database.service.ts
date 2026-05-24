import { Injectable } from '@nestjs/common';
import { Database } from 'sqlite3';

@Injectable()
export class DatabaseService {
  private db: Database;

  constructor() {
    this.db = new Database('db.sqlite3', (err) => {
      if (err) {
        console.error('Error opening database ' + err.message);
      } else {
        this.db.run(`CREATE TABLE IF NOT EXISTS entries (
          id TEXT PRIMARY KEY,
          title TEXT NOT NULL,
          content TEXT NOT NULL,
          lastModifiedBy TEXT,
          lastModifiedAt TEXT
        )`);
      }
    });
  }

  // Add methods for database operations here
}