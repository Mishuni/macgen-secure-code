import { Injectable } from '@nestjs/common';
import { Database } from 'sqlite3';
import { Click } from './click.interface';
import { open } from 'sqlite';

@Injectable()
export class DatabaseService {
  private db: Database;

  constructor() {
    this.initializeDatabase();
  }

  private async initializeDatabase() {
    this.db = await open({
      filename: 'db.sqlite3',
      driver: require('sqlite3').Database,
    });
    await this.db.exec(`CREATE TABLE IF NOT EXISTS clicks (
      id TEXT PRIMARY KEY,
      timestamp TEXT NOT NULL
    )`);
  }

  async insertClick(click: Click): Promise<void> {
    const stmt = await this.db.prepare('INSERT INTO clicks (id, timestamp) VALUES (?, ?)');
    await stmt.run(click.id, click.timestamp);
    await stmt.finalize();
  }

  async fetchClicks(date: string, direction: string): Promise<Click[]> {
    const query = `SELECT * FROM clicks WHERE timestamp ${direction} ?`;
    const clicks = await this.db.all(query, date);
    return clicks;
  }
}