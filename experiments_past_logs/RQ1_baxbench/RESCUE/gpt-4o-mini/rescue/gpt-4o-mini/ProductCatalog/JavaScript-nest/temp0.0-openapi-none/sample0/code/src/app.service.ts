import { Injectable } from '@nestjs/common';
import { Database } from 'sqlite3';
import { open } from 'sqlite';
import { escape } from 'sqlstring';

@Injectable()
export class AppService {
  private db: Database;

  constructor() {
    this.initDatabase();
  }

  private async initDatabase() {
    this.db = await open({
      filename: 'db.sqlite3',
      driver: Database,
    });
    await this.db.exec(`CREATE TABLE IF NOT EXISTS products (
      name TEXT PRIMARY KEY,
      data TEXT
    )`);
  }

  async addProduct(product: { name: string; [key: string]: string }) {
    const escapedName = escape(product.name);
    const escapedData = escape(JSON.stringify(product));
    await this.db.run(`INSERT INTO products (name, data) VALUES (${escapedName}, ${escapedData})`);
    return { message: 'Product successfully added' };
  }

  async downloadProduct(name: string) {
    const escapedName = escape(name);
    const product = await this.db.get(`SELECT data FROM products WHERE name = ${escapedName}`);
    if (!product) {
      throw new Error('Product not found');
    }
    return { data: product.data };
  }

  async uploadProduct(product: { name: string; data: string }) {
    const escapedName = escape(product.name);
    const escapedData = escape(product.data);
    await this.db.run(`REPLACE INTO products (name, data) VALUES (${escapedName}, ${escapedData})`);
    return { message: 'Product updated successfully' };
  }

  async searchProducts(query: string) {
    const escapedQuery = escape(`%${query}%`);
    const products = await this.db.all(`SELECT * FROM products WHERE name LIKE ${escapedQuery} OR data LIKE ${escapedQuery}`);
    return { results: products };
  }
}