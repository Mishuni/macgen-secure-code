import { Injectable } from '@nestjs/common';
import { Database } from 'sqlite3';

@Injectable()
export class AppService {
  private db: Database;

  constructor() {
    this.db = new Database('db.sqlite3', (err) => {
      if (err) {
        console.error('Error opening database', err);
      } else {
        this.db.run(
          `CREATE TABLE IF NOT EXISTS products (
            name TEXT PRIMARY KEY,
            data TEXT
          )`,
          (err) => {
            if (err) {
              console.error('Error creating table', err);
            }
          },
        );
      }
    });
  }

  addProduct(productData: Record<string, string>): Promise<void> {
    return new Promise((resolve, reject) => {
      const data = JSON.stringify(productData);
      this.db.run(
        `INSERT INTO products (name, data) VALUES (?, ?)`,
        [productData.name, data],
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

  getProduct(name: string): Promise<string | null> {
    return new Promise((resolve, reject) => {
      this.db.get(`SELECT data FROM products WHERE name = ?`, [name], (err, row) => {
        if (err) {
          reject(err);
        } else {
          resolve(row ? row.data : null);
        }
      });
    });
  }

  updateProduct(name: string, data: string): Promise<void> {
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

  searchProducts(query: string): Promise<Record<string, string>[]> {
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