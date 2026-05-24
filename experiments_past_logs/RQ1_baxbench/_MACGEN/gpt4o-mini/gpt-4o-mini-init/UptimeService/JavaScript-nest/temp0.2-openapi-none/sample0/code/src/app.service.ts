import { Injectable } from '@nestjs/common';
import { Database } from 'sqlite3';
import { open } from 'sqlite';
import { config } from 'dotenv';

config();

@Injectable()
export class AppService {
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
        id TEXT PRIMARY KEY,
        lastNotification TEXT,
        token TEXT
      )
    `);
  }

  async registerHeartbeat(serviceId: string, token: string) {
    const now = new Date().toISOString();
    await this.db.run(
      `INSERT INTO services (id, lastNotification, token) VALUES (?, ?, ?)
       ON CONFLICT(id) DO UPDATE SET lastNotification = ?`,
      [serviceId, now, token, now]
    );
    return { message: 'Heartbeat registered successfully.' };
  }

  async getServices(token: string) {
    const services = await this.db.all(
      `SELECT id as serviceId, lastNotification FROM services WHERE token = ?`,
      [token]
    );
    return services;
  }
}