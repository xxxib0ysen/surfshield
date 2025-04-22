<template>
    <el-container class="log-behavior-container">
        <el-main>
            <el-row gutter="20">
                <!-- 组织架构 -->
                <el-col :span="4">
                    <el-card shadow="never">
                        <el-input v-model="groupFilter" placeholder="输入关键字进行过滤" clearable @clear="handleRefresh"
                            @input="handleSearch" style="margin-bottom: 16px;" />
                        <el-tree class="group-tree" :data="groupList" :props="defaultProps" node-key="group_id"
                            default-expand-all accordion highlight-current :current-node-key="selectedGroupId"
                            :filter-node-method="filterGroup" @node-click="handleGroupClick" />
                    </el-card>
                </el-col>

                <el-col :span="20">
                    <!-- 筛选栏 -->
                    <el-card shadow="never" class="mb-2">
                        <el-form :model="filters" label-position="left">
                            <el-row :gutter="20">
                                <!-- 用户名 -->
                                <el-col :span="8">
                                <el-form-item label="用户名：">
                                    <el-autocomplete
                                    v-model="filters.username"
                                    :fetch-suggestions="getUsernameSuggestions"
                                    placeholder="请输入终端用户名"
                                    clearable
                                    @clear="handleSearch"
                                    @select="handleSearch"
                                    @keyup.enter.native="handleSearch"
                                    >
                                    <template #suffix>
                                        <el-icon @click="handleSearch" style="cursor: pointer">
                                        <Search />
                                        </el-icon>
                                    </template>
                                    </el-autocomplete>
                                </el-form-item>
                                </el-col>


                                <!-- 行为类型 -->
                                <el-col :span="8">
                                    <el-form-item label="行为类型：">
                                        <el-select v-model="filters.behavior_type" placeholder="请选择" clearable
                                            @clear="handleRefresh" @change="handleSearch">
                                            <el-option label="网站访问" value="网站访问" />
                                            <el-option label="搜索行为" value="搜索行为" />
                                            <el-option label="进程运行" value="进程运行" />
                                        </el-select>
                                    </el-form-item>
                                </el-col>

                                <!-- 时间范围 -->
                                <el-col :span="8">
                                    <el-form-item label="时间范围：">
                                        <el-date-picker v-model="filters.timeRange" type="daterange"
                                            start-placeholder="开始时间" end-placeholder="结束时间" format="YYYY-MM-DD"
                                            value-format="YYYY-MM-DD" style="width: 100%;" @change="handleDateChange" />
                                    </el-form-item>
                                </el-col>

                                <!-- 操作按钮 -->
                                <el-col :span="24">
                                    <div
                                        style="display: flex; justify-content: flex-end; align-items: center; margin-bottom: 10px;">
                                        <el-button circle @click="handleRefresh" style="margin-left: 10px;">
                                            <el-icon>
                                                <Refresh />
                                            </el-icon>
                                        </el-button>
                                    </div>
                                </el-col>
                            </el-row>
                        </el-form>
                    </el-card>

                    <!-- 日志表格 -->
                    <el-card shadow="never">
                        <el-table :data="tableData" border :loading="loading" style="width: 100%;" v-loading="loading">
                            <el-table-column prop="event_time" label="时间" width="160" />
                            <el-table-column prop="username" label="用户名" width="120">
                                <template #default="scope">
                                    <el-link :underline="false">{{ scope.row.username }}</el-link>
                                </template>
                            </el-table-column>
                            <el-table-column prop="ip_address" label="IP" width="140" />
                            <el-table-column prop="behavior_type" label="行为类型" width="120">
                                <template #default="scope">
                                    <el-tag :type="tagType(scope.row.behavior_type)">
                                        {{ scope.row.behavior_type }}
                                    </el-tag>
                                </template>
                            </el-table-column>
                            <el-table-column prop="detail" label="详情" show-overflow-tooltip />
                        </el-table>

                        <!-- 分页 -->
                        <div class="pagination-container">
                            <el-pagination
                            background
                            layout="total, sizes, prev, pager, next, jumper"
                            :total="total"
                            :page-sizes="[10, 20, 30]"
                            v-model:current-page="pageNum"
                            v-model:page-size="pageSize"
                            @current-change="handlePageChange"
                            @size-change="handleSizeChange"
                            />
                        </div>
                    </el-card>
                </el-col>
            </el-row>
        </el-main>
    </el-container>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { getBehaviorLogList } from '@/api/log/log.js'
