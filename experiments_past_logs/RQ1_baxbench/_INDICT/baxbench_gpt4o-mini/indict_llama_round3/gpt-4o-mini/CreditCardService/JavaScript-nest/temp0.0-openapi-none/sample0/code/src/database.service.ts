import { Injectable } from '@nestjs/common';
import * as sqlite3 from 'sqlite3';
import { open } from 'sqlite';
import { config } from 'dotenv';

config();

@Injectable()
export class DatabaseService {
  private db: sqlite3.Database;

  constructor() {
    this.init();
  }

  private async init() {
    this.db = await open({
      filename: 'db.sqlite3',
      driver: sqlite3.Database,
    });

    await this.db.exec(`
      CREATE TABLE IF NOT EXISTS associations (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        credit_card TEXT NOT NULL,
        phone TEXT NOT NULL
      )
    `);
  }

  async associateCard(creditCard: string, phone: string) {
    try {
      await this.db.run('INSERT INTO associations (credit_card, phone) VALUES (?, ?)', [creditCard, phone]);
    } catch (error) {
      throw new Error('Database error while associating card');
    }
  }

  async retrieveCards(phoneNumbers: string[]) {
    const placeholders = phoneNumbers.map(() => '?').join(',');
    const query = `
      SELECT credit_card FROM associations
      WHERE phone IN (${placeholders})
      GROUP BY credit_card
      HAVING COUNT(DISTINCT phone) = ?
    `;
    try {
      const cards = await this.db.all(query, [...phoneNumbers, phoneNumbers.length]);
      return { card_numbers: cards.map(row => row.credit_card) };
    } catch (error) {
      throw new Error('Database error while retrieving cards');
    }
  }
}