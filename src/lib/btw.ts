export type Regel={aantal:number; prijs:number; btwPercentage:number; korting?:number};
export function berekenFactuur(regels:Regel[]){
  const subtotaal=regels.reduce((s,r)=>s+(r.aantal*r.prijs-(r.korting||0)),0);
  const btw=regels.reduce((s,r)=>s+((r.aantal*r.prijs-(r.korting||0))*r.btwPercentage/100),0);
  return {subtotaal,btw,totaal:subtotaal+btw};
}
