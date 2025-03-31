<template>
    <el-container style="height: 100vh;">
      <SideMenu />
      <el-container>
        <TopNav />
        <el-main>
          <Dashboard />
        </el-main>
      </el-container>
    </el-container>
</template>

<script setup>
import SideMenu from '@/components/SideMenu.vue'
import TopNav from '@/components/TopNav.vue'
import Dashboard from '@/components/Dashboard.vue'
</script>
  