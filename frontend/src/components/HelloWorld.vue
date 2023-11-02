<script lang="ts">
  import { defineComponent } from 'vue';
  import axios from 'axios';

  export default defineComponent({
      name: 'Search',
      data: () => ({
        searchQuery: '',
      }),
      methods: {
        async handleSearch() {
          console.log('handleSearch %s' , this.searchQuery);
          
          const response = await axios.get('http://localhost:8000/artist_search', {
            params: {
              q: this.searchQuery,
            }
          });
          
          //Go to a search results page with the results
          console.log(response.data);

        },
      }
  });

</script>

<template>
  <input type="text" v-model="searchQuery" placeholder="Search..."/>
  <button @click="handleSearch">Search</button>
</template>

<style scoped>
.read-the-docs {
  color: #888;
}
</style>
