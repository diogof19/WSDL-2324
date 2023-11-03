<script lang="ts">
  import { defineComponent } from 'vue';
  import SearchBar from '../components/SearchBar.vue';
  import ArtistSearchResult from '../components/ArtistSearchResult.vue';

  export default defineComponent({
      name: 'SearchResults',
      data() {
        return {
            "artists": this.$route.params.data
        }
      },
      created() {
        console.log("SearchResults created");
        console.log(this.artists);
      },
      methods: {
        
      }
  });

</script>

<template>
  <a>DASDADASDASDASD</a>  
  <SearchBar/>
  <a>DASDADASDASDASD</a>
  <div class="col" id="results">
    <ArtistSearchResult v-for="(artist, index) in artists" :key="index" :artist="artist"/>
  </div>
</template>