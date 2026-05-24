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
    it('should return success message on valid heartbeat', async () => {
      const result = await appController.registerHeartbeat({
        serviceId: 'my-service',
        token: 'pass1',
      });
      expect(result).toEqual({ message: 'Heartbeat registered successfully.' });
    });
  });

  describe('getServicesOverview', () => {
    it('should return an array of services', async () => {
      const result = await appController.getServicesOverview({ token: 'pass1' });
      expect(result).toBeInstanceOf(Array);
    });
  });
});