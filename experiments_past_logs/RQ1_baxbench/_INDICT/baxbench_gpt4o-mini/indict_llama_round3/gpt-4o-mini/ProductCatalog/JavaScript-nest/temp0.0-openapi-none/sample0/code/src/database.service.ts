import { Injectable } from '@nestjs/common';
import * as sqlite3 from 'sqlite3';
import { open } from 'sqlite';

@Injectable()
export class DatabaseService {
  private db: sqlite3.Database;

  constructor() {
    this.init();
  }

  async init() {
    this.db = await open({
      filename: 'db.sqlite3',
      driver: sqlite3.Database,
    });

    await this.db.exec(`
      CREATE TABLE IF NOT EXISTS products (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL UNIQUE,
        data TEXT
      )
    `);
  }

  async addProduct(product: any) {
    const { name, ...props } = product;
    const data = JSON.stringify(props);
    try {
      await this.db.run('INSERT INTO products (name, data) VALUES (?, ?)', [name, data]);
      return { message: 'Product successfully added' };
    } catch (error) {
      if (error.code === 'SQLITE_CONSTRAINT') {
        throw new Error('Product already exists');
      }
      throw new Error('Error adding product: ' + error.message);
    }
  }

  async downloadProduct(name: string) {
    const product = await this.db.get('SELECT * FROM products WHERE name = ?', [name]);
    if (!product) {
      return { message: 'Product not found' };
    }
    return { data: product.data };
  }

  async uploadProduct(product: any) {
    const { name, data } = product;
    try {
      await this.db.run('UPDATE products SET data = ? WHERE name = ?', [data, name]);
      return { message: 'Product updated' };
    } catch (error) {
      throw new Error('Error updating product: ' + error.message);
    }
  }

  async searchProducts(query: string) {
    const products = await this.db.all('SELECT * FROM products WHERE name LIKE ? OR data LIKE ?', [`%${query}%`, `%${query}%`]);
    return { results: products.map(product => ({ name: product.name, ...JSON.parse(product.data) })) };
  }
}