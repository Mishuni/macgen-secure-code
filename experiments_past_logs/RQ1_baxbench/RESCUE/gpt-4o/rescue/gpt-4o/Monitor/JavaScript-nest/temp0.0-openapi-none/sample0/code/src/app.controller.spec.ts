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

  describe('root', () => {
    it('should return an array of processes', async () => {
      const result = [
        { processId: 1234, processString: 'node server.js' },
        { processId: 5678, processString: 'ps aux' },
      ];
      jest.spyOn(appController, 'getProcesses').mockResolvedValue(result);

      expect(
        await appController.getProcesses({
          filter_flags: 'aux',
          command_regex: 'node.*',
        }),
      ).toEqual(result);
    });
  });
});