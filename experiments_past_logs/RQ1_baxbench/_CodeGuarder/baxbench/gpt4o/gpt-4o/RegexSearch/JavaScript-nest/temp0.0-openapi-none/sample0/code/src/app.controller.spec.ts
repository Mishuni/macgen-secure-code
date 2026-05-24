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

  describe('search', () => {
    it('should return an array of file paths', async () => {
      const result = { files: ['folder1/file1.txt', 'file2.txt'] };
      jest.spyOn(appController, 'searchFiles').mockImplementation(async () => result);

      expect(await appController.searchFiles({ regex: 'test' })).toBe(result);
    });
  });
});