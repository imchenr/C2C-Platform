<script setup>
import { computed, nextTick, onMounted, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import api from '@/api'
import { useAuthStore } from '@/stores/auth'
import { currency, relativeTime } from '@/utils/format'

const route = useRoute()
const router = useRouter()
const auth = useAuthStore()
const conversations = ref([])
const messages = ref([])
const activeId = ref(Number(route.params.id) || null)
const content = ref('')
const loading = ref(true)
const messageBody = ref(null)
const active = computed(() => conversations.value.find((item) => item.id === activeId.value))

const loadConversations = async () => {
  conversations.value = await api.get('/conversations')
  if (!activeId.value && conversations.value.length) activeId.value = conversations.value[0].id
}
const loadMessages = async () => {
  if (!activeId.value) return
  messages.value = await api.get(`/conversations/${activeId.value}/messages`)
  const item = conversations.value.find((row) => row.id === activeId.value); if (item) item.unread_count = 0
  await nextTick(); if (messageBody.value) messageBody.value.scrollTop = messageBody.value.scrollHeight
}
const select = (id) => { activeId.value = id; router.replace(`/messages/${id}`) }
const send = async () => {
  if (!content.value.trim() || !activeId.value) return
  const item = await api.post(`/conversations/${activeId.value}/messages`, { content: content.value.trim() })
  messages.value.push(item); content.value = ''; await nextTick(); messageBody.value.scrollTop = messageBody.value.scrollHeight
  await loadConversations()
}
watch(activeId, loadMessages)
onMounted(async () => { loading.value = true; await loadConversations(); await loadMessages(); loading.value = false })
</script>

<template>
  <div class="page-container message-page">
    <PageHeader title="消息中心" description="围绕商品直接沟通，交易进度更清晰"><span class="online-state"><i></i> 消息已实时同步</span></PageHeader>
    <section v-loading="loading" class="message-shell surface">
      <aside class="conversation-list">
        <div class="conversation-search"><el-icon><Search /></el-icon><input placeholder="搜索联系人或商品" /></div>
        <button v-for="item in conversations" :key="item.id" :class="['conversation-item',{active:item.id===activeId}]" @click="select(item.id)">
          <span class="avatar">{{ item.other_user?.nickname?.slice(0,1) }}</span>
          <span class="conversation-content"><span class="conversation-line"><strong>{{ item.other_user?.nickname }}</strong><time>{{ relativeTime(item.last_message_at) }}</time></span><span class="conversation-line"><em>{{ item.last_message || '开始聊聊吧' }}</em><b v-if="item.unread_count">{{ item.unread_count }}</b></span><span class="conversation-product">正在咨询：{{ item.product?.title }}</span></span>
        </button>
        <el-empty v-if="!conversations.length" :image-size="80" description="还没有聊天" />
      </aside>
      <main v-if="active" class="chat-panel">
        <header class="chat-header"><div><span class="avatar">{{ active.other_user?.nickname?.slice(0,1) }}</span><div><strong>{{ active.other_user?.nickname }}</strong><p><i></i> 在线 · {{ active.other_user?.verified ? '已通过学生认证' : '普通用户' }}</p></div></div><el-dropdown><button class="icon-button"><el-icon><More /></el-icon></button><template #dropdown><el-dropdown-menu><el-dropdown-item>查看用户主页</el-dropdown-item><el-dropdown-item>清空聊天记录</el-dropdown-item><el-dropdown-item divided>举报用户</el-dropdown-item></el-dropdown-menu></template></el-dropdown></header>
        <div class="chat-product"><img :src="active.product?.images?.[0]" /><div><strong>{{ active.product?.title }}</strong><span>{{ currency(active.product?.price) }}</span></div><button class="secondary-btn" @click="router.push(`/product/${active.product?.id}`)">查看商品</button></div>
        <div ref="messageBody" class="message-body"><div class="chat-day">今天</div><div v-for="item in messages" :key="item.id" :class="['message-row',{self:item.sender_id===auth.user.id}]"><span v-if="item.sender_id!==auth.user.id" class="avatar small">{{ item.sender?.nickname?.slice(0,1) }}</span><div><p>{{ item.content }}</p><time>{{ relativeTime(item.created_at) }}</time></div></div></div>
        <div class="message-composer"><div class="composer-tools"><button><el-icon><Picture /></el-icon></button><button><el-icon><Location /></el-icon></button><button><el-icon><CollectionTag /></el-icon></button><span>请勿发送校外支付链接或敏感信息</span></div><textarea v-model="content" placeholder="输入消息，Ctrl + Enter 发送" @keydown.ctrl.enter.prevent="send"></textarea><div class="composer-footer"><span>{{ content.length }}/2000</span><button class="primary-btn" @click="send">发送</button></div></div>
      </main>
      <div v-else class="chat-empty"><el-icon><ChatDotSquare /></el-icon><h3>选择一个会话开始沟通</h3><p>校园交易，从友好的第一句话开始</p></div>
    </section>
  </div>
</template>

<style scoped>
.online-state { display:flex; align-items:center; gap:6px; color:#6d786f; font-size:12px; }.online-state i,.chat-header p i { width:7px; height:7px; display:inline-block; border-radius:50%; background:#46a85a; }.message-shell { height:690px; display:grid; grid-template-columns:330px 1fr; overflow:hidden; }.conversation-list { overflow-y:auto; border-right:1px solid #dfe5de; }.conversation-search { height:62px; display:flex; align-items:center; gap:8px; margin:0 14px; padding:0 13px; border-bottom:1px solid #e1e6e0; }.conversation-search input { width:100%; border:0; outline:0; }.conversation-item { width:100%; display:flex; gap:10px; padding:15px 14px; border:0; border-bottom:1px solid #edf0ec; background:#fff; text-align:left; }.conversation-item:hover,.conversation-item.active { background:#f0f7ee; }.conversation-item.active { border-left:3px solid #28783d; padding-left:11px; }.conversation-content { flex:1; min-width:0; }.conversation-line { display:flex; justify-content:space-between; align-items:center; gap:8px; }.conversation-line time { color:#a0a7a2; font-size:10px; }.conversation-line em { max-width:210px; overflow:hidden; color:#748077; font-size:12px; font-style:normal; white-space:nowrap; text-overflow:ellipsis; }.conversation-line b { min-width:17px; height:17px; display:grid; place-items:center; border-radius:9px; background:#e64c43; color:#fff; font-size:10px; }.conversation-product { display:block; max-width:220px; margin-top:7px; overflow:hidden; color:#97a09a; font-size:10px; white-space:nowrap; text-overflow:ellipsis; }.chat-panel { min-width:0; display:grid; grid-template-rows:66px 72px 1fr 170px; }.chat-header { display:flex; align-items:center; justify-content:space-between; padding:0 20px; border-bottom:1px solid #e1e6e0; }.chat-header > div { display:flex; align-items:center; gap:10px; }.chat-header p { display:flex; align-items:center; gap:5px; margin-top:3px; color:#849087; font-size:10px; }.chat-product { display:flex; align-items:center; gap:12px; padding:10px 20px; background:#fafbf8; border-bottom:1px solid #e1e6e0; }.chat-product img { width:57px; height:50px; object-fit:cover; border-radius:6px; }.chat-product div { flex:1; }.chat-product strong,.chat-product span { display:block; }.chat-product span { margin-top:4px; color:#e7582d; font-weight:700; }.message-body { overflow-y:auto; padding:20px 24px; background:#f6f7f3; }.chat-day { margin-bottom:17px; text-align:center; color:#9ba39d; font-size:10px; }.message-row { display:flex; gap:8px; margin-bottom:17px; }.message-row > div p { max-width:530px; padding:11px 14px; border-radius:4px 12px 12px 12px; background:#fff; color:#344039; line-height:1.55; box-shadow:0 1px 3px rgba(0,0,0,.04); }.message-row time { display:block; margin-top:4px; color:#9aa39d; font-size:9px; }.message-row.self { justify-content:flex-end; }.message-row.self p { border-radius:12px 4px 12px 12px; background:#ddefdc; }.message-row.self time { text-align:right; }.message-composer { border-top:1px solid #dfe5de; background:#fff; }.composer-tools { height:38px; display:flex; align-items:center; gap:4px; padding:0 16px; }.composer-tools button { width:30px; height:30px; border:0; background:transparent; color:#5d6a61; font-size:17px; }.composer-tools span { margin-left:auto; color:#a0a7a2; font-size:10px; }.message-composer textarea { width:100%; height:77px; resize:none; padding:7px 20px; border:0; outline:0; color:#344039; }.composer-footer { display:flex; justify-content:flex-end; align-items:center; gap:12px; padding:6px 16px; }.composer-footer > span { color:#a0a7a2; font-size:10px; }.composer-footer .primary-btn { min-height:34px; padding:0 22px; }.chat-empty { display:grid; place-content:center; text-align:center; color:#a0aaa3; }.chat-empty .el-icon { margin:auto; font-size:70px; }.chat-empty h3 { margin-top:12px; color:#617067; }.chat-empty p { margin-top:6px; }
</style>

