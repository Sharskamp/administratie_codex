import { prisma } from '@/lib/prisma';import { NextResponse } from 'next/server';
export async function GET(){return NextResponse.json(await prisma.categorie.findMany({orderBy:{naam:'asc'}}))}
export async function POST(req:Request){const b=await req.json();return NextResponse.json(await prisma.categorie.create({data:{naam:b.naam}}))}
