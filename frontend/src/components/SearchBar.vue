<template>
  <div class="row">
    <div class="col" style="width: 50%;">
        <input type="search" v-model="searchQuery" placeholder="Search..." style="width: 100%;margin: 5px;">
    </div>
    <div class="col-xl-1" style="width: 10%;">
        <div class="dropdown"><button class="btn btn-primary dropdown-toggle" aria-expanded="false" data-bs-toggle="dropdown" type="button">Dropdown </button>
            <div class="dropdown-menu">
                <a class="dropdown-item" href="#">First Item</a>
                <a class="dropdown-item" href="#">Second Item</a>
                <a class="dropdown-item" href="#">Third Item</a></div>
        </div>
    </div>
    <div class="col">
        <button @click="handleSearch" class="btn btn-primary" type="button">Search</button>
    </div>
  </div>
  <div class="row"></div>
    
</template>

<script lang="ts">
  import { defineComponent } from 'vue';
  import axios from 'axios';

  export default defineComponent({
      name: 'SearchBar',
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

          console.log(response.data);
          //Go to a search results page with the results
          this.$router.push({name: 'search-results', params: {results: JSON.stringify(response.data)}});

        },
      }
  });

</script>