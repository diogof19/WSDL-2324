<template>
    <div class="card">
        <div class="container">
            <div class="row">
                <div class="col-md-4 col-xl-2">
                    <img v-if="artist.thumbnail != null" :src=artist.thumbnail style="height: 100%; width: 100%;">
                </div>
                <div class="col-md-4 col-xl-8">
                    <h4>{{artist.name}}</h4>
                    <h6 class="text-muted mb-2">URI</h6>
                </div>
                <div class="col-md-4 col-xl-2">
                    <button class="btn btn-primary" type="button">Go to Artist</button>
                </div>
            </div>
        </div>
    </div>
</template>

<script lang="ts">
import { defineComponent} from 'vue';


export default defineComponent({
    name: "ArtistSearchResult",
    props: ['artist'],
    components: {},
    data() {
        return {
        }
    },
    created() {
    },
    methods: {
        goToArtistPage() {
            //this.$router.push({name: 'ArtistPage', params: {id: this.artist.id}});
        }
    }
})
</script>