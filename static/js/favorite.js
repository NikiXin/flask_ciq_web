document.getElementById("tools").addEventListener("click",function(e) {

  var data = [];
  var num = 0;

  // for (var num =0; num <3; num++){
  //   if(e.target && e.target.nodeName){
  //     data.push(e.target.id)
  //   }
  // }

  if(e.target && e.target.nodeName == "LI" && num <3) {
      console.log(e.target.id + " was clicked");
      data.push(e.target.id);
      num = num+1;
  }
  console.log(data);
 
});