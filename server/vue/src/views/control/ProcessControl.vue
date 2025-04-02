<template>
    <el-container class="process-control-container">
        <el-main>
            <!-- 操作 -->
            <el-card shadow="never" class="card-spacing">
                <el-icon size="small">
                    <Tickets />
                </el-icon>
                <span> 数据列表</span>

                <el-button size="mini" circle @click="fetchData" style="float:right" :loading="loading">
                    <el-icon>
                        <RefreshRight />
                    </el-icon>
                </el-button>
                <el-button size="mini" @click="dialogVisible = true"
                    style="float:right;margin-right: 15px">添加</el-button>
                <el-button size="mini" :disabled="!multipleSelection.length" @click="handleBatchDelete"
                    style="margin-left: 15px">
                    删除所选
                </el-button>
            </el-card>

            <!-- 数据 -->
            <el-table v-loading="loading" :data="tableData" border style="width: 100%;" height="500px"
                @selection-change="handleSelectionChange">
                <el-table-column type="selection" width="55" />
                <el-table-column label="进程名称/路径" prop="process_name" />
                <el-table-column label="状态" width="100">
                    <template #default="scope">
                        <el-switch v-model="scope.row.status" :active-value="1" :inactive-value="0"
                            @change="val => handleToggle(scope.row.id, val)" />
                    </template>
                </el-table-column>
                <el-table-column label="操作" width="100">
                    <template #default="scope">
                        <el-button type="text" size="small" @click="handleDelete(scope.row.id)">删除</el-button>
                    </template>
                </el-table-column>
            </el-table>

        </el-main>

        <!-- 添加进程 -->
        <el-dialog title="添加进程" v-model="dialogVisible" width="500px">
            <el-alert type="info" :closable="false" show-icon
                title="支持关键词匹配;系统将自动去重并进行包含匹配（不支持完整路径）。"
                style="margin-bottom: 20px" />

            <el-form>
                <el-form-item label="进程关键词">
                    <el-input type="textarea" rows="6" v-model="addInput"
                        placeholder="请输入进程名或关键词，每行一个，如：game.exe、vpn、chrome" />
                </el-form-item>
            </el-form>

            <template #footer>
                <el-button @click="dialogVisible = false">取消</el-button>
                <el-button type="primary" @click="submitAdd">添加</el-button>
            </template>
        </el-dialog>

    </el-container>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
    getProcessList,
    addBatchProcess,
    deleteSingleProcess,
    deleteBatchProcess,
    toggleProcessStatus
} from '@/api/control/process_control'

const loading = ref(false)
const tableData = ref([])
const multipleSelection = ref([])
const dialogVisible = ref(false)
const addInput = ref('')

// 获取数据
const fetchData = async () => {
    loading.value = true
    const res = await getProcessList()
    loading.value = false
    if (res.code === 200) {
        tableData.value = res.data
    }
}

// 添加
const submitAdd = async () => {
    const list = addInput.value.split('\n').map(s => s.trim()).filter(s => s)
    if (!list.length) return ElMessage.warning('请输入至少一个进程')
    const res = await addBatchProcess({ process_list: list })
    if (res.code === 200) {
        ElMessage.success('添加成功')
        dialogVisible.value = false
        addInput.value = ''
        fetchData()
    }
}

// 删除单个
const handleDelete = async (id) => {
    try {
        await ElMessageBox.confirm('确认删除该规则？', '提示', { type: 'warning' })
        await deleteSingleProcess({ id })
        ElMessage.success('删除成功')
        fetchData()
    } catch (e) { }
}

// 批量删除
const handleBatchDelete = async () => {
    const ids = multipleSelection.value.map(row => row.id)
    if (!ids.length) return
    try {
        await ElMessageBox.confirm(`确认删除 ${ids.length} 条规则？`, '提示', { type: 'warning' })
        await deleteBatchProcess({ ids })
        ElMessage.success('批量删除成功')
        fetchData()
    } catch (e) { }
}

// 状态切换
const handleToggle = async (id, nextStatus) => {
    const actionText = nextStatus === 1 ? '启用' : '禁用'
    const originalItem = tableData.value.find(item => item.id === id)
    const originalStatus = originalItem ? originalItem.status : (nextStatus === 1 ? 0 : 1)

    try {
        await ElMessageBox.confirm(`确定要${actionText}该规则？`, '确认操作', {
            type: 'warning',
            confirmButtonText: '确定',
            cancelButtonText: '取消'
        })

        const res = await toggleProcessStatus({ id, status: nextStatus })
        if (res.code === 200) {
            ElMessage.success(`${actionText}成功`)
            fetchData()
        } else {
            ElMessage.error(res.message || `${actionText}失败`)
            if (originalItem) originalItem.status = originalStatus // 还原
        }
    } catch (e) {
        if (originalItem) originalItem.status = originalStatus
    }
}

// 多选变化
const handleSelectionChange = (val) => {
    multipleSelection.value = val
}

onMounted(fetchData)
</script>

<style scoped>
.process-control-container {
    padding: 0 15px;
}

.card-spacing {
    margin-top: 18px;
    margin-bottom: 16px;
    height: auto;
}
</style>