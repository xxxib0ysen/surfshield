<template>
    <el-main>
        <div class="forbidden-container">
            <el-empty description="您暂无访问权限，请联系管理员授权">
                <el-button type="primary" @click="goHome">返回首页</el-button>
            </el-empty>
        </div>
    </el-main>

</template>

<script setup>
import { useRouter } from 'vue-router'
const router = useRouter()

// 返回首页
const goHome = () => {
    router.push('/home')
}
</script>

<style scoped>
.forbidden-container {
    display: flex;
    width: 100%;
    height: 100vh;
    justify-content: center;
    align-items: center;
    background-color: #f5f7fa;
}
</style>