<script setup>
import { RouterView } from 'vue-router'
import { jwtDecode } from 'jwt-decode';
import { useUserStore } from './stores/useUserStore';
import { ElMessageBox } from 'element-plus';
import { useRouter } from 'vue-router';
import { onMounted } from 'vue';

const userStore = useUserStore()
const router = useRouter()

onMounted(() => {
  userStore.init()
  const token = userStore.userInfo?.token
  if (token) {
    try {
      const payload = jwtDecode(token)
      const now = Date.now() / 1000
      if (payload.exp && payload.exp < now) {
        ElMessageBox.alert('登录已过期，请重新登录', '提示', {
          type: 'warning',
          confirmButtonText: '确定',
          callback: () => {
            userStore.logout()
            router.push('/login')
          }
        })
      }
    } catch (e) {
      console.error('token 无效', e)
      userStore.logout()
      router.push('/login')
    }
  }
})

</script>

<template>
  <RouterView />
</template>

<style>
html,
body,
#app {
  margin: 0;
  padding: 0;
  height: 100%;
  width: 100%;
  font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
  background-color: #F2F3F5;
}
</style>
