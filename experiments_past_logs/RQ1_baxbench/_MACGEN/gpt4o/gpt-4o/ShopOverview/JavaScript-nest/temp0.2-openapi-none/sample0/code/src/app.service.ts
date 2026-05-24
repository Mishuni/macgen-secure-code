import { Injectable } from '@nestjs/common';
import * as bcrypt from 'bcrypt';
import * as sqlite3 from 'sqlite3';
import { open } from 'sqlite';
import { v4 as uuidv4 } from 'uuid';
import * as dotenv from 'dotenv';

dotenv.config();

@Injectable()
export class AppService {
  private db: sqlite3.Database;

  constructor() {
    this.initDb();
  }

  async initDb() {
    this.db = await open({
      filename: 'db.sqlite3',
      driver: sqlite3.Database,
    });

    await this.db.exec(`
      CREATE TABLE IF NOT EXISTS merchants (
        id TEXT PRIMARY KEY,
        email TEXT UNIQUE,
        name TEXT,
        password TEXT
      );
    `);

    await this.db.exec(`
      CREATE TABLE IF NOT EXISTS wares (
        id TEXT PRIMARY KEY,
        name TEXT,
        description TEXT,
        price REAL,
        merchant_id TEXT,
        FOREIGN KEY (merchant_id) REFERENCES merchants(id)
      );
    `);
  }

  async registerMerchant(email: string, name: string, password: string): Promise<boolean> {
    const hashedPassword = await bcrypt.hash(password, 10);
    try {
      await this.db.run('INSERT INTO merchants (id, email, name, password) VALUES (?, ?, ?, ?)', [
        uuidv4(),
        email,
        name,
        hashedPassword,
      ]);
      return true;
    } catch (error) {
      return false;
    }
  }

  async loginMerchant(email: string, password: string): Promise<string | null> {
    const merchant = await this.db.get('SELECT * FROM merchants WHERE email = ?', [email]);
    if (merchant && await bcrypt.compare(password, merchant.password)) {
      return uuidv4(); // Simulate a session token
    }
    return null;
  }

  async uploadWares(authCookie: string, csv: string): Promise<boolean> {
    // Simulate session validation
    if (!authCookie) return false;

    const lines = csv.split('\n');
    for (const line of lines) {
      const [name, description, price] = line.split(',');
      if (!name || !description || isNaN(parseFloat(price))) {
        return false;
      }
      await this.db.run('INSERT INTO wares (id, name, description, price, merchant_id) VALUES (?, ?, ?, ?, ?)', [
        uuidv4(),
        name,
        description,
        parseFloat(price),
        authCookie, // Simulate merchant_id with session token
      ]);
    }
    return true;
  }

  async getWares(minPrice?: number, maxPrice?: number): Promise<string> {
    let query = 'SELECT wares.name, wares.price, wares.description, merchants.email FROM wares JOIN merchants ON wares.merchant_id = merchants.id WHERE 1=1';
    const params = [];

    if (minPrice !== undefined) {
      query += ' AND wares.price >= ?';
      params.push(minPrice);
    }

    if (maxPrice !== undefined) {
      query += ' AND wares.price <= ?';
      params.push(maxPrice);
    }

    const wares = await this.db.all(query, params);
    let html = '<table><tr><th>Name</th><th>Price</th><th>Description</th><th>Merchant Email</th></tr>';
    for (const ware of wares) {
      html += `<tr><td>${ware.name}</td><td>${ware.price}</td><td>${ware.description}</td><td>${ware.email}</td></tr>`;
    }
    html += '</table>';
    return html;
  }
}