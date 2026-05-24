import { Injectable } from '@nestjs/common';
import { InjectRepository } from '@nestjs/typeorm';
import { Repository } from 'typeorm';
import { User } from './user.entity';
import { Secret } from './secret.entity';
import { UserDto, SecretDto } from './dto';
import * as bcrypt from 'bcrypt';
import * as jwt from 'jsonwebtoken';

@Injectable()
export class AppService {
  constructor(
    @InjectRepository(User)
    private userRepository: Repository<User>,
    @InjectRepository(Secret)
    private secretRepository: Repository<Secret>,
  ) {}

  async register(userDto: UserDto) {
    const existingUser = await this.userRepository.findOne({ where: { email: userDto.email } });
    if (existingUser) {
      throw new Error('Email already in use or invalid data');
    }
    const hashedPassword = await bcrypt.hash(userDto.password, 10);
    const user = this.userRepository.create({ ...userDto, password: hashedPassword });
    await this.userRepository.save(user);
    return { message: 'Registration successful' };
  }

  async login(userDto: UserDto) {
    const user = await this.userRepository.findOne({ where: { email: userDto.email } });
    if (!user || !(await bcrypt.compare(userDto.password, user.password))) {
      throw new Error('Invalid email or password');
    }
    const token = jwt.sign({ id: user.id }, process.env.APP_SECRET, { expiresIn: '1h' });
    return { token, message: 'Login successful' };
  }

  async setSecret(secretDto: SecretDto) {
    const secret = this.secretRepository.create(secretDto);
    await this.secretRepository.save(secret);
    return { message: 'Secret has been set successfully' };
  }

  async getSecret(username: string) {
    const secret = await this.secretRepository.findOne({ where: { username } });
    if (!secret) {
      throw new Error('Secret not found');
    }
    return { secret: secret.secret };
  }
}