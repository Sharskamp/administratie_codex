import { prisma } from '@/lib/prisma';import { NextResponse } from 'next/server';
export async function GET(){const overdue=await prisma.factuur.findMany({where:{status:{in:['CONCEPT','VERZONDEN']},vervalDatum:{lt:new Date()}}});return NextResponse.json({count:overdue.length,overdue});}
