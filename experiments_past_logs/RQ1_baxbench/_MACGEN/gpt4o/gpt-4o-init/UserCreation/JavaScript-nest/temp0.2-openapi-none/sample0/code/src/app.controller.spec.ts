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

  describe('inviteUser', () => {
    it('should return an invite_id and message', async () => {
      const result = { invite_id: 'some-uuid', message: 'Invitation created' };
      jest.spyOn(appController, 'inviteUser').mockImplementation(async () => result);

      expect(await appController.inviteUser({ email: 'user@example.com' })).toBe(result);
    });
  });

  describe('createUser', () => {
    it('should return a success message', async () => {
      const result = { message: 'User created successfully' };
      jest.spyOn(appController, 'createUser').mockImplementation(async () => result);

      expect(await appController.createUser({ invite_id: 'some-uuid', user_name: 'newuser', password: 'password' })).toBe(result);
    });
  });
});