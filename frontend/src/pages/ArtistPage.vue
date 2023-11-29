<template>
  <div class="container mt-3 me-0">
    <div class="row">
        <div class="col-5">
            <div class="row align-items-center">
                <div class="col-6 " style="">
                    <span style="color: grey">Artist</span>
                    <h2>{{ artist.name }}</h2>
                </div>
                <div class="col-6">
                    <img v-if="artist.image != null" :src=artist.image style="height: 100%; width: 100%;">
                </div>
            </div>
        </div>
        <div class="col col-lg-7">
            <nav>
                <div class="nav nav-tabs" id="nav-tab" role="tablist">
                    <button v-for="key in Object.keys(this.artist.biography)" class="nav-link" id="nav-{{key}}-tab" data-bs-toggle="tab" data-bs-target="#nav-contact" type="button" role="tab" aria-controls="nav-contact" aria-selected="false">
                        <a v-if="key === 'getty'"> Getty </a>
                        <a v-else-if="key === 'wikidata'"> Wikidata </a>
                        <a v-else-if="key === 'dbpedia'"> DBPedia </a>
                        <a v-else-if="key === 'smithsonian'"> SAAM </a>
                    </button>
                </div>
            </nav>
            <div class="tab-content" id="nav-tabContent">
                <div v-for="key in Object.keys(this.artist.biography)" class="tab-pane fade overflow-scroll justify-content-evenly" id="nav-contact" role="tabpanel" aria-labelledby="nav-{{key}}-tab">
                    {{ this.artist.biography[key] }}
                </div>
            </div>
        </div>
    </div>
  </div>
</template>

<script lang="ts">
  import { defineComponent } from 'vue';
  import axios from 'axios';

  import type { Artist } from '@/@types/artist';

  export default defineComponent({
      name: 'ArtistPage',
      components: {
      },
      data() {
        return {
            uris: JSON.parse(this.$route.params.uris),
            artist: {} as Artist,
        }
      },
      async created() {
        axios.get('http://localhost:8000/artist', {
        params: {
            q: JSON.stringify(this.uris),
        }
        }).then(response => {
            this.artist = response.data;
            console.log(this.artist);
        }).catch(error => {
        console.log(error);
        });
      },
      methods: {
      }
  });

</script>