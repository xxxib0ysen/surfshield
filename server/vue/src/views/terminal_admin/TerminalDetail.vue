<template>
  <el-container class="terminal-container">
    <el-main>

      <el-card shadow="never" style="margin-bottom: 24px">
        <el-row align="middle" justify="space-between">
          <el-button link type="info" @click="goBack">返回列表</el-button>

          <el-text style="font-size: 20px; font-weight: 600;">
            {{ terminalInfo.username || '-' }}
          </el-text>

          <div style="width: 100px"></div>
        </el-row>
      </el-card>

      <el-card shadow="never">
        <el-tabs v-model="activeTab">
          <el-tab-pane label="终端信息" name="info">

              <el-descriptions :column="2" size="large" border title="基本信息"
                style="background: #fff; border: 1px solid #ebeef5; border-radius: 8px; padding: 20px;"
                :label-style="{ width: '50%' }" :content-style="{ width: '50%' }">
                <el-descriptions-item label="ID">{{ terminalInfo.id }}</el-descriptions-item>
                <el-descriptions-item label="用户名">{{ terminalInfo.username }}</el-descriptions-item>
                <el-descriptions-item label="创建时间">{{ terminalInfo.createdon }}</el-descriptions-item>
                <el-descriptions-item label="唯一标识符">{{ terminalInfo.uuid }}</el-descriptions-item>
                <el-descriptions-item label="计算机名">{{ terminalInfo.hostname }}</el-descriptions-item>
                <el-descriptions-item label="本地 IP">{{ terminalInfo.local_ip }}</el-descriptions-item>
                <el-descriptions-item label="公网 IP">{{ terminalInfo.ip_address }}</el-descriptions-item>
                <el-descriptions-item label="MAC">{{ terminalInfo.mac_address }}</el-descriptions-item>
                <el-descriptions-item label="操作系统">{{ terminalInfo.os_name }}</el-descriptions-item>
                <el-descriptions-item label="操作系统版本">{{ terminalInfo.os_version }}</el-descriptions-item>
                <el-descriptions-item label="操作系统安装时间">{{ terminalInfo.install_time }}</el-descriptions-item>
                <el-descriptions-item label="是否 64 位">{{ terminalInfo.is_64bit === 1 ? '64位' : '32位'
                  }}</el-descriptions-item>
                <el-descriptions-item label="在线状态">
                  <el-tag :type="terminalInfo.status === 1 ? 'success' : 'info'">
                    {{ terminalInfo.status === 1 ? '在线' : '离线' }}
                  </el-tag>
                </el-descriptions-item>
                <el-descriptions-item label="最后在线时间">{{ terminalInfo.last_login }}</el-descriptions-item>
                <el-descriptions-item label="分组ID">{{ terminalInfo.group_id }}</el-descriptions-item>
                <el-descriptions-item label="所在分组">{{ terminalInfo.group_name }}</el-descriptions-item>
                <el-descriptions-item label="分组路径">{{ terminalInfo.group_path }}</el-descriptions-item>
              </el-descriptions>

          </el-tab-pane>
        </el-tabs>
      </el-card>

    </el-main>
  </el-container>
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
    terminalInfo.value = res.data.data || {}
  } catch (err) {
    console.error('获取终端详情失败:', err)
  }
}

const goBack = () => {
  router.push('/management/terminal') 
}

onMounted(loadDetail)
</script>

<style scoped>
.terminal-container {
  padding: 0 15px;
}
</style>