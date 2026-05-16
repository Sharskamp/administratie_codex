import Sidebar from '@/components/layout/sidebar';
export default function Layout({children}:{children:React.ReactNode}){return <div className='container' style={{display:'flex',gap:16}}><Sidebar/><main style={{flex:1}}>{children}</main></div>}
