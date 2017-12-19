const Sagiri = require('sagiri');
const handler = new Sagiri('TOKEN', {
  getRating: true
});

var url = "" + process.argv.slice(2);
handler.getSauce(url).then(function(v){
  v = JSON.stringify(v);
  console.log(v);
}).catch(function() {
  console.log("");
});
