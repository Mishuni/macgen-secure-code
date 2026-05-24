import { Injectable } from '@nestjs/common';
import { Database } from 'sqlite3';
import { open } from 'sqlite';
import { config } from 'dotenv';

config();

@Injectable()
export class DatabaseService {
  private db: Database;

  constructor() {
    this.init();
  }

  async init() {
    this.db = await open({
      filename: 'db.sqlite3',
      driver: Database,
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

  async registerHeartbeat(serviceId: string, token: string) {
    const stmt = await this.db.prepare(`
      INSERT INTO services (serviceId, token, lastNotification)
      VALUES (?, ?, CURRENT_TIMESTAMP)
      ON CONFLICT(serviceId) DO UPDATE SET lastNotification = CURRENT_TIMESTAMP
    `);
    await stmt.run(serviceId, token);
    await stmt.finalize();
    return { message: 'Heartbeat registered successfully.' };
  }

  async getServices(token: string) {
    const services = await this.db.all(`
      SELECT serviceId, lastNotification FROM services WHERE token = ?
    `, token);
    return services;
  }
}