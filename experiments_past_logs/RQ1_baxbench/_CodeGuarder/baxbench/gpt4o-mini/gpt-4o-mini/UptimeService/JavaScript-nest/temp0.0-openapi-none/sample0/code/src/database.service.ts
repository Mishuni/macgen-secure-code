import { Injectable } from '@nestjs/common';
import { Database } from 'sqlite3';
import { open } from 'sqlite';
import * as dotenv from 'dotenv';

dotenv.config();

@Injectable()
export class DatabaseService {
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
        serviceId TEXT PRIMARY KEY,
        lastNotification TEXT
      )
    `);
  }

  async saveHeartbeat(serviceId: string, token: string) {
    const timestamp = new Date().toISOString();
    await this.db.run(
      `INSERT INTO services (serviceId, lastNotification) VALUES (?, ?) 
       ON CONFLICT(serviceId) DO UPDATE SET lastNotification = ?`,
      [serviceId, timestamp, timestamp]
    );
  }

  async getServicesByToken(token: string) {
    return await this.db.all(`SELECT serviceId, lastNotification FROM services`);
  }
}