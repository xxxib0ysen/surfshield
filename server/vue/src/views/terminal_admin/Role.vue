<template>
    <el-container class="role-container">
        <el-main>
            <!-- 操作栏 -->
            <el-card shadow="never" class="card-spacing">
                <el-icon size="small">
                    <Tickets />
                </el-icon>
                <span> 数据列表</span>
                <el-button size="mini" circle @click="refreshPage" style="float:right" :loading="loading">
                    <el-icon>
                        <RefreshRight />
                    </el-icon>
                </el-button>
                <el-button size="mini" @click="openAddDialog" style="float:right;margin-right: 15px">新增角色</el-button>
            </el-card>

            <el-row :gutter="20">
                <!-- 角色列表 -->
                <el-col :span="4" class="sidebar-wrapper">
                    <el-scrollbar height="500px">
                        <el-menu class="sidebar-menu" :default-active="String(currentRoleId)" @select="handleSelectRole"
                            text-color="#333">
                            <el-menu-item v-for="item in roleList" :key="item.role_id" :index="String(item.role_id)">
                                {{ item.role_name }}
                            </el-menu-item>
                        </el-menu>
                    </el-scrollbar>
                </el-col>

                <!-- 角色详情 -->
                <el-col :span="20">
                    <el-card shadow="never" class="detail-card" v-if="currentRole">
                        <el-table :data="[currentRole]" border style="width: 100%">
                            <el-table-column label="角色名称" width="180px">
                                <template #default="scope">
                                    <el-input 
                                        v-model="scope.row.role_name" 
                                        @change="confirmSave" 
                                        class="editable-input"
                                        />
                                </template>
                            </el-table-column>
                            <el-table-column label="说明">
                                <template #default="scope">
                                    <el-input type="textarea" v-model="scope.row.description" :rows="1"
                                        @change="confirmSave" class="editable-input" />
                                </template>
                            </el-table-column>
                            <el-table-column label="启用状态" width="140">
                                    <el-switch :model-value="currentRole.status" :active-value="1" :inactive-value="0"
                                        @change="val => confirmToggleStatus(currentRole.role_id, val)" />
                            </el-table-column>
                            <el-table-column label="操作" width="140">
                                <template #default="scope">
                                    <el-button type="text" icon="Delete"
                                        @click="confirmDelete(scope.row.role_id)">删除</el-button>
                                </template>
                            </el-table-column>
                        </el-table>

                        <div style="margin-top: 25px;">
                            <div style="font-weight: bold; margin-bottom: 10px;">权限绑定</div>
                            <el-checkbox-group v-model="currentRole.permissions">
                                <el-checkbox v-for="perm in permissionList" :key="perm.id" :label="perm.id">
                                    {{ perm.name }}
                                </el-checkbox>
                            </el-checkbox-group>
                        </div>

                        <div class="footer-btns">
                            <el-button @click="cancelEdit">取消</el-button>
                            <el-button type="primary" @click="confirmSave">保存</el-button>
                        </div>
                    </el-card>
                </el-col>
            </el-row>
            <!-- 新增角色 -->
            <el-dialog v-model="dialogVisible" title="新增角色" width="500px">
                <el-form :model="addForm" label-width="100px" ref="addFormRef" :rules="rules">
                    <el-form-item label="角色名称" prop="role_name">
                        <el-input v-model="addForm.role_name" placeholder="请输入角色名" style="width: 80%;" />
                    </el-form-item>
                    <el-form-item label="说明">
                        <el-input type="textarea" v-model="addForm.description" placeholder="请输入说明" :rows="5"
                            style="width: 80%;" />
                    </el-form-item>
                </el-form>
                <template #footer>
                    <el-button @click="dialogVisible = false">取消</el-button>
                    <el-button type="primary" @click="confirmAdd">确定</el-button>
                </template>
            </el-dialog>
        </el-main>
    </el-container>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
    getAllRoles, getRoleDetail, updateRole, deleteRole, addRole,updateRoleStatus
} from '@/api/terminal_admin/role'

const roleList = ref([])
const currentRole = ref(null)
const currentRoleId = ref(null)
const permissionList = ref([])

const loading = ref(false)
const dialogVisible = ref(false)
const addForm = ref({ role_name: '', description: '', permissions: [], status: 0 })
const addFormRef = ref(null)

const rules = {
    role_name: [{ required: true, message: '请输入角色名称', trigger: 'blur' }]
}

const originalRole = ref({})


// 加载角色列表（默认第一个）
const loadData = async () => {
    loading.value = true
    try {
        const res = await getAllRoles()
        if (res.data.code === 200) {
            roleList.value = res.data.data
            if (roleList.value.length > 0) {
                await handleSelectRole(roleList.value[0].role_id)
            }
        } else {
            ElMessage.error(res.data.message || '获取角色失败')
        }
    } catch (err) {
        console.error('角色加载失败', err)
        ElMessage.error('加载角色失败')
    } finally {
        loading.value = false
    }
}

// 加载权限列表
const loadPermissions = async () => {
}


