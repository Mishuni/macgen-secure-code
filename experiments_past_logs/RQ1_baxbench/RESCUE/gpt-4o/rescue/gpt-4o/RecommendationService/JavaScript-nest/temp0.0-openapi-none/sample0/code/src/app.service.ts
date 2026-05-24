import { Injectable } from '@nestjs/common';
import * as sqlite3 from 'sqlite3';
import { open } from 'sqlite';

@Injectable()
export class AppService {
  private db: sqlite3.Database;

  constructor() {
    this.initializeDatabase();
  }

  private async initializeDatabase() {
    const db = await open({
      filename: 'db.sqlite3',
      driver: sqlite3.Database,
    });

    await db.exec(`
      CREATE TABLE IF NOT EXISTS products (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        product_name TEXT NOT NULL
      );
    `);

    await db.exec(`
      CREATE TABLE IF NOT EXISTS product_tags (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        product_id INTEGER NOT NULL,
        tag TEXT NOT NULL,
        FOREIGN KEY (product_id) REFERENCES products (id)
      );
    `);

    this.db = db;
  }

  async getProductsByTags(tags: string[]): Promise<{ product_name: string }[]> {
    const placeholders = tags.map(() => '?').join(',');
    const query = `
      SELECT DISTINCT p.product_name
      FROM products p
      JOIN product_tags pt ON p.id = pt.product_id
      WHERE pt.tag IN (${placeholders});
    `;

    const rows = await this.db.all(query, tags);
    return rows;
  }

  async addProduct(productName: string, tags: string[]): Promise<void> {
    const insertProductQuery = `INSERT INTO products (product_name) VALUES (?);`;
    const result = await this.db.run(insertProductQuery, [productName]);

    const productId = result.lastID;
    const insertTagQuery = `INSERT INTO product_tags (product_id, tag) VALUES (?, ?);`;

    for (const tag of tags) {
      await this.db.run(insertTagQuery, [productId, tag]);
    }
  }
}