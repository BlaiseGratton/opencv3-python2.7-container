Vue.use(VueGoogleMaps, {
  load: {
    key: "AIzaSyBEueVyUF6ZWIfBu54xiBhWSFQdO_k7Nfg"
  }
})

const map = new Vue({
  el: '#app',
  data: {
    message: 'This map',
    cameras: [],
    infoWindows: [],
    zoom: 12,
    center: {
      lat: 36.1627,
      lng: -86.7816
    },

  },
  mounted() {
    axios.get('/api/cameras/')
      .then(response => this.cameras = response.data,
            error => console.error(error))
      .catch(error => console.error(error))
  },
  methods: {
    openInfoWindow: function (camera) {
      const streamUrl = encodeURIComponent(camera.rtspVideoUrl)

      this.infoWindows.push({
        options: {
          content: `
            <section class="info-window">
              <h2>${camera.description}</h2>
              <img @error="alert" src="/api/stream?streamUrl=${streamUrl}">
            </section>
          `
        },
        position: camera.location.coordinates[0]
      })
    },
    alert: function (event, a, b) {
      debugger
    }
  }
})

const footer = new Vue({
  el: '#footer'
})

$('body').on('click', 'img', function(e) {
  explode(e.pageX, e.pageY);
})

// explosion construction
function explode(x, y) {
  var particles = 15,
    // explosion container and its reference to be able to delete it on animation end
    explosion = $('<div class="explosion"></div>');

  // put the explosion container into the body to be able to get it's size
  $('body').append(explosion);

  // position the container to be centered on click
  explosion.css('left', x - explosion.width() / 2);
  explosion.css('top', y - explosion.height() / 2);

  for (var i = 0; i < particles; i++) {
    // positioning x,y of the particle on the circle (little randomized radius)
    var x = (explosion.width() / 2) + rand(80, 150) * Math.cos(2 * Math.PI * i / rand(particles - 10, particles + 10)),
      y = (explosion.height() / 2) + rand(80, 150) * Math.sin(2 * Math.PI * i / rand(particles - 10, particles + 10)),
      color = rand(0, 255) + ', ' + rand(0, 255) + ', ' + rand(0, 255), // randomize the color rgb
        // particle element creation (could be anything other than div)
      elm = $('<div class="particle" style="' +
        'background-color: rgb(' + color + ') ;' +
        'top: ' + y + 'px; ' +
        'left: ' + x + 'px"></div>');

    if (i == 0) { // no need to add the listener on all generated elements
      // css3 animation end detection
      elm.one('webkitAnimationEnd oanimationend msAnimationEnd animationend', function(e) {
        explosion.remove(); // remove this explosion container when animation ended
      });
    }
    explosion.append(elm);
  }
}

// get random number between min and max value
function rand(min, max) {
  return Math.floor(Math.random() * (max + 1)) + min;
}
