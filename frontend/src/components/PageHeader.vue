<script setup>
defineProps({ title: String, description: String })
</script>
<template>
  <div class="page-header"><div><h1>{{ title }}</h1><p v-if="description">{{ description }}</p></div><div><slot /></div></div>
</template>

