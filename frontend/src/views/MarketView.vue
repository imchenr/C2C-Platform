<script setup>
import { computed, onMounted, reactive, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import api from '@/api'
import ProductCard from '@/components/ProductCard.vue'

const route = useRoute()
const router = useRouter()
const loading = ref(false)
const categories = ref([])
const result = reactive({ items: [], total: 0 })
const filters = reactive({ keyword: route.query.keyword || '', category_id: Number(route.query.category_id) || undefined, condition: '', min_price: undefined, max_price: undefined, sort: 'recommended', page: 1, page_size: 12 })
const conditions = ['全新', '95新', '9成新', '8成新', '7成新及以下']
const sortOptions = [{ label: '综合推荐', value: 'recommended' }, { label: '最新发布', value: 'latest' }, { label: '价格从低到高', value: 'price_asc' }, { label: '价格从高到低', value: 'price_desc' }, { label: '人气优先', value: 'popular' }]
const activeCategory = computed(() => categories.value.find((item) => item.id === filters.category_id)?.name || '全部好物')

const load = async () => {
  loading.value = true
  try {
    const data = await api.get('/products', { params: Object.fromEntries(Object.entries(filters).filter(([, value]) => value !== '' && value !== undefined)) })
    Object.assign(result, data)
    router.replace({ query: { ...(filters.keyword ? { keyword: filters.keyword } : {}), ...(filters.category_id ? { category_id: filters.category_id } : {}) } })
  } finally { loading.value = false }
}
const reset = () => Object.assign(filters, { keyword: '', category_id: undefined, condition: '', min_price: undefined, max_price: undefined, sort: 'recommended', page: 1 })
watch(() => [filters.category_id, filters.condition, filters.sort], () => { filters.page = 1; load() })
watch(() => filters.page, load)
onMounted(async () => { categories.value = await api.get('/categories'); await load() })
</script>

<template>
  <div class="page-container market-page">
    <div class="market-heading"><div><span>同校闲置</span><h1>{{ activeCategory }}</h1><p>发现 {{ result.total }} 件来自真实同学的校园好物</p></div><router-link to="/publish" class="primary-btn"><el-icon><Plus /></el-icon> 发布闲置</router-link></div>
    <div class="market-layout">
      <aside class="filter-panel surface">
        <div class="filter-title"><strong>筛选条件</strong><button @click="reset"><el-icon><Refresh /></el-icon> 重置</button></div>
        <div class="filter-section"><h3>商品分类</h3><button :class="{ active: !filters.category_id }" @click="filters.category_id = undefined">全部分类 <span>{{ result.total }}</span></button><button v-for="item in categories" :key="item.id" :class="{ active: filters.category_id === item.id }" @click="filters.category_id = item.id"><el-icon><component :is="item.icon" /></el-icon>{{ item.name }}</button></div>
        <div class="filter-section"><h3>价格范围</h3><div class="price-range"><el-input-number v-model="filters.min_price" :min="0" :controls="false" placeholder="最低" /><span>—</span><el-input-number v-model="filters.max_price" :min="0" :controls="false" placeholder="最高" /></div><button class="filter-submit" @click="load">应用价格</button></div>
        <div class="filter-section"><h3>商品成色</h3><label v-for="item in conditions" :key="item"><input v-model="filters.condition" type="radio" :value="item" />{{ item }}</label><label><input v-model="filters.condition" type="radio" value="" />不限</label></div>
        <div class="filter-tip"><el-icon><CircleCheck /></el-icon><div><strong>同校实名交易</strong><p>建议在校内公共场所面交</p></div></div>
      </aside>
      <section class="market-results">
        <div class="result-toolbar surface"><form @submit.prevent="load"><el-icon><Search /></el-icon><input v-model="filters.keyword" placeholder="在结果中搜索" /><button>搜索</button></form><el-select v-model="filters.sort" style="width: 150px"><el-option v-for="option in sortOptions" :key="option.value" :label="option.label" :value="option.value" /></el-select></div>
        <div v-loading="loading" class="product-grid market-grid"><ProductCard v-for="item in result.items" :key="item.id" :product="item" /></div>
        <el-empty v-if="!loading && !result.items.length" description="暂时没有匹配的商品，换个条件试试" />
        <div v-if="result.total > filters.page_size" class="market-pagination"><el-pagination v-model:current-page="filters.page" background layout="prev, pager, next" :total="result.total" :page-size="filters.page_size" /></div>
      </section>
    </div>
  </div>
</template>

<style scoped>
.market-heading { display: flex; align-items: end; justify-content: space-between; margin-bottom: 24px; }
.market-heading span { color: #43834a; font-weight: 700; }
.market-heading h1 { margin-top: 6px; color: #093f25; font-size: 34px; }
.market-heading p { margin-top: 8px; color: #778078; }
.market-layout { display: grid; grid-template-columns: 245px 1fr; gap: 22px; align-items: start; }
.filter-panel { position: sticky; top: 96px; overflow: hidden; }
.filter-title { height: 58px; display: flex; align-items: center; justify-content: space-between; padding: 0 18px; border-bottom: 1px solid #e5e9e3; }
.filter-title button { display: flex; align-items: center; gap: 4px; border: 0; background: transparent; color: #7c867f; font-size: 12px; }
.filter-section { padding: 17px 18px; border-bottom: 1px solid #e8ece7; }
.filter-section h3 { margin-bottom: 10px; font-size: 14px; }
.filter-section > button:not(.filter-submit) { width: 100%; height: 35px; display: flex; align-items: center; gap: 8px; padding: 0 9px; border: 0; border-radius: 6px; background: transparent; color: #5d675f; text-align: left; }
.filter-section > button span { margin-left: auto; color: #a1a8a3; }
.filter-section > button.active { background: #e9f3e7; color: #21713a; font-weight: 700; }
.filter-section label { height: 31px; display: flex; align-items: center; gap: 8px; color: #59645c; font-size: 13px; cursor: pointer; }
.filter-section input[type=radio] { accent-color: #277a3d; }
.price-range { display: flex; align-items: center; gap: 6px; }
.price-range .el-input-number { width: 90px; }
.filter-submit { width: 100%; height: 34px; margin-top: 9px; border: 1px solid #a9c1aa; border-radius: 6px; background: #f6faf4; color: #246f38; }
.filter-tip { display: flex; gap: 9px; padding: 16px; color: #28733c; font-size: 13px; }
.filter-tip p { margin-top: 3px; color: #7b857d; font-size: 11px; }
.result-toolbar { height: 62px; display: flex; align-items: center; justify-content: space-between; padding: 9px 12px 9px 17px; margin-bottom: 18px; }
.result-toolbar form { width: 420px; height: 40px; display: flex; align-items: center; gap: 8px; padding-left: 12px; border: 1px solid #dbe1da; border-radius: 8px; }
.result-toolbar input { flex: 1; border: 0; outline: 0; }
.result-toolbar form button { align-self: stretch; padding: 0 18px; border: 0; border-radius: 0 7px 7px 0; background: #26783c; color: #fff; }
.market-grid { grid-template-columns: repeat(3, minmax(0, 1fr)); }
.market-pagination { display: flex; justify-content: center; margin-top: 32px; }
</style>

