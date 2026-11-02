import { createApp } from 'vue'
import { createPinia } from 'pinia'
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
import * as ElementPlusIconsVue from '@element-plus/icons-vue'
import App from './App.vue'
import router from './router'
import PageHeader from './components/PageHeader.vue'
import './styles/main.css'

const app = createApp(App)
Object.entries(ElementPlusIconsVue).forEach(([key, component]) => app.component(key, component))
app.component('PageHeader', PageHeader)
app.use(createPinia())
app.use(router)
app.use(ElementPlus)
app.mount('#app')
