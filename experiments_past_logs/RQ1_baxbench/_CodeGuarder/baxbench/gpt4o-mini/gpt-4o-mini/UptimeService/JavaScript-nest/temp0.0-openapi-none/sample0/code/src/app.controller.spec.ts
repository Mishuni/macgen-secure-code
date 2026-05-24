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

  describe('registerHeartbeat', () => {
    it('should return success message', async () => {
      const result = await appController.registerHeartbeat({ serviceId: 'test-service', token: 'test-token' });
      expect(result).toEqual({ message: 'Heartbeat registered successfully.' });
    });

    it('should throw error for invalid payload', async () => {
      await expect(appController.registerHeartbeat({ serviceId: '', token: '' })).rejects.toThrow();
    });
  });

  describe('getServices', () => {
    it('should return services', async () => {
      const result = await appController.getServices({ token: 'test-token' });
      expect(result).toBeDefined();
    });

    it('should throw error for invalid payload', async () => {
      await expect(appController.getServices({ token: '' })).rejects.toThrow();
    });
  });
});