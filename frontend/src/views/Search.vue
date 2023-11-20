<template>
  <div>
    <SearchBar @receivedResponse="handleResponse"/>
  </div>
  <div class="col" id="results">
    <SearchResult v-for="(result, index) in searchResults" :key="index" :result="result"/>
  </div>
</template>

<script lang="ts">
  import { defineComponent } from 'vue';
  import SearchBar from '@/components/SearchBar.vue';
  import SearchResult from '@/components/SearchResult.vue';

  import type { Artist } from '@/@types/artist';
  import type { Artwork } from '@/@types/artwork';

  export default defineComponent({
      name: 'SearchResults',
      components: {
        SearchBar,
        SearchResult,
      },
      data() {
        return {
            searchResults: [] as (Artist | Artwork)[],
        }
      },
      created() {
        console.log("SearchResults created");
      },
      methods: {
        handleResponse(response: [], reset : boolean) : void { 
          if (reset) {
            this.searchResults = [] as (Artist | Artwork)[]
          }       
          this.searchResults = this.searchResults.concat(this.makeObjectArray(response));

          console.log(this.searchResults);
        },
        makeObjectArray(response: any[]) : (Artist | Artwork)[] {
          let results = [] as (Artist | Artwork)[];
          for (let i = 0; i < response.length; i++) {
            let result = response[i];
            if (result.type === "artist") {
              results.push(result as Artist);
            } else if (result.type === "artwork") {
              results.push(result as Artwork);
            }
          }
          return results;
        }
      }
  });

</script>