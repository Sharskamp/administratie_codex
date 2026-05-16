import { prisma } from '@/lib/prisma';import { NextResponse } from 'next/server';
export async function GET(){return NextResponse.json(await prisma.uitgave.findMany({include:{categorie:true}}))}
export async function POST(req:Request){const b=await req.json();return NextResponse.json(await prisma.uitgave.create({data:{datum:new Date(b.datum),bedrag:Number(b.bedrag),btw:Number(b.btw||0),leverancier:b.leverancier,bonPad:b.bonPad,categorieId:b.categorieId||null}}))}
