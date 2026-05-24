import { Test, TestingModule } from '@nestjs/testing';
import { AppController } from './app.controller';
import { AppService } from './app.service';

describe('AppController', () => {
  let appController: AppController;

  beforeEach(async () => {
    const app: TestingModule = await Test.createTestingModule({
      controllers: [AppController],
      providers: [AppService],
    }).compile();

    appController = app.get<AppController>(AppController);
  });

  describe('getProcesses', () => {
    it('should return an array of processes', async () => {
      const result = await appController.getProcesses('aux', 'node');
      expect(Array.isArray(result)).toBe(true);
    });
  });
});