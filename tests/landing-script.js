
    (function () {
      const input = document.getElementById('date');
      const $ = (id) => document.getElementById(id);
      const fmt = (d) => String(d.getUTCFullYear()).padStart(4,'0')+'-'+String(d.getUTCMonth()+1).padStart(2,'0')+'-'+String(d.getUTCDate()).padStart(2,'0');
      function calculate(s) {
        const match = /^(\d{4})-(\d{2})-(\d{2})$/.exec(s||'');
        if (!match) return;
        const [y,m,day] = match.slice(1).map(Number);
        const d = new Date(0);
        d.setUTCHours(12,0,0,0);
        d.setUTCFullYear(y,m-1,day);
        if (fmt(d) !== s) return;
        const dow = d.getUTCDay() || 7;
        const monday = new Date(d);
        monday.setUTCDate(d.getUTCDate()-(dow-1));
        const thursday = new Date(d);
        thursday.setUTCDate(d.getUTCDate()+(4-dow));
        const weekYear = thursday.getUTCFullYear();
        const jan4 = new Date(d);
        jan4.setUTCFullYear(weekYear,0,4);
        const jan4Dow=jan4.getUTCDay() || 7;
        const firstMonday = new Date(jan4);
        firstMonday.setUTCDate(jan4.getUTCDate()-(jan4Dow-1));
        const week = Math.round((monday-firstMonday)/604800000)+1;
        const sunday = new Date(monday);
        sunday.setUTCDate(monday.getUTCDate()+6);
        $('weekDate').textContent = String(weekYear).padStart(4,'0')+'-W'+String(week).padStart(2,'0')+'-'+dow;
        $('cy').textContent = String(y);
        $('wy').textContent = String(weekYear);
        $('ws').textContent=fmt(monday);
        $('we').textContent=fmt(sunday);
      }
      input.addEventListener('change',()=>calculate(input.value));
      calculate(input.value);
    }());
  