<template>
    <div class="login-bg">
        <div class="login-box">
            <div class="login-logo">
                <img src="@/components/icons/surfshield.ico" />
            </div>
            <div class="login-title">欢迎登录，请使用企业内部账号登录</div>
            <el-form :model="form" ref="formRef" @submit.prevent="onLogin">
                <el-form-item prop="username">
                    <el-input v-model="form.username" placeholder="请输入用户名" prefix-icon="User" />
                </el-form-item>
                <el-form-item prop="password">
                    <el-input v-model="form.password" placeholder="请输入密码" type="password" show-password
                        prefix-icon="Lock" />
                </el-form-item>
                <div class="login-options">
                    <el-checkbox v-model="form.remember">记住密码</el-checkbox>
                    <el-link type="primary" :underline="false">忘记密码？</el-link>
                </div>
                <el-button type="primary" class="login-btn" @click="onLogin" round>登录</el-button>
            </el-form>
        </div>
    </div>
</template>

<script setup>
import { ref } from 'vue'
import { ElMessage } from 'element-plus'
import { useRouter } from 'vue-router'
import { login, getCurrentUser } from '@/api/login'

const router = useRouter()

const form = ref({
    username: '',
    password: '',
    remember: true
})

const onLogin = async () => {
    try {
        const res = await login(form.value.username, form.value.password)
        const token = res.data.access_token
        localStorage.setItem('token', token)

        const userRes = await getCurrentUser()
        localStorage.setItem('user', JSON.stringify(userRes.data))

        ElMessage.success('登录成功')
        router.push('/home')
    } catch (err) {
        ElMessage.error(err.response?.data?.detail || '登录失败')
    }
}
</script>

<style scoped>
.login-bg {
    width: 100%;
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