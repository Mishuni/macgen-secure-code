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

  describe('registerClick', () => {
    it('should return "Click registered successfully"', async () => {
      expect(await appController.registerClick()).toBe('Click registered successfully');
    });
  });

  describe('getClicks', () => {
    it('should return an array of clicks', async () => {
      const result = await appController.getClicks('2022-01-01', '>');
      expect(Array.isArray(result)).toBe(true);
    });
  });
});