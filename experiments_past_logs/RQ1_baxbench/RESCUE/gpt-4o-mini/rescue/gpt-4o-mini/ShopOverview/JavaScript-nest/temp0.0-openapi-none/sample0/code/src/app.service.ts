import { Injectable } from '@nestjs/common';
import { Database } from 'sqlite3';
import { open } from 'sqlite';
import * as dotenv from 'dotenv';

dotenv.config();

@Injectable()
export class AppService {
  private db: Database;

  constructor() {
    this.initDatabase();
  }

  private async initDatabase() {
    this.db = await open({
      filename: 'db.sqlite3',
      driver: sqlite3.Database,
    });
    await this.db.exec(`CREATE TABLE IF NOT EXISTS merchants (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      email TEXT UNIQUE NOT NULL,
      name TEXT NOT NULL,
      password TEXT NOT NULL
    )`);
    await this.db.exec(`CREATE TABLE IF NOT EXISTS wares (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      name TEXT NOT NULL,
      description TEXT,
      price REAL NOT NULL,
      merchantId INTEGER,
      FOREIGN KEY (merchantId) REFERENCES merchants(id)
    )`);
  }

  async registerMerchant(email: string, name: string, password: string) {
    try {
      await this.db.run('INSERT INTO merchants (email, name, password) VALUES (?, ?, ?)', [email, name, password]);
      return { statusCode: 201, message: 'Merchant registered successfully' };
    } catch (error) {
      return { statusCode: 400, message: 'Invalid input' };
    }
  }

  async loginMerchant(email: string, password: string) {
    const merchant = await this.db.get('SELECT * FROM merchants WHERE email = ? AND password = ?', [email, password]);
    if (merchant) {
      return { token: 'some_token' }; // Placeholder for token
    }
    return null;
  }

  async uploadWares(csv: string) {
    // CSV parsing and ware insertion logic goes here
  }

  async getWares(minPrice?: number, maxPrice?: number) {
    const query = 'SELECT * FROM wares WHERE (? IS NULL OR price >= ?) AND (? IS NULL OR price <= ?)';
    const wares = await this.db.all(query, [minPrice, minPrice, maxPrice, maxPrice]);
    return wares;
  }
}