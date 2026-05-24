import { Injectable } from '@nestjs/common';
import { v4 as uuidv4 } from 'uuid';
import * as bcrypt from 'bcrypt';
import { DatabaseService } from './database.service';
import { CreateUserDto } from './dto';

@Injectable()
export class AppService {
  constructor(private readonly databaseService: DatabaseService) {}

  async inviteUser(email: string): Promise<{ invite_id: string; message: string }> {
    const existingInvite = await this.databaseService.getInviteByEmail(email);
    if (existingInvite) {
      return { invite_id: existingInvite.invite_id, message: 'Invite already exists' };
    }

    const invite_id = uuidv4();
    await this.databaseService.createInvite(email, invite_id);
    return { invite_id, message: 'Invitation created successfully' };
  }

  async createUser(createUserDto: CreateUserDto): Promise<{ message: string }> {
    const invite = await this.databaseService.getInviteById(createUserDto.invite_id);
    if (!invite) {
      throw new Error('Invalid invite_id');
    }

    const existingUser = await this.databaseService.getUserByUsername(createUserDto.user_name);
    if (existingUser) {
      throw new Error('Username already exists. Try providing different username.');
    }

    const hashedPassword = await bcrypt.hash(createUserDto.password, 10);
    await this.databaseService.createUser(createUserDto.user_name, hashedPassword);
    return { message: 'User created successfully' };
  }
}