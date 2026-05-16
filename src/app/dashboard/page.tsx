import { prisma } from '@/lib/prisma';
import { euro } from '@/lib/utils';
export default async function Dashboard(){
 const [facturen,inkomen,uitgaven]=await Promise.all([prisma.factuur.findMany({orderBy:{datum:'desc'},take:5}),prisma.inkomen.aggregate({_sum:{bedrag:true}}),prisma.uitgave.aggregate({_sum:{bedrag:true}})]);
 const omzet=inkomen._sum.bedrag||0; const kosten=uitgaven._sum.bedrag||0;
 return <div className='grid'><h1>Dashboard</h1><div className='grid grid-4'><div className='card'><div className='muted'>Omzet</div><h2>{euro(omzet)}</h2></div><div className='card'><div className='muted'>Kosten</div><h2>{euro(kosten)}</h2></div><div className='card'><div className='muted'>Resultaat</div><h2>{euro(omzet-kosten)}</h2></div><div className='card'><div className='muted'>Openstaand</div><h2>{facturen.filter(f=>f.status!=='BETAALD').length}</h2></div></div><div className='card'><h3>Recente facturen</h3><table><thead><tr><th>Nummer</th><th>Status</th><th>Totaal</th></tr></thead><tbody>{facturen.map(f=><tr key={f.id}><td>{f.nummer}</td><td>{f.status}</td><td>{euro(f.totaal)}</td></tr>)}</tbody></table></div></div>
}
