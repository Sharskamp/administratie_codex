export function whatsappLink(phone:string,text:string){
  const cleaned = phone.replace(/\D/g,'');
  return `https://wa.me/${cleaned}?text=${encodeURIComponent(text)}`;
}
