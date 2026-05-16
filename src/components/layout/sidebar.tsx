import Link from 'next/link';
const items=[['Dashboard','/dashboard'],['Klanten','/dashboard/klanten'],['Facturen','/dashboard/facturen'],['Agenda','/dashboard/agenda'],['Inkomen','/dashboard/inkomen'],['Uitgaven','/dashboard/uitgaven'],['Rapporten','/dashboard/rapporten'],['Instellingen','/dashboard/instellingen']];
export default function Sidebar(){return <aside className='card' style={{width:240,height:'calc(100vh - 48px)'}}><h3>ZZP Pro</h3><div className='grid'>{items.map(([t,h])=><Link key={h} href={h} className='muted'>{t}</Link>)}</div></aside>}
