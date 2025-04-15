<template>
    <el-container class="process-monitor-container">
        <el-main>
            <!-- 搜索 -->
            <el-card shadow="never" class="mb-3">
                <el-autocomplete v-model="filters.username" :fetch-suggestions="searchSuggestions"
                    placeholder="请输入终端用户名" clearable class="custom-search-input" @clear="handleClear"
                    @select="handleSelect" @keyup.enter.native="handleSearch">
                    <template #suffix>
                        <el-icon class="search-icon" @click="handleSearch">
                            <Search />
                        </el-icon>
                    </template>
                </el-autocomplete>
            </el-card>

            <!-- 数据列表 -->
            <el-card shadow="never">
                <el-table :data="processList" border 
                    :default-sort="{ prop: 'start_time', order: 'descending' }"
                    v-loading="loading" style="width: 100%;" height="550">
                    <el-table-column prop="username" label="用户名" />
                    <el-table-column prop="process_name" label="进程名" />
                    <el-table-column prop="pid" label="PID" />
                    <el-table-column prop="status" label="状态">
                        <template #default="{ row }">
                            <el-tag :type="row.status === 1 ? 'success' : 'danger'">
                                {{ row.status === 1 ? '正在运行' : '已挂起' }}
                            </el-tag>
                        </template>
                    </el-table-column>
                    <el-table-column prop="description" label="描述" />
                    <el-table-column prop="start_time" label="启动时间" sortable />
                    <el-table-column prop="is_network" label="是否联网">
                        <template #default="{ row }">
                            <el-tag :type="row.is_network ? 'success' : 'info'">
                                {{ row.is_network ? '是' : '否' }}
                            </el-tag>
                        </template>
                    </el-table-column>
                    <el-table-column label="联网目标IP：端口" width="150px">
                        <template #default="{ row }">
                            <span v-if="row.remote_ip">
                                {{ row.remote_ip }}:{{ row.remote_port }}
                            </span>
                            <span v-else>-</span>
                        </template>
                    </el-table-column>
                    <el-table-column prop="network_status" label="当前连接状态" />

                </el-table>
            </el-card>
        </el-main>
    </el-container>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { getProcessList } from '@/api/monitor/process_monitor'
import { ElMessage } from 'element-plus'

const filters = ref({
    username: ''
})
const processList = ref([])
const loading = ref(false)
const terminalUserList = ref([])
let lastDataHash = ''
let timer = null

// 获取进程数据
const loadProcessList = async () => {
  try {
    loading.value = true
    const res = await getProcessList()

    if (res.data.code === 200 && Array.isArray(res.data.data)) {
      const list = res.data.data
      const filtered = filters.value.username
        ? list.filter(item => item.username?.includes(filters.value.username))
        : list
    const currentHash = JSON.stringify(filtered)
    if (currentHash !== lastDataHash) {
        processList.value = filtered
        updateTerminalUserList(list) 
        lastDataHash = currentHash
      } else {
        console.log('[跳过刷新] 数据无变化')
      }
    } else {
      ElMessage.error(res.data.message || '接口错误')
    }
  } catch (err) {
    ElMessage.error('获取进程数据失败')
  } finally {
    loading.value = false
  }
}

// 自动刷新定时器
const startTimer = () => {
  timer = setInterval(() => {
    loadProcessList()
  }, 30000) 
}
const stopTimer = () => {
  if (timer) clearInterval(timer)
}

// 页面不可见时不刷新
document.addEventListener('visibilitychange', () => {
  if (document.hidden) {
    stopTimer()
  } else {
    loadProcessList()
    startTimer()
  }
})


// 用户名列表
const updateTerminalUserList = (data) => {
    terminalUserList.value = [...new Set(data.map(item => item.username))].sort().map(name => ({ value: name }))
}

// 搜索
const searchSuggestions = (queryString, cb) => {
    const results = terminalUserList.value.filter(item =>
        item.value.toLowerCase().includes(queryString.toLowerCase())
    )
    cb(results)
}
const handleSelect = (item) => {
  // 选中的用户名
  filters.value.username = item.value
  loadProcessList()
}

// 搜索按钮
const handleSearch = () => {
    loadProcessList()
}

// 清空时刷新
const handleClear = () => {
    filters.value.username = ''
    loadProcessList()
}

onMounted(() => {
    loadProcessList()
})
</script>

<style scoped>
.process-monitor-container {
    padding: 0 15px;
}

.mb-3 {
    margin-bottom: 16px;
}

.custom-search-input {
    width: 350px;
}

.search-icon {
    cursor: pointer;
    color: #909399;
}

.search-icon:hover {
    color: #409EFF;
}
</style>