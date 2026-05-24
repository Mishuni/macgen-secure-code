import { Injectable, OnModuleInit } from '@nestjs/common';
import * as sqlite3 from 'sqlite3';
import { open, Database } from 'sqlite';

@Injectable()
export class AppService implements OnModuleInit {
  private db: Database;

  async onModuleInit() {
    this.db = await open({
      filename: 'db.sqlite3',
      driver: sqlite3.Database,
    });

    // Initialize the database schema
    await this.db.exec(`
      CREATE TABLE IF NOT EXISTS card_phone_associations (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        credit_card TEXT NOT NULL,
        phone TEXT NOT NULL
      );
    `);
  }

  async associateCard(creditCard: string, phone: string): Promise<void> {
    // Insert the association into the database using parameterized queries
    await this.db.run(
      'INSERT INTO card_phone_associations (credit_card, phone) VALUES (?, ?)',
      [creditCard, phone],
    );
  }

  async retrieveCards(phoneNumbers: string[]): Promise<string[]> {
    // Dynamically construct the query to find cards associated with all phone numbers
    const placeholders = phoneNumbers.map(() => '?').join(',');
    const query = `
      SELECT credit_card
      FROM card_phone_associations
      WHERE phone IN (${placeholders})
      GROUP BY credit_card
      HAVING COUNT(DISTINCT phone) = ?
    `;

    const rows = await this.db.all(query, [...phoneNumbers, phoneNumbers.length]);
    return rows.map((row) => row.credit_card);
  }
}