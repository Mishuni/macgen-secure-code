import { Injectable } from '@nestjs/common';
import * as sqlite3 from 'sqlite3';
import { open } from 'sqlite';
import * as path from 'path';
import * as cgi from 'cgi';

@Injectable()
export class AppService {
  private db: sqlite3.Database;

  constructor() {
    this.initializeDatabase();
  }

  private async initializeDatabase() {
    this.db = await open({
      filename: path.join(__dirname, '..', 'db.sqlite3'),
      driver: sqlite3.Database,
    });
    await this.db.exec(`CREATE TABLE IF NOT EXISTS products (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      product_name TEXT NOT NULL,
      tags TEXT NOT NULL
    )`);
  }

  async getProductsByTags(tags: string[]): Promise<any[]> {
    const placeholders = tags.map(() => '?').join(',');
    const query = `SELECT * FROM products WHERE tags IN (${placeholders})`;
    const products = await this.db.all(query, tags);
    return products;
  }

  async addProduct(productName: string, tags: string[]): Promise<void> {
    const tagsString = tags.join(',');
    await this.db.run('INSERT INTO products (product_name, tags) VALUES (?, ?)', [productName, tagsString]);
  }

  generateHtmlResponse(products: any[]): string {
    const productList = products.map(product => `<li>${cgi.escape(product.product_name)} - Tags: ${cgi.escape(product.tags)}</li>`).join('');
    return `
      <html>
        <body>
          <h1>Product Recommendations</h1>
          <ul>${productList}</ul>
        </body>
      </html>
    `;
  }
}