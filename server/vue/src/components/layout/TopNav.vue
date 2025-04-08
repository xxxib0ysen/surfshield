<template>
    <el-header class="top-nav">
      <div class="top-nav-content">
        <el-page-header @back="onBack"></el-page-header>
          <el-dropdown @command="handleCommand">
              <span class="el-dropdown-link" tabindex="0">
                  <el-icon><User /></el-icon> 
                  <span>{{ userStore.userInfo?.user?.admin_name || '用户' }}</span>
              </span>
              <template #dropdown>
                  <el-dropdown-menu>
                      <el-dropdown-item command="changePassword">修改密码</el-dropdown-item>
                      <el-dropdown-item command="logout">退出登录</el-dropdown-item>
                  </el-dropdown-menu>
              </template>
          </el-dropdown>
      </div>
    </el-header>
</template>

<script setup>
import { useRouter } from 'vue-router'
import { ElMessageBox, ElMessage } from 'element-plus'
import { useUserStore } from '@/stores/useUserStore'

const router = useRouter()
const userStore = useUserStore()

const onBack = () => {
    router.back()
}

const handleCommand = async(command) => {
    if(command === 'changePassword') {
        ElMessage.info("跳转到“修改密码”页面")
        // TODO: 跳转
    } else if(command === 'logout') {
        const confirm = await ElMessageBox.confirm('确定退出登录？', '提示', {
            type: 'warning',
        }).catch(() => false)

        if(confirm) {
        userStore.logout()
        ElMessage.success('已退出登录')
        router.push('/login')
    }
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

.top-nav-content {
  display: flex;
  align-items: center;
  justify-content: space-between;
  width: 100%;
}

.el-dropdown-link {
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 6px;
  font-weight: bold;
  color: #606266;
  padding: 6px 10px;
  border-radius: 6px;
  transition: background-color 0.2s;
}

.el-dropdown-link:hover {
  background-color: #f2f3f5;
}

.el-dropdown-link:focus {
  outline: none;
  box-shadow: none;
}
</style>