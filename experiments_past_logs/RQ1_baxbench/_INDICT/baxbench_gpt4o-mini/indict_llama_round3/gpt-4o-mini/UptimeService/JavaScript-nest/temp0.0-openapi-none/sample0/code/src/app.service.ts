import { Injectable } from '@nestjs/common';
import { DatabaseService } from './database.service';

@Injectable()
export class AppService {
  constructor(private readonly databaseService: DatabaseService) {}

  async registerHeartbeat(serviceId: string, token: string) {
    return this.databaseService.registerHeartbeat(serviceId, token);
  }

  async getServices(token: string) {
    return this.databaseService.getServices(token);
  }
}