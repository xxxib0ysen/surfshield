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

                <!-- 右侧内容 -->
                <el-col :span="20">
                    <!-- 筛选区域 -->
                    <el-card shadow="never" class="mb-2">
                        <el-form :model="filters" label-position="left">
                            <el-row :gutter="20">
                                <el-col :span="8">
                                    <el-form-item label="用户名：">
                                        <el-input v-model="filters.username" placeholder="请输入" clearable
                                            @clear="handleRefresh" @keyup.enter="handleSearch">
                                            <template #suffix>
                                                <span @click="handleSearch" style="cursor: pointer;">
                                                    <el-icon class="search-icon">
                                                        <Search />
                                                    </el-icon>
                                                </span>
                                            </template>
                                        </el-input>
                                    </el-form-item>
                                </el-col>
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
                                        <el-button @click="handleExport">
                                            <el-icon>
                                                <Download />
                                            </el-icon> 导出
                                        </el-button>
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
                        <el-table :data="tableData" border :loading="loading" style="width: 100%;">
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
                            <el-pagination background layout="total, sizes, prev, pager, next, jumper" :total="total"
                                :page-size="pageSize" :page-sizes="[6, 10, 20]" :current-page="pageNum"
                                @current-change="handlePageChange" @size-change="handleSizeChange" />
                        </div>
                    </el-card>
                </el-col>
            </el-row>
        </el-main>
    </el-container>
</template>

<script setup>
import { ref } from 'vue'
import { ElMessage } from 'element-plus'

const loading = ref(false)

// 筛选项
const filters = ref({
    username: '',
    behavior_type: '',
    timeRange: [],
    group_id: null
})

// 分页
const pageNum = ref(1)
const pageSize = ref(10)
const total = ref(0)
const tableData = ref([]) // TODO: 接入接口数据

// 分组树
const groupList = ref([])
const selectedGroupId = ref(0)
const groupFilter = ref('')
const defaultProps = { children: 'children', label: 'group_name' }

const filterGroup = (value, data) => data.group_name.includes(value)
const handleGroupClick = (node) => {
    selectedGroupId.value = node.group_id
    filters.value.group_id = node.group_id === 0 ? null : node.group_id
    pageNum.value = 1
    handleSearch()
}

// 操作行为
const handleSearch = async () => {
  try {
    loading.value = true
    pageNum.value = 1
    // await 接口请求
  } catch (err) {
    ElMessage.error("加载失败")
  } finally {
    loading.value = false
  }
}

const handlePageChange = (val) => {
    pageNum.value = val
    handleSearch()
}
const handleSizeChange = (val) => {
    pageSize.value = val
    pageNum.value = 1
    handleSearch()
}
const handleDateChange = (val) => {
    // 仅在选择完一对起止时间后触发搜索
    if (val && val.length === 2) {
        handleSearch()
    }
}
const handleRefresh = () => {
    handleSearch()
}
const handleExport = () => {
    ElMessage.success('导出功能暂未实现')
}

// 行为类型标签样式
const tagType = (type) => {
    switch (type) {
        case '网站访问': return 'success'
        case '搜索行为': return 'info'
        case '进程运行': return 'warning'
        default: return 'default'
    }
}
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