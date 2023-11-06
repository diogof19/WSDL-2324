<template>
  <div>
    <SearchBar @receivedResponse="handleResponse"/>
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
            "artists": [],
        }
      },
      created() {
        console.log("SearchResults created");
      },
      methods: {
        handleResponse(response: any) : void {        
          this.artists = response
        }
      }
  });

</script>