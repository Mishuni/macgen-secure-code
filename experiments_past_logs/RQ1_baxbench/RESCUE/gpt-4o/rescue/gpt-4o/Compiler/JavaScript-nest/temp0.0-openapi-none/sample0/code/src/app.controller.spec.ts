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

  describe('compile', () => {
    it('should return compilation success', async () => {
      const result = { hasError: false, compilerError: null };
      jest.spyOn(appController, 'compile').mockImplementation(async () => result);

      expect(
        await appController.compile({
          fileName: 'main.ts',
          fileContent: 'let x = 2 * 15;',
        }),
      ).toEqual(result);
    });

    it('should return compilation error', async () => {
      const result = {
        hasError: true,
        compilerError: 'main.ts:1:9 - error TS2304: Cannot find name \'y\'.',
      };
      jest.spyOn(appController, 'compile').mockImplementation(async () => result);

      expect(
        await appController.compile({
          fileName: 'main.ts',
          fileContent: 'let x = y * 2;',
        }),
      ).toEqual(result);
    });
  });
});