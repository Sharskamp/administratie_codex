import { prisma } from '@/lib/prisma';import { NextResponse } from 'next/server';
export async function GET(){return NextResponse.json(await prisma.inkomen.findMany({include:{factuur:true}}))}
export async function POST(req:Request){const b=await req.json();return NextResponse.json(await prisma.inkomen.create({data:{datum:new Date(b.datum),bedrag:Number(b.bedrag),omschrijving:b.omschrijving,factuurId:b.factuurId||null}}))}
