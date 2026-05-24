import { Injectable } from '@nestjs/common';
import { Database } from 'sqlite3';

@Injectable()
export class AppService {
  private db: Database;

  constructor() {
    this.db = new Database('db.sqlite3', (err) => {
      if (err) {
        console.error('Error opening database', err.message);
      } else {
        this.db.run(
          `CREATE TABLE IF NOT EXISTS products (
            name TEXT PRIMARY KEY,
            data TEXT
          )`,
          (err) => {
            if (err) {
              console.error('Error creating table', err.message);
            }
          },
        );
      }
    });
  }

  addProduct(product: any): Promise<void> {
    return new Promise((resolve, reject) => {
      const data = JSON.stringify(product);
      this.db.run(
        `INSERT INTO products (name, data) VALUES (?, ?)`,
        [product.name, data],
        (err) => {
          if (err) {
            reject(err);
          } else {
            resolve();
          }
        },
      );
    });
  }

  downloadProduct(name: string): Promise<string> {
    return new Promise((resolve, reject) => {
      this.db.get(
        `SELECT data FROM products WHERE name = ?`,
        [name],
        (err, row) => {
          if (err || !row) {
            reject(err || new Error('Product not found'));
          } else {
            resolve(row.data);
          }
        },
      );
    });
  }

  uploadProduct(name: string, data: string): Promise<void> {
    return new Promise((resolve, reject) => {
      this.db.run(
        `UPDATE products SET data = ? WHERE name = ?`,
        [data, name],
        (err) => {
          if (err) {
            reject(err);
          } else {
            resolve();
          }
        },
      );
    });
  }

  searchProducts(query: string): Promise<any[]> {
    return new Promise((resolve, reject) => {
      this.db.all(
        `SELECT data FROM products WHERE name LIKE ? OR data LIKE ?`,
        [`%${query}%`, `%${query}%`],
        (err, rows) => {
          if (err) {
            reject(err);
          } else {
            const results = rows.map((row) => JSON.parse(row.data));
            resolve(results);
          }
        },
      );
    });
  }
}