import './assets/main.css'

import { createApp } from 'vue'
import App from './App.vue'
import router from './router'
import { createPinia } from 'pinia'
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
import * as ElementPlusIconsVue from '@element-plus/icons-vue'
import zhCn from 'element-plus/es/locale/lang/zh-cn'
import hasPerm from './utils/hasPerm'


const app = createApp(App)

// 全局注册图标组件
for (const [key, component] of Object.entries(ElementPlusIconsVue)) {
    app.component(key, component)
}
app.directive('has-perm',hasPerm) //按钮权限指令
app.use(createPinia())
app.use(router)
app.use(ElementPlus,{
    locale: zhCn
})
app.mount('#app')
