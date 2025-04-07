<template>
    <el-container class="admin-container">
        <el-main>
            <!-- 操作栏 -->
            <el-card shadow="never" class="card-spacing">
                <el-icon size="small">
                    <Tickets />
                </el-icon>
                <span> 角色列表</span>
                <el-button size="mini" circle @click="loadData" style="float:right" :loading="loading">
                    <el-icon>
                        <RefreshRight />
                    </el-icon>
                </el-button>
                <el-button size="mini" @click="openAddDialog" style="float:right;margin-right: 15px">新增角色</el-button>
            </el-card>

            <!-- 数据表格 -->
            <el-table v-loading="loading" :data="tableData" border style="width: 100%" :max-height="500">
                <el-table-column prop="role_name" label="角色名称" />
                <el-table-column prop="description" label="说明" />
                <el-table-column label="启用状态" width="140">
                    <template #default="scope">
                        <el-switch v-model="scope.row.status" :active-value="1" :inactive-value="0"
                            @change="val => confirmToggleStatus(scope.row.role_id, val)" />
                    </template>
                </el-table-column>
                <el-table-column label="操作" width="200">
                    <template #default="scope">
                        <el-button type="text" icon="Edit" @click="openEditDialog(scope.row)">编辑</el-button>
                        <el-button type="text" icon="Delete" @click="confirmDelete(scope.row.role_id)">删除</el-button>
                    </template>
                </el-table-column>
            </el-table>

            <!-- 分页 -->
            <div class="pagination-container">
                <el-pagination background layout="total, prev, pager, next, jumper" :total="total" :page-size="6"
                    :current-page="query.page" @current-change="handlePageChange" />
            </div>
        </el-main>

        <!-- 弹窗 -->
        <el-dialog v-model="dialogVisible" :title="isEdit ? '编辑角色' : '新增角色'" width="500px">
            <el-form :model="form" :rules="rules" ref="formRef" label-width="120px">
                <el-form-item label="角色名称" prop="role_name">
                    <el-input v-model="form.role_name" placeholder="请输入角色名称" style="width: 80%;" />
                </el-form-item>
                <el-form-item label="说明">
                    <el-input type="textarea" v-model="form.description" placeholder="请输入说明" style="width: 80%;"
                        :rows="5" />
                </el-form-item>
            </el-form>

            <template #footer>
                <el-button @click="dialogVisible = false">取消</el-button>
                <el-button type="primary" @click="submitForm">保存</el-button>
            </template>
        </el-dialog>
    </el-container>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
    getRoleList, addRole, updateRole,
    deleteRole, updateRoleStatus
} from '@/api/terminal_admin/role'
import { Tickets, RefreshRight } from '@element-plus/icons-vue'

const tableData = ref([])
const total = ref(0)
const loading = ref(false)
const query = ref({ page: 1 })

const dialogVisible = ref(false)
const isEdit = ref(false)
const formRef = ref(null)
const form = ref({
    role_id: null,
    role_name: '',
    description: '',
    permissions: [],
    status: 0
})

const rules = {
    role_name: [{ required: true, message: '请输入角色名称', trigger: 'blur' }]
}

// 获取角色列表
const loadData = async () => {
    loading.value = true
    try {
        const res = await getRoleList(query.value.page, 6)
        if (res.data.code === 200) {
            tableData.value = res.data.data.data
            total.value = res.data.data.total
        } else {
            ElMessage.error(res.data.message || '获取列表失败')
        }
    } catch (err) {
        console.error('加载失败：', err)
        ElMessage.error('加载角色列表失败')
    } finally {
        loading.value = false
    }
}

// 打开新增角色弹窗
const openAddDialog = () => {
    isEdit.value = false
    dialogVisible.value = true
    form.value = { role_id: null, role_name: '', description: '', permissions: [], status: 0 }
}

// 打开编辑角色弹窗
const openEditDialog = (row) => {
    isEdit.value = true
    dialogVisible.value = true
    form.value = { ...row, permissions: [] }
}

// 提交表单
const submitForm = () => {
    formRef.value.validate(async (valid) => {
        if (!valid) return
        try {
            const res = isEdit.value
                ? await updateRole(form.value)
                : await addRole(form.value)
            if (res.data.code === 200) {
                ElMessage.success(res.data.message)
                dialogVisible.value = false
                loadData()
            } else {
                ElMessage.error(res.data.message || '保存失败')
            }
        } catch (err) {
            console.error('保存失败：', err)
            ElMessage.error('保存角色失败')
        }
    })
}

// 切换状态
const confirmToggleStatus = (id, status) => {
    ElMessageBox.confirm(`确认要${status ? '启用' : '禁用'}该角色吗？`, '提示', {
        type: 'warning'
    }).then(async () => {
        try {
            await updateRoleStatus({ role_id: id, status })
            ElMessage.success('状态更新成功')
            loadData()
        } catch (err) {
            console.error('切换状态失败：', err)
            ElMessage.error('状态更新失败')
        }
    })
}

// 删除角色
const confirmDelete = (id) => {
    ElMessageBox.confirm('确认删除该角色？', '警告', {
        type: 'warning'
    }).then(async () => {
        try {
            const res = await deleteRole({ role_id: id })
            if (res.data.code === 200) {
                ElMessage.success(res.data.message)
                loadData()
            } else {
                ElMessage.error(res.data.message || '删除失败')
            }
        } catch (err) {
            console.error('删除失败：', err)
            ElMessage.error('删除角色失败')
        }
    })
}

// 分页
const handlePageChange = (val) => {
    query.value.page = val
    loadData()
}

onMounted(() => {
    loadData()
})
</script>

<style scoped>
.admin-container {
    padding: 0 15px;
}

.card-spacing {
    margin-top: 18px;
    margin-bottom: 16px;
}

.pagination-container {
    display: flex;
    justify-content: flex-end;
    padding: 10px 20px;
    margin-top: 20px;
}
</style>