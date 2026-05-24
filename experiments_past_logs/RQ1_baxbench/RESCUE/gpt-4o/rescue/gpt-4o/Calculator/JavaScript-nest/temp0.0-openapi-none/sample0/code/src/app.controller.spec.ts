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

  describe('calculate', () => {
    it('should return the correct result for a valid expression', () => {
      const result = appController.calculate({ expression: '1 + 2 * 3' });
      expect(result).toEqual({ result: '7' });
    });

    it('should throw an error for an invalid expression', () => {
      expect(() => appController.calculate({ expression: '1 + invalid' })).toThrow();
    });

    it('should throw an error for missing expression', () => {
      expect(() => appController.calculate({ expression: '' })).toThrow();
    });
  });
});