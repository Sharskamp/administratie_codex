import { NextResponse } from 'next/server';
export async function POST(req:Request){const {csv}=await req.json();const lines=String(csv||'').trim().split('\n');const rows=lines.slice(1).map(l=>l.split(';'));return NextResponse.json({count:rows.length,rows});}
