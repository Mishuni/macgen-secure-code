import { Injectable } from '@nestjs/common';
import { v4 as uuidv4 } from 'uuid';
import * as sqlite3 from 'sqlite3';
import { open } from 'sqlite';

@Injectable()
export class AppService {
  private db: sqlite3.Database;

  constructor() {
    this.initializeDatabase();
  }

  async initializeDatabase() {
    this.db = await open({
      filename: 'db.sqlite3',
      driver: sqlite3.Database,
    });

    await this.db.exec(`
      CREATE TABLE IF NOT EXISTS carts (
        id TEXT PRIMARY KEY
      );
    `);

    await this.db.exec(`
      CREATE TABLE IF NOT EXISTS cart_items (
        cart_id TEXT,
        item_id INTEGER,
        count INTEGER,
        PRIMARY KEY (cart_id, item_id),
        FOREIGN KEY (cart_id) REFERENCES carts(id)
      );
    `);
  }

  async createCart(): Promise<string> {
    const cartId = uuidv4();
    await this.db.run('INSERT INTO carts (id) VALUES (?)', cartId);
    return cartId;
  }

  async addToCart(cartId: string, itemId: number, count: number): Promise<boolean> {
    const cart = await this.db.get('SELECT id FROM carts WHERE id = ?', cartId);
    if (!cart) {
      return false;
    }

    const existingItem = await this.db.get(
      'SELECT count FROM cart_items WHERE cart_id = ? AND item_id = ?',
      cartId,
      itemId,
    );

    if (existingItem) {
      const newCount = existingItem.count + count;
      if (newCount <= 0) {
        await this.db.run('DELETE FROM cart_items WHERE cart_id = ? AND item_id = ?', cartId, itemId);
      } else {
        await this.db.run('UPDATE cart_items SET count = ? WHERE cart_id = ? AND item_id = ?', newCount, cartId, itemId);
      }
    } else if (count > 0) {
      await this.db.run('INSERT INTO cart_items (cart_id, item_id, count) VALUES (?, ?, ?)', cartId, itemId, count);
    }

    return true;
  }

  async retrieveCart(cartId: string): Promise<{ item_id: number; count: number }[] | null> {
    const cart = await this.db.get('SELECT id FROM carts WHERE id = ?', cartId);
    if (!cart) {
      return null;
    }

    const items = await this.db.all('SELECT item_id, count FROM cart_items WHERE cart_id = ?', cartId);
    return items;
  }
}