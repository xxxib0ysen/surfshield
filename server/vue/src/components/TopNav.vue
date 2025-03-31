<template>
    <el-header class="top-nav">
      <el-page-header @back="onBack">

        <template #extra>
            <el-dropdown @command="handleCommand">
                <div class="user-info">
                    <el-icon><User /></el-icon>
                    <span> User</span>  <!--放当前用户，暂定-->
                </div>
                <template #dropdown>
                    <el-dropdown-menu>
                    <el-dropdown-item command="changePassword">修改密码</el-dropdown-item>
                    <el-dropdown-item command="logout">退出登录</el-dropdown-item>
                    </el-dropdown-menu>
                </template>
            </el-dropdown>
        </template>
      </el-page-header>
    </el-header>
</template>

<script setup>
import { useRouter } from 'vue-router'
import { ElMessageBox, ElMessage } from 'element-plus'

const router = useRouter()
const onBack = () => {
    router.back()
}

const handleCommand = async(command) => {
    if(command === 'changePassword') {
        ElMessage.info("跳转到“修改密码”页面")
        // 跳转
    } else if(command === 'logout') {
        const confirm = await ElMessageBox.confirm('确定退出登录？', '提示', {
            type: 'warning',
        }).catch(() => false)
    }
    if(confirm) {
        ElMessage.success('已退出登录')
        // 清除状态，且跳转到login
    }
}
</script>

<style scoped>
.top-nav {
  background-color: #fff;
  height: 60px;
  border-bottom: 1px solid #e4e7ed;
  padding: 0 20px;
  display: flex;
  align-items: center;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: bold;
  color: #606266;
  cursor: pointer;
  user-select: none;
}
</style>