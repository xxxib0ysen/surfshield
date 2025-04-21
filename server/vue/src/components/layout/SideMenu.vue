<template>
  <el-aside width="200px" class="side-menu">
    <div class="menu-title">管理中心</div>
    <el-menu 
      router 
      :default-active="route.path" 
      background-color="#2c2f36" 
      text-color="#fff" 
      active-text-color="#fff"
      unique-opened>
      <el-menu-item index="/home">
        <el-icon>
          <House />
        </el-icon>
        <span>首页概况</span>
      </el-menu-item>

      <el-sub-menu index="/management">
        <template #title>
          <el-icon><Monitor /></el-icon>
          <span>用户终端管理</span>
        </template>
        <el-menu-item-group>
          <el-menu-item index="/management/terminal">
            <el-icon><PictureRounded /></el-icon>
            <span>终端列表</span>
          </el-menu-item>
          <el-menu-item index="/management/admin">
            <el-icon><User /></el-icon>
            <span>用户列表</span>
          </el-menu-item>
          <el-menu-item index="/management/role">
            <el-icon><User /></el-icon>
            <span>角色权限列表</span>
          </el-menu-item>
          <el-menu-item index="/management/group">
            <el-icon><Timer /></el-icon>
            <span>组织架构</span>
          </el-menu-item>
        </el-menu-item-group>
      </el-sub-menu>

      <el-sub-menu index="/policy">
        <template #title>
          <el-icon><Cpu /></el-icon>
          <span>策略管控</span>
        </template>
        <el-menu-item-group>
          <el-menu-item index="/policy/website">
            <el-icon><Link /></el-icon>
            <span>网站访问控制</span>
          </el-menu-item>
          <el-menu-item index="/policy/process">
            <el-icon><Timer /></el-icon>
            <span>进程运行控制</span>
          </el-menu-item>
        </el-menu-item-group>
      </el-sub-menu>

      <el-sub-menu index="/monitor">
        <template #title>
          <el-icon><VideoPlay /></el-icon>
          <span>实时管控</span>
        </template>
        <el-menu-item-group>
          <el-menu-item index="/monitor/process_monitor">
            <el-icon><Timer /></el-icon>
            <span>进程管控</span>
          </el-menu-item>
          <el-menu-item index="/monitor/behavior">
            <el-icon><Timer /></el-icon>
            <span>行为管控</span>
          </el-menu-item>
        </el-menu-item-group>
      </el-sub-menu>

      <el-sub-menu index="/log">
        <template #title>
          <el-icon><Document /></el-icon>
          <span>日志分析</span>
        </template>
        <el-menu-item-group>
          <el-menu-item index="/log/behavior">
            <el-icon><Memo /></el-icon>
            <span>终端管控日志</span>
          </el-menu-item>
          <el-menu-item index="/log/operation">
            <el-icon><Notebook /></el-icon>
            <span>系统操作日志</span>
          </el-menu-item>
        </el-menu-item-group>
      </el-sub-menu>

    </el-menu>
  </el-aside>
</template>

<script setup>
import { useRoute } from 'vue-router'

const route = useRoute()
</script>

<style scoped>
.side-menu {
  background-color: #2c2f36;
  height: 100vh;
  width: 100%;
  box-sizing: border-box;
  overflow: hidden;
}

.menu-title {
  width: 100%;
  box-sizing: border-box;
  color: #fff;
  font-size: 18px;
  padding: 16px 20px;
  font-weight: bold;
  border-bottom: 1px solid #1f222a;
  display: flex;
  align-items: center;
  height: 60px;
}

.el-menu-item.is-active {
  background-color: #1f222a !important;
  position: relative;
}

.el-menu-item.is-active::before {
  content: '';
  position: absolute;
  left: 0;
  top: 8px;
  bottom: 8px;
  width: 4px;
  border-radius: 2px;
  background-color: #2774D8;
}
</style>