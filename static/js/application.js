$(document).ready(function() {
  $('button').on('click', function() {
	  var message = $('<span>You clicked a button</span>');
  	$('.button').append(message);
  });
});
