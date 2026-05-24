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

  describe('compile', () => {
    it('should return compilation result', async () => {
      const result = { hasError: false, compilerError: null };
      jest.spyOn(appController['appService'], 'compileCode').mockResolvedValue(result);
      expect(await appController.compile({ fileName: 'main.ts', fileContent: 'let x = 2 * 15;' })).toBe(result);
    });
  });
});