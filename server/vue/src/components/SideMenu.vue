<template>
    <el-aside width="200px" class="side-menu">
      <div class="menu-title">管理中心</div>
      <el-menu
        router
        :default-active="route.path"
        background-color="#2c2f36"
        text-color="#fff"
        active-text-color="#fff"
        unique-opened
      >
        <el-menu-item index="/">
          <el-icon><House /></el-icon>
          <span>首页概况</span>
        </el-menu-item>
        <el-menu-item index="/terminal">
          <el-icon><Monitor /></el-icon>
          <span>终端与管理</span>
        </el-menu-item>
        <el-menu-item index="/policy">
          <el-icon><Cpu /></el-icon>
          <span>策略管控</span>
        </el-menu-item>
        <el-menu-item index="/realtime">
          <el-icon><VideoPlay /></el-icon>
          <span>实时管控</span>
        </el-menu-item>
        <el-menu-item index="/logs">
          <el-icon><Document /></el-icon>
          <span>日志分析</span>
        </el-menu-item>
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
}

.menu-title {
  color: #fff;
  font-size: 18px;
  padding: 16px;
  font-weight: bold;
  border-bottom: 1px solid #1f222a;
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
  