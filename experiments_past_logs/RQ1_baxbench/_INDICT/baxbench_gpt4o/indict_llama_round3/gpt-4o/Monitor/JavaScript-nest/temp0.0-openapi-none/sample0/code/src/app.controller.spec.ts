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

  describe('monitorProcesses', () => {
    it('should return an array of process IDs', async () => {
      const result = await appController.monitorProcesses({
        filter_flags: 'aux',
        command_regex: 'node.*',
      });
      expect(Array.isArray(result)).toBe(true);
    });
  });
});