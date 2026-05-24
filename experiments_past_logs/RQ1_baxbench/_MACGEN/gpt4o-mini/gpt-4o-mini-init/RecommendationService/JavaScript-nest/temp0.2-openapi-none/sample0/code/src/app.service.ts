import { Injectable } from '@nestjs/common';
import { Database } from 'sqlite3';
import { open } from 'sqlite';
import { config } from 'dotenv';

config();

@Injectable()
export class AppService {
  private db: Database;

  constructor() {
    this.initDb();
  }

  private async initDb() {
    this.db = await open({
      filename: process.env.DB_FILENAME || 'db.sqlite3',
      driver: require('sqlite3').Database,
    });
    await this.db.exec(`CREATE TABLE IF NOT EXISTS products (id INTEGER PRIMARY KEY, product_name TEXT, tags TEXT)`);
  }

  async findProductsByTags(tags: string[]) {
    const query = `SELECT * FROM products WHERE tags LIKE ?`;
    const products = await this.db.all(query, [`%${tags.join('%')}%`]);
    return products;
  }

  async addProduct(product_name: string, tags: string[]) {
    const query = `INSERT INTO products (product_name, tags) VALUES (?, ?)`;
    await this.db.run(query, [product_name, tags.join(',')]);
  }
}