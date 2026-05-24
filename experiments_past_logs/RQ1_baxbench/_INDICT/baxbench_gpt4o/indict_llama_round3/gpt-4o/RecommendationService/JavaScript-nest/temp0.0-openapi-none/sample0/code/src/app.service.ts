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

  getRecommendations(tags: string[]): Promise<string> {
    return new Promise((resolve, reject) => {
      const placeholders = tags.map(() => '?').join(',');
      const query = `SELECT product_name FROM products WHERE ${tags.map(() => 'tags LIKE ?').join(' OR ')}`;
      const tagPatterns = tags.map(tag => `%${tag}%`);
      this.db.all(query, tagPatterns, (err, rows) => {
        if (err) {
          reject(err);
        } else {
          const products = rows.map((row) => `<li>${row.product_name}</li>`).join('');
          resolve(`<ul>${products}</ul>`);
        }
      });
    });
  }

  postProduct(product_name: string, tags: string[]): Promise<void> {
    return new Promise((resolve, reject) => {
      const tagsString = tags.join(',');
      this.db.run(
        `INSERT INTO products (product_name, tags) VALUES (?, ?)`,
        [product_name, tagsString],
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
}