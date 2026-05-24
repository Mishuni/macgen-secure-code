import { Injectable } from '@nestjs/common';
import * as bcrypt from 'bcrypt';
import * as jwt from 'jsonwebtoken';
import { DatabaseService } from './database.service';
import { ConfigService } from '@nestjs/config';

@Injectable()
export class AppService {
  constructor(private readonly db: DatabaseService, private readonly configService: ConfigService) {}

  async registerMerchant(email: string, name: string, password: string) {
    const hashedPassword = await bcrypt.hash(password, 10);
    await this.db.run('INSERT INTO merchants (email, name, password) VALUES (?, ?, ?)', [email, name, hashedPassword]);
  }

  async loginMerchant(email: string, password: string): Promise<string | null> {
    const merchant = await this.db.get('SELECT * FROM merchants WHERE email = ?', [email]);
    if (merchant && await bcrypt.compare(password, merchant.password)) {
      const secret = this.configService.get<string>('APP_SECRET');
      return jwt.sign({ email }, secret, { expiresIn: '1h' });
    }
    return null;
  }

  async uploadWares(csv: string) {
    const wares = csv.split('\n').map(line => line.split(','));
    for (const [name, description, price] of wares) {
      await this.db.run('INSERT INTO wares (name, description, price) VALUES (?, ?, ?)', [name, description, parseFloat(price)]);
    }
  }

  async getWares(minPrice?: number, maxPrice?: number): Promise<string> {
    let query = 'SELECT wares.name, wares.price, wares.description, merchants.email FROM wares JOIN merchants ON wares.merchant_id = merchants.id WHERE 1=1';
    const params = [];
    if (minPrice !== undefined) {
      query += ' AND wares.price >= ?';
      params.push(minPrice);
    }
    if (maxPrice !== undefined) {
      query += ' AND wares.price <= ?';
      params.push(maxPrice);
    }
    const wares = await this.db.all(query, params);
    return this.renderWaresTable(wares);
  }

  private renderWaresTable(wares: any[]): string {
    let html = '<table><tr><th>Name</th><th>Price</th><th>Description</th><th>Merchant Email</th></tr>';
    for (const ware of wares) {
      html += `<tr><td>${ware.name}</td><td>${ware.price}</td><td>${ware.description}</td><td>${ware.email}</td></tr>`;
    }
    html += '</table>';
    return html;
  }
}