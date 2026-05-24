import { Injectable, HttpException, HttpStatus } from '@nestjs/common';
import * as sqlite3 from 'sqlite3';
import { open } from 'sqlite';
import * as bcrypt from 'bcrypt';
import * as jwt from 'jsonwebtoken';
import * as dotenv from 'dotenv';

dotenv.config();

@Injectable()
export class AppService {
  private db;

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
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        email TEXT UNIQUE NOT NULL,
        name TEXT NOT NULL,
        password TEXT NOT NULL
      );
    `);

    await this.db.exec(`
      CREATE TABLE IF NOT EXISTS wares (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        description TEXT NOT NULL,
        price REAL NOT NULL,
        merchant_id INTEGER NOT NULL,
        FOREIGN KEY (merchant_id) REFERENCES merchants(id)
      );
    `);
  }

  async registerMerchant(email: string, name: string, password: string) {
    const hashedPassword = await bcrypt.hash(password, 10);
    try {
      await this.db.run(
        'INSERT INTO merchants (email, name, password) VALUES (?, ?, ?)',
        [email, name, hashedPassword],
      );
      return { message: 'Merchant registered successfully' };
    } catch (error) {
      throw new HttpException('Email already exists', HttpStatus.BAD_REQUEST);
    }
  }

  async loginMerchant(email: string, password: string) {
    const merchant = await this.db.get(
      'SELECT * FROM merchants WHERE email = ?',
      [email],
    );
    if (!merchant || !(await bcrypt.compare(password, merchant.password))) {
      return null;
    }
    const token = jwt.sign({ id: merchant.id }, process.env.APP_SECRET, {
      expiresIn: '1h',
    });
    return token;
  }

  async uploadWares(authCookie: string, csv: string) {
    const decoded = jwt.verify(authCookie, process.env.APP_SECRET);
    const merchantId = decoded.id;

    const rows = csv.split('\n').map((row) => row.split(','));
    for (const [name, description, price] of rows) {
      if (!name || !description || isNaN(Number(price))) {
        throw new HttpException('Invalid CSV format', HttpStatus.BAD_REQUEST);
      }
      await this.db.run(
        'INSERT INTO wares (name, description, price, merchant_id) VALUES (?, ?, ?, ?)',
        [name, description, parseFloat(price), merchantId],
      );
    }
    return { message: 'Wares uploaded successfully' };
  }

  async getWares(minPrice: number, maxPrice: number) {
    let query = 'SELECT wares.name, wares.description, wares.price, merchants.email FROM wares JOIN merchants ON wares.merchant_id = merchants.id WHERE 1=1';
    const params = [];

    if (minPrice) {
      query += ' AND wares.price >= ?';
      params.push(minPrice);
    }
    if (maxPrice) {
      query += ' AND wares.price <= ?';
      params.push(maxPrice);
    }

    const wares = await this.db.all(query, params);
    let html = '<table><tr><th>Name</th><th>Description</th><th>Price</th><th>Merchant Email</th></tr>';
    for (const ware of wares) {
      html += `<tr><td>${ware.name}</td><td>${ware.description}</td><td>${ware.price}</td><td>${ware.email}</td></tr>`;
    }
    html += '</table>';
    return html;
  }
}