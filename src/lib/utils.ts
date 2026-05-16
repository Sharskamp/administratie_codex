import { format } from 'date-fns';
export const euro = (n:number)=> new Intl.NumberFormat('nl-NL',{style:'currency',currency:'EUR'}).format(n);
export const d = (value:Date|string)=> format(new Date(value),'dd-MM-yyyy');
