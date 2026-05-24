import { Injectable } from '@nestjs/common';
import { Database } from 'sqlite3';

@Injectable()
export class DatabaseService {
  private db: Database;

  constructor() {
    this.db = new Database('db.sqlite3', (err) => {
      if (err) {
        console.error('Error opening database ' + err.message);
      }
    });
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

  createMerchant(email: string, name: string, password: string) {
    return new Promise((resolve, reject) => {
      this.db.run(`INSERT INTO merchants (email, name, password) VALUES (?, ?, ?)`, [email, name, password], function(err) {
        if (err) {
          return reject(err);
        }
        resolve({ id: this.lastID });
      });
    });
  }

  findMerchantByEmail(email: string) {
    return new Promise((resolve, reject) => {
      this.db.get(`SELECT * FROM merchants WHERE email = ?`, [email], (err, row) => {
        if (err) {
          return reject(err);
        }
        resolve(row);
      });
    });
  }

  uploadWares(wares: any[]) {
    return new Promise((resolve, reject) => {
      const stmt = this.db.prepare(`INSERT INTO wares (name, description, price, merchantId) VALUES (?, ?, ?, ?)`);
      wares.forEach(ware => {
        stmt.run(ware.name, ware.description, ware.price, ware.merchantId);
      });
      stmt.finalize((err) => {
        if (err) {
          return reject(err);
        }
        resolve();
      });
    });
  }

  getWares(minPrice?: number, maxPrice?: number) {
    return new Promise((resolve, reject) => {
      let query = `SELECT * FROM wares`;
      const params: any[] = [];
      if (minPrice !== undefined) {
        query += ` WHERE price >= ?`;
        params.push(minPrice);
      }
      if (maxPrice !== undefined) {
        query += minPrice !== undefined ? ` AND` : ` WHERE`;
        query += ` price <= ?`;
        params.push(maxPrice);
      }
      this.db.all(query, params, (err, rows) => {
        if (err) {
          return reject(err);
        }
        resolve(rows);
      });
    });
  }
}