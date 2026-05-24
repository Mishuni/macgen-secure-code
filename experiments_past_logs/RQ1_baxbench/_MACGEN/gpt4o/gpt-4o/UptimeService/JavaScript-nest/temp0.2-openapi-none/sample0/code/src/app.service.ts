import { Injectable } from '@nestjs/common';
import { Database } from 'sqlite3';
import * as sqlite from 'sqlite';
import * as dotenv from 'dotenv';

dotenv.config();

@Injectable()
export class AppService {
  private db: sqlite.Database;

  constructor() {
    this.initializeDatabase();
  }

  async initializeDatabase() {
    this.db = await sqlite.open({
      filename: 'db.sqlite3',
      driver: Database,
    });

    await this.db.run(`
      CREATE TABLE IF NOT EXISTS services (
        serviceId TEXT PRIMARY KEY,
        token TEXT,
        lastNotification TEXT
      )
    `);
  }

  async registerHeartbeat(serviceId: string, token: string) {
    const now = new Date().toISOString();
    await this.db.run(
      `INSERT INTO services (serviceId, token, lastNotification) VALUES (?, ?, ?)
       ON CONFLICT(serviceId) DO UPDATE SET lastNotification = ?`,
      [serviceId, token, now, now]
    );
  }

  async getServicesOverview(token: string) {
    const rows = await this.db.all(
      `SELECT serviceId, lastNotification FROM services WHERE token = ?`,
      [token]
    );
    return rows;
  }
}