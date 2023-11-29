<template>
  <div class="row">
    <div class="col" style="width: 50%;" :onkeydown="handleKeyDown">
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
      emits: ['receivedResponse'],
      methods: {
        async handleSearch() {   
          let firstResult = true;

          // Artist search
          axios.get('http://localhost:8000/artist_search', {
            params: {
              q: this.searchQuery,
            }
          }).then(response => {
            this.$emit('receivedResponse', response.data, firstResult);
            firstResult = false;
          }).catch(error => {
            console.log(error);
          });

          // Artwork search
          axios.get('http://localhost:8000/artwork_search', {
            params: {
              q: this.searchQuery,
            }
          }).then(response => {
            this.$emit('receivedResponse', response.data, firstResult);
            firstResult = false;
          }).catch(error => {
            console.log(error);
          });
        },
        async handleKeyDown(event: any) {
          if (event.key === 'Enter') {
            await this.handleSearch();
          }
        }
      }
  });

</script>