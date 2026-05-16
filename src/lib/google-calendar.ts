import { google } from 'googleapis';
export function googleClient(){
  return new google.auth.OAuth2(process.env.GOOGLE_CLIENT_ID, process.env.GOOGLE_CLIENT_SECRET, `${process.env.NEXTAUTH_URL}/api/agenda/callback`);
}
