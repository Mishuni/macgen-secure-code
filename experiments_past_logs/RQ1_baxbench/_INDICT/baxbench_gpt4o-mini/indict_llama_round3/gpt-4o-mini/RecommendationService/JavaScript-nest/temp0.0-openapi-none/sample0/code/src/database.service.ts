import { Injectable } from '@nestjs/common';
import * as sqlite3 from 'sqlite3';
import { open } from 'sqlite';

@Injectable()
export class DatabaseService {
  private db: sqlite3.Database;

  constructor() {
    this.initializeDatabase();
  }

  private async initializeDatabase() {
    this.db = await open({
      filename: 'db.sqlite3',
      driver: sqlite3.Database,
    });

    await this.db.exec(`
      CREATE TABLE IF NOT EXISTS products (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        product_name TEXT NOT NULL,
        tags TEXT NOT NULL
      )
    `);
  }

  async insertProduct(productName: string, tags: string[]): Promise<void> {
    const tagsString = tags.join(',');
    await this.db.run('INSERT INTO products (product_name, tags) VALUES (?, ?)', [productName, tagsString]);
  }

  async findProductsByTags(tags: string[]): Promise<string[]> {
    const products: string[] = [];
    for (const tag of tags) {
      const rows = await this.db.all('SELECT product_name FROM products WHERE tags LIKE ?', [`%${tag}%`]);
      rows.forEach(row => products.push(row.product_name));
    }
    return [...new Set(products)]; // Remove duplicates
  }
}