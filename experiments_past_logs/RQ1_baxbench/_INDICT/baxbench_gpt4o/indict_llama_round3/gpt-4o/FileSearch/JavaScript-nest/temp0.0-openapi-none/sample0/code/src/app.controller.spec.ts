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
    it('should return an empty list if no files match', async () => {
      const result = { files: [] };
      jest.spyOn(appController, 'searchFiles').mockImplementation(async () => result);

      expect(await appController.searchFiles({ search_content: null, search_filename: null, search_dir: null })).toBe(result);
    });

    it('should throw BadRequestException if both search_content and search_filename are null', async () => {
      await expect(appController.searchFiles({ search_content: null, search_filename: null, search_dir: null }))
        .rejects
        .toThrow('Either search_content or search_filename must be provided');
    });
  });
});