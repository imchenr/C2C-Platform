<script setup>
import { computed, onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import api from '@/api'

const auth = useAuthStore()
const route = useRoute()
const router = useRouter()
const keyword = ref(route.query.keyword || '')
const notifications = ref([])
const unreadCount = computed(() => notifications.value.filter((item) => !item.is_read).length)

const search = () => router.push({ name: 'market', query: { keyword: keyword.value } })
const loadNotifications = async () => {
  if (!auth.isLoggedIn) return
  notifications.value = await api.get('/notifications')
}
const logout = () => {
  auth.logout()
  router.push('/')
}
onMounted(async () => {
  await auth.refresh()
  await loadNotifications()
})
</script>

<template>
  <div class="app-shell">
    <header class="site-header">
      <router-link to="/" class="brand" aria-label="校园集市首页">
        <span class="brand-mark"><el-icon><ShoppingBag /></el-icon></span>
        <span>校园集市</span>
      </router-link>
      <button class="campus-switch"><el-icon><Location /></el-icon> 同济大学 <el-icon><ArrowDown /></el-icon></button>
      <form class="global-search" @submit.prevent="search">
        <el-icon><Search /></el-icon>
        <input v-model="keyword" aria-label="搜索商品" placeholder="搜索教材、数码、生活好物" />
        <button type="submit">搜索</button>
      </form>
      <nav class="site-nav" aria-label="主导航">
        <router-link to="/">首页</router-link>
        <router-link to="/market">逛市场</router-link>
        <router-link v-if="auth.isLoggedIn" to="/messages">消息</router-link>
        <router-link v-if="auth.isLoggedIn" to="/orders">订单</router-link>
      </nav>
      <router-link class="primary-btn header-publish" to="/publish"><el-icon><EditPen /></el-icon> 发布闲置</router-link>
      <template v-if="auth.isLoggedIn">
        <el-popover placement="bottom-end" :width="360" trigger="click">
          <template #reference>
            <button class="icon-button notification-button" aria-label="通知"><el-icon><Bell /></el-icon><span v-if="unreadCount" class="badge">{{ unreadCount }}</span></button>
          </template>
          <div class="notification-panel">
            <div class="popover-title"><strong>通知中心</strong><router-link to="/profile">查看全部</router-link></div>
            <div v-if="notifications.length" class="notification-list">
              <div v-for="item in notifications.slice(0, 5)" :key="item.id" :class="['notification-item', { unread: !item.is_read }]">
                <strong>{{ item.title }}</strong><p>{{ item.content }}</p>
              </div>
            </div>
            <el-empty v-else :image-size="70" description="暂无通知" />
          </div>
        </el-popover>
        <el-dropdown trigger="click">
          <button class="user-menu">
            <img v-if="auth.user?.avatar" class="avatar" :src="auth.user.avatar" :alt="auth.user.nickname" />
            <span v-else class="avatar">{{ auth.user?.nickname?.slice(0, 1) }}</span>
            <span class="user-name">{{ auth.user?.nickname }}</span>
            <el-icon><ArrowDown /></el-icon>
          </button>
          <template #dropdown>
            <el-dropdown-menu>
              <el-dropdown-item @click="router.push('/profile')">个人中心</el-dropdown-item>
              <el-dropdown-item @click="router.push('/favorites')">我的收藏</el-dropdown-item>
              <el-dropdown-item v-if="auth.isAdmin" divided @click="router.push('/admin')">管理后台</el-dropdown-item>
              <el-dropdown-item divided @click="logout">退出登录</el-dropdown-item>
            </el-dropdown-menu>
          </template>
        </el-dropdown>
      </template>
      <router-link v-else class="login-link" to="/login">登录 / 注册</router-link>
    </header>
    <main><router-view /></main>
    <footer class="site-footer">
      <div class="footer-inner">
        <div><div class="brand footer-brand"><span class="brand-mark"><el-icon><ShoppingBag /></el-icon></span><span>校园集市</span></div><p>让闲置流转起来，让校园生活更美好。</p></div>
        <div class="footer-links"><a>交易指南</a><a>安全中心</a><a>帮助反馈</a><a>隐私政策</a></div>
        <div class="footer-contact"><strong>校园共建 · 安全交易</strong><span>工作日 09:00-18:00</span></div>
      </div>
      <div class="copyright">© 2026 校园集市 · 校园二手交易服务平台</div>
    </footer>
  </div>
</template>
