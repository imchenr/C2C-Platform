<script setup>
import { computed, reactive, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { useAuthStore } from '@/stores/auth'

const route = useRoute()
const router = useRouter()
const auth = useAuthStore()
const isRegister = computed(() => route.name === 'register')
const loading = ref(false)
const form = reactive({ account: '20230001', password: 'demo123', username: '', email: '', nickname: '', campus: '同济大学', student_no: '' })
const submit = async () => {
  loading.value = true
  try {
    if (isRegister.value) await auth.register({ username: form.username, email: form.email, password: form.password, nickname: form.nickname, campus: form.campus, student_no: form.student_no })
    else await auth.login({ account: form.account, password: form.password })
    ElMessage.success(isRegister.value ? '注册成功，欢迎加入校园集市' : '登录成功')
    router.push(route.query.redirect || (auth.isAdmin ? '/admin' : '/'))
  } finally { loading.value = false }
}
const fillAdmin = () => { form.account = 'admin'; form.password = 'admin123' }
const fillDemo = () => { form.account = '20230001'; form.password = 'demo123' }
</script>

<template>
  <div class="auth-page">
    <section class="auth-visual">
      <router-link to="/" class="brand auth-brand"><span class="brand-mark"><el-icon><ShoppingBag /></el-icon></span><span>校园集市</span></router-link>
      <div class="auth-copy"><span>同校 · 实名 · 安心</span><h1>让每一件闲置，<br />都遇见新的主人。</h1><p>真实学生社区、校内当面交易、平台全程留痕，简单买卖，也能连接有温度的校园生活。</p><div class="auth-proof"><div><strong>12,860+</strong><small>在校用户</small></div><div><strong>8,420+</strong><small>闲置流转</small></div><div><strong>98.6%</strong><small>满意交易</small></div></div></div>
      <div class="auth-quote">“刚开学就淘到了学长的全套教材，比新书省了一大半。”<br /><span>— 2025 级新生 小林</span></div>
    </section>
    <section class="auth-panel">
      <div class="auth-form-wrap">
        <div class="auth-title"><h2>{{ isRegister ? '创建校园账号' : '欢迎回来' }}</h2><p>{{ isRegister ? '使用校园身份，开启安心交易' : '登录后继续你的校园交易' }}</p></div>
        <el-form label-position="top" @submit.prevent="submit">
          <template v-if="isRegister">
            <div class="two-cols"><el-form-item label="用户名"><el-input v-model="form.username" placeholder="至少 4 位" /></el-form-item><el-form-item label="昵称"><el-input v-model="form.nickname" placeholder="同学们如何称呼你" /></el-form-item></div>
            <el-form-item label="校园邮箱"><el-input v-model="form.email" placeholder="name@tongji.edu.cn" /></el-form-item>
            <div class="two-cols"><el-form-item label="学校"><el-input v-model="form.campus" /></el-form-item><el-form-item label="学号（用于认证）"><el-input v-model="form.student_no" /></el-form-item></div>
          </template>
          <el-form-item v-else label="账号"><el-input v-model="form.account" size="large" placeholder="用户名 / 邮箱 / 手机号" /></el-form-item>
          <el-form-item label="密码"><el-input v-model="form.password" size="large" type="password" show-password placeholder="至少 6 位" @keyup.enter="submit" /></el-form-item>
          <div v-if="!isRegister" class="demo-accounts"><span>快速体验：</span><button type="button" @click="fillDemo">C 端账号</button><button type="button" @click="fillAdmin">管理员账号</button></div>
          <button class="auth-submit" type="button" :disabled="loading" @click="submit">{{ loading ? '请稍候…' : isRegister ? '同意协议并注册' : '登录校园集市' }}</button>
        </el-form>
        <p class="auth-switch">{{ isRegister ? '已有账号？' : '还没有账号？' }}<router-link :to="isRegister ? '/login' : '/register'">{{ isRegister ? '立即登录' : '注册新账号' }}</router-link></p>
        <p class="auth-terms">登录或注册即代表同意《用户服务协议》和《隐私政策》</p>
      </div>
    </section>
  </div>
</template>

<style scoped>
.auth-page { min-height: 100vh; display: grid; grid-template-columns: 1.08fr .92fr; background: #f8f7f0; }
.auth-visual { position: relative; min-height: 720px; padding: 42px 70px; overflow: hidden; background: #174c2d url('/assets/hero-campus.png') center/cover no-repeat; color: #fff; }
.auth-visual::after { content: ''; position: absolute; inset: 0; background: rgba(8,54,29,.78); }
.auth-visual > * { position: relative; z-index: 1; }
.auth-brand { color: #fff; }.auth-brand .brand-mark { border-color: #fff; }
.auth-copy { max-width: 570px; margin-top: 125px; }
.auth-copy > span { color: #d0e5ba; font-weight: 700; letter-spacing: 2px; }
.auth-copy h1 { margin-top: 18px; font-size: 49px; line-height: 1.24; }
.auth-copy > p { max-width: 530px; margin-top: 23px; color: #d9e7dd; font-size: 16px; line-height: 1.8; }
.auth-proof { display: flex; gap: 46px; margin-top: 38px; }
.auth-proof strong { display: block; font-size: 24px; }.auth-proof small { color: #bad0c0; }
.auth-quote { position: absolute; left: 70px; bottom: 55px; color: #d7e4da; line-height: 1.7; }.auth-quote span { color: #a8c8b2; font-size: 12px; }
.auth-panel { display: grid; place-items: center; padding: 50px; }
.auth-form-wrap { width: 450px; }
.auth-title { margin-bottom: 30px; }.auth-title h2 { color: #103e25; font-size: 32px; }.auth-title p { margin-top: 8px; color: #7a837c; }
.two-cols { display: grid; grid-template-columns: 1fr 1fr; gap: 14px; }
.demo-accounts { display: flex; align-items: center; gap: 7px; margin: -2px 0 17px; color: #808982; font-size: 12px; }.demo-accounts button { padding: 4px 9px; border: 1px solid #c6d4c5; border-radius: 5px; background: #f5faf4; color: #2d743e; }
.auth-submit { width: 100%; height: 48px; border: 0; border-radius: 8px; background: #27783d; color: #fff; font-size: 16px; font-weight: 700; }
.auth-switch { margin-top: 22px; text-align: center; color: #7b847d; }.auth-switch a { margin-left: 6px; color: #24743a; font-weight: 700; }
.auth-terms { margin-top: 26px; text-align: center; color: #a0a7a2; font-size: 11px; }
</style>

