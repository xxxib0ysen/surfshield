import { useUserStore } from "@/stores/useUserStore"

export default {
  mounted(el, binding) {
    const { value } = binding
    const userStore = useUserStore()
    const permissions = userStore.userInfo?.permissions || []

    if (value && typeof value === 'string') {
      if (!permissions.includes(value)) {
        // 统一处理禁用
        disableElement(el)
      }
    } else {
      console.warn(`v-has-perm 指令需要权限码字符串，例如 v-has-perm="'admin:add'"`)
    }
  },
  updated(el, binding) {
    const { value } = binding
    const userStore = useUserStore()
    const permissions = userStore.userInfo?.permissions || []

    if (!permissions.includes(value)) {
      disableElement(el)
    }
  }
}


function disableElement(el) {
  // 禁用属性
  el.disabled = true

  el.style.pointerEvents = 'none'
  el.style.opacity = '0.5'

  el.classList.add('is-disabled')

  const tag = el.tagName.toLowerCase()
  if (['input', 'textarea', 'select'].includes(tag)) {
    el.setAttribute('readonly', true)
  }

  if (el.querySelectorAll) {
    el.querySelectorAll('input, button, textarea, select').forEach(child => {
      child.disabled = true
      child.style.pointerEvents = 'none'
      child.style.opacity = '0.5'
      child.classList.add('is-disabled')
    })
  }
}
