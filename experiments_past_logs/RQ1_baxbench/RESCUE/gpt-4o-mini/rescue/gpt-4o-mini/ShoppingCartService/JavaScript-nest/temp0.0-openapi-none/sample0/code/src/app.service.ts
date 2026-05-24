import { Injectable } from '@nestjs/common';
import { Database } from 'sqlite3';
import { open } from 'sqlite';
import { v4 as uuidv4 } from 'uuid';

@Injectable()
export class AppService {
  private db: Database;

  constructor() {
    this.initDatabase();
  }

  private async initDatabase() {
    this.db = await open({
      filename: 'db.sqlite3',
      driver: Database,
    });

    await this.db.exec(`
      CREATE TABLE IF NOT EXISTS carts (
        id TEXT PRIMARY KEY,
        items TEXT
      )
    `);
  }

  async createCart(): Promise<string> {
    const cartId = uuidv4();
    await this.db.run('INSERT INTO carts (id, items) VALUES (?, ?)', [cartId, JSON.stringify([])]);
    return cartId;
  }

  async addToCart(cartId: string, itemId: number, count: number): Promise<boolean> {
    const cart = await this.db.get('SELECT * FROM carts WHERE id = ?', [cartId]);
    if (!cart) return false;

    const items = JSON.parse(cart.items);
    const existingItem = items.find((item: { item_id: number }) => item.item_id === itemId);

    if (existingItem) {
      existingItem.count += count;
      if (existingItem.count <= 0) {
        items.splice(items.indexOf(existingItem), 1);
      }
    } else if (count > 0) {
      items.push({ item_id: itemId, count });
    }

    await this.db.run('UPDATE carts SET items = ? WHERE id = ?', [JSON.stringify(items), cartId]);
    return true;
  }

  async retrieveCart(cartId: string): Promise<any[]> {
    const cart = await this.db.get('SELECT * FROM carts WHERE id = ?', [cartId]);
    if (!cart) return null;

    return JSON.parse(cart.items);
  }
}