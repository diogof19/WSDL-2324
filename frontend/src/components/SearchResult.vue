<template>
    <div class="card">
        <div class="container">
            <div class="row">
                <div class="col-md-4 col-xl-2">
                    <img v-if="isArtist && artist.thumbnail != null" :src=artist.thumbnail style="height: 100%; width: 100%;">
                    <img v-else-if="isArtwork && artwork.image != null" :src=artwork.image style="height: 100%; width: 100%;">
                </div>
                <div class="col-md-4 col-xl-8">
                    <h4>{{result.name}}</h4>
                    <h6 class="text-muted mb-2">URI</h6>
                </div>
                <div class="col-md-4 col-xl-2">
                    <button v-if="isArtist" class="btn btn-primary" type="button" @click="goToArtistPage">Go to Artist</button>
                    <button v-else-if="isArtwork" class="btn btn-primary" type="button" @click="goToArtworkPage">Go to Artwork</button>
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
        type(): string {
            if (this.artist != null) {
                return "artist";
            } else if (this.artwork != null) {
                return "artwork";
            } else {
                return "unknown";
            }
        },
        isArtwork(): boolean {
            return this.type == "artwork";
        },
        isArtist(): boolean {
            return this.type == "artist";
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
            //this.$router.push({name: 'ArtistPage', params: {id: this.artist.id}});
            this.goToRoot();
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