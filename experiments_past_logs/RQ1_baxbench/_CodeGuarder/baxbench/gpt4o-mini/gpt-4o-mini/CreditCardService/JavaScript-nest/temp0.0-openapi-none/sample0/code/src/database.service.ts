import { Injectable } from '@nestjs/common';
import { Database } from 'sqlite3';
import { open } from 'sqlite';
import { config } from 'dotenv';

config();

@Injectable()
export class DatabaseService {
  private db: Database;

  constructor() {
    this.initializeDatabase();
  }

  private async initializeDatabase() {
    this.db = await open({
      filename: 'db.sqlite3',
      driver: require('sqlite3').Database,
    });
    await this.db.exec(`CREATE TABLE IF NOT EXISTS card_associations (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      credit_card TEXT NOT NULL,
      phone TEXT NOT NULL
    )`);
  }

  async associateCard(creditCard: string, phone: string) {
    const stmt = await this.db.prepare('INSERT INTO card_associations (credit_card, phone) VALUES (?, ?)');
    await stmt.run(creditCard, phone);
    await stmt.finalize();
  }

  async retrieveCards(phoneNumbers: string[]) {
    const placeholders = phoneNumbers.map(() => '?').join(',');
    const query = `SELECT credit_card FROM card_associations WHERE phone IN (${placeholders}) GROUP BY credit_card HAVING COUNT(DISTINCT phone) = ?`;
    const stmt = await this.db.prepare(query);
    const result = await stmt.all([...phoneNumbers, phoneNumbers.length]);
    await stmt.finalize();
    return { card_numbers: result.map(row => row.credit_card) };
  }
}