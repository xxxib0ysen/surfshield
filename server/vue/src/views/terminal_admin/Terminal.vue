<template>
    <div class="terminal-list-container">
        <el-row gutter="20">
            <!-- 左侧分组树 -->
            <el-col :span="4">
                <el-input v-model="groupFilter" placeholder="输入关键词进行过滤" clearable size="small" />
                <el-tree class="group-tree" :data="groupList" :props="defaultProps" node-key="group_id"
                    default-expand-all highlight-current :filter-node-method="filterGroup"
                    @node-click="handleGroupClick" />
            </el-col>

            <!-- 右侧主区域 -->
            <el-col :span="20">
                <!-- 查询表单 -->
                <el-card class="filter-card">
                    <el-form :inline="true" :model="filters" size="small">
                        <el-form-item label="用户名">
                            <el-input v-model="filters.username" placeholder="请输入" clearable />
                        </el-form-item>
                        <el-form-item label="在线状态">
                            <el-select v-model="filters.status" placeholder="请选择" clearable>
                                <el-option label="在线" :value="1" />
                                <el-option label="离线" :value="0" />
                            </el-select>
                        </el-form-item>
                        <el-form-item label="计算机名">
                            <el-input v-model="filters.hostname" placeholder="请输入" clearable />
                        </el-form-item>
                        <el-form-item label="IP">
                            <el-input v-model="filters.ip_address" placeholder="请输入" clearable />
                        </el-form-item>
                        <el-form-item label="唯一标识符">
                            <el-input v-model="filters.uuid" placeholder="请输入" clearable />
                        </el-form-item>
                        <el-form-item label="操作系统">
                            <el-input v-model="filters.os_name" placeholder="请输入" clearable />
                        </el-form-item>
                        <el-form-item label="系统版本">
                            <el-input v-model="filters.os_version" placeholder="请输入" clearable />
                        </el-form-item>
                        <el-form-item>
                            <el-switch v-model="filters.fuzzy" active-text="模糊匹配" />
                        </el-form-item>
                        <el-form-item>
                            <el-button type="primary" @click="fetchData">搜索</el-button>
                            <el-button @click="resetFilters">重置</el-button>
                        </el-form-item>
                    </el-form>
                </el-card>

                <!-- 表格操作栏 -->
                <div class="toolbar">
                    <el-button type="primary" size="small" :disabled="!multipleSelection.length"
                        @click="openMoveDialog">
                        移动到分组
                    </el-button>
                </div>

                <!-- 表格 -->
                <el-table :data="tableData" border stripe highlight-current-row
                    @selection-change="handleSelectionChange">
                    <el-table-column type="selection" width="50" />
                    <el-table-column label="用户名" prop="username" min-width="100">
                        <template #default="scope">
                            <el-link type="primary" @click="openDetail(scope.row)">{{ scope.row.username }}</el-link>
                        </template>
                    </el-table-column>
                    <el-table-column label="在线状态" prop="status" width="80">
                        <template #default="scope">
                            <el-tag v-if="scope.row.status === 1" type="success">在线</el-tag>
                            <el-tag v-else type="info">离线</el-tag>
                        </template>
                    </el-table-column>
                    <el-table-column label="计算机名" prop="hostname" />
                    <el-table-column label="操作系统" prop="os_name" />
                    <el-table-column label="IP" prop="ip_address" />
                </el-table>

                <!-- 分页 -->
                <el-pagination background layout="prev, pager, next, total" :total="pagination.total"
                    :current-page.sync="pagination.page" :page-size.sync="pagination.pageSize"
                    @current-change="fetchData" />
            </el-col>
        </el-row>

        <!-- 终端详情弹窗 -->
        <TerminalDetail v-if="detailDialog.visible" :terminal="detailDialog.data"
            @close="detailDialog.visible = false" />
    </div>
</template>

<script setup>
import { ref, reactive, watch } from 'vue'
import TerminalDetail from './TerminalDetail.vue'
import { getTerminalList, moveTerminalToGroup } from '@/api/terminal_admin/terminal'

const groupFilter = ref('')
const groupList = ref([])
const defaultProps = { children: 'children', label: 'group_name' }

const filters = reactive({
    username: '', hostname: '', ip_address: '', uuid: '', os_name: '', os_version: '', status: '', fuzzy: false
})

const pagination = reactive({ page: 1, pageSize: 10, total: 0 })
const tableData = ref([])
const multipleSelection = ref([])
const currentGroupId = ref(null)

const detailDialog = reactive({ visible: false, data: {} })

const fetchData = async () => {
    // TODO: 调用 getTerminalList(filters, pagination, currentGroupId)
    // 并设置 tableData.value、pagination.total
}

const resetFilters = () => {
    Object.assign(filters, { username: '', hostname: '', ip_address: '', uuid: '', os_name: '', os_version: '', status: '', fuzzy: false })
    fetchData()
}

const handleSelectionChange = (val) => {
    multipleSelection.value = val
}

const openDetail = (row) => {
    detailDialog.data = row
    detailDialog.visible = true
}

const openMoveDialog = () => {
    // TODO: 弹出选择分组对话框，调用 moveTerminalToGroup
}

const filterGroup = (value, data) => {
    if (!value) return true
    return data.group_name.includes(value)
}

const handleGroupClick = (node) => {
    currentGroupId.value = node.group_id
    fetchData()
}
</script>

<style scoped>
.terminal-list-container {
    padding: 20px;
}

.group-tree {
    border: 1px solid #dcdfe6;
    padding: 10px;
}

.filter-card {
    margin-bottom: 15px;
}

.toolbar {
    margin: 10px 0;
    display: flex;
    justify-content: flex-start;
}
</style>