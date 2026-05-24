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

  describe('calculate', () => {
    it('should return the result of the expression', () => {
      const result = appController.calculate({ expression: '1 + 2 * 3' });
      expect(result).toEqual({ result: '7' });
    });

    it('should throw an error for invalid expression', () => {
      expect(() => appController.calculate({ expression: 'invalid' })).toThrow();
    });
  });
});