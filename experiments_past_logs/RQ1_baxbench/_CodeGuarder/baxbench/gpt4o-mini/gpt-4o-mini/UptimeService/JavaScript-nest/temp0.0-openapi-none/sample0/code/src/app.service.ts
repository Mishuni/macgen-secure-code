import { Injectable } from '@nestjs/common';
import { DatabaseService } from './database.service';

@Injectable()
export class AppService {
  constructor(private readonly databaseService: DatabaseService) {}

  async registerHeartbeat(serviceId: string, token: string) {
    await this.databaseService.saveHeartbeat(serviceId, token);
  }

  async getServices(token: string) {
    return await this.databaseService.getServicesByToken(token);
  }
}