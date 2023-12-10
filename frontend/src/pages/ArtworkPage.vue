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
                    <a @click="goToArtistPage(this.artwork.authorUri)" style="text-decoration: underline; cursor:pointer;">
                        {{ this.artwork.authorName }}
                    </a>
                </nobr>
            </div>
        </div>
        <div v-if="this.artwork.museumName != null" class="col-6">
            <div v-if="this.artwork.museumName.length > 0">
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
    </div>
    <div v-if="this.dbpediaSameSubject.length > 0" class="card container mt-5 mb-5">
    <div class="row ms-1">
        <h5 style="color: #a02905;">
            Artworks with same subject
        </h5>
    </div>
    <div class="row ps-4 flex-nowrap overflow-auto">
        <div v-for="artwork in this.dbpediaSameSubject" class="card col-2 me-4 mt-3" @click="goToArtworkPage(artwork)" style="cursor:pointer;">
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
    <div v-if="this.provenance.length > 0" class="card container mt-5 mb-5">
        <div class="row ms-1">
            <h5 style="color: #a02905;">
                Provenance
            </h5>
        </div>
        <div v-for="provenance in this.provenance" class="row ms-1">
            <div>
                <b>{{ provenance[1] }} : </b> {{ provenance[0] }}
            </div>
        </div>
    </div>

    <div v-if="this.exhibitedWith.length > 0" class="card container mt-5 mb-5">
        <div class="row ms-1">
            <h5 style="color: #a02905;">
                Exhibited with
            </h5>
        </div>
        <div class="row ps-4 flex-nowrap overflow-auto">
            <div v-for="artwork in this.exhibitedWith" class="card col-2 me-4 mt-3" @click="goToArtworkPage(artwork)" style="cursor:pointer;">
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
            dbpediaSameSubject: [] as Artwork[],
            exhibitedWith: [] as Artwork[],
            provenance: [] as string[][]
        };
    },
    async created() {
        this.getArtworkInfo();
    },
    methods: {
        async getArtworkInfo(){
            axios.get('http://localhost:8000/artwork', {
                params: {
                    q: JSON.stringify(this.uris),
                }
            }).then(response => {
                this.handleArtworkData(response.data);
            }).catch(error => {
                console.log(error);
            });            

            if (this.uris['dbpedia'] != null) {
                axios.get('http://localhost:8000/artwork_with_same_subject', {
                    params: {
                        q: this.uris['dbpedia'],
                    }
                }).then(response => {
                    this.dbpediaSameSubject.push(...response.data);
                }).catch(error => {
                    console.log(error);
                });
            }

            if (this.uris['getty'] != null) {
                axios.get('http://localhost:8000/artwork/exhibited_with', {
                    params: {
                        q: this.uris['getty'],
                    }
                }).then(response => {
                    this.exhibitedWith.push(...response.data);
                }).catch(error => {
                    console.log(error);
                });

                axios.get('http://localhost:8000/artwork/provenance', {
                    params: {
                        q: this.uris['getty'],
                    }
                }).then(response => {
                    console.log(response.data);

                    this.provenance.push(...response.data);
                }).catch(error => {
                    console.log(error);
                });
            }

        },
        handleArtworkData(artwork: Artwork) {
            this.artwork = artwork;

            this.keys = Object.keys(this.artwork.description);
        },
        goToArtworkPage(artwork: Artwork){
            this.$router.push({ name: 'artwork', params: { uris: JSON.stringify(artwork.uris) } });
        },
        goToArtistPage(artistUris: Map<string, string>){
            this.$router.push({ name: 'artist', params: { uris: JSON.stringify(artistUris) } });
        }

    },
});
</script>
  