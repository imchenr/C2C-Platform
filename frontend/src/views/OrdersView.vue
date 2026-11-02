<script setup>
import { onMounted, reactive, ref } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import api from '@/api'
import { currency, dateTime, statusMap } from '@/utils/format'

const loading = ref(true)
const orders = ref([])
const role = ref('all')
const statusFilter = ref('')
const reviewVisible = ref(false)
const selectedOrder = ref(null)
const review = reactive({ score: 5, content: '' })
const tabs = [{label:'全部',value:''},{label:'待付款',value:'pending'},{label:'已付款',value:'paid'},{label:'待面交',value:'meeting'},{label:'已完成',value:'completed'},{label:'售后/争议',value:'disputed'}]

const load = async () => { loading.value = true; try { orders.value = await api.get('/orders',{params:{role:role.value,status_filter:statusFilter.value}}) } finally { loading.value=false } }
const actionText = { pay:'立即付款', confirm_meetup:'确认面交', complete:'确认完成', cancel:'取消订单', refund:'申请退款', dispute:'发起争议' }
const perform = async (order, action) => {
  let reason = ''
  if (['cancel','refund','dispute'].includes(action)) {
    const result = await ElMessageBox.prompt(`请填写${actionText[action]}原因`, actionText[action], { inputPlaceholder:'简要说明原因', confirmButtonText:'确认', cancelButtonText:'再想想' }).catch(()=>null)
    if (!result) return
    reason = result.value
  }
  await api.patch(`/orders/${order.id}/status`,{action,reason,meetup_place:order.meetup_place})
  ElMessage.success(`已${actionText[action]}`); load()
}
const openReview = (order) => { selectedOrder.value=order; review.score=5; review.content=''; reviewVisible.value=true }
const submitReview = async () => { await api.post(`/orders/${selectedOrder.value.id}/reviews`,review); ElMessage.success('评价已提交'); reviewVisible.value=false }
const actionsFor = (order) => {
  if (order.status==='pending' && order.perspective==='buyer') return ['pay','cancel']
  if (order.status==='paid') return order.perspective==='seller' ? ['confirm_meetup','cancel'] : ['cancel']
  if (order.status==='meeting' && order.perspective==='buyer') return ['complete','dispute']
  if (order.status==='meeting' && order.perspective==='seller') return ['dispute']
  return []
}
onMounted(load)
</script>

<template>
  <div class="page-container order-page">
    <PageHeader title="我的订单" description="统一管理买入、卖出和售后进度"><div class="role-switch"><button v-for="item in [{l:'全部订单',v:'all'},{l:'我买到的',v:'buyer'},{l:'我卖出的',v:'seller'}]" :key="item.v" :class="{active:role===item.v}" @click="role=item.v;load()">{{ item.l }}</button></div></PageHeader>
    <div class="order-tabs"><button v-for="item in tabs" :key="item.value" :class="{active:statusFilter===item.value}" @click="statusFilter=item.value;load()">{{item.label}}</button></div>
    <div v-loading="loading" class="order-list">
      <article v-for="order in orders" :key="order.id" class="order-card surface">
        <header><span>订单号 {{order.order_no}}</span><time>{{dateTime(order.created_at)}}</time><span class="perspective">{{order.perspective==='buyer'?'我买到的':'我卖出的'}}</span><el-tag :type="statusMap[order.status]?.[1]">{{statusMap[order.status]?.[0]||order.status}}</el-tag></header>
        <div class="order-body"><img :src="order.product?.images?.[0]" /><div class="order-product"><router-link :to="`/product/${order.product_id}`">{{order.product?.title}}</router-link><span>{{order.product?.condition}} · {{order.product?.transaction_method}}</span><span>交易对象：{{order.perspective==='buyer'?order.seller?.nickname:order.buyer?.nickname}} <em v-if="(order.perspective==='buyer'?order.seller:order.buyer)?.verified">已实名</em></span></div><div class="order-meet"><small>见面地点</small><span><el-icon><Location /></el-icon>{{order.meetup_place||'待协商'}}</span><small v-if="order.pickup_code">取货码：<strong>{{order.pickup_code}}</strong></small></div><div class="order-amount"><small>实付金额</small><strong>{{currency(order.amount)}}</strong></div></div>
        <footer><div class="order-progress"><span :class="{done:['paid','meeting','completed'].includes(order.status)}">创建订单</span><i></i><span :class="{done:['paid','meeting','completed'].includes(order.status)}">完成付款</span><i></i><span :class="{done:['meeting','completed'].includes(order.status)}">确认面交</span><i></i><span :class="{done:order.status==='completed'}">交易完成</span></div><div class="order-actions"><router-link :to="`/messages`" class="secondary-btn">联系对方</router-link><button v-for="action in actionsFor(order)" :key="action" :class="action==='cancel'||action==='dispute'?'text-btn':'primary-btn'" @click="perform(order,action)">{{actionText[action]}}</button><button v-if="order.status==='completed'" class="primary-btn" @click="openReview(order)">评价交易</button></div></footer>
      </article>
      <el-empty v-if="!loading&&!orders.length" description="当前没有订单"><router-link to="/market" class="primary-btn">去逛市场</router-link></el-empty>
    </div>
    <el-dialog v-model="reviewVisible" title="评价本次交易" width="460px"><div class="review-form"><p>你的评价将帮助校园社区建立更可靠的信用环境</p><el-rate v-model="review.score" size="large" show-text :texts="['很差','较差','一般','满意','非常满意']" /><el-input v-model="review.content" type="textarea" :rows="4" maxlength="200" show-word-limit placeholder="分享你的交易体验" /></div><template #footer><el-button @click="reviewVisible=false">取消</el-button><el-button type="success" @click="submitReview">提交评价</el-button></template></el-dialog>
  </div>
