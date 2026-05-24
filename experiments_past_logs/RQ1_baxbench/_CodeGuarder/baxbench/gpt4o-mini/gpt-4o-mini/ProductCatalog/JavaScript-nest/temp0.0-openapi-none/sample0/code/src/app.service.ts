import { Injectable } from '@nestjs/common';
import { DatabaseService } from './database.service';

@Injectable()
export class AppService {
  constructor(private readonly databaseService: DatabaseService) {}

  async addProduct(product: { name: string; [key: string]: any }) {
    return this.databaseService.addProduct(product);
  }

  async downloadProduct(name: string) {
    return this.databaseService.downloadProduct(name);
  }

  async uploadProduct(product: { name: string; data: string }) {
    return this.databaseService.uploadProduct(product);
  }

  async searchProducts(query: string) {
    return this.databaseService.searchProducts(query);
  }
}