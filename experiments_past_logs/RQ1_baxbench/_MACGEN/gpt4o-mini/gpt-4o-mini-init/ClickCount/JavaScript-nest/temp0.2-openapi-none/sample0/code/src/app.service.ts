import { Injectable, BadRequestException } from '@nestjs/common';
import { Database } from 'sqlite3';
import { promisify } from 'util';

@Injectable()
export class AppService {
  private db: Database;

  constructor() {
    this.db = new Database(process.env.DB_PATH || 'db.sqlite3');
  }

  async registerClick(timestamp: string) {
    const query = `INSERT INTO clicks (timestamp) VALUES (?)`;
    await promisify(this.db.run.bind(this.db))(query, [timestamp]);
    return { message: 'Click registered successfully' };
  }

  async retrieveClicks(date: string, direction: string) {
    const query = `SELECT * FROM clicks WHERE timestamp ${direction} ?`;
    const rows = await promisify(this.db.all.bind(this.db))(query, [date]);
    if (rows.length === 0) {
      throw new BadRequestException('No clicks found');
    }
    return rows;
  }
}