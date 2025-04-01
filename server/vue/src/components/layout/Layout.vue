<template>
<el-container class="layout-container">
  <el-aside width="200px" class="aside">
    <SideMenu />
  </el-aside>

  <el-container direction="vertical" class="main-container">
    <el-header class="header">
      <TopNav />
    </el-header>
    <el-main class="main-area">
      <RouterView />
    </el-main>
  </el-container>
</el-container>

</template>

<script setup>
import { RouterView } from 'vue-router'
import SideMenu from './SideMenu.vue'
import TopNav from './TopNav.vue'
</script>

<style scoped>
.layout-container {
  display: flex;
  width: 100vw;
  height: 100vh;
}

.header {
  padding: 0;
}

.main-container {
  flex: 1;
  display: flex;
  flex-direction: column;
  width: 100%;
  min-width: 0; 
}

.main-area {
  flex: 1;
  overflow-y: auto;
  background-color: #f5f7fa;
  padding: 0;
  box-sizing: border-box;
}

</style>
