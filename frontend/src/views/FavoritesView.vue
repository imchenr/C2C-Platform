<script setup>
import { onMounted, ref } from 'vue'
import api from '@/api'
import ProductCard from '@/components/ProductCard.vue'

const loading = ref(true)
const products = ref([])
const load = async () => { loading.value = true; try { products.value = await api.get('/favorites') } finally { loading.value = false } }
const remove = (product) => { if (!product.is_favorite) products.value = products.value.filter((item) => item.id !== product.id) }
onMounted(load)
</script>
<template><div class="page-container"><PageHeader title="我的收藏" :description="`已收藏 ${products.length} 件同校好物`"><router-link to="/market" class="secondary-btn">继续逛市场</router-link></PageHeader><div v-loading="loading"><div v-if="products.length" class="product-grid"><ProductCard v-for="item in products" :key="item.id" :product="item" @favorite-change="remove" /></div><el-empty v-else description="还没有收藏商品"><router-link to="/market" class="primary-btn">去逛逛</router-link></el-empty></div></div></template>

