<template>
  <div class="container mt-3 mb-3 p-3">
    <div class="row mb-3 text-center">
      <h2 style="color: #a02905;">
        Search for Artists and Artworks
      </h2>
    </div>
    <div class="row">
      <div class="col-2">
      </div>
      <div class="col-7" style="width: 50%;" :onkeydown="handleKeyDown">
          <input class="form-control-lg" v-model="searchQuery" type="search" placeholder="Search..." style="width: 100%;border-radius: 15px;border: 1px solid #a02905;">
      </div>
      <div class="col-2 text-center">
          <button @click="handleSearch" class="btn-lg btn-primary" type="button" style="background-color: #a02905; border: 0px; border-radius: 10px; color: whitesmoke;">Search</button>
      </div>
      <div class="col-2">
      </div>
    </div>
  </div>
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