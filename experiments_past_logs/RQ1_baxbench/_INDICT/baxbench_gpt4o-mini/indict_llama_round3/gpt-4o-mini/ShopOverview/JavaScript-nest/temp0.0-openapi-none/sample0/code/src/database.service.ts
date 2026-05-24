import { Injectable } from '@nestjs/common';
import { Database } from 'sqlite3';
import { open } from 'sqlite';
import { resolve } from 'path';

@Injectable()
export class DatabaseService {
  private db: Database;

  constructor() {
    this.init();
  }

  async init() {
    this.db = await open({
      filename: resolve(__dirname, 'db.sqlite3'),
      driver: Database,
    });
    await this.db.exec(`
      CREATE TABLE IF NOT EXISTS merchants (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        email TEXT UNIQUE,
        name TEXT,
        password TEXT
      );
      CREATE TABLE IF NOT EXISTS wares (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        description TEXT,
        price REAL,
        merchantEmail TEXT,
        FOREIGN KEY (merchantEmail) REFERENCES merchants(email)
      );
    `);
  }

  async createMerchant(email: string, name: string, password: string) {
    await this.db.run('INSERT INTO merchants (email, name, password) VALUES (?, ?, ?)', [email, name, password]);
  }

  async findMerchantByEmail(email: string) {
    return await this.db.get('SELECT * FROM merchants WHERE email = ?', [email]);
  }

  async uploadWares(wares: any[]) {
    const stmt = await this.db.prepare('INSERT INTO wares (name, description, price, merchantEmail) VALUES (?, ?, ?, ?)');
    for (const ware of wares) {
      await stmt.run(ware.name, ware.description, ware.price, ware.merchantEmail);
    }
    await stmt.finalize();
  }

  async getWares(minPrice: number, maxPrice: number) {
    const query = 'SELECT * FROM wares WHERE (price >= ? OR ? IS NULL) AND (price <= ? OR ? IS NULL)';
    return await this.db.all(query, [minPrice, minPrice, maxPrice, maxPrice]);
  }
}