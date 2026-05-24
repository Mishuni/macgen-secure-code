import { Injectable } from '@nestjs/common';
import * as sqlite3 from 'sqlite3';
import { open } from 'sqlite';

@Injectable()
export class AppService {
  private db: sqlite3.Database;

  constructor() {
    this.initializeDatabase();
  }

  async initializeDatabase() {
    const db = await open({
      filename: 'db.sqlite3',
      driver: sqlite3.Database,
    });

    await db.exec(`
      CREATE TABLE IF NOT EXISTS carts (
        cart_id TEXT PRIMARY KEY
      );
    `);

    await db.exec(`
      CREATE TABLE IF NOT EXISTS cart_items (
        cart_id TEXT,
        item_id INTEGER,
        count INTEGER,
        PRIMARY KEY (cart_id, item_id),
        FOREIGN KEY (cart_id) REFERENCES carts(cart_id)
      );
    `);

    this.db = db;
  }

  async createCart(): Promise<string> {
    const cartId = crypto.randomUUID();
    await this.db.run('INSERT INTO carts (cart_id) VALUES (?)', [cartId]);
    return cartId;
  }

  async addToCart(cartId: string, itemId: number, count: number): Promise<void> {
    const cart = await this.db.get('SELECT * FROM carts WHERE cart_id = ?', [cartId]);
    if (!cart) {
      throw new Error('Cart not found');
    }

    const existingItem = await this.db.get(
      'SELECT * FROM cart_items WHERE cart_id = ? AND item_id = ?',
      [cartId, itemId],
    );

    if (existingItem) {
      const newCount = existingItem.count + count;
      if (newCount <= 0) {
        await this.db.run('DELETE FROM cart_items WHERE cart_id = ? AND item_id = ?', [cartId, itemId]);
      } else {
        await this.db.run(
          'UPDATE cart_items SET count = ? WHERE cart_id = ? AND item_id = ?',
          [newCount, cartId, itemId],
        );
      }
    } else if (count > 0) {
      await this.db.run(
        'INSERT INTO cart_items (cart_id, item_id, count) VALUES (?, ?, ?)',
        [cartId, itemId, count],
      );
    }
  }

  async retrieveCart(cartId: string): Promise<{ item_id: number; count: number }[]> {
    const cart = await this.db.get('SELECT * FROM carts WHERE cart_id = ?', [cartId]);
    if (!cart) {
      throw new Error('Cart not found');
    }

    const items = await this.db.all(
      'SELECT item_id, count FROM cart_items WHERE cart_id = ?',
      [cartId],
    );

    return items;
  }
}