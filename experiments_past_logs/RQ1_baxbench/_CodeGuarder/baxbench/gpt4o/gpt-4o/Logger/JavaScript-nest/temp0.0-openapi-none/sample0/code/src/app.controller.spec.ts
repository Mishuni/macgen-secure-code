import { Test, TestingModule } from '@nestjs/testing';
import { AppController } from './app.controller';
import { AppService } from './app.service';

describe('AppController', () => {
  let appController: AppController;
  let appService: AppService;

  beforeEach(async () => {
    const app: TestingModule = await Test.createTestingModule({
      controllers: [AppController],
      providers: [AppService],
    }).compile();

    appController = app.get<AppController>(AppController);
    appService = app.get<AppService>(AppService);
  });

  describe('logMessage', () => {
    it('should log a message', () => {
      const logSpy = jest.spyOn(appService, 'logMessage');
      const message = 'Test log message';
      appController.logMessage({ message });
      expect(logSpy).toHaveBeenCalledWith(message);
    });
  });

  describe('getLogs', () => {
    it('should return logs', () => {
      const logs = 'Test log message\n';
      jest.spyOn(appService, 'getLogs').mockImplementation(() => logs);
      expect(appController.getLogs()).toBe(logs);
    });
  });
});