</template>

<style scoped>
.role-switch { display:flex; padding:3px; border-radius:8px; background:#e9eee8; }.role-switch button { height:34px; padding:0 14px; border:0; border-radius:6px; background:transparent; color:#627067; }.role-switch button.active { background:#fff; color:#24733b; font-weight:700; box-shadow:0 1px 4px rgba(0,0,0,.06); }.order-tabs { display:flex; gap:30px; height:52px; padding:0 18px; margin-bottom:16px; border-bottom:1px solid #dfe5de; background:#fff; }.order-tabs button { position:relative; border:0; background:transparent; color:#657168; }.order-tabs button.active { color:#24743a; font-weight:700; }.order-tabs button.active::after { content:''; position:absolute; left:0; right:0; bottom:0; height:3px; background:#28783d; }.order-list { display:grid; gap:15px; }.order-card { overflow:hidden; }.order-card header { height:46px; display:flex; align-items:center; gap:18px; padding:0 18px; background:#f7f9f5; color:#7e8881; font-size:12px; }.order-card header time { color:#9ba39e; }.order-card header .perspective { margin-left:auto; }.order-body { display:grid; grid-template-columns:90px minmax(230px,1fr) 260px 130px; align-items:center; gap:16px; padding:18px; }.order-body>img { width:90px; height:78px; object-fit:cover; border-radius:8px; background:#eee; }.order-product a { display:block; color:#1e3929; font-weight:700; }.order-product span { display:block; margin-top:7px; color:#8a938d; font-size:11px; }.order-product em { color:#318146; font-style:normal; }.order-meet { padding-left:24px; border-left:1px solid #e4e8e3; }.order-meet small,.order-meet span { display:block; }.order-meet small { color:#9aa29c; font-size:10px; }.order-meet span { display:flex; align-items:center; gap:4px; margin:7px 0; color:#4d5b52; font-size:12px; }.order-meet strong { color:#27783d; letter-spacing:2px; }.order-amount { text-align:right; }.order-amount small,.order-amount strong { display:block; }.order-amount small { color:#9aa29c; }.order-amount strong { margin-top:5px; color:#e5572d; font-size:22px; }.order-card footer { min-height:58px; display:flex; justify-content:space-between; align-items:center; gap:20px; padding:9px 18px; border-top:1px solid #e7ebe6; }.order-progress { display:flex; align-items:center; color:#a3aaa5; font-size:10px; }.order-progress span.done { color:#2f7e42; }.order-progress i { width:34px; height:1px; margin:0 5px; background:#d9dfd9; }.order-actions { display:flex; align-items:center; gap:7px; }.order-actions .primary-btn,.order-actions .secondary-btn,.order-actions .text-btn { min-height:34px; padding:0 13px; font-size:12px; }.review-form>p { margin-bottom:16px; color:#778178; }.review-form .el-rate { margin-bottom:18px; }
</style>

