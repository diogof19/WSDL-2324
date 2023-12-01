<template>
    <nav class="navbar navbar-light navbar-expand bg-light navigation-clean" style="width: 100%;">
      <div class="container">
        <a class="navbar-brand fs-4 fw-bold" href="/" style="--bs-body-color: #a02905;color: #a02905;">
          Art Attack!
        </a>
        <div class="navbar-text" id="navcol-1">
        </div>
      </div>
    </nav>
    <hr class="m-0">
  </template>
  
  <script lang="ts">
    import { defineComponent } from 'vue';
  
    export default defineComponent({
      name: 'Header',
      methods: {
        goToHome() {
          this.$router.push({ name: 'home'});
        },
      },
    });
  </script>
  