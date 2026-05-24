import { Injectable } from '@nestjs/common';
import { DatabaseService } from './database.service';

@Injectable()
export class AppService {
  constructor(private readonly databaseService: DatabaseService) {}

  async getProductsByTags(tags: string[]): Promise<string> {
    const products = await this.databaseService.findProductsByTags(tags);
    return `<html><body><h1>Recommended Products</h1><ul>${products.map(product => `<li>${product}</li>`).join('')}</ul></body></html>`;
  }

  async addProduct(productName: string, tags: string[]): Promise<void> {
    await this.databaseService.insertProduct(productName, tags);
  }
}