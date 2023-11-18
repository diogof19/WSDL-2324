<template>
  <div>
    <SearchBar @receivedResponse="handleResponse"/>
  </div>
  <div class="col" id="results">
    <ArtistSearchResult v-for="(artist, index) in searchResults" :key="index" :artist="artist"/>
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
            "searchResults": [],
        }
      },
      created() {
        console.log("SearchResults created");
      },
      methods: {
        handleResponse(response: [], reset : boolean) : void { 
          if (reset) {
            this.searchResults = []
          }       
          this.searchResults.push(...response);
        }
      }
  });

</script>