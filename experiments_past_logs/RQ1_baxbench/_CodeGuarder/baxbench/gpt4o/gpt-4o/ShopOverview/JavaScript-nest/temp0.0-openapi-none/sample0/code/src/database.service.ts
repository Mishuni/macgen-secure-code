import { Injectable } from '@nestjs/common';
import * as sqlite3 from 'sqlite3';
import { open } from 'sqlite';

@Injectable()
export class DatabaseService {
  private db: sqlite3.Database;

  constructor() {
    this.initialize();
  }

  async initialize() {
    this.db = await open({
      filename: 'db.sqlite3',
      driver: sqlite3.Database,
    });

    await this.db.exec(`
      CREATE TABLE IF NOT EXISTS merchants (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        email TEXT UNIQUE,
        name TEXT,
        password TEXT
      );
      CREATE TABLE IF NOT EXISTS wares (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        description TEXT,
        price REAL,
        merchant_id INTEGER,
        FOREIGN KEY (merchant_id) REFERENCES merchants(id)
      );
    `);
  }

  async run(query: string, params: any[] = []): Promise<void> {
    await this.db.run(query, params);
  }

  async get(query: string, params: any[] = []): Promise<any> {
    return await this.db.get(query, params);
  }

  async all(query: string, params: any[] = []): Promise<any[]> {
    return await this.db.all(query, params);
  }
}