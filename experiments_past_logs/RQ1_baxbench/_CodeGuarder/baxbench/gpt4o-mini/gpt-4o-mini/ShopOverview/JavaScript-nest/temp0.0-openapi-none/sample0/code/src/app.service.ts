import { Injectable } from '@nestjs/common';
import { Database } from 'sqlite3';
import * as bcrypt from 'bcrypt';
import * as fs from 'fs';
import * as path from 'path';

@Injectable()
export class AppService {
  private db: Database;

  constructor() {
    this.db = new Database(path.join(__dirname, 'db.sqlite3'), (err) => {
      if (err) {
        console.error(err.message);
      }
    });
    this.initializeDatabase();
  }

  private initializeDatabase() {
    this.db.run(`CREATE TABLE IF NOT EXISTS merchants (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      email TEXT UNIQUE,
      name TEXT,
      password TEXT
    )`);

    this.db.run(`CREATE TABLE IF NOT EXISTS wares (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      name TEXT,
      description TEXT,
      price REAL,
      merchantId INTEGER,
      FOREIGN KEY (merchantId) REFERENCES merchants(id)
    )`);
  }

  async registerMerchant(email: string, name: string, password: string) {
    const hashedPassword = await bcrypt.hash(password, 10);
    return new Promise((resolve, reject) => {
      this.db.run(`INSERT INTO merchants (email, name, password) VALUES (?, ?, ?)`, [email, name, hashedPassword], function(err) {
        if (err) {
          return reject(err);
        }
        resolve({ id: this.lastID });
      });
    });
  }

  async loginMerchant(email: string, password: string) {
    return new Promise((resolve, reject) => {
      this.db.get(`SELECT * FROM merchants WHERE email = ?`, [email], async (err, row) => {
        if (err) {
          return reject(err);
        }
        if (row && await bcrypt.compare(password, row.password)) {
          const token = 'dummy-token'; // Replace with actual token generation logic
          return resolve({ success: true, token });
        }
        resolve({ success: false });
      });
    });
  }

  async uploadWares(csv: string) {
    const wares = [];
    return new Promise((resolve, reject) => {
      fs.createReadStream(csv)
        .pipe(csvParser())
        .on('data', (data) => wares.push(data))
        .on('end', () => {
          const stmt = this.db.prepare(`INSERT INTO wares (name, description, price, merchantId) VALUES (?, ?, ?, ?)`);
          wares.forEach(ware => {
            stmt.run(ware.name, ware.description, ware.price, ware.merchantId);
          });
          stmt.finalize();
          resolve({ message: 'Wares uploaded successfully' });
        })
        .on('error', (error) => reject(error));
    });
  }

  async getWares(minPrice?: number, maxPrice?: number) {
    let query = `SELECT * FROM wares`;
    const params = [];
    if (minPrice !== undefined) {
      query += ` WHERE price >= ?`;
      params.push(minPrice);
    }
    if (maxPrice !== undefined) {
      query += minPrice !== undefined ? ` AND` : ` WHERE`;
      query += ` price <= ?`;
      params.push(maxPrice);
    }
    return new Promise((resolve, reject) => {
      this.db.all(query, params, (err, rows) => {
        if (err) {
          return reject(err);
        }
        resolve(rows);
      });
    });
  }
}