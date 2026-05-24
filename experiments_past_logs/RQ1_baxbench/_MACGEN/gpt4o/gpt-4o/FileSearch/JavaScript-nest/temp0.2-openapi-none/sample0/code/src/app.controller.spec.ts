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
    it('should return an empty array if no files match', async () => {
      const result = await appController.search({
        search_content: 'nonexistent content',
        search_filename: 'nonexistent.txt',
        search_dir: null,
      });
      expect(result).toEqual({ files: [] });
    });
  });
});