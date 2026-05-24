import { Injectable, HttpException, HttpStatus } from '@nestjs/common';
import { DatabaseService } from './database.service';
import { v4 as uuidv4 } from 'uuid';
import * as bcrypt from 'bcrypt';

@Injectable()
export class AppService {
  constructor(private readonly databaseService: DatabaseService) {}

  async inviteUser(email: string) {
    const existingInvite = await this.databaseService.getInviteByEmail(email);
    if (existingInvite) {
      return { invite_id: existingInvite.invite_id, message: 'Invitation already exists.' };
    }

    const invite_id = uuidv4();
    await this.databaseService.createInvite(email, invite_id);
    return { invite_id, message: 'Invitation email sent.' };
  }

  async createUser(invite_id: string, user_name: string, password: string) {
    const invite = await this.databaseService.getInviteById(invite_id);
    if (!invite) {
      throw new HttpException('Invalid invite_id', HttpStatus.UNAUTHORIZED);
    }

    const existingUser = await this.databaseService.getUserByUsername(user_name);
    if (existingUser) {
      throw new HttpException('Username already exists. Try providing a different username.', HttpStatus.BAD_REQUEST);
    }

    const hashedPassword = await bcrypt.hash(password, 10);
    await this.databaseService.createUser(user_name, hashedPassword);
    return { message: 'User created' };
  }
}