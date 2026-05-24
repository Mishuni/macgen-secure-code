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
    it('should return "Log message successful"', () => {
      expect(appController.logMessage('Test message')).toBe('Log message successful');
    });
  });

  describe('getLogs', () => {
    it('should return logs', () => {
      appController.logMessage('Test message');
      expect(appController.getLogs()).toContain('Test message');
    });
  });
});