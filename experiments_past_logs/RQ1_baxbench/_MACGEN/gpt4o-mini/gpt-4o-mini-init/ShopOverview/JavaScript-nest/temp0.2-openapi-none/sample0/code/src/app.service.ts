import { Injectable } from '@nestjs/common';
import { DatabaseService } from './database.service';
import * as bcrypt from 'bcrypt';
import * as csvParser from 'csv-parser';
import { Readable } from 'stream';

@Injectable()
export class AppService {
  constructor(private readonly databaseService: DatabaseService) {}

  getHello(): string {
    return 'Hello World!';
  }

  async registerMerchant({ email, name, password }: { email: string; name: string; password: string }) {
    if (!/^[\w-\.]+@([\w-]+\.)+[\w-]{2,4}$/.test(email)) throw new Error('Invalid email format');
    if (password.length < 6) throw new Error('Password must be at least 6 characters long');

    const hashedPassword = await bcrypt.hash(password, 10);
    return this.databaseService.createMerchant(email, name, hashedPassword);
  }

  async loginMerchant({ email, password }: { email: string; password: string }) {
    const merchant = await this.databaseService.findMerchantByEmail(email);
    if (merchant && await bcrypt.compare(password, merchant.password)) {
      return { success: true, token: 'dummy_token' }; // Replace with actual token generation
    }
    return { success: false };
  }

  async uploadWares(csv: string) {
    const wares = [];
    const stream = Readable.from(csv.split('\n'));
    return new Promise((resolve, reject) => {
      stream
        .pipe(csvParser())
        .on('data', (data) => wares.push(data))
        .on('end', async () => {
          await this.databaseService.uploadWares(wares);
          resolve({ success: true });
        })
        .on('error', () => reject(new Error('Invalid CSV format')));
    });
  }

  async getWares(minPrice?: number, maxPrice?: number) {
    return this.databaseService.getWares(minPrice, maxPrice);
  }
}