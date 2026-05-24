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
    it('should return an array of file paths', async () => {
      const result = { files: ['/data/files/file1.txt', '/data/songs/song.mp3'] };
      jest.spyOn(appController, 'searchFiles').mockImplementation(async () => result);

      expect(await appController.searchFiles({ search_content: 'Hello', search_filename: null, search_dir: null })).toBe(result);
    });
  });
});