import { Test, TestingModule } from '@nestjs/testing';
import { AppController } from './app.controller';
import { AppService } from './app.service';
import * as fs from 'fs';
import * as path from 'path';

describe('AppController', () => {
  let appController: AppController;
  let appService: AppService;

  beforeEach(async () => {
    const app: TestingModule = await Test.createTestingModule({
      controllers: [AppController],
      providers: [AppService],
    }).compile();

    appController = app.get<AppController>(AppController);
    appService = app.get<AppService>(AppService);
  });

  describe('convert', () => {
    it('should return concatenated text from zip file', async () => {
      const zipFilePath = path.join(__dirname, '../test/test.zip');
      const zipFile = fs.createReadStream(zipFilePath);

      const result = await appController.convert({ file: zipFile });
      expect(result).toContain('This is file 1');
      expect(result).toContain('This is file 2');
    });
  });
});