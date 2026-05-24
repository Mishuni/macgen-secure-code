import { Injectable } from '@nestjs/common';
import { Database } from 'sqlite3';

@Injectable()
export class AppService {
  private db: Database;

  constructor() {
    this.db = new Database('db.sqlite3', (err) => {
      if (err) {
        console.error('Error opening database', err.message);
      } else {
        this.db.run(
          `CREATE TABLE IF NOT EXISTS associations (
            credit_card TEXT,
            phone TEXT,
            PRIMARY KEY (credit_card, phone)
          )`,
          (err) => {
            if (err) {
              console.error('Error creating table', err.message);
            }
          },
        );
      }
    });
  }

  associateCard(creditCard: string, phone: string): Promise<void> {
    return new Promise((resolve, reject) => {
      const stmt = this.db.prepare('INSERT INTO associations (credit_card, phone) VALUES (?, ?)');
      stmt.run(creditCard, phone, (err) => {
        if (err) {
          reject(err);
        } else {
          resolve();
        }
      });
      stmt.finalize();
    });
  }

  retrieveCards(phoneNumbers: string[]): Promise<string[]> {
    return new Promise((resolve, reject) => {
      const placeholders = phoneNumbers.map(() => '?').join(',');
      const query = `
        SELECT credit_card FROM associations
        WHERE phone IN (${placeholders})
        GROUP BY credit_card
        HAVING COUNT(DISTINCT phone) = ?
      `;
      this.db.all(query, [...phoneNumbers, phoneNumbers.length], (err, rows) => {
        if (err) {
          reject(err);
        } else {
          resolve(rows.map(row => row.credit_card));
        }
      });
    });
  }
}