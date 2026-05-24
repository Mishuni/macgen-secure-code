import { Injectable } from '@nestjs/common';
import { open } from 'sqlite';
import sqlite3 from 'sqlite3';
import { config } from 'dotenv';

config();

@Injectable()
export class DatabaseService {
  private db: any;

  constructor() {
    this.init();
  }

  private async init() {
    this.db = await open({
      filename: 'db.sqlite3',
      driver: sqlite3.Database,
    });
    await this.db.exec(`CREATE TABLE IF NOT EXISTS products (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      name TEXT NOT NULL,
      data TEXT
    )`);
  }

  async addProduct(product: { name: string; [key: string]: any }) {
    const stmt = await this.db.prepare('INSERT INTO products (name, data) VALUES (?, ?)');
    await stmt.run(product.name, JSON.stringify(product));
    await stmt.finalize();
    return { message: 'Product successfully added' };
  }

  async downloadProduct(name: string) {
    const product = await this.db.get('SELECT * FROM products WHERE name = ?', name);
    if (!product) {
      return { message: 'Product not found' };
    }
    return { data: product.data };
  }

  async uploadProduct(product: { name: string; data: string }) {
    const stmt = await this.db.prepare('UPDATE products SET data = ? WHERE name = ?');
    await stmt.run(product.data, product.name);
    await stmt.finalize();
    return { message: 'Product updated successfully' };
  }

  async searchProducts(query: string) {
    const products = await this.db.all('SELECT * FROM products WHERE name LIKE ? OR data LIKE ?', `%${query}%`, `%${query}%`);
    return { results: products };
  }
}