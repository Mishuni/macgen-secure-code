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

  it('should compile TypeScript code', async () => {
    const result = await appController.compile({ fileName: 'test.ts', fileContent: 'let x = 2;' });
    expect(result).toEqual({ hasError: false, compilerError: null });
  });

  it('should return error for invalid TypeScript code', async () => {
    const result = await appController.compile({ fileName: 'test.ts', fileContent: 'let x = y;' });
    expect(result.hasError).toBe(true);
    expect(result.compilerError).toBeDefined();
  });
});