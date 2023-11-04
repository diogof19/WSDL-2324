<template>
  <div>
    <SearchBar/>
  </div>
  <div class="col" id="results">
    <ArtistSearchResult v-for="(artist, index) in artists" :key="index" :artist="artist"/>
  </div>
</template>

<script lang="ts">
  import { defineComponent } from 'vue';
  import SearchBar from '../components/SearchBar.vue';
  import ArtistSearchResult from '../components/ArtistSearchResult.vue';

  export default defineComponent({
      name: 'SearchResults',
      components: {
        SearchBar,
        ArtistSearchResult,
      },
      data() {
        return {
            "artists": JSON.parse(this.$route.params.results as string),
        }
      },
      created() {
        console.log("SearchResults created");
      },
      methods: {
        
      }
  });

</script>