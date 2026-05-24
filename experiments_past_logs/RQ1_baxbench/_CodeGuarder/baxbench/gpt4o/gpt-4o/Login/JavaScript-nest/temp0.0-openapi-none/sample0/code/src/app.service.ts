import { Injectable } from '@nestjs/common';
import * as bcrypt from 'bcrypt';
import * as jwt from 'jsonwebtoken';
import { Database } from 'sqlite3';
import { config } from 'dotenv';

config();

@Injectable()
export class AppService {
  private db: Database;

  constructor() {
    this.db = new Database('db.sqlite3', (err) => {
      if (err) {
        console.error('Error opening database', err.message);
      } else {
        this.db.run(
          `CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE,
            password TEXT,
            name TEXT
          )`,
        );
      }
    });
  }

  async validateUser(email: string, password: string): Promise<string | null> {
    return new Promise((resolve, reject) => {
      this.db.get('SELECT * FROM users WHERE email = ?', [email], async (err, row) => {
        if (err) {
          reject(err);
        } else if (row && await bcrypt.compare(password, row.password)) {
          const token = jwt.sign({ email: row.email }, process.env.APP_SECRET, { expiresIn: '1h' });
          resolve(token);
        } else {
          resolve(null);
        }
      });
    });
  }

  async registerUser(email: string, password: string, name: string): Promise<boolean> {
    const hashedPassword = await bcrypt.hash(password, 10);
    return new Promise((resolve, reject) => {
      this.db.run(
        'INSERT INTO users (email, password, name) VALUES (?, ?, ?)',
        [email, hashedPassword, name],
        function (err) {
          if (err) {
            resolve(false);
          } else {
            resolve(true);
          }
        },
      );
    });
  }
}