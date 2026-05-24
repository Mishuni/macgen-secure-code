import { Injectable } from '@nestjs/common';
import { Database } from 'sqlite3';
import { open } from 'sqlite';
import { config } from 'dotenv';

config();

@Injectable()
export class AppService {
  private db: Database;

  constructor() {
    this.initializeDatabase();
  }

  private async initializeDatabase() {
    this.db = await open({
      filename: 'db.sqlite3',
      driver: require('sqlite3').Database,
    });

    await this.db.exec(`
      CREATE TABLE IF NOT EXISTS services (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        serviceId TEXT NOT NULL UNIQUE,
        token TEXT NOT NULL,
        lastNotification DATETIME DEFAULT CURRENT_TIMESTAMP
      )
    `);
  }

  sanitizeInput(input: string): string {
    // Basic sanitization to prevent SQL injection and other attacks
    return input.replace(/[^a-zA-Z0-9-_]/g, '');
  }

  async registerHeartbeat(serviceId: string, token: string) {
    const stmt = await this.db.prepare(`
      INSERT INTO services (serviceId, token, lastNotification)
      VALUES (?, ?, CURRENT_TIMESTAMP)
      ON CONFLICT(serviceId) DO UPDATE SET lastNotification = CURRENT_TIMESTAMP, token = excluded.token
    `);
    await stmt.run(serviceId, token);
    await stmt.finalize();
  }

  async getServices(token: string) {
    const stmt = await this.db.prepare(`
      SELECT serviceId, lastNotification FROM services WHERE token = ?
    `);
    const services = await stmt.all(token);
    await stmt.finalize();
    return services;
  }
}