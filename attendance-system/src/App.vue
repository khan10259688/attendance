<!-- App.vue -->
<script setup lang="ts">
import { useRoute } from 'vue-router'

const route = useRoute()
</script>

<template>
  <!-- 路由出口应在此处 -->
  <router-view />
</template>

<style>
#app {
  height: 100vh;
}
</style>