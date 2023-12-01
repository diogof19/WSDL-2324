<template>
    <div class="card mt-3 mb-3" style="margin-left: 10%; margin-right: 10%;" >
        <div class="container">
            <div class="row">
                <div class="col-xl-2" style="max-height: 30vh;">
                    <img v-if="result.image != null" :src=result.image style="height: 100%; width: 100%;">
                </div>
                <div class="col-xl-8">
                    <span v-if="isArtist" class="badge badge-mine">Artist</span>
                    <span v-else-if="isArtwork" class="badge badge-mine">Artwork</span>
                    <h4>{{result.name}}</h4>
                </div>
                <div class="col-xl-2">
                    <button v-if="isArtist" class="btn btn-mine" type="button" @click="goToArtistPage">Go to Artist</button>
                    <button v-else-if="isArtwork" class="btn btn-mine" type="button" @click="goToArtworkPage">Go to Artwork</button>
                </div>
            </div>
        </div>
    </div>
</template>

<script lang="ts">
import { defineComponent} from 'vue';

import type { Artist } from '@/@types/artist';
import type { Artwork } from '@/@types/artwork';

export default defineComponent({
    name: "SearchResult",
    props: {
        result: {
            type: Object as () => Artist | Artwork,
            required: true
        }
    },
    components: {},
    computed: {
        artist(): Artist {
            return this.result as Artist;
        },
        artwork(): Artwork {
            return this.result as Artwork;
        },
        isArtwork(): boolean {
            return this.result.type == "artwork";
        },
        isArtist(): boolean {
            return this.result.type == "artist";
        }
    },
    data() {
        return {
        }
    },
    created() {
    },
    methods: {
        goToArtistPage() {
            this.$router.push({name: 'artist', params: {uris: JSON.stringify(this.artist.uris)}});
            //this.goToRoot();
        },
        goToArtworkPage() {
            //this.$router.push({name: 'ArtworkPage', params: {id: this.artwork.id}});
            this.goToRoot();
        },
        goToRoot() {
            this.$router.push({name: 'home'});
        }
    }
})
</script>