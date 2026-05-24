import { Injectable } from '@nestjs/common';
import * as bcrypt from 'bcrypt';
import { Database } from 'sqlite3';
import { v4 as uuidv4 } from 'uuid';

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
            id TEXT PRIMARY KEY,
            email TEXT UNIQUE,
            password TEXT,
            name TEXT
          )`,
        );
      }
    });
  }

  async login(email: string, password: string): Promise<{ message: string } | null> {
    return new Promise((resolve, reject) => {
      this.db.get('SELECT * FROM users WHERE email = ?', [email], async (err, row) => {
        if (err) {
          console.error('Database error:', err);
          reject(err);
        } else if (row && (await bcrypt.compare(password, row.password))) {
          resolve({ message: 'Login successful' });
        } else {
          resolve(null);
        }
      });
    });
  }

  async register(email: string, password: string, name: string): Promise<{ message: string } | null> {
    const hashedPassword = await bcrypt.hash(password, 10);
    return new Promise((resolve, reject) => {
      this.db.run(
        'INSERT INTO users (id, email, password, name) VALUES (?, ?, ?, ?)',
        [uuidv4(), email, hashedPassword, name],
        function (err) {
          if (err) {
            console.error('Database error:', err);
            resolve(null);
          } else {
            resolve({ message: 'Registration successful' });
          }
        },
      );
    });
  }
}