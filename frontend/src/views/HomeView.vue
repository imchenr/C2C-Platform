<script setup>
import { onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import api from '@/api'
import ProductCard from '@/components/ProductCard.vue'

const router = useRouter()
const loading = ref(true)
const data = ref({ banners: [], announcements: [], categories: [], products: [] })
const keyword = ref('')
const currentBanner = ref(0)

const load = async () => {
  loading.value = true
  try { data.value = await api.get('/home') } finally { loading.value = false }
}
const search = () => router.push({ path: '/market', query: { keyword: keyword.value } })
const openCategory = (category) => router.push({ path: '/market', query: { category_id: category.id } })
onMounted(load)
</script>

<template>
  <div>
    <section class="home-hero" :style="{ backgroundImage: `url(${data.banners[currentBanner]?.image || '/assets/hero-campus.png'})` }">
      <div class="hero-inner">
        <div class="hero-copy">
          <span class="hero-kicker"><el-icon><Sunny /></el-icon> 同校好物，触手可及</span>
          <h1>清新校园市集，遇见同校好物</h1>
          <p>同济大学专属二手交易平台，让闲置流转起来，让校园生活更美好。</p>
          <div class="hero-actions"><button class="primary-btn" @click="router.push('/market')"><el-icon><Search /></el-icon> 搜索好物</button><button class="text-btn" @click="router.push('/market')">或&nbsp; 浏览全部 <el-icon><Right /></el-icon></button></div>
        </div>
      </div>
    </section>

    <section class="category-strip">
      <div class="container category-grid">
        <button v-for="category in data.categories" :key="category.id" class="category-item" @click="openCategory(category)">
          <span class="category-icon" :style="{ color: category.color }"><el-icon><component :is="category.icon" /></el-icon></span>
          <span>{{ category.name }}</span>
        </button>
      </div>
    </section>

    <section class="section home-products">
      <div class="container">
        <div class="section-title"><div><h2>同校好物</h2><p>校园里正在被关注的高品质闲置</p></div><router-link to="/market">查看更多 <el-icon><Right /></el-icon></router-link></div>
        <div v-loading="loading" class="product-grid home-product-grid">
          <ProductCard v-for="item in data.products.slice(0, 6)" :key="item.id" :product="item" />
        </div>
      </div>
    </section>

    <section class="safety-section">
      <div class="container safety-banner">
        <div class="safety-icon"><el-icon><Lock /></el-icon></div>
        <div><strong>安全交易 · 校园共建</strong><p>{{ data.announcements[0]?.content || '优先选择校内公共场所当面交易，贵重物品请现场验货。' }}</p></div>
        <button class="secondary-btn" @click="router.push('/market')">了解安全指南 <el-icon><Right /></el-icon></button>
      </div>
    </section>

    <section class="section why-section">
      <div class="container">
        <div class="section-title centered"><div><h2>为什么选择校园集市</h2><p>更近、更真、更放心的校园二手交易体验</p></div></div>
        <div class="why-grid">
          <div><span><el-icon><UserFilled /></el-icon></span><h3>同校实名</h3><p>学生身份认证，交易对象真实可信</p></div>
          <div><span><el-icon><LocationFilled /></el-icon></span><h3>校内面交</h3><p>无需快递，随时看货，交易更高效</p></div>
          <div><span><el-icon><ChatDotRound /></el-icon></span><h3>即时沟通</h3><p>围绕商品直接交流，进度清晰可追踪</p></div>
          <div><span><el-icon><Medal /></el-icon></span><h3>信用评价</h3><p>交易后双向评价，共建友好校园社区</p></div>
        </div>
      </div>
    </section>
  </div>
</template>

<style scoped>
.home-hero { min-height: 308px; background-size: cover; background-position: center; border-bottom: 1px solid #dfe5dc; }
.hero-inner { width: min(1320px, calc(100% - 80px)); min-height: 308px; display: flex; align-items: center; margin: 0 auto; }
.hero-copy { width: 760px; padding: 32px 0; }
.hero-kicker { display: inline-flex; align-items: center; gap: 7px; margin-bottom: 12px; color: #3c7d43; font-weight: 700; }
.hero-copy h1 { color: #083c22; font-size: 43px; line-height: 1.2; letter-spacing: -1.5px; white-space: nowrap; }
.hero-copy > p { margin: 16px 0 20px; color: #516158; font-size: 16px; }
.hero-actions { display: flex; align-items: center; gap: 10px; }
.category-strip { background: #fff; border-bottom: 1px solid #e2e7df; }
.category-grid { height: 121px; display: grid; grid-template-columns: repeat(8, 1fr); align-items: center; }
.category-item { height: 94px; display: flex; flex-direction: column; align-items: center; justify-content: center; gap: 9px; border: 0; background: transparent; color: #26352c; transition: .16s; }
.category-item:hover { color: #23723c; transform: translateY(-3px); }
.category-icon { width: 45px; height: 45px; display: grid; place-items: center; font-size: 28px; }
.home-products { padding-top: 10px; padding-bottom: 22px; background: #fff; }
.home-products .section-title { margin-bottom: 10px; }
.home-products .section-title h2 { font-size: 24px; line-height: 1.2; }
.home-products .section-title p { display: none; }
.home-product-grid { grid-template-columns: repeat(6, minmax(0, 1fr)); gap: 12px; }
.home-product-grid :deep(.product-image-wrap) { aspect-ratio: 1.08 / 1; }
.home-product-grid :deep(.product-body) { padding: 11px; }
.home-product-grid :deep(.product-body h3) { font-size: 14px; }
.home-product-grid :deep(.seller-row) { gap: 3px; font-size: 10px; }
.safety-section { padding: 0 0 54px; background: #fff; }
.safety-banner { display: flex; align-items: center; gap: 17px; padding: 20px 24px; border: 1px solid #cbdcc8; border-radius: 12px; background: #f6faf3; }
.safety-icon { width: 48px; height: 48px; display: grid; place-items: center; border-radius: 12px; background: #dcefdc; color: #23743a; font-size: 27px; }
.safety-banner strong { color: #1b5a31; }
.safety-banner p { margin-top: 5px; color: #667169; font-size: 13px; }
.safety-banner button { margin-left: auto; }
.why-section { background: #f4f2e9; }
.section-title.centered { justify-content: center; text-align: center; }
.why-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 36px; margin-top: 36px; text-align: center; }
.why-grid > div { padding: 28px 20px; }
.why-grid span { width: 58px; height: 58px; display: grid; place-items: center; margin: 0 auto 15px; border-radius: 16px; background: #dcead8; color: #236f3a; font-size: 28px; }
.why-grid h3 { color: #153e27; }
.why-grid p { margin-top: 8px; color: #707a73; font-size: 13px; }
</style>
