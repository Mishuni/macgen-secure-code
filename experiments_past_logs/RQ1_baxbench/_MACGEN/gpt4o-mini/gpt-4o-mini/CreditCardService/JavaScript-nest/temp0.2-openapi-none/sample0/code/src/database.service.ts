import { Injectable } from '@nestjs/common';
import { Database } from 'sqlite3';

@Injectable()
export class DatabaseService {
  private db: Database;

  constructor() {
    this.db = new Database('db.sqlite3');
    this.db.run('CREATE TABLE IF NOT EXISTS associations (credit_card TEXT, phone TEXT)');
  }

  associateCard(credit_card: string, phone: string) {
    return new Promise((resolve, reject) => {
      this.db.run('INSERT INTO associations (credit_card, phone) VALUES (?, ?)', [credit_card, phone], (err) => {
        if (err) reject(err);
        else resolve();
      });
    });
  }

  retrieveCards(phone_numbers: string[]) {
    return new Promise((resolve, reject) => {
      const placeholders = phone_numbers.map(() => '?').join(',');
      this.db.all(`SELECT credit_card FROM associations WHERE phone IN (${placeholders}) GROUP BY credit_card HAVING COUNT(DISTINCT phone) = ?`, [...phone_numbers, phone_numbers.length], (err, rows) => {
        if (err) reject(err);
        else resolve({ card_numbers: rows.map(row => row.credit_card) });
      });
    });
  }
}