import { Injectable } from '@nestjs/common';
import { Database } from 'sqlite3';
import * as sqlite from 'sqlite';

@Injectable()
export class AppService {
  private db: sqlite.Database;

  constructor() {
    this.initDb();
  }

  async initDb() {
    this.db = await sqlite.open({
      filename: 'db.sqlite3',
      driver: Database,
    });

    await this.db.run(`
      CREATE TABLE IF NOT EXISTS products (
        name TEXT PRIMARY KEY,
        data TEXT
      )
    `);
  }

  async addProduct(product: any) {
    const data = JSON.stringify(product);
    await this.db.run('INSERT INTO products (name, data) VALUES (?, ?)', [product.name, data]);
  }

  async downloadProduct(name: string): Promise<string> {
    const row = await this.db.get('SELECT data FROM products WHERE name = ?', [name]);
    if (!row) throw new Error('Product not found');
    return row.data;
  }

  async uploadProduct(name: string, data: string) {
    await this.db.run('UPDATE products SET data = ? WHERE name = ?', [data, name]);
  }

  async searchProducts(query: string): Promise<any[]> {
    const rows = await this.db.all('SELECT data FROM products WHERE data LIKE ?', [`%${query}%`]);
    return rows.map(row => JSON.parse(row.data));
  }
}