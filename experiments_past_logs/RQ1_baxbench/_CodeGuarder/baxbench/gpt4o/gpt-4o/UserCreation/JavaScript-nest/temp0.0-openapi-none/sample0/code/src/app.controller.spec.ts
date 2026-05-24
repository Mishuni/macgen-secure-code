import { Test, TestingModule } from '@nestjs/testing';
import { AppController } from './app.controller';
import { AppService } from './app.service';
import { DatabaseService } from './database.service';

describe('AppController', () => {
  let appController: AppController;

  beforeEach(async () => {
    const app: TestingModule = await Test.createTestingModule({
      controllers: [AppController],
      providers: [AppService, DatabaseService],
    }).compile();

    appController = app.get<AppController>(AppController);
  });

  describe('inviteUser', () => {
    it('should return an invite_id and message', async () => {
      const result = await appController.inviteUser({ email: 'test@example.com' });
      expect(result).toHaveProperty('invite_id');
      expect(result).toHaveProperty('message', 'Invitation created successfully');
    });
  });

  describe('createUser', () => {
    it('should return a success message', async () => {
      const result = await appController.createUser({
        invite_id: 'some-valid-invite-id',
        user_name: 'newuser',
        password: 'securepassword',
      });
      expect(result).toHaveProperty('message', 'User created successfully');
    });
  });
});