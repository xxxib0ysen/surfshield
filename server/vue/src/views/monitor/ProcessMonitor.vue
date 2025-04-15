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
                    @row-contextmenu="handleContextMenu"
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
                <div style="margin-top: 10px; font-size: 12px; color: #909399;">
                🛈 右键进程可执行操作
                </div>
            </el-card>
            <!-- 右键菜单 -->
            <div
                v-if="contextMenu.visible"
                class="custom-context-menu"
                :style="{ top: contextMenu.y + 'px', left: contextMenu.x + 'px' }"
                >
                <div class="menu-item" @click="refreshSingleTerminal(contextMenu.row)">
                      刷新
                </div>
                <div class="menu-item" @click="killProcess(contextMenu.row)">
                      终止进程
                </div>
            </div>
        </el-main>
    </el-container>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { getProcessList, postKillProcess } from '@/api/monitor/process_monitor'
import { ElMessage ,ElMessageBox} from 'element-plus'

const filters = ref({
    username: ''
})
const processList = ref([])
const loading = ref(false)
const terminalUserList = ref([])
let lastDataHash = ''
let timer = null

// 获取进程数据
const loadProcessList = async (force = false) => {
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
  }, 120000) 
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

// 右键菜单控制
const contextMenu = ref({
  visible: false,
  x: 0,
  y: 0,
  row: null
})
const handleContextMenu = (row, column, event) => {
  event.preventDefault()
  contextMenu.value = {
    visible: true,
    x: event.clientX,
    y: event.clientY,
    row
  }
}

document.addEventListener('click', () => {
  contextMenu.value.visible = false
})
const refreshSingleTerminal = (row) => {
  contextMenu.value.visible = false
  filters.value.username = row.username
  loadProcessList()
}

// 终止进程
const killProcess = async (row) => {
  contextMenu.value.visible = false
  try {
    await ElMessageBox.confirm(
      `确定要终止终端 [${row.username}] 的进程 "${row.process_name}" (PID: ${row.pid}) 吗？`,
      '确认操作',
      { type: 'warning' }
    )
    const res = await postKillProcess({
      terminal_id: row.terminal_id,
      pid: row.pid
    })
    if (res.data.code === 200) {
      ElMessage.success('已终止该用户进程')
      loadProcessList(true)
    } else {
      ElMessage.error(res.data.message || '终止失败')
    }
  } catch (e) {
  }
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

.custom-context-menu {
  position: fixed;
  background-color: #ffffff;
  border-radius: 6px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  z-index: 9999;
  width: 150px;
  padding: 6px 0;
}

.menu-item {
  padding: 6px 12px;
  margin: 2px 0;
  font-size: 13px;
  color: #333;
  cursor: pointer;
  transition: background-color 0.2s;
}

.menu-item:hover {
  background-color: #f1f1f1;
  color: #333;
  border-radius: 4px;
}

</style>