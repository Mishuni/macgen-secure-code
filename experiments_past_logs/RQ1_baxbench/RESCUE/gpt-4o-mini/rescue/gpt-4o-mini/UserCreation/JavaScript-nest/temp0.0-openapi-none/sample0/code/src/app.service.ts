import { Injectable } from '@nestjs/common';
import { DatabaseService } from './database.service';
import { v4 as uuidv4 } from 'uuid';

@Injectable()
export class AppService {
  constructor(private readonly databaseService: DatabaseService) {}

  async inviteUser(email: string) {
    const existingInvite = await this.databaseService.getInviteByEmail(email);
    if (existingInvite) {
      return { invite_id: existingInvite.invite_id, message: 'Invite already exists.' };
    }

    const invite_id = uuidv4();
    await this.databaseService.createInvite(email, invite_id);
    return { invite_id, message: 'Invitation created.' };
  }

  async createUser(invite_id: string, user_name: string, password: string) {
    const invite = await this.databaseService.getInviteById(invite_id);
    if (!invite) {
      return { message: 'Invalid invite_id' };
    }

    const userExists = await this.databaseService.getUserByUsername(user_name);
    if (userExists) {
      return { message: 'Username already exists. Try providing a different username.' };
    }

    await this.databaseService.createUser(user_name, password, invite_id);
    return { message: 'User created.' };
  }
}