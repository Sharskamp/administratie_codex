import { prisma } from '@/lib/prisma';import { NextResponse } from 'next/server';
export async function GET(){return NextResponse.json(await prisma.factuur.findMany({include:{regels:true,klant:true}}))}
