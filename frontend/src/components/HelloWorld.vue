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
  <div class="col">
        <div class="row">
            <div class="col" style="width: 50%;margin-left: 20%;"><input type="search" style="width: 100%;margin: 5px;"></div>
            <div class="col-xl-1" style="width: 10%;">
                <div class="dropdown"><button class="btn btn-primary dropdown-toggle" aria-expanded="false" data-bs-toggle="dropdown" type="button">Dropdown </button>
                    <div class="dropdown-menu"><a class="dropdown-item" href="#">First Item</a><a class="dropdown-item" href="#">Second Item</a><a class="dropdown-item" href="#">Third Item</a></div>
                </div>
            </div>
            <div class="col"><button class="btn btn-primary" type="button">Button</button></div>
        </div>
        <div class="row"></div>
    </div>
</template>

<style scoped>
.read-the-docs {
  color: #888;
}
</style>
