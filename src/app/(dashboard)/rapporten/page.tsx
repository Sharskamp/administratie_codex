import { prisma } from '@/lib/prisma';import { euro } from '@/lib/utils';
export default async function P(){
 const facturen=await prisma.factuur.findMany({include:{regels:true}});
 const omzet=facturen.reduce((s,f)=>s+f.subtotaal,0); const btw21=facturen.flatMap(f=>f.regels).filter(r=>r.btwPercentage===21).reduce((s,r)=>s+(r.aantal*r.prijs*0.21),0);
 const btw9=facturen.flatMap(f=>f.regels).filter(r=>r.btwPercentage===9).reduce((s,r)=>s+(r.aantal*r.prijs*0.09),0);
 const btw0=0;
 return <div className='card'><h1>BTW Overzicht (kwartaal)</h1><p>Omzet: {euro(omzet)}</p><p>BTW 21%: {euro(btw21)}</p><p>BTW 9%: {euro(btw9)}</p><p>BTW 0%: {euro(btw0)}</p></div>
}
