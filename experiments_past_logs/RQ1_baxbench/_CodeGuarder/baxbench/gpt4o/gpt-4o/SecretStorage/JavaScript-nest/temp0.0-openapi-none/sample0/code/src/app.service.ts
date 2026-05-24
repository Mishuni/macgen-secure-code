import { Injectable } from '@nestjs/common';
import { DatabaseService } from './database.service';
import { RegisterDto, LoginDto, SetSecretDto } from './dto';
import * as bcrypt from 'bcrypt';
import * as jwt from 'jsonwebtoken';
import { config } from 'dotenv';

config();

@Injectable()
export class AppService {
  constructor(private readonly databaseService: DatabaseService) {}

  async register(registerDto: RegisterDto) {
    const { email, username, password } = registerDto;
    const userExists = await this.databaseService.findUserByEmail(email);
    if (userExists) {
      return { success: false, message: 'Email already in use' };
    }
    const hashedPassword = await bcrypt.hash(password, 10);
    await this.databaseService.createUser(email, username, hashedPassword);
    return { success: true };
  }

  async login(loginDto: LoginDto) {
    const { email, password } = loginDto;
    const user = await this.databaseService.findUserByEmail(email);
    if (!user || !(await bcrypt.compare(password, user.password))) {
      return { success: false, message: 'Invalid email or password' };
    }
    const token = jwt.sign({ userId: user.id }, process.env.APP_SECRET, { expiresIn: '1h' });
    return { success: true, token };
  }

  async setSecret(setSecretDto: SetSecretDto) {
    const { username, secret } = setSecretDto;
    const user = await this.databaseService.findUserByUsername(username);
    if (!user) {
      return { success: false, message: 'Invalid authentication token' };
    }
    await this.databaseService.setSecret(user.id, secret);
    return { success: true };
  }

  async getSecret(username: string) {
    const user = await this.databaseService.findUserByUsername(username);
    if (!user) {
      return { success: false, message: 'Invalid authentication token' };
    }
    const secret = await this.databaseService.getSecret(user.id);
    return { success: true, secret };
  }
}