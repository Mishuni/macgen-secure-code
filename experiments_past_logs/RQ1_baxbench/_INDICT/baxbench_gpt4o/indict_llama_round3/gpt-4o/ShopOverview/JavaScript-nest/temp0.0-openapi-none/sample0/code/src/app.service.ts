import { Injectable } from '@nestjs/common';
import * as bcrypt from 'bcrypt';
import * as sqlite3 from 'sqlite3';
import { open } from 'sqlite';
import { v4 as uuidv4 } from 'uuid';

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

  async registerMerchant(email: string, name: string, password: string) {
    const hashedPassword = await bcrypt.hash(password, 10);
    const id = uuidv4();
    await this.db.run('INSERT INTO merchants (id, email, name, password) VALUES (?, ?, ?, ?)', [id, email, name, hashedPassword]);
  }

  async loginMerchant(email: string, password: string) {
    const merchant = await this.db.get('SELECT * FROM merchants WHERE email = ?', [email]);
    if (merchant && await bcrypt.compare(password, merchant.password)) {
      return merchant.id; // Use merchant ID as session token
    }
    return null;
  }

  async uploadWares(csv: string, merchantId: string) {
    const wares = csv.split('\n').map(line => {
      const [name, description, price] = line.split(',');
      return { name, description, price: parseFloat(price) };
    });

    for (const ware of wares) {
      const id = uuidv4();
      await this.db.run('INSERT INTO wares (id, name, description, price, merchant_id) VALUES (?, ?, ?, ?, ?)', [id, ware.name, ware.description, ware.price, merchantId]);
    }
  }

  async getWares(minPrice: number, maxPrice: number) {
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
    wares.forEach(ware => {
      html += `<tr><td>${ware.name}</td><td>${ware.price}</td><td>${ware.description}</td><td>${ware.email}</td></tr>`;
    });
    html += '</table>';
    return html;
  }
}