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
    it('should throw an error if no search parameters are provided', async () => {
      await expect(
        appController.searchFiles(null, null, null),
      ).rejects.toThrowError();
    });
  });
});