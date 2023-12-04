<template >
    <footer class="footer-fluid mt-0 mb-3 bg-light" style="width:100%;position:fixed; bottom:0px;">
        <hr class="m-0">
        <div class="container mt-3">
            <div class="row">
                <div class="col-lg-6 text-center text-lg-start my-auto h-100">
                    <ul class="list-inline mb-2">
                        <li class="list-inline-item">
                            <a href="#" style="color:#a02905;">
                                About
                            </a>
                        </li>
                        <li class="list-inline-item">
                            <span style="color: var(--bs-black);font-size: 16;font-weight: bold;">
                                ⋅ 
                            </span>
                        </li>
                        <li class="list-inline-item">
                            <a href="#" style="color:#a02905;">
                                Contact
                            </a>
                        </li>
                        <li class="list-inline-item">
                            <span style="font-size: 16px;font-weight: bold;">
                                ⋅
                            </span>
                        </li>
                        <li class="list-inline-item">
                            <a href="#" style="color:#a02905;">
                                Terms of Use
                            </a>
                        </li>
                        <li class="list-inline-item">
                            <span style="font-weight: bold;">
                                ⋅
                            </span>
                        </li>
                        <li class="list-inline-item">
                            <a href="#" style="color:#a02905;">
                                Privacy Policy
                            </a>
                        </li>
                    </ul>
                    <p class="text-muted small mb-4 mb-lg-0">© Art Attack 2023. All Rights Reserved.</p>
                </div>
                <div class="col-lg-6 text-center text-lg-end my-auto h-100"></div>
            </div>
        </div>
    </footer>
</template>

<script lang="ts">
  import { defineComponent } from 'vue';

  export default defineComponent({
    name: 'Footer',
  });
</script>