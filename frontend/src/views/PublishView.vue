<script setup>
import { onMounted, reactive, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import api from '@/api'

const route = useRoute()
const router = useRouter()
const categories = ref([])
const saving = ref(false)
const uploading = ref(false)
const fileInput = ref(null)
const form = reactive({ title: '', description: '', price: undefined, original_price: undefined, condition: '9成新', category_id: undefined, campus: '同济大学', pickup_location: '四平路校区', transaction_method: '当面交易 / 校内自提', images: [] })
const isEdit = Boolean(route.params.id)

const chooseFile = () => fileInput.value?.click()
const upload = async (event) => {
  const files = Array.from(event.target.files || [])
  if (!files.length) return
  uploading.value = true
  try {
    for (const file of files.slice(0, 9 - form.images.length)) {
      const body = new FormData(); body.append('file', file)
      const result = await api.post('/upload', body, { headers: { 'Content-Type': 'multipart/form-data' } })
      form.images.push(result.url)
    }
  } finally { uploading.value = false; event.target.value = '' }
}
const submit = async () => {
  if (!form.title || !form.description || !form.category_id || !form.price || !form.images.length) return ElMessage.warning('请填写完整信息并至少上传一张图片')
  saving.value = true
  try {
    const item = isEdit ? await api.put(`/products/${route.params.id}`, form) : await api.post('/products', form)
    ElMessage.success(item.status === 'pending' ? '已提交，等待平台审核' : '发布成功')
    router.push('/profile')
  } finally { saving.value = false }
}
onMounted(async () => {
  categories.value = await api.get('/categories')
  if (isEdit) {
    const data = await api.get(`/products/${route.params.id}`)
    Object.assign(form, { ...data.product, category_id: data.product.category_id })
  }
})
</script>

<template>
  <div class="page-container publish-page">
    <PageHeader :title="isEdit ? '编辑闲置' : '发布闲置'" description="真实描述、清晰图片，会让好物更快遇见新主人"><span class="publish-progress"><el-icon><CircleCheckFilled /></el-icon> 实名认证已完成</span></PageHeader>
    <div class="publish-layout">
      <section class="surface publish-form">
        <div class="form-section"><h2 class="form-section-title">商品图片</h2><p class="field-tip">第一张将作为商品封面，建议上传自然光下清晰实拍图，最多 9 张</p><div class="upload-grid"><div v-for="(image,index) in form.images" :key="image" class="upload-item"><img :src="image" /><button class="upload-remove" @click="form.images.splice(index,1)"><el-icon><Close /></el-icon></button><span v-if="index===0" class="cover-label">封面</span></div><button v-if="form.images.length<9" v-loading="uploading" class="upload-trigger" @click="chooseFile"><div><el-icon><Plus /></el-icon><span>上传实拍图</span></div></button><input ref="fileInput" hidden type="file" accept="image/*" multiple @change="upload" /></div></div>
        <div class="form-section"><h2 class="form-section-title">基本信息</h2><el-form label-position="top"><el-form-item label="商品标题"><el-input v-model="form.title" maxlength="40" show-word-limit placeholder="清楚说明品牌、型号或用途" /></el-form-item><el-form-item label="商品分类"><el-select v-model="form.category_id" placeholder="选择分类" style="width:100%"><el-option v-for="item in categories" :key="item.id" :label="item.name" :value="item.id" /></el-select></el-form-item><el-form-item label="详细描述"><el-input v-model="form.description" type="textarea" :rows="7" maxlength="2000" show-word-limit placeholder="介绍购买时间、使用情况、配件、瑕疵等，让买家充分了解商品" /></el-form-item></el-form></div>
        <div class="form-section"><h2 class="form-section-title">价格与成色</h2><div class="form-grid"><el-form-item label="出售价格"><el-input-number v-model="form.price" :min="0.01" :precision="2" :controls="false" style="width:100%"><template #prefix>¥</template></el-input-number></el-form-item><el-form-item label="购买原价"><el-input-number v-model="form.original_price" :min="0" :precision="2" :controls="false" style="width:100%" /></el-form-item><el-form-item label="商品成色"><el-select v-model="form.condition" style="width:100%"><el-option v-for="item in ['全新','95新','9成新','8成新','7成新及以下']" :key="item" :label="item" :value="item" /></el-select></el-form-item></div></div>
        <div class="form-section"><h2 class="form-section-title">交易信息</h2><div class="form-grid"><el-form-item label="所在学校"><el-input v-model="form.campus" /></el-form-item><el-form-item label="推荐取货地点"><el-select v-model="form.pickup_location" filterable allow-create style="width:100%"><el-option v-for="item in ['四平路校区','嘉定校区','彰武路校区','沪西校区','图书馆门口','学生服务中心']" :key="item" :label="item" :value="item" /></el-select></el-form-item><el-form-item label="交易方式"><el-select v-model="form.transaction_method" style="width:100%"><el-option label="当面交易 / 校内自提" value="当面交易 / 校内自提" /><el-option label="仅校内自提" value="仅校内自提" /><el-option label="可快递邮寄" value="可快递邮寄" /></el-select></el-form-item></div></div>
        <div class="publish-submit"><el-checkbox>我承诺商品信息真实，不发布违禁或侵权物品</el-checkbox><div><button class="secondary-btn" @click="router.back()">取消</button><button class="primary-btn" :disabled="saving" @click="submit">{{ saving ? '正在提交…' : isEdit ? '保存并重新审核' : '提交发布' }}</button></div></div>
      </section>
      <aside class="publish-tips"><div class="surface surface-padded"><h3><el-icon><Opportunity /></el-icon> 更快卖出的秘诀</h3><ul><li><strong>实拍更可信</strong><span>清晰展示商品整体与细节瑕疵</span></li><li><strong>描述要具体</strong><span>写明使用时长、功能状态和配件</span></li><li><strong>定价要合理</strong><span>参考原价、成色和同类商品行情</span></li><li><strong>及时回复</strong><span>保持消息畅通，尽快确认交易安排</span></li></ul></div><div class="surface prohibited"><h3><el-icon><Warning /></el-icon> 禁止发布</h3><p>账号、虚拟币、处方药、危险品、盗版资料等违规商品。</p></div></aside>
    </div>
  </div>
</template>

<style scoped>
.publish-progress { display:flex; align-items:center; gap:6px; color:#2a7840; font-size:13px; }.publish-layout { display:grid; grid-template-columns:1fr 290px; gap:24px; align-items:start; }.publish-form { padding:30px 34px; }.field-tip { margin:-9px 0 15px; color:#8a938c; font-size:12px; }.cover-label { position:absolute; left:5px; bottom:5px; padding:3px 6px; border-radius:4px; background:#24743b; color:#fff; font-size:10px; }.form-grid { display:grid; grid-template-columns:repeat(3,1fr); gap:18px; }.publish-submit { display:flex; justify-content:space-between; align-items:center; padding-top:22px; border-top:1px solid #e1e7e0; }.publish-submit > div { display:flex; gap:10px; }.publish-tips { position:sticky; top:95px; display:grid; gap:16px; }.publish-tips h3 { display:flex; align-items:center; gap:7px; color:#19532f; }.publish-tips ul { list-style:none; padding:0; margin:18px 0 0; }.publish-tips li { position:relative; padding:0 0 18px 20px; border-left:1px solid #d5e2d3; }.publish-tips li::before { content:''; position:absolute; left:-5px; top:3px; width:9px; height:9px; border-radius:50%; background:#4b9253; }.publish-tips li:last-child { padding-bottom:0; }.publish-tips li strong,.publish-tips li span { display:block; }.publish-tips li strong { font-size:13px; }.publish-tips li span { margin-top:3px; color:#879089; font-size:11px; line-height:1.5; }.prohibited { padding:18px; border-color:#ead9cb; background:#fffaf4; }.prohibited h3 { color:#965f35; }.prohibited p { margin-top:8px; color:#8c7868; font-size:12px; line-height:1.6; }
</style>

