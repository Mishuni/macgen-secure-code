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

  describe('registerHeartbeat', () => {
    it('should return success message', async () => {
      const result = await appController.registerHeartbeat({ serviceId: 'test-service', token: 'test-token' });
      expect(result).toEqual({ message: 'Heartbeat registered successfully.' });
    });
  });

  describe('getServices', () => {
    it('should return an array of services', async () => {
      const result = await appController.getServices({ token: 'test-token' });
      expect(Array.isArray(result)).toBe(true);
    });
  });
});