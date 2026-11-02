<script setup>
import { computed, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const collapsed = ref(false)
const route = useRoute()
const router = useRouter()
const auth = useAuthStore()
const active = computed(() => route.path)
const pageTitle = computed(() => route.meta.title || {
  '/admin': '数据概览', '/admin/users': '用户管理', '/admin/products': '商品审核',
  '/admin/orders': '订单管理', '/admin/reports': '举报与风控', '/admin/operations': '运营管理', '/admin/settings': '系统设置',
}[route.path] || '管理后台')
const logout = () => { auth.logout(); router.push('/login') }
</script>

<template>
  <div class="admin-shell">
    <aside :class="['admin-sidebar', { collapsed }]">
      <div class="admin-brand" @click="router.push('/admin')">
        <span class="brand-mark"><el-icon><ShoppingBag /></el-icon></span>
        <span v-if="!collapsed">校园集市<small>管理后台</small></span>
      </div>
      <el-menu :default-active="active" router :collapse="collapsed">
        <el-menu-item index="/admin"><el-icon><DataLine /></el-icon><template #title>数据概览</template></el-menu-item>
        <el-menu-item index="/admin/users"><el-icon><User /></el-icon><template #title>用户管理</template></el-menu-item>
        <el-menu-item index="/admin/products"><el-icon><Goods /></el-icon><template #title>商品审核</template></el-menu-item>
        <el-menu-item index="/admin/orders"><el-icon><Tickets /></el-icon><template #title>订单管理</template></el-menu-item>
        <el-menu-item index="/admin/reports"><el-icon><Warning /></el-icon><template #title>举报与风控</template></el-menu-item>
        <el-menu-item index="/admin/operations"><el-icon><Promotion /></el-icon><template #title>运营管理</template></el-menu-item>
        <el-menu-item index="/admin/settings"><el-icon><Setting /></el-icon><template #title>系统设置</template></el-menu-item>
      </el-menu>
      <div class="sidebar-bottom">
        <button @click="router.push('/')"><el-icon><Back /></el-icon><span v-if="!collapsed">返回 C 端</span></button>
        <button @click="collapsed = !collapsed"><el-icon><Fold v-if="!collapsed" /><Expand v-else /></el-icon><span v-if="!collapsed">收起菜单</span></button>
      </div>
    </aside>
    <section class="admin-main">
      <header class="admin-header">
        <div><h1>{{ pageTitle }}</h1><p>校园集市运营管理中心</p></div>
        <div class="admin-actions">
          <button class="icon-button"><el-icon><Bell /></el-icon><span class="badge">3</span></button>
          <el-dropdown>
            <button class="user-menu"><span class="avatar admin-avatar">管</span><span>{{ auth.user?.nickname }}</span><el-icon><ArrowDown /></el-icon></button>
            <template #dropdown><el-dropdown-menu><el-dropdown-item @click="router.push('/')">返回 C 端</el-dropdown-item><el-dropdown-item divided @click="logout">退出登录</el-dropdown-item></el-dropdown-menu></template>
          </el-dropdown>
        </div>
      </header>
      <main class="admin-content"><router-view /></main>
    </section>
  </div>
</template>

