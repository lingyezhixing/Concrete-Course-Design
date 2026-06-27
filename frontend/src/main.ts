import { createApp } from 'vue'
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
import './assets/styles/tokens.css'
import App from './App.vue'
import router from './router'

// 挂载前应用初始主题，避免刷新闪烁
const storedTheme = localStorage.getItem('ccd-theme')
const theme = storedTheme === 'light' || storedTheme === 'warm' ? storedTheme : 'dark'
document.documentElement.dataset.theme = theme

const app = createApp(App)
app.use(ElementPlus)
app.use(router)
app.mount('#app')
