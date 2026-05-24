import { Injectable, HttpException, HttpStatus } from '@nestjs/common';
import { Database } from 'sqlite3';

@Injectable()
export class AppService {
  private db: Database;

  constructor() {
    this.db = new Database(process.env.DB_PATH || 'db.sqlite3', (err) => {
      if (err) throw new HttpException('Database connection error', HttpStatus.INTERNAL_SERVER_ERROR);
    });
    this.db.run(`CREATE TABLE IF NOT EXISTS carts (id TEXT PRIMARY KEY)`);
    this.db.run(`CREATE TABLE IF NOT EXISTS items (cart_id TEXT, item_id INTEGER, count INTEGER, 
      FOREIGN KEY(cart_id) REFERENCES carts(id))`);
  }

  createCart() {
    const cartId = this.generateCartId();
    this.db.run(`INSERT INTO carts (id) VALUES (?)`, [cartId]);
    return { cart_id: cartId };
  }

  addToCart(cartId: string, itemId: number, count: number) {
    this.db.run(`INSERT INTO items (cart_id, item_id, count) VALUES (?, ?, ?)
      ON CONFLICT(cart_id, item_id) DO UPDATE SET count = count + ?`, [cartId, itemId, count, count]);
    return { message: 'Item added or removed successfully' };
  }

  retrieveCart(cartId: string) {
    return new Promise((resolve, reject) => {
      this.db.all(`SELECT item_id, count FROM items WHERE cart_id = ?`, [cartId], (err, rows) => {
        if (err) reject(new HttpException('Database error', HttpStatus.INTERNAL_SERVER_ERROR));
        resolve({ items: rows });
      });
    });
  }

  private generateCartId(): string {
    return 'cart_' + Date.now();
  }
}