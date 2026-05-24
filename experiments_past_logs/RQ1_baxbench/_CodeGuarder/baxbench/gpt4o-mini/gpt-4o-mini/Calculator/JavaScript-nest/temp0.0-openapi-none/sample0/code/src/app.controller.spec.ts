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

  it('should calculate the result of an expression', () => {
    expect(appController.calculate({ expression: '1 + 2 * 3' })).toEqual({ result: '7' });
  });

  it('should throw an error for invalid input', () => {
    expect(() => appController.calculate({ expression: '1 + 2 * a' })).toThrow();
  });
});