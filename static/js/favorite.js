var data = [];
var num = 0;

document.getElementById("tools").addEventListener("click",function(e) {

  if(e.target && e.target.nodeName == "LI" && num <3) {
      console.log(e.target.id + " was clicked");
      data.push(e.target.id);
      num = num+1;
  }
  console.log(num);
  console.log(data);
 
  if (num ==3){
    $.ajax({
      type : "POST",
      url : "/engine/<username>",
      contentType : "application/json",
      data : JSON.stringify(data),
      dataType: "json",
      async: false,
      success: function(data) {
          alert("success: " + data);
      }
  });
  }
});