// 选择角色并加载详情
const handleSelectRole = async (roleId) => {
    currentRoleId.value = roleId
    try {
        const res = await getRoleDetail(roleId)
        if (res.data.code === 200) {
            currentRole.value = res.data.data
            originalRole.value = JSON.parse(JSON.stringify(res.data.data)) //拷贝
        }
    } catch (err) {
        console.error('加载角色详情失败', err)
    }
}

// 保存
let saving = false
const confirmSave = async () => {
    if (saving) return
    if (!currentRole.value.role_name.trim()) {
        ElMessage.warning('角色名称不能为空')
        refreshPage()
        return
    }
    try {
        await ElMessageBox.confirm('是否保存当前角色修改？', '确认保存', {
            type: 'warning',
            confirmButtonText: '保存',
            cancelButtonText: '取消'
        })
        saving = true
        const res = await updateRole(currentRole.value)
        if (res.data.code === 200) {
            ElMessage.success('保存成功')
            refreshPage()
        } else {
            ElMessage.error(res.data.message || '保存失败')
        }
    } catch (err) {
        ElMessage.info('已取消保存')
        currentRole.value = JSON.parse(JSON.stringify(originalRole.value))
    } finally {
        saving = false
    }
}


// 启用/禁用角色
const confirmToggleStatus = async (id, nextStatus) => {
  const actionText = nextStatus === 1 ? '启用' : '禁用'
  const originalStatus = currentRole.value.status

  try {
    await ElMessageBox.confirm(`确定要${actionText}该角色吗？`, '确认操作', {
      type: 'warning',
      confirmButtonText: '确定',
      cancelButtonText: '取消'
    })

    // 发送请求
    const res = await updateRoleStatus({ role_id: id, status: nextStatus })

    if (res.data.code === 200) {
      ElMessage.success(`${actionText}成功`)
      currentRole.value.status = nextStatus
    } else {
      ElMessage.error(res.data.message || `${actionText}失败`)
      currentRole.value.status = originalStatus 
    }
  } catch (err) {
    currentRole.value.status = originalStatus 
    ElMessage.info('已取消操作')
  }
}

// 删除角色
const confirmDelete = async (roleId) => {
    try {
        await ElMessageBox.confirm('确认删除该角色？', '警告', {
            type: 'warning',
            confirmButtonText: '删除',
            cancelButtonText: '取消'
        })

        const res = await deleteRole({ role_id: roleId })
        if (res.data.code === 200) {
            ElMessage.success('删除成功')
            refreshPage()
        } else {
            ElMessage.error(res.data.message || '删除失败')
        }
    } catch (err) {
        ElMessage.info('已取消删除')
    }
}


// 取消编辑
const cancelEdit = () => {
    currentRole.value = null
}

// 弹窗
const openAddDialog = () => {
    dialogVisible.value = true
    addForm.value = { role_name: '', description: '', permissions: [], status: 0 }
}

// 新增角色
const confirmAdd = () => {
    addFormRef.value.validate(async (valid) => {
        if (!valid) return
        try {
            const res = await addRole({ ...addForm.value, permissions: [], status: 0 })
            if (res.data.code === 200) {
                ElMessage.success('新增成功')
                dialogVisible.value = false
                refreshPage()
            } else {
                ElMessage.error(res.data.message || '新增失败')
            }
        } catch (err) {
            console.error('新增失败', err)
            ElMessage.error('新增失败')
        }
    })
}

// 刷新
const refreshPage = async () => {
    await loadPermissions()
    await loadData()
}

onMounted(() => {
    loadPermissions()
    loadData()
})
</script>

<style scoped>
.role-container {
    padding: 0 15px;
}

.card-spacing {
    margin: 18px 0 12px;
}

.detail-card {
    min-height: 500px;
    padding-bottom: 80px;
    position: relative;
}

.footer-btns {
    position: absolute;
    bottom: 40px;
    left: 0;
    right: 0;
    text-align: center;
}

.role-menu {
    border: none;
}

.sidebar-wrapper {
    background: #ffffff;
    border-right: 1px solid #dcdfe6;
    height: 100%;
    padding: 10px 0;
}

.sidebar-menu {
    border: none;
    background-color: #f5f7fa;
    width: 100%;
}

.sidebar-menu .el-menu-item {
    height: 40px;
    line-height: 40px;
    font-size: 14px;
    padding-left: 20px;
}

.sidebar-menu .el-menu-item.is-active {
    background-color: #e6f7ff !important;
    color: #409EFF !important;
    font-weight: bold;
}

:deep(.editable-input .el-input__wrapper) {
  border: none !important;
  background-color: transparent !important;
  box-shadow: none !important;
  padding: 0 !important;
}

:deep(.editable-input .el-input__inner) {
  background-color: transparent !important;
  border: none !important;
  box-shadow: none !important;
  padding: 0 !important;
  font-size: 14px;
}
:deep(.editable-input .el-textarea__inner) {
  border: none !important;
  background-color: transparent !important;
  box-shadow: none !important;
  padding: 0 !important;
  font-size: 14px;
  line-height: 1.5;
  resize: none !important;
}
</style>
