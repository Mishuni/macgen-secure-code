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
    expect(appController.getLogs()).toContain('Test log');
  });

  it('should handle invalid log message', () => {
    expect(appController.logMessage({ message: 'Invalid log message\n' })).toBe('Invalid log message');
  });
});