import { Injectable } from '@nestjs/common';
import { Database } from 'sqlite3';
import * as sqlite from 'sqlite';

@Injectable()
export class AppService {
  private db: sqlite.Database;

  constructor() {
    this.initializeDatabase();
  }

  private async initializeDatabase() {
    this.db = await sqlite.open({
      filename: 'db.sqlite3',
      driver: Database,
    });

    await this.db.run(`
      CREATE TABLE IF NOT EXISTS services (
        serviceId TEXT PRIMARY KEY,
        token TEXT NOT NULL,
        lastNotification TEXT
      )
    `);
  }

  async registerHeartbeat(serviceId: string, token: string): Promise<void> {
    const now = new Date().toISOString();
    await this.db.run(
      `INSERT INTO services (serviceId, token, lastNotification) VALUES (?, ?, ?)
       ON CONFLICT(serviceId) DO UPDATE SET lastNotification = ?`,
      [serviceId, token, now, now]
    );
  }

  async getServicesOverview(token: string): Promise<{ serviceId: string; lastNotification: string }[]> {
    const rows = await this.db.all(
      `SELECT serviceId, lastNotification FROM services WHERE token = ?`,
      [token]
    );
    return rows;
  }
}