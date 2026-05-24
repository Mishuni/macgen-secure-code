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

  it('should log a message', () => {
    expect(appController.logMessage({ message: 'Test log' })).toBe('Log message successful');
  });

  it('should retrieve logs', () => {
    appController.logMessage({ message: 'Test log' });
    const logs = appController.getLogs();
    expect(logs).toContain('Test log');
  });
});