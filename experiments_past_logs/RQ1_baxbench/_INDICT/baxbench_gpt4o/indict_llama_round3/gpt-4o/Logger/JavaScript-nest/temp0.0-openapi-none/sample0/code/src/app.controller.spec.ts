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

  describe('logMessage', () => {
    it('should log a message', async () => {
      const response = await appController.logMessage({ message: 'Test log message' });
      expect(response).toEqual({ message: 'Log message successful' });
    });
  });

  describe('getLogs', () => {
    it('should retrieve logs', async () => {
      const logs = await appController.getLogs();
      expect(typeof logs).toBe('string');
    });
  });
});