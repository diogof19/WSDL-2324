<template>
  <div class="card container mt-5 mb-3">
    <div class="row">
        <div class="col-5">
            <div class="row align-items-center" style="min-height: 20vh;">
                <div class="col-6 text-center" >
                    <span style="color: grey">Artist</span>
                    <h2>{{ artist.name }}</h2>
                </div>
                <div class="col-6 text-center">
                    <img v-if="artist.image != null" :src=artist.image style="height: 100%; width: 100%;">
                </div>
            </div>
        </div>
        <div v-if="this.keys.length > 0" class="col col-lg-7" >
            <nav>
                <div class="nav nav-tabs" id="nav-tab" role="tablist">
                    <button v-for="key in this.keys" class="nav-link" :class="{'active' : this.keys[0] === key}" :id="'nav-tab-'+key" data-bs-toggle="tab" :data-bs-target="'#nav-contact-'+key" type="button" role="tab" :aria-controls="'nav-contact-'+key" aria-selected="false" style="color: #a02905;">
                        <a v-if="key === 'getty'"> Getty </a>
                        <a v-else-if="key === 'wikidata'"> Wikidata </a>
                        <a v-else-if="key === 'dbpedia'"> DBPedia </a>
                        <a v-else-if="key === 'smithsonian'"> SAAM </a>
                    </button>
                </div>
            </nav>
            <div class="tab-content" id="nav-tabContent">
                <div v-html="this.artist.biography[key]" v-for="key in this.keys" class="tab-pane fade overflow-y-scroll" :class="{'show active' : this.keys[0] === key}" :id="'nav-contact-'+key" role="tabpanel" :aria-labelledby="'nav-tab-'+key" style="max-height: 40vh;">
                </div>
            </div>
        </div>
    </div>
    <hr>
    <div class="row">
        <div v-if="this.artist.birth_date != null || this.artist.birth_place != null" class="col-6">
            <div class="row ms-1">
                <h5 style="color: #a02905;">
                    Birth
                </h5>
            </div>
            <div v-if="this.artist.birth_date != null" class="row ms-1">
                <nobr>
                    <b>
                        Date: 
                    </b>
                    {{ this.artist.birth_date }}
                </nobr>
            </div>
            <div v-if="this.artist.birth_place != null" class="row ms-1">
                <nobr>
                    <b>
                        Place: 
                    </b>
                    {{ this.artist.birth_place }}
                </nobr>
            </div>
        </div>
        <div v-if="this.artist.death_date != null || this.artist.death_place != null" class="col-6">
            <div class="row ms-1">
                <h5 style="color: #a02905;">
                    Death
                </h5>
            </div>
            <div v-if="this.artist.death_date != null" class="row ms-1">
                <nobr>
                    <b>
                        Date: 
                    </b>
                    {{ this.artist.death_date }}
                </nobr>
            </div>
            <div v-if="this.artist_death_place != null" class="row ms-1">
                <nobr>
                    <b>
                        Place: 
                    </b>
                    {{ this.artist.death_place }}
                </nobr>
            </div>
            <div v-if="this.artist.death_manner != null" class="row ms-1">
                <nobr>
                    <b>
                        Manner: 
                    </b>
                    {{ this.artist.death_manner }}
                </nobr>
            </div>
        </div>
    </div>
  </div>
  <div v-if="this.artist.artworks != null && this.artist.artworks.length > 0" class="card container mt-5 mb-5">
    <div class="row ms-1">
        <h5 style="color: #a02905;">
            Artworks
        </h5>
    </div>
    <div class="row ps-4 flex-nowrap overflow-auto">
        <div v-for="artwork in this.artist.artworks" class="card col-2 me-4 mt-3" @click="goToArtworkPage(artwork)" style="cursor:pointer;">
            <div class="row">
                <img :src="artwork.image" style="width: 100%; height: 100%;">
            </div>
            <div class="row text-center mt-2">
                <span style="color: #a02905;">
                    {{ artwork.name }}
                </span>
            </div>
        </div>
    </div>

  </div>
  <div v-if="this.similarArtists.length > 0" class="card container mt-5 mb-5">
    <div class="row ms-1">
        <h5 style="color: #a02905;">
            Artists with the same Artistic Movement
        </h5>
    </div>
    <div class="row ps-4 flex-nowrap overflow-auto">
        <div v-for="artist in this.similarArtists" class="card col-2 me-4 mt-3" @click="goToArtistPage(artist)" style="cursor:pointer;">
            <div class="row ms-2 me-2">
                <img :src="artist.image" style="width: 100%; height: 100%;">
            </div>
            <div class="row text-center mt-2">
                <span style="color: #a02905;">
                    {{ artist.name }}
                </span>
            </div>
        </div>
    </div>

  </div>
