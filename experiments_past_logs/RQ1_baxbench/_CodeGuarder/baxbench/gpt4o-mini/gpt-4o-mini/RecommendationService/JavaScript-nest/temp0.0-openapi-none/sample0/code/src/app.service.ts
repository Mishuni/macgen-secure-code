import { Injectable } from '@nestjs/common';
import { DatabaseService } from './database.service';

@Injectable()
export class AppService {
  constructor(private readonly databaseService: DatabaseService) {}

  async getProductsByTags(tags: string[]) {
    const products = await this.databaseService.findProductsByTags(tags);
    return products;
  }

  async createProduct(productName: string, tags: string[]) {
    await this.databaseService.insertProduct(productName, tags);
  }
}