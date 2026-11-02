<script setup>
import { computed } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import api from '@/api'
import { useAuthStore } from '@/stores/auth'
import { currency } from '@/utils/format'

const props = defineProps({ product: { type: Object, required: true }, compact: Boolean })
const emit = defineEmits(['favorite-change'])
const router = useRouter()
const auth = useAuthStore()
const image = computed(() => props.product.images?.[0] || '/assets/products/default.png')
const open = () => router.push(`/product/${props.product.id}`)
const toggleFavorite = async () => {
  if (!auth.isLoggedIn) return router.push('/login')
  const result = await api.post(`/products/${props.product.id}/favorite`)
  props.product.is_favorite = result.favorited
  props.product.favorite_count = result.favorite_count
  ElMessage.success(result.favorited ? '已收藏' : '已取消收藏')
  emit('favorite-change', props.product)
}
</script>

<template>
  <article :class="['product-card', { compact }]" @click="open">
    <div class="product-image-wrap">
      <img :src="image" :alt="product.title" class="product-image" />
      <span v-if="product.featured" class="featured-tag">优选</span>
      <button class="favorite-btn" :aria-label="product.is_favorite ? '取消收藏' : '收藏'" @click.stop="toggleFavorite">
        <el-icon><StarFilled v-if="product.is_favorite" /><Star v-else /></el-icon>
      </button>
    </div>
    <div class="product-body">
      <h3>{{ product.title }}</h3>
      <div class="product-meta"><span class="condition">{{ product.condition }}</span><span><el-icon><Location /></el-icon>{{ product.pickup_location }}</span></div>
      <div class="product-price-row"><strong>{{ currency(product.price) }}</strong><del v-if="product.original_price">{{ currency(product.original_price) }}</del></div>
      <div class="seller-row"><img v-if="product.seller?.avatar" class="avatar small" :src="product.seller.avatar" :alt="product.seller.nickname" /><span v-else class="avatar small">{{ product.seller?.nickname?.slice(0, 1) }}</span><span>{{ product.seller?.nickname }}</span><span v-if="product.seller?.verified" class="verified"><el-icon><CircleCheckFilled /></el-icon>已实名</span><span class="credit"><el-icon><Pointer /></el-icon>{{ product.seller?.credit_score }}%</span></div>
    </div>
  </article>
</template>