</template>

<script lang="ts">
  import { defineComponent } from 'vue';
  import axios from 'axios';

  import type { Artist } from '@/@types/artist';
  import type { Artwork } from '@/@types/artwork'; 

  export default defineComponent({
      name: 'ArtistPage',
      components: {
      },
      data() {
        return {
            uris: JSON.parse(this.$route.params.uris),
            artist: {} as Artist,
            keys: [] as string[],
            similarArtists: [] as Artist[]
        }
      },
      async created() {
        await this.getArtistInfo();
        await this.getArtworks();

        if (this.artist.movements.length > 0)
            await this.getSimilarArtistByMovement();
      },
      methods: {
        async getArtistInfo(){
           await axios.get('http://localhost:8000/artist', {
                params: {
                    q: JSON.stringify(this.uris),
                }
            }).then(response => {
                this.handleArtistData(response.data);
            }).catch(error => {
                console.log(error);
            });
        },
        handleArtistData(artist: Artist) {
            this.artist = artist;

            if (this.artist.death_manner != null){
                this.artist.death_manner = this.artist.death_manner[0].toUpperCase() + this.artist.death_manner.slice(1);
            }

            //This says it's wrong and has errors but it's fully working and the suggestions don't work
            if (this.artist.biography['getty'] != null && this.artist.getty_link != null){
                this.artist.biography['getty'] += "<br><a href='" + this.artist.getty_link + "' target='_blank'>More information on Getty</a>";
            }

            if (this.artist.biography['wikidata'] != null && this.artist.wikipedia_link != null){
                this.artist.biography['wikidata'] += "<br><a href='" + this.artist.wikipedia_link + "' target='_blank'>More information on Wikidata</a>";
            }
            
            this.keys = Object.keys(this.artist.biography);

            if (this.keys.includes('getty')){
                this.keys.splice(this.keys.indexOf('getty'), 1);
                this.keys.unshift('getty');
            }

            if(this.keys.includes('smithsonian')){
                this.keys.splice(this.keys.indexOf('smithsonian'), 1);
                this.keys.unshift('smithsonian');
            }

            console.log(this.artist);
        },
        async getArtworks() {
            await axios.get('http://localhost:8000/artworks_by_artist', {
                params: {
                    q: JSON.stringify(this.uris),
                }
            }).then(response => {
                this.artist.artworks = response.data;
                console.log(this.artist.artworks);
            }).catch(error => {
                console.log(error);
            });
        },
        goToArtworkPage(artwork: Artwork){
            this.$router.push({ name: 'artwork', params: { uris: JSON.stringify(artwork.uris) } });
        },
        async getSimilarArtistByMovement(){
            await axios.get('http://localhost:8000/similar_artists_movement', {
                params: {
                    uris: JSON.stringify(this.artist.uris),
                    movements: JSON.stringify(this.artist.movements)
                }
            }).then(response => {
                this.similarArtists = response.data;
                //console.log(this.similarArtists);
            }).catch(error => {
                console.log(error);
            });
        },
        goToArtistPage(artist: Artist){
            axios.get('http://localhost:8000/artist_search', {
                params: {
                q: artist.name,
                exact: true
                }
            }).then(response => {
                console.log(response.data);
            
                if (response.data.length > 0)
                    this.$router.push({ name: 'artist', params: { uris: JSON.stringify(response.data[0].uris) } });
            }).catch(error => {
                console.log(error);
            });
            
        }
      }
  });

</script>