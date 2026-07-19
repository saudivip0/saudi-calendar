export default {
  async fetch(request) {
    const ICS="https://raw.githubusercontent.com/saudivip0/saudi-calendar/main/saudi-calendar.ics";
    const r=await fetch(ICS);
    return new Response(await r.text(),{
      headers:{
        "Content-Type":"text/calendar; charset=utf-8",
        "Access-Control-Allow-Origin":"*"
      }
    });
  }
}
