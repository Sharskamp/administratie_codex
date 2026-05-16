import { prisma } from '@/lib/prisma';import { NextResponse } from 'next/server';
export async function GET(){return NextResponse.json(await prisma.afspraak.findMany({orderBy:{start:'asc'}}))}
export async function POST(req:Request){const b=await req.json();const item=await prisma.afspraak.create({data:{titel:b.titel,start:new Date(b.start),einde:new Date(b.einde),klantNaam:b.klantNaam||null,externId:b.externId||null}});return NextResponse.json(item)}
