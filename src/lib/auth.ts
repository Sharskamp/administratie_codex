import { prisma } from '@/lib/prisma';
import CredentialsProvider from 'next-auth/providers/credentials';
import { compare } from 'bcryptjs';
import type { NextAuthOptions } from 'next-auth';

export const authOptions: NextAuthOptions = {
  session: { strategy: 'jwt' },
  providers: [CredentialsProvider({
    name: 'Inloggen',
    credentials: { email: { label: 'E-mail', type: 'email' }, password: { label: 'Wachtwoord', type: 'password' } },
    async authorize(credentials) {
      if (!credentials?.email || !credentials?.password) return null;
      const user = await prisma.user.findUnique({ where: { email: credentials.email } });
      if (!user) return null;
      if (!(await compare(credentials.password, user.passwordHash))) return null;
      return { id: user.id, email: user.email, name: user.bedrijfsnaam ?? user.email };
    }
  })],
  pages: { signIn: '/login' },
  secret: process.env.NEXTAUTH_SECRET
};
