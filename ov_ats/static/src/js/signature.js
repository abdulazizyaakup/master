$(document).ready(function(){
  $('.signature-panel').jSignature();
  
  $('.clear-button').on('click', function(e) {
    e.preventDefault();
    $('.signature-panel').jSignature("reset");
  });
  
  $('.submit-button').on('click', function(e) {
    e.preventDefault();
    if(isValidSignature()) {
      $('.submit-button').removeClass('btn--disabled');
    } else {
      $('.submit-button').addClass('btn--disabled');
    }
  });
  
  $(".signature-panel").bind("change", function(event){
    if(isValidSignature()) {
      $('.submit-button').removeClass('btn--disabled');
    } else {
      $('.submit-button').addClass('btn--disabled');
    }
  });
  
  $('.cancel-link').on('click', function(e) {
    e.preventDefault();
  });
  
  $('.skip-link').on('click', function(e) {
    e.preventDefault();
  });
});

function isValidSignature() {
  var canvas = $('.signature-panel canvas')[0];
    var ctx = canvas.getContext('2d');
    var imageData = ctx.getImageData(0,0,canvas.width,canvas.height);
    var filledCount = 0;
    var totalCount = 0;
    for(var i = 0; i < imageData.data.length; i++) {
      if(imageData.data[i] > 0) {
        filledCount++;
      } 
      totalCount++;
    }
    var percentRequired = 0;
    if(window.innerWidth < 330) {
      percentRequired = 3;
    } else if (window.innerWidth > 330 && window.innerWidth < 400) {
      percentRequired = 2;
    } else {
      percentRequired = 0.95;
    }
    console.log(`total filled: ${filledCount / totalCount * 100} / ${percentRequired}`);
    return ((filledCount / totalCount) * 100) > percentRequired;
}