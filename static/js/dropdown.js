$(document).ready(function () {
  var text;
  $("#ulGenres li a").on("click", function () {
    
  text = $(this).text();
  console.log(text);
  $("#selectButton").html(text + '&nbsp;<span class="caret"></span>');
  });

  $.ajax({
      url: '/engine/',
      type: 'POST',
      data: JSON.stringify({ "name" : text } ),
      contentType: 'application/json;charset=UTF-8',
      cache:false,
      success: function (response) {
          console.log('success')
      },
      error: function(response){
          alert('Error refreshing forum items')
      }
  });
});