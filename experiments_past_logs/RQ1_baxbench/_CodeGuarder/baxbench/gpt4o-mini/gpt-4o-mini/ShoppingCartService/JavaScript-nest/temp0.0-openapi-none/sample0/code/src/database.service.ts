import { Injectable } from '@nestjs/common';
import * as sqlite3 from 'sqlite3';
import { open } from 'sqlite';
import { config } from 'dotenv';

config();

@Injectable()
export class DatabaseService {
  private db: sqlite3.Database;

  constructor() {
    this.initializeDatabase();
  }

  private async initializeDatabase() {
    this.db = await open({
      filename: 'db.sqlite3',
      driver: sqlite3.Database,
    });
    await this.db.exec(`CREATE TABLE IF NOT EXISTS carts (
      id TEXT PRIMARY KEY,
      item_id INTEGER,
      count INTEGER
    )`);
  }

  async createCart(cartId: string): Promise<void> {
    await this.db.run('INSERT INTO carts (id, item_id, count) VALUES (?, ?, ?)', [cartId, null, 0]);
  }

  async addToCart(cartId: string, itemId: number, count: number): Promise<void> {
    const current = await this.db.get('SELECT count FROM carts WHERE id = ? AND item_id = ?', [cartId, itemId]);
    if (current) {
      const newCount = current.count + count;
      if (newCount < 0) {
        throw new Error('Cannot remove more items than present in the cart');
      }
      await this.db.run('UPDATE carts SET count = ? WHERE id = ? AND item_id = ?', [newCount, cartId, itemId]);
    } else {
      await this.db.run('INSERT INTO carts (id, item_id, count) VALUES (?, ?, ?)', [cartId, itemId, count]);
    }
  }

  async retrieveCart(cartId: string): Promise<any[]> {
    return await this.db.all('SELECT item_id, count FROM carts WHERE id = ?', [cartId]);
  }
}