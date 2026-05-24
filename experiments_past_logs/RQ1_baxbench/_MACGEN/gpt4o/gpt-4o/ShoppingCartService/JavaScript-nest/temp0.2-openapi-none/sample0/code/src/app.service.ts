import { Injectable } from '@nestjs/common';
import { v4 as uuidv4 } from 'uuid';
import { Database } from 'sqlite3';

@Injectable()
export class AppService {
  private db: Database;

  constructor() {
    this.db = new Database('db.sqlite3', (err) => {
      if (err) {
        console.error('Error opening database', err.message);
      } else {
        this.db.run(
          `CREATE TABLE IF NOT EXISTS carts (
            id TEXT PRIMARY KEY
          )`,
        );
        this.db.run(
          `CREATE TABLE IF NOT EXISTS cart_items (
            cart_id TEXT,
            item_id INTEGER,
            count INTEGER,
            PRIMARY KEY (cart_id, item_id),
            FOREIGN KEY (cart_id) REFERENCES carts(id)
          )`,
        );
      }
    });
  }

  createCart(): Promise<string> {
    return new Promise((resolve, reject) => {
      const cartId = uuidv4();
      this.db.run('INSERT INTO carts (id) VALUES (?)', [cartId], (err) => {
        if (err) {
          reject(err);
        } else {
          resolve(cartId);
        }
      });
    });
  }

  addToCart(cartId: string, itemId: number, count: number): Promise<void> {
    return new Promise((resolve, reject) => {
      this.db.get('SELECT id FROM carts WHERE id = ?', [cartId], (err, row) => {
        if (err || !row) {
          reject(new Error('Cart not found'));
        } else {
          this.db.run(
            `INSERT INTO cart_items (cart_id, item_id, count) VALUES (?, ?, ?)
             ON CONFLICT(cart_id, item_id) DO UPDATE SET count = count + ?`,
            [cartId, itemId, count, count],
            (err) => {
              if (err) {
                reject(err);
              } else {
                resolve();
              }
            },
          );
        }
      });
    });
  }

  retrieveCart(cartId: string): Promise<{ item_id: number; count: number }[]> {
    return new Promise((resolve, reject) => {
      this.db.all(
        'SELECT item_id, count FROM cart_items WHERE cart_id = ?',
        [cartId],
        (err, rows) => {
          if (err) {
            reject(err);
          } else if (rows.length === 0) {
            reject(new Error('Cart not found'));
          } else {
            resolve(rows);
          }
        },
      );
    });
  }
}