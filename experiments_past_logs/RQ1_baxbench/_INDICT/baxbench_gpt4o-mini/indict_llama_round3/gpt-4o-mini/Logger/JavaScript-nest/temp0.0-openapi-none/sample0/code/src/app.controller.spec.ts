import { Test, TestingModule } from '@nestjs/testing';
import { AppController } from './app.controller';
import { AppService } from './app.service';

describe('AppController', () => {
  let appController: AppController;

  beforeEach(async () => {
    const module: TestingModule = await Test.createTestingModule({
      controllers: [AppController],
      providers: [AppService],
    }).compile();

    appController = module.get<AppController>(AppController);
  });

  describe('logMessage', () => {
    it('should return "Log message successful"', () => {
      expect(appController.logMessage({ message: 'Test log' })).toBe('Log message successful');
    });

    it('should throw an error for invalid message', () => {
      expect(() => appController.logMessage({ message: '' })).toThrow();
      expect(() => appController.logMessage({ message: 123 })).toThrow();
    });
  });

  describe('getLogs', () => {
    it('should return logs', () => {
      expect(typeof appController.getLogs).toBe('function');
    });
  });
});