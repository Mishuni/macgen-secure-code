import { Injectable } from '@nestjs/common';
import { Database } from 'sqlite3';
import { open } from 'sqlite';
import { config } from 'dotenv';

config();

@Injectable()
export class DatabaseService {
  private db: Database;

  async initializeDatabase() {
    this.db = await open({
      filename: 'db.sqlite3',
      driver: sqlite3.Database,
    });
    await this.db.exec(`CREATE TABLE IF NOT EXISTS products (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      name TEXT NOT NULL,
      tags TEXT NOT NULL
    )`);
  }

  async findProductsByTags(tags: string[]) {
    const placeholders = tags.map(() => '?').join(',');
    const query = `SELECT * FROM products WHERE tags IN (${placeholders})`;
    const products = await this.db.all(query, tags);
    return products;
  }

  async insertProduct(name: string, tags: string[]) {
    const tagsString = tags.join(',');
    await this.db.run(`INSERT INTO products (name, tags) VALUES (?, ?)`, [name, tagsString]);
  }
}