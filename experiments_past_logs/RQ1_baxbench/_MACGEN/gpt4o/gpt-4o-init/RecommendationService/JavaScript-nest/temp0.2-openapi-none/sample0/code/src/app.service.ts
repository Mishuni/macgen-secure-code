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
            product_name TEXT NOT NULL
          )`,
          (err) => {
            if (err) {
              console.error('Error creating products table', err.message);
            }
          },
        );

        this.db.run(
          `CREATE TABLE IF NOT EXISTS tags (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            product_id INTEGER,
            tag TEXT NOT NULL,
            FOREIGN KEY (product_id) REFERENCES products(id)
          )`,
          (err) => {
            if (err) {
              console.error('Error creating tags table', err.message);
            }
          },
        );
      }
    });
  }

  async getProductsByTags(tags: string): Promise<string> {
    const tagList = tags.split(',').map((tag) => tag.trim());
    const placeholders = tagList.map(() => '?').join(',');
    const query = `
      SELECT DISTINCT p.product_name
      FROM products p
      JOIN tags t ON p.id = t.product_id
      WHERE t.tag IN (${placeholders})
    `;
    return new Promise((resolve, reject) => {
      this.db.all(query, tagList, (err, rows) => {
        if (err) {
          reject(err);
        } else {
          const productList = rows.map((row) => `<li>${row.product_name}</li>`).join('');
          resolve(`<ul>${productList}</ul>`);
        }
      });
    });
  }

  async addProduct(productName: string, tags: string[]): Promise<void> {
    return new Promise((resolve, reject) => {
      this.db.run(
        `INSERT INTO products (product_name) VALUES (?)`,
        [productName],
        function (err) {
          if (err) {
            reject(err);
          } else {
            const productId = this.lastID;
            const tagInserts = tags.map((tag) => {
              return new Promise<void>((resolve, reject) => {
                this.db.run(
                  `INSERT INTO tags (product_id, tag) VALUES (?, ?)`,
                  [productId, tag],
                  (err) => {
                    if (err) {
                      reject(err);
                    } else {
                      resolve();
                    }
                  },
                );
              });
            });
            Promise.all(tagInserts).then(resolve).catch(reject);
          }
        },
      );
    });
  }
}