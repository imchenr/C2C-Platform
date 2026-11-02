<script setup>
import { computed, onMounted, reactive, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import api from '@/api'
import ProductCard from '@/components/ProductCard.vue'
import { useAuthStore } from '@/stores/auth'
import { currency, relativeTime } from '@/utils/format'

const route = useRoute()
const router = useRouter()
const auth = useAuthStore()
const loading = ref(true)
const data = ref({ product: null, similar: [] })
const activeImage = ref(0)
const orderVisible = ref(false)
const reportVisible = ref(false)
const orderForm = reactive({ meetup_place: '', buyer_note: '' })
const reportForm = reactive({ reason: '信息不实', description: '' })
const product = computed(() => data.value.product)
const isOwn = computed(() => auth.user?.id === product.value?.seller_id)

const load = async () => {
  loading.value = true
  try { data.value = await api.get(`/products/${route.params.id}`); orderForm.meetup_place = data.value.product.pickup_location } finally { loading.value = false }
}
const favorite = async () => {
  if (!auth.isLoggedIn) return router.push('/login')
  const result = await api.post(`/products/${product.value.id}/favorite`)
  product.value.is_favorite = result.favorited
  product.value.favorite_count = result.favorite_count
  ElMessage.success(result.favorited ? '已加入收藏' : '已取消收藏')
}
const contact = async () => {
  if (!auth.isLoggedIn) return router.push('/login')
  const conversation = await api.post('/conversations', { product_id: product.value.id })
  router.push(`/messages/${conversation.id}`)
}
const createOrder = async () => {
  const order = await api.post('/orders', { product_id: product.value.id, ...orderForm })
  ElMessage.success('订单创建成功，请确认并付款')
  orderVisible.value = false
  router.push({ path: '/orders', query: { order: order.id } })
}
const report = async () => {
  await api.post('/reports', { target_type: 'product', target_id: product.value.id, ...reportForm })
  ElMessage.success('举报已提交，感谢你共同维护校园环境')
  reportVisible.value = false
}
watch(() => route.params.id, load)
onMounted(load)
</script>

<template>
  <div v-loading="loading" class="page-container detail-page">
    <template v-if="product">
      <div class="breadcrumb"><router-link to="/">首页</router-link><el-icon><ArrowRight /></el-icon><router-link to="/market">{{ product.category?.name }}</router-link><el-icon><ArrowRight /></el-icon><span>{{ product.title }}</span></div>
      <section class="detail-main">
        <div class="gallery">
          <div class="main-image"><img :src="product.images[activeImage]" :alt="product.title" /><span v-if="product.featured">同校优选</span></div>
          <div class="thumbnails"><button v-for="(image, index) in product.images" :key="image" :class="{ active: activeImage === index }" @click="activeImage = index"><img :src="image" :alt="`${product.title} 图片 ${index + 1}`" /></button></div>
        </div>
        <div class="detail-info">
          <div class="detail-badges"><span>{{ product.condition }}</span><span>{{ product.transaction_method }}</span><span v-if="product.seller?.verified"><el-icon><CircleCheckFilled /></el-icon> 实名同学</span></div>
          <h1>{{ product.title }}</h1>
          <p class="detail-desc">{{ product.description }}</p>
          <div class="detail-price"><strong>{{ currency(product.price) }}</strong><del>{{ currency(product.original_price) }}</del><span>较原价省 {{ Math.round((1 - product.price / product.original_price) * 100) }}%</span></div>
          <dl class="detail-specs"><div><dt>商品成色</dt><dd>{{ product.condition }}</dd></div><div><dt>交易方式</dt><dd>{{ product.transaction_method }}</dd></div><div><dt>取货地点</dt><dd><el-icon><Location /></el-icon>{{ product.pickup_location }}</dd></div><div><dt>发布时间</dt><dd>{{ relativeTime(product.created_at) }}</dd></div></dl>
          <div class="detail-actions" v-if="!isOwn"><button class="buy-button" @click="auth.isLoggedIn ? orderVisible = true : router.push('/login')">立即购买</button><button class="contact-button" @click="contact"><el-icon><ChatDotRound /></el-icon> 联系卖家</button><button :class="['favorite-detail', { active: product.is_favorite }]" @click="favorite"><el-icon><StarFilled v-if="product.is_favorite" /><Star v-else /></el-icon><span>{{ product.is_favorite ? '已收藏' : '收藏' }}</span></button></div>
          <div v-else class="detail-actions"><button class="buy-button" @click="router.push(`/publish/${product.id}`)">编辑商品</button><button class="contact-button" @click="router.push('/profile')">管理我的商品</button></div>
          <div class="buyer-note"><el-icon><Warning /></el-icon><span>安全提醒：请优先在校内公共场所当面交易，贵重物品务必现场验货，切勿脱离平台提前转账。</span></div>
          <button v-if="!isOwn" class="report-link" @click="auth.isLoggedIn ? reportVisible = true : router.push('/login')"><el-icon><Warning /></el-icon> 举报商品</button>
        </div>
        <aside class="seller-card surface">
          <div class="seller-head"><img v-if="product.seller?.avatar" class="avatar seller-avatar" :src="product.seller.avatar" :alt="product.seller.nickname" /><span v-else class="avatar seller-avatar">{{ product.seller?.nickname?.slice(0, 1) }}</span><div><h3>{{ product.seller?.nickname }}</h3><p><el-icon><CircleCheckFilled /></el-icon> 同济大学认证学生</p></div></div>
          <div class="seller-stats"><div><strong>{{ product.seller?.credit_score }}</strong><span>信用分</span></div><div><strong>5.0</strong><span>综合评价</span></div><div><strong>12</strong><span>在售好物</span></div></div>
          <p class="seller-bio">{{ product.seller?.bio || '已完成校园实名认证，支持校内当面交易。' }}</p>
          <button class="secondary-btn full" @click="router.push(`/market?keyword=${product.seller?.nickname}`)">查看 Ta 的主页</button>
          <div class="seller-credit"><el-icon><Medal /></el-icon><div><strong>交易信用优秀</strong><p>平均 8 分钟内回复 · 准时率 98%</p></div></div>
        </aside>
      </section>

      <section class="detail-description surface surface-padded"><h2>商品详情</h2><p>{{ product.description }}</p><div class="detail-points"><span><el-icon><CircleCheckFilled /></el-icon> 功能正常</span><span><el-icon><CircleCheckFilled /></el-icon> 支持当面验货</span><span><el-icon><CircleCheckFilled /></el-icon> 描述真实</span></div></section>
      <section class="similar-section"><div class="section-title"><div><h2>你可能还喜欢</h2><p>同分类的校园好物</p></div></div><div class="product-grid"><ProductCard v-for="item in data.similar" :key="item.id" :product="item" /></div></section>
    </template>

    <el-dialog v-model="orderVisible" title="确认购买" width="500px">
      <div class="order-preview" v-if="product"><img :src="product.images[0]" /><div><strong>{{ product.title }}</strong><span>{{ currency(product.price) }}</span></div></div>
      <el-form label-position="top"><el-form-item label="见面地点"><el-input v-model="orderForm.meetup_place" /></el-form-item><el-form-item label="给卖家留言"><el-input v-model="orderForm.buyer_note" type="textarea" :rows="3" placeholder="例如：今晚 7 点方便吗？" /></el-form-item></el-form>
      <template #footer><el-button @click="orderVisible = false">取消</el-button><el-button type="success" @click="createOrder">提交订单</el-button></template>
    </el-dialog>
    <el-dialog v-model="reportVisible" title="举报该商品" width="460px"><el-form label-position="top"><el-form-item label="举报原因"><el-select v-model="reportForm.reason" style="width:100%"><el-option v-for="reason in ['信息不实','疑似诈骗','违禁商品','价格异常','其他']" :key="reason" :label="reason" :value="reason" /></el-select></el-form-item><el-form-item label="补充说明"><el-input v-model="reportForm.description" type="textarea" :rows="4" /></el-form-item></el-form><template #footer><el-button @click="reportVisible=false">取消</el-button><el-button type="danger" @click="report">提交举报</el-button></template></el-dialog>
  </div>
</template>

<style scoped>
.breadcrumb { display: flex; align-items: center; gap: 8px; margin-bottom: 22px; color: #879087; font-size: 13px; }.breadcrumb a:hover { color: #28753c; }
.detail-main { display: grid; grid-template-columns: 505px minmax(390px, 1fr) 280px; gap: 30px; align-items: start; }
.main-image { position: relative; overflow: hidden; aspect-ratio: 1.06/1; border-radius: 12px; background: #eef0e9; }.main-image img { width: 100%; height: 100%; object-fit: cover; }.main-image > span { position: absolute; left: 14px; top: 14px; padding: 6px 10px; border-radius: 5px; background: #f5c927; color: #3c3308; font-weight: 800; }
.thumbnails { display: flex; gap: 10px; margin-top: 12px; }.thumbnails button { width: 70px; height: 70px; padding: 2px; border: 2px solid transparent; border-radius: 8px; background: #fff; overflow: hidden; }.thumbnails button.active { border-color: #27783d; }.thumbnails img { width:100%; height:100%; object-fit:cover; border-radius:5px; }
.detail-info { min-width: 0; padding-top: 3px; }.detail-badges { display:flex; gap:8px; margin-bottom:12px; }.detail-badges span { display:inline-flex; align-items:center; gap:4px; padding:5px 9px; border-radius:5px; background:#e7f3e5; color:#28743d; font-size:12px; }.detail-info h1 { color:#143d27; font-size:29px; line-height:1.35; }.detail-desc { margin-top:14px; color:#606d64; line-height:1.75; }
.detail-price { display:flex; align-items:baseline; gap:10px; padding:20px 0; margin:15px 0 5px; border-top:1px solid #e5e9e4; border-bottom:1px solid #e5e9e4; }.detail-price strong { color:#ed582a; font-size:36px; }.detail-price del { color:#9aa39c; }.detail-price span { padding:3px 7px; border-radius:4px; background:#fff0e9; color:#d9542d; font-size:12px; }
.detail-specs { display:grid; grid-template-columns:1fr 1fr; gap:15px 20px; margin:22px 0; }.detail-specs div { display:flex; }.detail-specs dt { width:76px; color:#8a938d; }.detail-specs dd { display:flex; align-items:center; gap:4px; margin:0; color:#35423a; }
.detail-actions { display:flex; gap:10px; margin-top:25px; }.detail-actions button { height:48px; border-radius:8px; font-weight:700; }.buy-button { flex:1; border:0; background:#27783d; color:#fff; }.contact-button { flex:1; border:1px solid #7fa682; background:#fff; color:#226d37; }.favorite-detail { width:70px; display:flex; flex-direction:column; justify-content:center; align-items:center; border:1px solid #d4ddd4; background:#fff; color:#68736b; font-size:12px; }.favorite-detail.active { color:#e9a400; }
.buyer-note { display:flex; gap:8px; margin-top:18px; padding:12px; border-radius:8px; background:#f6f5ed; color:#7b7460; font-size:12px; line-height:1.55; }.report-link { display:flex; align-items:center; gap:5px; margin:12px 0 0 auto; border:0; background:transparent; color:#9b655f; font-size:12px; }
.seller-card { padding:19px; }.seller-head { display:flex; align-items:center; gap:11px; }.seller-avatar { width:47px; height:47px; }.seller-head h3 { color:#173f29; }.seller-head p { display:flex; align-items:center; gap:3px; margin-top:4px; color:#4e8b59; font-size:12px; }.seller-stats { display:grid; grid-template-columns:repeat(3,1fr); padding:16px 0; margin:17px 0; border-top:1px solid #e5e9e4; border-bottom:1px solid #e5e9e4; text-align:center; }.seller-stats div+div { border-left:1px solid #e5e9e4; }.seller-stats strong,.seller-stats span { display:block; }.seller-stats strong { color:#1c5c32; font-size:18px; }.seller-stats span { margin-top:3px; color:#929a94; font-size:10px; }.seller-bio { min-height:42px; color:#68726b; font-size:12px; line-height:1.6; }.full { width:100%; margin-top:14px; }.seller-credit { display:flex; gap:8px; margin-top:17px; padding-top:15px; border-top:1px solid #e8ece7; color:#2a783e; }.seller-credit p { margin-top:3px; color:#89918b; font-size:10px; }
.detail-description { margin-top:36px; }.detail-description h2 { color:#164129; font-size:21px; }.detail-description > p { max-width:900px; margin-top:17px; color:#556159; line-height:1.9; }.detail-points { display:flex; gap:28px; margin-top:19px; color:#397b47; font-size:13px; }.detail-points span { display:flex; align-items:center; gap:5px; }
.similar-section { padding-top:44px; }.order-preview { display:flex; align-items:center; gap:13px; padding:12px; margin-bottom:18px; border-radius:8px; background:#f5f7f3; }.order-preview img { width:76px; height:65px; object-fit:cover; border-radius:6px; }.order-preview strong,.order-preview span { display:block; }.order-preview span { margin-top:7px; color:#ee572b; font-size:20px; font-weight:700; }
</style>
