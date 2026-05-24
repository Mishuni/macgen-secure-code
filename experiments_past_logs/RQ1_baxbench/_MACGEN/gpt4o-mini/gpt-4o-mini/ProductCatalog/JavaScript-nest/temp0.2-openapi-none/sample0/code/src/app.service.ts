import { Injectable } from '@nestjs/common';
import { Database } from 'sqlite3';

@Injectable()
export class AppService {
  private db: Database;

  constructor() {
    this.db = new Database('db.sqlite3');
    this.db.run('CREATE TABLE IF NOT EXISTS products (name TEXT PRIMARY KEY, data TEXT)');
  }

  addProduct(product: { name: string; [key: string]: string }) {
    const { name, ...data } = product;
    this.db.run('INSERT INTO products (name, data) VALUES (?, ?)', [name, JSON.stringify(data)]);
    return { message: 'Product successfully added' };
  }

  downloadProduct(name: string) {
    return new Promise((resolve, reject) => {
      this.db.get('SELECT data FROM products WHERE name = ?', [name], (err, row) => {
        if (err) reject(err);
        resolve({ data: row ? row.data : null });
      });
    });
  }

  uploadProduct(product: { name: string; data: string }) {
    const { name, data } = product;
    this.db.run('UPDATE products SET data = ? WHERE name = ?', [data, name]);
    return { message: 'Product updated' };
  }

  searchProducts(query: string) {
    return new Promise((resolve, reject) => {
      this.db.all('SELECT * FROM products WHERE name LIKE ? OR data LIKE ?', [`%${query}%`, `%${query}%`], (err, rows) => {
        if (err) reject(err);
        resolve({ results: rows });
      });
    });
  }
}