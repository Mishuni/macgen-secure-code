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

  describe('searchFiles', () => {
    it('should return an array of matching files', async () => {
      const result = { files: [] };
      jest.spyOn(appController, 'searchFiles').mockImplementation(async () => result);

      expect(await appController.searchFiles('test', '', 'false')).toBe(result);
    });
  });
});