import { Injectable } from '@nestjs/common';
import { Database } from 'sqlite3';
import * as path from 'path';
import * as bcrypt from 'bcrypt';

@Injectable()
export class AppService {
  private db: Database;

  constructor() {
    this.db = new Database(path.resolve(__dirname, '../db.sqlite3'), (err) => {
      if (err) {
        console.error('Error opening database', err);
      } else {
        this.db.run(
          `CREATE TABLE IF NOT EXISTS services (
            serviceId TEXT PRIMARY KEY,
            token TEXT,
            lastNotification TEXT
          )`,
          (err) => {
            if (err) {
              console.error('Error creating table', err);
            }
          },
        );
      }
    });
  }

  async registerHeartbeat(serviceId: string, token: string): Promise<void> {
    const now = new Date().toISOString();
    const hashedToken = await bcrypt.hash(token, 10);
    this.db.run(
      `INSERT INTO services (serviceId, token, lastNotification) VALUES (?, ?, ?)
       ON CONFLICT(serviceId) DO UPDATE SET lastNotification=excluded.lastNotification`,
      [serviceId, hashedToken, now],
      (err) => {
        if (err) {
          console.error('Error registering heartbeat', err);
          throw new Error('Internal server error');
        }
      },
    );
  }

  async getServices(token: string): Promise<any[]> {
    return new Promise((resolve, reject) => {
      this.db.all(
        `SELECT serviceId, token, lastNotification FROM services`,
        [],
        async (err, rows) => {
          if (err) {
            console.error('Error retrieving services', err);
            reject(new Error('Internal server error'));
          } else {
            const validServices = [];
            for (const row of rows) {
              const isMatch = await bcrypt.compare(token, row.token);
              if (isMatch) {
                validServices.push({ serviceId: row.serviceId, lastNotification: row.lastNotification });
              }
            }
            resolve(validServices);
          }
        },
      );
    });
  }
}