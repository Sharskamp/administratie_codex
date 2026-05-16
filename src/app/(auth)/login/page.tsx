'use client';
import { signIn } from 'next-auth/react';
import { useState } from 'react';

export default function LoginPage() {
  const [error, setError] = useState('');
  async function onSubmit(formData: FormData) {
    const email = String(formData.get('email') || '');
    const password = String(formData.get('password') || '');
    const res = await signIn('credentials', { email, password, redirect: true, callbackUrl: '/dashboard' });
    if (res?.error) setError('Inloggen mislukt');
  }
  return <div className='container'><form className='card' action={onSubmit} style={{maxWidth:420, margin:'80px auto'}}><h1>Inloggen</h1><input name='email' placeholder='E-mail' type='email' required/><input name='password' placeholder='Wachtwoord' type='password' required/>{error && <p>{error}</p>}<button className='btn'>Login</button></form></div>;
}
