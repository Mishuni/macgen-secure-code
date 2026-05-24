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

  it('should return compilation result', async () => {
    const result = await appController.compile({
      fileName: 'main.ts',
      fileContent: 'let x = 2 * 15;',
    });
    expect(result).toHaveProperty('hasError');
    expect(result).toHaveProperty('compilerError');
  });
});