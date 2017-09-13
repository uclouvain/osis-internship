const carouselId = "#carousel_academic_event"
normalizeCarouselHeight(carouselId);

window.addEventListener("resize", function(){
  normalizeCarouselHeight(carouselId);
});

/*
 * carouselId: String id of a carousel of jumbotrons
 * Normalize the size of the jumbtrons composing the carousel by setting their height
 * equal to the height of the biggest one.
 */
function normalizeCarouselHeight(carouselId){
  var slidesHeight = [];

  $(carouselId +' .jumbotron').css('height', '');

  $(carouselId + '  .item').each(function(){
    slidesHeight.push($(this).height());
  });

  const maxHeight = Math.max.apply(null, slidesHeight);

  $(carouselId +' .jumbotron').each(function()
  {
    $(this).css('height', maxHeight+'px');
  });

}
