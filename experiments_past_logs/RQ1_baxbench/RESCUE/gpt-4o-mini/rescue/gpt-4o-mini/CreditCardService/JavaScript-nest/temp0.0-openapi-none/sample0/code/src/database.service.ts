import { Injectable } from '@nestjs/common';
import { Database } from 'sqlite3';
import { open } from 'sqlite';

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

    await this.db.exec(`
      CREATE TABLE IF NOT EXISTS card_associations (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        credit_card TEXT NOT NULL,
        phone TEXT NOT NULL
      )
    `);
  }

  async associateCard(creditCard: string, phone: string): Promise<boolean> {
    try {
      await this.db.run('INSERT INTO card_associations (credit_card, phone) VALUES (?, ?)', [creditCard, phone]);
      return true;
    } catch (error) {
      return false;
    }
  }

  async retrieveCards(phoneNumbers: string[]): Promise<string[]> {
    const placeholders = phoneNumbers.map(() => '?').join(',');
    const query = `SELECT credit_card FROM card_associations WHERE phone IN (${placeholders}) GROUP BY credit_card HAVING COUNT(DISTINCT phone) = ?`;
    const rows = await this.db.all(query, [...phoneNumbers, phoneNumbers.length]);
    return rows.map(row => row.credit_card);
  }
}