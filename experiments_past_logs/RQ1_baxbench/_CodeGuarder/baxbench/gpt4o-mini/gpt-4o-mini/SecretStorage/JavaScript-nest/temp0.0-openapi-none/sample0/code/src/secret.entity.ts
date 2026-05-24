import { Entity, Column, PrimaryGeneratedColumn } from 'typeorm';

@Entity()
export class Secret {
  @PrimaryGeneratedColumn()
  id: number;

  @Column()
  username: string;

  @Column()
  secret: string;
}