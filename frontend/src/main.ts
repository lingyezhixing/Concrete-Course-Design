import { createApp } from 'vue'
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
import './assets/styles/tokens.css'
import './assets/styles/report-print.css'
import App from './App.vue'
import router from './router'
import { useAuth } from './composables/useAuth'

// 恢复登录态并按当前用户载入主题/侧栏偏好（useTheme 在导入时已应用全局主题）
void useAuth().bootstrap()

const app = createApp(App)
app.use(ElementPlus)
app.use(router)
app.mount('#app')
