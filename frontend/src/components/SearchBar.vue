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
  import { defineComponent, defineEmits } from 'vue';
  import axios from 'axios';

  export default defineComponent({
      name: 'SearchBar',
      data: () => ({
        searchQuery: '',
      }),
      setup(_, ctx) {
          defineEmits({ 
            receivedResponse: (response: any) => {
              ctx.emit('receivedResponse', response);
            }
          })
      },
      methods: {
        async handleSearch() {          
          const response = await axios.get('http://localhost:8000/artist_search', {
            params: {
              q: this.searchQuery,
            }
          });

          //Go to a search results page with the results
          this.$emit('receivedResponse', response.data)
        },
        async handleKeyDown(event: any) {
          if (event.key === 'Enter') {
            await this.handleSearch();
          }
        }
      }
  });

</script>