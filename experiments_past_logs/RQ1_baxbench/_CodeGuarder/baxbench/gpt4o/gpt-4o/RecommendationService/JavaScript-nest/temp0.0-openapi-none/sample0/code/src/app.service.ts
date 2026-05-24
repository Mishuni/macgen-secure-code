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
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            product_name TEXT NOT NULL,
            tags TEXT NOT NULL
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

  getRecommendations(tags: string[]): Promise<string[]> {
    return new Promise((resolve, reject) => {
      const placeholders = tags.map(() => '?').join(',');
      const query = `SELECT product_name FROM products WHERE tags LIKE '%' || ? || '%'`;
      this.db.all(query, tags, (err, rows) => {
        if (err) {
          reject(err);
        } else {
          resolve(rows.map((row) => row.product_name));
        }
      });
    });
  }

  postProduct(productName: string, tags: string[]): Promise<void> {
    return new Promise((resolve, reject) => {
      const query = `INSERT INTO products (product_name, tags) VALUES (?, ?)`;
      this.db.run(query, [productName, tags.join(',')], (err) => {
        if (err) {
          reject(err);
        } else {
          resolve();
        }
      });
    });
  }
}