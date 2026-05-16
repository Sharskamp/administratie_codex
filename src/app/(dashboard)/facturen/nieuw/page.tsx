import { prisma } from '@/lib/prisma';
export default async function NewInvoice(){
 const klanten=await prisma.klant.findMany({orderBy:{naam:'asc'}});
 return <form className='card' action='/api/facturen' method='post'><h1>Nieuwe factuur</h1><select name='klantId' required><option value=''>Selecteer klant</option>{klanten.map(k=><option key={k.id} value={k.id}>{k.naam}</option>)}</select><input name='omschrijving' placeholder='Omschrijving' required/><div style={{display:'grid',gridTemplateColumns:'1fr 1fr 1fr',gap:8}}><input name='aantal' defaultValue='1'/><input name='prijs' defaultValue='75'/><select name='btwPercentage'><option>21</option><option>9</option><option>0</option></select></div><button className='btn'>Factuur opslaan</button></form>
}
