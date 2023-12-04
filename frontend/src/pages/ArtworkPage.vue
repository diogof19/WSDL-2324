<template>
    <div class="card container mt-5 mb-3">
        <div class="row">
            <div class="col-5">
                <div class="row align-items-center" style="min-height: 20vh;">
                    <div class="col-6 text-center" >
                        <span style="color: grey">Artwork</span>
                        <h2>{{ artwork.name }}</h2>
                    </div>
                    <div class="col-6 text-center">
                        <img v-if="artwork.image != null" :src=artwork.image style="height: 100%; width: 100%;">
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
                    <div v-html="this.artwork.description[key]" v-for="key in this.keys" class="tab-pane fade overflow-y-scroll" :class="{'show active' : this.keys[0] === key}" :id="'nav-contact-'+key" role="tabpanel" :aria-labelledby="'nav-tab-'+key" style="max-height: 40vh;">
                    </div>
                </div>
            </div>
        </div>
        <hr>
    <div class="row">
        <div v-if="this.artwork.year != null || this.artwork.author != null" class="col-6">
            <div class="row ms-1">
                <h5 style="color: #a02905;">
                    Creation
                </h5>
            </div>
            <div v-if="this.artwork.year != null" class="row ms-1">
                <nobr>
                    <b>
                        Year: 
                    </b>
                    {{ this.artwork.year }}
                </nobr>
            </div>
            <div v-if="this.artwork.authorName != null" class="row ms-1">
                <nobr>
                    <b>
                        Author: 
                    </b>
                    {{ this.artwork.authorName }}
                </nobr>
            </div>
        </div>
        <div v-if="this.artwork.museumName.length > 0" class="col-6">
            <div class="row ms-1">
                <h5 style="color: #a02905;">
                    Museum
                </h5>
            </div>
            <div v-for="museum in this.artwork.museumName" class="row ms-1">
                <nobr>
                    {{ museum }}
                </nobr>
            </div>
        </div>
    </div>
    </div>
</template>
  
<script lang="ts">
import { defineComponent } from 'vue';
import axios from 'axios';

import type { Artwork } from '@/@types/artwork';

export default defineComponent({
    name: 'ArtworkPage',
    data() {
        return {
            uris: JSON.parse(this.$route.params.uris),
            artwork: {} as Artwork,
            keys: [] as string[],
        };
    },
    async created() {
        await this.getArtworkInfo();
    },
    methods: {
        async getArtworkInfo(){
            await axios.get('http://localhost:8000/artwork', {
                params: {
                    q: JSON.stringify(this.uris),
                }
            }).then(response => {
                this.handleArtworkData(response.data);
            }).catch(error => {
                console.log(error);
            });
        },
        handleArtworkData(artwork: Artwork) {
            this.artwork = artwork;

            this.keys = Object.keys(this.artwork.description);

            console.log(this.artwork)
        }

    },
});
</script>
  