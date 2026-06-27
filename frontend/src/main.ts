import { createApp } from 'vue'
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
import 'element-plus/theme-chalk/dark/css-vars.css'
import './assets/styles/theme.css'
import './assets/styles/index.css'
import App from './App.vue'
import router from './router'

// 挂载前应用初始主题，避免刷新闪烁
const storedTheme = localStorage.getItem('ccd-theme')
const isDark = storedTheme === null ? true : storedTheme === 'dark'
document.documentElement.classList.toggle('dark', isDark)

const app = createApp(App)
app.use(ElementPlus)
app.use(router)
app.mount('#app')
