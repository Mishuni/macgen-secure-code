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

  describe('registerHeartbeat', () => {
    it('should return success message on valid input', async () => {
      jest.spyOn(appService, 'registerHeartbeat').mockImplementation(async () => {});
      const result = await appController.registerHeartbeat({ serviceId: 'test-service', token: 'test-token' });
      expect(result).toEqual({ message: 'Heartbeat registered successfully.' });
    });

    it('should throw error on invalid input', async () => {
      await expect(appController.registerHeartbeat({ serviceId: '', token: '' })).rejects.toThrow();
    });
  });

  describe('getServicesOverview', () => {
    it('should return services overview on valid token', async () => {
      const mockServices = [{ serviceId: 'test-service', lastNotification: new Date().toISOString() }];
      jest.spyOn(appService, 'getServicesOverview').mockImplementation(async () => mockServices);
      const result = await appController.getServicesOverview({ token: 'test-token' });
      expect(result).toEqual(mockServices);
    });

    it('should throw error on invalid token', async () => {
      await expect(appController.getServicesOverview({ token: '' })).rejects.toThrow();
    });
  });
});