import { prisma } from '@/lib/prisma';
import { NextResponse } from 'next/server';
export async function GET(){return NextResponse.json(await prisma.klant.findMany())}
export async function POST(req:Request){const f=await req.formData(); await prisma.klant.create({data:{naam:String(f.get('naam')||''),email:String(f.get('email')||''),telefoon:String(f.get('telefoon')||'')}}); return NextResponse.redirect(new URL('/klanten',req.url));}
