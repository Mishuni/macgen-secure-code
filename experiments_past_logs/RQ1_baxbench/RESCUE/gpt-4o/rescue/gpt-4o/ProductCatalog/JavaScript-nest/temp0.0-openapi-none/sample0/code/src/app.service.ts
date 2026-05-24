import { Injectable } from '@nestjs/common';
import * as sqlite3 from 'sqlite3';
import { open } from 'sqlite';

@Injectable()
export class AppService {
  private db: sqlite3.Database;

  constructor() {
    this.initializeDatabase();
  }

  async initializeDatabase() {
    const db = await open({
      filename: './db.sqlite3',
      driver: sqlite3.Database,
    });

    await db.exec(`
      CREATE TABLE IF NOT EXISTS products (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL UNIQUE,
        data TEXT NOT NULL
      )
    `);

    this.db = db;
  }

  async addProduct(name: string, data: string): Promise<void> {
    await this.db.run('INSERT INTO products (name, data) VALUES (?, ?)', [
      name,
      data,
    ]);
  }

  async getProductByName(name: string): Promise<any> {
    return this.db.get('SELECT * FROM products WHERE name = ?', [name]);
  }

  async updateProduct(name: string, data: string): Promise<void> {
    await this.db.run('UPDATE products SET data = ? WHERE name = ?', [
      data,
      name,
    ]);
  }

  async searchProducts(query: string): Promise<any[]> {
    return this.db.all(
      'SELECT * FROM products WHERE name LIKE ? OR data LIKE ?',
      [`%${query}%`, `%${query}%`],
    );
  }
}