<template>
    <div class="terminal-detail">
      <!-- 返回按钮 -->
      <el-page-header @back="goBack" :content="terminalInfo.username" />
  
      <el-tabs v-model="activeTab" class="mt-3">
        <el-tab-pane label="终端信息" name="info">
          <el-card shadow="never">
            <el-descriptions title="基本信息" :column="2" border>
              <el-descriptions-item label="id">{{ terminalInfo.id }}</el-descriptions-item>
              <el-descriptions-item label="创建时间">{{ terminalInfo.created_time }}</el-descriptions-item>
              <el-descriptions-item label="更新时间">{{ terminalInfo.updated_time }}</el-descriptions-item>
              <el-descriptions-item label="唯一标识符">{{ terminalInfo.unique_id }}</el-descriptions-item>
              <el-descriptions-item label="用户名">{{ terminalInfo.username }}</el-descriptions-item>
              <el-descriptions-item label="计算机名">{{ terminalInfo.hostname }}</el-descriptions-item>
              <el-descriptions-item label="终端版本">{{ terminalInfo.version }}</el-descriptions-item>
              <el-descriptions-item label="本地IP">{{ terminalInfo.local_ip }}</el-descriptions-item>
              <el-descriptions-item label="公网IP">{{ terminalInfo.ip }}</el-descriptions-item>
              <el-descriptions-item label="MAC">{{ terminalInfo.mac }}</el-descriptions-item>
              <el-descriptions-item label="操作系统">{{ terminalInfo.os }}</el-descriptions-item>
              <el-descriptions-item label="操作系统版本">{{ terminalInfo.os_version }}</el-descriptions-item>
              <el-descriptions-item label="是否64位">{{ terminalInfo.is_64bit ? 'true' : 'false' }}</el-descriptions-item>
              <el-descriptions-item label="在线状态">
                <el-tag :type="terminalInfo.status === 1 ? 'success' : 'info'">
                  {{ terminalInfo.status === 1 ? '在线' : '离线' }}
                </el-tag>
              </el-descriptions-item>
              <el-descriptions-item label="最后在线时间">{{ terminalInfo.last_online_time }}</el-descriptions-item>
              <el-descriptions-item label="操作系统安装时间">{{ terminalInfo.os_install_time }}</el-descriptions-item>
              <el-descriptions-item label="所在分组">{{ terminalInfo.group_name }}</el-descriptions-item>
              <el-descriptions-item label="分组路径">{{ terminalInfo.group_path }}</el-descriptions-item>
            </el-descriptions>
          </el-card>
        </el-tab-pane>
  
        <el-tab-pane label="单点策略" name="policy">
          <!-- 后续扩展策略相关信息 -->
          <el-empty description="暂无数据" />
        </el-tab-pane>
      </el-tabs>
    </div>
  </template>
  
  <script setup>
  import { ref, onMounted } from 'vue'
  import { useRoute, useRouter } from 'vue-router'
  import { getTerminalDetail } from '@/api/terminal_admin/terminal'
  
  const route = useRoute()
  const router = useRouter()
  const terminalId = route.params.id
  
  const activeTab = ref('info')
  const terminalInfo = ref({})
  
  const loadDetail = async () => {
    try {
      const res = await getTerminalDetail(terminalId)
      terminalInfo.value = res.data || {}
    } catch (err) {
      console.error('获取终端详情失败:', err)
    }
  }
  
  const goBack = () => {
    router.back()
  }
  
  onMounted(loadDetail)
  </script>
  
  <style scoped>
  .terminal-detail {
    padding: 20px;
  }
  .mt-3 {
    margin-top: 20px;
  }
  </style>
  