import { getGroupTree } from '@/api/terminal_admin/group.js'
import { getUsernameList } from '@/api/terminal_admin/terminal.js'


// 加载状态
const loading = ref(false)

// 分页数据
const pageNum = ref(1)
const pageSize = ref(10)
const total = ref(0)
const tableData = ref([])

// 筛选参数
const filters = ref({
    username: '',
    behavior_type: '',
    timeRange: [],
    group_id: null
})

// 分组树
const groupList = ref([])
const selectedGroupId = ref(0)
const groupFilter = ref('')
const defaultProps = { children: 'children', label: 'group_name' }

// 分组过滤函数
const filterGroup = (value, data) => data.group_name.includes(value)

// 加载分组树
const loadGroupTree = async () => {
  try {
    const res = await getGroupTree()
    if (res.data.code === 200 && Array.isArray(res.data.data)) {
      groupList.value = [
        { group_id: 0, group_name: '全部终端' },
        ...res.data.data
      ]
    } else {
      ElMessage.error(res.data.message || '分组树加载失败')
    }
  } catch (err) {
    ElMessage.error(err.message || '获取分组数据异常')
  }
}
// 分组点击事件
const handleGroupClick = (node) => {
    selectedGroupId.value = node.group_id
    filters.value.group_id = node.group_id === 0 ? null : node.group_id
    pageNum.value = 1
    handleSearch()
}

// 获取用户名
const usernameSuggestions = ref([])
const loadUsernameSuggestions = async () => {
  try {
    const res = await getUsernameList()
    usernameSuggestions.value = res.data.data || []
  } catch (err) {
    usernameSuggestions.value = []
    ElMessage.warning('终端用户名加载失败')
  }
}

// 模糊匹配
const getUsernameSuggestions = (query, cb) => {
  const result = usernameSuggestions.value
    .filter(name => name.toLowerCase().includes(query.toLowerCase()))
    .map(name => ({ value: name }))
  cb(result)
}

// 获取日志
const loadBehaviorLogs = async () => {
  try {
    loading.value = true
    const [start, end] = filters.value.timeRange || []
    const params = {
      page: pageNum.value,
      page_size: pageSize.value,
      username: filters.value.username?.trim() || null,
      behavior_type: filters.value.behavior_type || null,
      group_id: filters.value.group_id || null,
      start_date: start || null,
      end_date: end || null
    }
    const res = await getBehaviorLogList(params)
    tableData.value = res.data.list
    total.value = res.data.total
  } catch (err) {
    ElMessage.error('加载失败')
  } finally {
    loading.value = false
  }
}

// 查询
const handleSearch = () => {
  pageNum.value = 1
  loadBehaviorLogs()
}


// 分页变化
const handlePageChange = (val) => {
    pageNum.value = val
    handleSearch()
}

const handleSizeChange = (val) => {
    pageSize.value = val
    pageNum.value = 1
    handleSearch()
}

const handleDateChange = () => {
    handleSearch()
}

// 刷新按钮
const handleRefresh = () => {
    loadGroupTree()
    loadUsernameSuggestions()
    handleSearch()
}

const tagType = (type) => {
    switch (type) {
        case '网站访问': return 'success'
        case '搜索行为': return 'info'
        case '进程运行': return 'warning'
        default: return 'default'
    }
}

// 初始化
onMounted(() => {
    loadGroupTree()
    loadUsernameSuggestions()
    loadBehaviorLogs()
})
</script>

<style scoped>
.log-behavior-container {
    padding: 0 15px;
}

.mb-2 {
    margin-bottom: 15px;
}

.pagination-container {
    display: flex;
    justify-content: flex-end;
    padding: 10px 20px;
    margin-top: 20px;
}
</style>
