<template>
  <div class="login-bg">
    <div class="login-box">
      <div class="login-logo">
        <img src="@/components/icons/surfshield.ico" />
      </div>
      <div class="login-title">欢迎登录，请使用企业内部账号登录</div>
      <el-form :rules="rules" :model="form" ref="formRef" @submit.prevent="onLogin">
        <el-form-item prop="username">
          <el-input v-model="form.username" placeholder="请输入用户名" prefix-icon="User" />
        </el-form-item>
        <el-form-item prop="password">
          <el-input v-model="form.password" placeholder="请输入密码" type="password" @keyup.enter="onLogin" show-password
            prefix-icon="Lock" />
        </el-form-item>

        <div class="login-options">
          <el-checkbox v-model="form.remember">记住密码</el-checkbox>
          <el-link type="primary" :underline="false" @click="forgetVisible = true">
            忘记密码？
          </el-link>
        </div>

        <el-button type="primary" class="login-btn" @click="onLogin" round :loading="loading">
          登录
        </el-button>
      </el-form>

      <!-- 忘记密码说明 -->
      <el-dialog v-model="forgetVisible" title="忘记密码说明" width="400px" center>
        <div style="line-height: 1.8; font-size: 14px">
          <p><strong>初始化账号：</strong>admin</p>
          <p><strong>初始化密码：</strong>surfshield</p>
          <p>如果需要重置密码，请联系超级管理员在用户管理页面重置密码。</p>
        </div>
        <template #footer>
          <el-button type="primary" @click="forgetVisible = false">知道了</el-button>
        </template>
      </el-dialog>
    </div>
  </div>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import { ElMessage } from 'element-plus'
import { useRouter } from 'vue-router'
import { login, getCurrentUser } from '@/api/login'
import { useUserStore } from '@/stores/useUserStore'

const userStore = useUserStore()
const router = useRouter()
const loading = ref(false)
const forgetVisible = ref(false)
const formRef = ref(null)

const form = ref({
  username: '',
  password: '',
  remember: false
})

const rules = {
  username: [{ required: true, message: '请输入用户名', trigger: 'blur' }],
  password: [{ required: true, message: '请输入密码', trigger: 'blur' }]
}


// 登录逻辑
const onLogin = async () => {
  try {
    await formRef.value.validate()
    loading.value = true
    const res = await login(form.value.username, form.value.password)
    const token = res.data.access_token
    userStore.setUserInfo({
      token,
      user: null, 
      permissions: res.data.permissions || []
    })
    const userRes = await getCurrentUser()
    userStore.setUserInfo({
      token,
      user: userRes.data,
      permissions: res.data.permissions || []
    })




    // 记住密码逻辑
    if (form.value.remember) {
      localStorage.setItem('rememberUser', JSON.stringify({
        username: form.value.username,
        password: form.value.password
      }))
    } else {
      localStorage.removeItem('rememberUser')
    }

    // 如果是默认密码，跳转密码修改页
    if (form.value.password === 'surfshield' && userRes.data.admin_name !== 'admin') {
      ElMessage.warning('默认密码，请修改密码')
      router.push('/change-password')
    } else {
      ElMessage.success('登录成功')
      router.push('/home')
    }
  } catch (err) {
    ElMessage.error(err.response?.data?.detail || '登录失败')
    form.value.password = ''
  } finally {
    loading.value = false
  }
}

// 页面加载时回填保存的账号密码
onMounted(() => {
  const saved = localStorage.getItem('rememberUser')
  if (saved) {
    const { username, password } = JSON.parse(saved)
    form.value.username = username
    form.value.password = password
    form.value.remember = true
  }
})
</script>

<style scoped>
.login-bg {
  width: 100vw;
  height: 100vh;
  background: linear-gradient(to right, #e3f2fd, #e8f5e9);
  display: flex;
  align-items: center;
  justify-content: center;
}

.login-box {
  background: #fff;
  width: 400px;
  padding: 40px 30px;
  border-radius: 16px;
  box-shadow: 0 12px 24px rgba(0, 0, 0, 0.08);
}

.login-logo {
  display: flex;
  justify-content: center;
  margin-bottom: 20px;
}

.login-logo img {
  width: 60px;
}

.login-title {
  text-align: center;
  font-size: 16px;
  color: #666;
  margin-bottom: 30px;
}

.login-options {
  display: flex;
  justify-content: space-between;
  margin-bottom: 20px;
}

.login-btn {
  width: 100%;
  height: 40px;
  font-size: 16px;
}
</style>