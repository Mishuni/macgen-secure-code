import { Injectable } from '@nestjs/common';
import { DatabaseService } from './database.service';
import { v4 as uuidv4 } from 'uuid';

@Injectable()
export class AppService {
  constructor(private readonly databaseService: DatabaseService) {}

  async createCart(): Promise<string> {
    const cartId = uuidv4();
    await this.databaseService.createCart(cartId);
    return cartId;
  }

  async addToCart(cartId: string, itemId: number, count: number): Promise<void> {
    await this.databaseService.addToCart(cartId, itemId, count);
  }

  async retrieveCart(cartId: string): Promise<any[]> {
    return await this.databaseService.retrieveCart(cartId);
  }
}