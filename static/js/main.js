// animate function
$.fn.extend({
  animateCss: function(animationName, callback) {
    var animationEnd = (function(el) {
      var animations = {
        animation: 'animationend',
        OAnimation: 'oAnimationEnd',
        MozAnimation: 'mozAnimationEnd',
        WebkitAnimation: 'webkitAnimationEnd',
      };

      for (var t in animations) {
        if (el.style[t] !== undefined) {
          return animations[t];
        }
      }
    })(document.createElement('div'));

    this.addClass('animated ' + animationName).one(animationEnd, function() {
      $(this).removeClass('animated ' + animationName);

      if (typeof callback === 'function') callback();
    });

    return this;
  },
});

$(document).ready(() => {
  // Open modal
  $('.more').on('click', (e) => {
    e.preventDefault();

    $('.modal').fadeIn();
    $('.modal-container').animateCss('bounceInDown');
  });

  // Close modal
  $('.close-modal').on('click', (e) => {
    e.preventDefault()

    $('.modal-container').animateCss('bounceOutUp', function() {
    // Do something after animation
      $('.modal').css('display', 'none');
    });
  });

  // Click outside modal
  $(document).click(function (e) {
    if ($(e.target).is('.modal')) {
      $('.modal-container').animateCss('bounceOutUp', function() {
        // Do something after animation
        $('.modal').css('display', 'none');
      });
    }
  });
});




// Make a request for a user with a given ID
// axios.get('/user?ID=12345')
//   .then(function (response) {
//     // handle success
//     console.log(response);
//   })
//   .catch(function (error) {
//     // handle error
//     console.log(error);
//   })
//   .finally(function () {
//     // always executed
//   });
