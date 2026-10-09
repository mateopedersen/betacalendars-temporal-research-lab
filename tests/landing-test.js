const fs = require('node:fs');
const vm = require('node:vm');
const elements = {};
for (const id of ['date','weekDate','cy','wy','ws','we']) elements[id]={value:'',textContent:'',addEventListener(evt,fn){this.changed=fn}};
elements.date.value = '2027-01-01';
const document={ getElementById: id => elements[id] };
vm.runInNewContext(fs.readFileSync(process.argv[2], 'utf8'),{document,Date,String,Number,Math});
function check(input, expected){elements.date.value=input; elements.date.changed();if(elements.weekDate.textContent!==expected)throw Error(input+': '+elements.weekDate.textContent+' != '+expected); console.log(input+' -> '+elements.weekDate.textContent+' PASS')}
check('2027-01-01','2026-W53-5');
check('2027-01-04','2027-W01-1');
check('2018-12-31','2019-W01-1');
check('2021-01-01','2020-W53-5');
check('2028-02-29','2028-W09-2');
