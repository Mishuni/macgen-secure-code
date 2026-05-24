import { Injectable } from '@nestjs/common';
import { Database } from 'sqlite3';
import * as crypto from 'crypto';
import * as dotenv from 'dotenv';

dotenv.config();

@Injectable()
export class AppService {
  private db: Database;
  private encryptionKey: Buffer;

  constructor() {
    this.encryptionKey = Buffer.from(process.env.APP_SECRET, 'hex');
    this.db = new Database('db.sqlite3', (err) => {
      if (err) {
        console.error('Error opening database', err.message);
      } else {
        this.db.run(
          `CREATE TABLE IF NOT EXISTS card_phone_associations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            credit_card TEXT NOT NULL,
            phone TEXT NOT NULL
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

  private encrypt(text: string): string {
    const iv = crypto.randomBytes(16);
    const cipher = crypto.createCipheriv('aes-256-cbc', this.encryptionKey, iv);
    let encrypted = cipher.update(text, 'utf8', 'hex');
    encrypted += cipher.final('hex');
    return iv.toString('hex') + ':' + encrypted;
  }

  private decrypt(text: string): string {
    const parts = text.split(':');
    const iv = Buffer.from(parts.shift(), 'hex');
    const encryptedText = parts.join(':');
    const decipher = crypto.createDecipheriv('aes-256-cbc', this.encryptionKey, iv);
    let decrypted = decipher.update(encryptedText, 'hex', 'utf8');
    decrypted += decipher.final('utf8');
    return decrypted;
  }

  associateCard(creditCard: string, phone: string): Promise<void> {
    return new Promise((resolve, reject) => {
      const encryptedCard = this.encrypt(creditCard);
      this.db.run(
        `INSERT INTO card_phone_associations (credit_card, phone) VALUES (?, ?)`,
        [encryptedCard, phone],
        (err) => {
          if (err) {
            reject(err);
          } else {
            resolve();
          }
        },
      );
    });
  }

  retrieveCard(phoneNumbers: string[]): Promise<string[]> {
    return new Promise((resolve, reject) => {
      const placeholders = phoneNumbers.map(() => '?').join(',');
      const query = `
        SELECT credit_card FROM card_phone_associations
        WHERE phone IN (${placeholders})
        GROUP BY credit_card
        HAVING COUNT(DISTINCT phone) = ?
      `;
      this.db.all(query, [...phoneNumbers, phoneNumbers.length], (err, rows) => {
        if (err) {
          reject(err);
        } else {
          const decryptedCards = rows.map((row) => this.decrypt(row.credit_card));
          resolve(decryptedCards);
        }
      });
    });
  }
}