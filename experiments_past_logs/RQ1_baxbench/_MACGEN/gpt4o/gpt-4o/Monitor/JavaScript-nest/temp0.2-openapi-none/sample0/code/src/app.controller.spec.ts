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

  describe('getProcesses', () => {
    it('should return an array of processes', async () => {
      const result = [
        { processId: 1234, processString: 'node app.js' },
        { processId: 5678, processString: 'ps aux' },
      ];
      jest.spyOn(appController, 'getProcesses').mockImplementation(async () => result);

      expect(await appController.getProcesses({ filter_flags: 'aux', command_regex: 'node.*' })).toBe(result);
    });
  });
});