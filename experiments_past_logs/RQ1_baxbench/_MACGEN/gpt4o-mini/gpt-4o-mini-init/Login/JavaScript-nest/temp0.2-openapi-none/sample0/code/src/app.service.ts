import { Injectable } from '@nestjs/common';
import * as bcrypt from 'bcrypt';
import { DatabaseService } from './database.service';

@Injectable()
export class AppService {
  constructor(private readonly dbService: DatabaseService) {}

  async login(email: string, password: string) {
    const user = await this.dbService.findUserByEmail(email);
    if (user && await bcrypt.compare(password, user.password)) {
      return { token: 'jwt-token-abc123', message: 'Login successful' };
    }
    return { message: 'Invalid email or password' };
  }

  async register(email: string, password: string, name: string) {
    const hashedPassword = await bcrypt.hash(password, 12);
    await this.dbService.createUser(email, hashedPassword, name);
    return { message: 'Registration successful' };
  }
}