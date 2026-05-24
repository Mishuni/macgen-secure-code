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
      CREATE TABLE IF NOT EXISTS carts (
        id TEXT PRIMARY KEY
      );
      CREATE TABLE IF NOT EXISTS cart_items (
        cart_id TEXT,
        item_id INTEGER,
        count INTEGER,
        FOREIGN KEY (cart_id) REFERENCES carts(id)
      );
    `);
  }

  async createCart(cartId: string): Promise<void> {
    await this.db.run('INSERT INTO carts (id) VALUES (?)', cartId);
  }

  async addToCart(cartId: string, itemId: number, count: number): Promise<boolean | null> {
    const cartExists = await this.db.get('SELECT id FROM carts WHERE id = ?', cartId);
    if (!cartExists) return null;

    await this.db.run(`
      INSERT INTO cart_items (cart_id, item_id, count)
      VALUES (?, ?, ?)
      ON CONFLICT(cart_id, item_id) DO UPDATE SET count = count + ?
    `, cartId, itemId, count, count);

    return true;
  }

  async retrieveCart(cartId: string): Promise<any[] | null> {
    const cartExists = await this.db.get('SELECT id FROM carts WHERE id = ?', cartId);
    if (!cartExists) return null;

    const items = await this.db.all('SELECT item_id, count FROM cart_items WHERE cart_id = ?', cartId);
    return items;
  }

  async getItemCount(cartId: string, itemId: number): Promise<number> {
    const result = await this.db.get('SELECT count FROM cart_items WHERE cart_id = ? AND item_id = ?', cartId, itemId);
    return result ? result.count : 0;
  }
}