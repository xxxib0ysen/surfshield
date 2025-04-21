<template>
    <el-container class="log-operation-container">
        <el-main>
            <el-row gutter="20">
                <el-col :span="24">
                    <!-- 筛选区域 -->
                    <el-card shadow="never" class="mb-2">
                        <el-form :model="filters" label-position="left">
                            <el-row :gutter="20">
                                <!-- 用户 -->
                                <el-col :span="8">
                                    <el-form-item label="用户：">
                                        <el-autocomplete v-model="filters.admin_name"
                                            :fetch-suggestions="getAdminSuggestions" placeholder="请输入" clearable
                                            @clear="handleSearch"  @select="handleSearch" 
                                            @keyup.enter.native="handleSearch">
                                            <template #suffix>
                                                <el-icon @click="handleSearch" style="cursor: pointer">
                                                    <Search />
                                                </el-icon>
                                            </template>
                                        </el-autocomplete>
                                    </el-form-item>
                                </el-col>

                                <!-- 模块 -->
                                <el-col :span="8">
                                    <el-form-item label="模块：">
                                        <el-select v-model="filters.module" placeholder="请选择" clearable
                                            @clear="handleSearch" @change="handleSearch">
                                            <el-option v-for="m in moduleOptions" :key="m" :label="m" :value="m" />
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

                                <el-col :span="24">
                                <div class="actions">
                                    <el-button circle @click="handleRefresh">
                                    <el-icon><Refresh /></el-icon>
                                    </el-button>
                                </div>
                                </el-col>
                            </el-row>
                        </el-form>
                    </el-card>

                    <!-- 日志表格 -->
                    <el-card shadow="never" :loading="loading">
                        <el-table :data="tableData" border :loading="loading" style="width: 100%;" size="large">
                            <el-table-column prop="created_at" label="操作时间" />
                            <el-table-column prop="admin_name" label="用户">
                                <template #default="{ row }">
                                    <el-tag  type="info">{{ row.admin_name }}</el-tag>
                                </template>
                            </el-table-column>
                            <el-table-column prop="ip_address" label="IP地址" />
                            <el-table-column prop="module" label="操作模块">
                                <template #default="{ row }">
                                    <el-tag size="small" type="success">{{ row.module }}</el-tag>
                                </template>
                            </el-table-column>
                            <el-table-column prop="action" label="行为" />
                            <el-table-column prop="detail" label="操作详情" show-overflow-tooltip />
                        </el-table>

                        <!-- 分页 -->
                        <div class="pagination-container">
                            <el-pagination background layout="total, sizes, prev, pager, next, jumper" :total="total"
                                :page-size="pageSize" :current-page="pageNum" :page-sizes="[10, 20, 50]"
                                @current-change="handlePageChange" @size-change="handleSizeChange" />
                        </div>
                    </el-card>
                </el-col>
            </el-row>
        </el-main>
    </el-container>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import { ElMessage } from 'element-plus'
import { getOperationLogList, getModuleList } from '@/api/log/log'
import { getAdminNameList } from '@/api/terminal_admin/admin'

// 加载状态
const loading = ref(false)

// 筛选项
const filters = ref({
    admin_name: '',
    module: '',
    timeRange: []
})

// 分页数据
const pageNum = ref(1)
const pageSize = ref(10)
const total = ref(0)
const tableData = ref([])

// 模块动态选项
const moduleOptions = ref([])

// 用户建议
const adminSuggestions = ref([])

// 加载日志
const loadOperationLogs = async () => {
    try {
        loading.value = true
        const params = {
            page: pageNum.value,
            page_size: pageSize.value,
        }
        if (filters.value.admin_name?.trim()) params.admin_name = filters.value.admin_name.trim()
        if (filters.value.module?.trim()) params.module = filters.value.module.trim()
        if (filters.value.timeRange?.length === 2) {
            params.start_date = filters.value.timeRange[0]
            params.end_date = filters.value.timeRange[1]
        }

        const res = await getOperationLogList(params)
        tableData.value = res.data.data.data
        total.value = res.data.data.total
    } catch (err) {
        ElMessage.error(err.message || '请求失败')
    } finally {
        setTimeout(() => {
            loading.value = false
        }, 300)
    }
}

// 加载模块选项
const loadModules = async () => {
    const res = await getModuleList()
    moduleOptions.value = res.data.data || []
}

// 用户列表
const getAdminSuggestions = (queryString, cb) => {
  const results = adminSuggestions.value
    .filter(name => name.toLowerCase().includes(queryString.toLowerCase()))
    .map(name => ({ value: name })) 

  cb(results)
}

// 加载用户名称列表
const loadAdminSuggestions = async () => {
    try {
        const res = await getAdminNameList()
        adminSuggestions.value = res.data.data || []
    } catch (err) {
        adminSuggestions.value = []
        ElMessage.warning('管理员名称加载失败')
    }
}



// 搜索/筛选
const handleSearch = () => {
    pageNum.value = 1
    loadOperationLogs()
}
const handlePageChange = (val) => {
    pageNum.value = val
    loadOperationLogs()
}
const handleSizeChange = (val) => {
    pageSize.value = val
    pageNum.value = 1
    loadOperationLogs()
}
const handleDateChange = () => {
    handleSearch()
}
const handleRefresh = () => {
    loadModules()
    loadAdminSuggestions()
    loadOperationLogs()
    ElMessage.success('刷新成功')
}


onMounted(() => {
    loadModules()
    loadAdminSuggestions()
    loadOperationLogs()
})
</script>

<style scoped>
.log-operation-container {
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

.actions {
    display: flex;
    justify-content: flex-end;
    align-items: center;
    margin-bottom: 10px;
    gap: 10px;
}
</style>
