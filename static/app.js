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
