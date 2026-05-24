import { Injectable } from '@nestjs/common';
import { DatabaseService } from './database.service';
import * as bcrypt from 'bcrypt';
import { Response } from 'express';
import { parse } from 'csv-parser';
import { Readable } from 'stream';

@Injectable()
export class AppService {
  constructor(private readonly databaseService: DatabaseService) {}

  async registerMerchant(body: { email: string; name: string; password: string }) {
    const hashedPassword = await bcrypt.hash(body.password, 10);
    return this.databaseService.createMerchant(body.email, body.name, hashedPassword);
  }

  async loginMerchant(body: { email: string; password: string }, res: Response) {
    const merchant = await this.databaseService.findMerchantByEmail(body.email);
    if (merchant && await bcrypt.compare(body.password, merchant.password)) {
      res.cookie('AUTH_COOKIE', 'some_auth_token'); // Set a cookie for session
      return res.status(HttpStatus.OK).json('Login successful');
    }
    return res.status(HttpStatus.UNAUTHORIZED).json({ error: 'Invalid email or password' });
  }

  async uploadWares(body: { csv: string }, res: Response) {
    const stream = Readable.from(body.csv.split('\n'));
    const wares = [];
    stream.pipe(parse({ columns: true }))
      .on('data', (row) => {
        if (row.name && row.description && row.price) {
          wares.push(row);
        }
      })
      .on('end', async () => {
        if (wares.length > 0) {
          await this.databaseService.uploadWares(wares);
          return res.status(HttpStatus.OK).json('Wares uploaded successfully');
        } else {
          return res.status(HttpStatus.BAD_REQUEST).json('Invalid CSV format');
        }
      })
      .on('error', () => {
        return res.status(HttpStatus.BAD_REQUEST).json('Invalid CSV format');
      });
  }

  async getWares(minPrice: number, maxPrice: number, res: Response) {
    const wares = await this.databaseService.getWares(minPrice, maxPrice);
    let html = '<table><tr><th>Name</th><th>Price</th><th>Description</th><th>Merchant Email</th></tr>';
    wares.forEach(ware => {
      html += `<tr><td>${ware.name}</td><td>${ware.price}</td><td>${ware.description}</td><td>${ware.merchantEmail}</td></tr>`;
    });
    html += '</table>';
    return res.status(HttpStatus.OK).send(html);
  }
}