<script setup>
import { nextTick, onBeforeUnmount, onMounted, ref } from 'vue'
import * as echarts from 'echarts'
import api from '@/api'
import { currency, dateTime, statusMap } from '@/utils/format'

const loading = ref(true)
const data = ref({ stats:{},trend:[],categories:[],recent_orders:[] })
const trendChart = ref(null)
const categoryChart = ref(null)
let chart1, chart2
const render = async () => {
  await nextTick()
  chart1 = echarts.init(trendChart.value)
  chart1.setOption({ tooltip:{trigger:'axis'},grid:{left:42,right:18,top:28,bottom:30},legend:{data:['订单数','交易额'],right:0},xAxis:{type:'category',data:data.value.trend.map(i=>i.date.slice(5)),axisLine:{lineStyle:{color:'#d9e0da'}}},yAxis:[{type:'value',splitLine:{lineStyle:{color:'#edf0ed'}}},{type:'value',splitLine:{show:false}}],series:[{name:'订单数',type:'bar',barWidth:18,data:data.value.trend.map(i=>i.orders),itemStyle:{color:'#7eae78',borderRadius:[4,4,0,0]}},{name:'交易额',type:'line',yAxisIndex:1,smooth:true,data:data.value.trend.map(i=>i.gmv),lineStyle:{color:'#1f6d39',width:3},itemStyle:{color:'#1f6d39'},areaStyle:{color:'rgba(74,145,80,.08)'}}] })
  chart2 = echarts.init(categoryChart.value)
  chart2.setOption({ tooltip:{trigger:'item'},legend:{orient:'vertical',right:4,top:'center'},series:[{type:'pie',radius:['42%','68%'],center:['38%','50%'],label:{show:false},data:data.value.categories,itemStyle:{borderColor:'#fff',borderWidth:3},color:['#1f6e3a','#5e985d','#9cbd7c','#d9b45c','#cf7a5c','#7776a8','#6e9fac','#a3aaa5']}] })
}
const resize=()=>{chart1?.resize();chart2?.resize()}
onMounted(async()=>{try{data.value=await api.get('/admin/dashboard');await render();window.addEventListener('resize',resize)}finally{loading.value=false}})
onBeforeUnmount(()=>{window.removeEventListener('resize',resize);chart1?.dispose();chart2?.dispose()})
</script>

<template><div v-loading="loading"><div class="stat-grid"><div class="stat-card"><span class="stat-icon"><el-icon><User /></el-icon></span><div><p>平台用户</p><strong>{{data.stats.users||0}}</strong></div><span class="stat-trend">今日 +{{data.stats.new_users_today||0}}</span></div><div class="stat-card"><span class="stat-icon"><el-icon><Goods /></el-icon></span><div><p>累计商品</p><strong>{{data.stats.products||0}}</strong></div><span class="stat-trend">待审核 {{data.stats.pending_products||0}}</span></div><div class="stat-card"><span class="stat-icon"><el-icon><Tickets /></el-icon></span><div><p>累计订单</p><strong>{{data.stats.orders||0}}</strong></div><span class="stat-trend">进行中 {{data.stats.trading_orders||0}}</span></div><div class="stat-card"><span class="stat-icon"><el-icon><Money /></el-icon></span><div><p>累计交易额</p><strong>{{currency(data.stats.gmv||0)}}</strong></div><span class="stat-trend warning">待处理举报 {{data.stats.pending_reports||0}}</span></div></div><div class="dashboard-grid"><section class="admin-card"><div class="admin-card-header"><div><h2>近 7 日交易趋势</h2><p>订单量与交易金额变化</p></div><el-tag type="success">实时数据</el-tag></div><div ref="trendChart" class="chart-box"></div></section><section class="admin-card"><div class="admin-card-header"><div><h2>商品分类分布</h2><p>各分类商品占比</p></div></div><div ref="categoryChart" class="chart-box"></div></section></div><section class="admin-card"><div class="admin-card-header"><div><h2>最新订单</h2><p>平台近期产生的交易</p></div><router-link to="/admin/orders" class="text-btn">查看全部</router-link></div><el-table :data="data.recent_orders"><el-table-column label="商品" min-width="250"><template #default="{row}"><div class="table-product"><img :src="row.product?.images?.[0]" /><div><strong>{{row.product?.title}}</strong><small>{{row.order_no}}</small></div></div></template></el-table-column><el-table-column label="买家" prop="buyer.nickname" /><el-table-column label="卖家" prop="seller.nickname" /><el-table-column label="金额"><template #default="{row}"><strong class="price-text">{{currency(row.amount)}}</strong></template></el-table-column><el-table-column label="状态"><template #default="{row}"><el-tag :type="statusMap[row.status]?.[1]">{{statusMap[row.status]?.[0]}}</el-tag></template></el-table-column><el-table-column label="创建时间" width="160"><template #default="{row}">{{dateTime(row.created_at)}}</template></el-table-column></el-table></section></div></template>
<style scoped>.admin-card-header p{margin-top:5px;color:#929a94;font-size:11px}.warning{color:#c26439}.price-text{color:#d9532d}</style>

