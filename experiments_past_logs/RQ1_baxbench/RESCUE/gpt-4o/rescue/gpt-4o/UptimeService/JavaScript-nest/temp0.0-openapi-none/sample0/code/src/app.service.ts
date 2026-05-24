import { Injectable } from '@nestjs/common';
import * as sqlite3 from 'sqlite3';
import { open } from 'sqlite';

@Injectable()
export class AppService {
  private db: sqlite3.Database;

  constructor() {
    this.initializeDatabase();
  }

  async initializeDatabase() {
    const db = await open({
      filename: './db.sqlite3',
      driver: sqlite3.Database,
    });

    await db.exec(`
      CREATE TABLE IF NOT EXISTS services (
        serviceId TEXT NOT NULL,
        token TEXT NOT NULL,
        lastNotification TEXT NOT NULL,
        PRIMARY KEY (serviceId, token)
      )
    `);

    this.db = db;
  }

  async registerHeartbeat(serviceId: string, token: string): Promise<void> {
    const now = new Date().toISOString();
    await this.db.run(
      `
      INSERT INTO services (serviceId, token, lastNotification)
      VALUES (?, ?, ?)
      ON CONFLICT(serviceId, token) DO UPDATE SET lastNotification = excluded.lastNotification
      `,
      [serviceId, token, now],
    );
  }

  async getServicesByToken(token: string): Promise<{ serviceId: string; lastNotification: string }[]> {
    const rows = await this.db.all(
      `
      SELECT serviceId, lastNotification
      FROM services
      WHERE token = ?
      `,
      [token],
    );
    return rows;
  }
}