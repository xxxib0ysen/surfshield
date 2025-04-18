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
                <el-button v-has-perm="'role:add'" size="mini" @click="openAddDialog"
                    style="float:right;margin-right: 15px">新增角色</el-button>
            </el-card>

            <el-row :gutter="20">
                <!-- 角色列表 -->
                <el-col :span="3" class="sidebar-wrapper">
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
                <el-col :span="21">
                    <el-card shadow="never" class="detail-card" v-if="currentRole">
                        <!-- 详情 -->
                        <el-table :data="[currentRole]" border style="width: 100%">
                            <el-table-column label="角色名称" width="180px">
                                <template #default="scope">
                                    <el-input v-has-perm="'role:edit'" v-model="scope.row.role_name"
                                        @change="confirmSave" class="editable-input" />
                                </template>
                            </el-table-column>
                            <el-table-column label="说明">
                                <template #default="scope">
                                    <el-input type="textarea" v-model="scope.row.description" :rows="1"
                                        v-has-perm="'role:edit'" @change="confirmSave" class="editable-input" />
                                </template>
                            </el-table-column>
                            <el-table-column label="启用状态" width="140">
                                <el-switch :model-value="currentRole.status" :active-value="1" :inactive-value="0"
                                    v-has-perm="'role:disable'"
                                    @change="val => confirmToggleStatus(currentRole.role_id, val)" />
                            </el-table-column>
                            <el-table-column label="操作" width="140">
                                <template #default="scope">
                                    <el-button type="text" icon="Delete" v-has-perm="'role:delete'"
                                        @click="confirmDelete(scope.row.role_id)">删除</el-button>
                                </template>
                            </el-table-column>
                        </el-table>

                        <!-- 权限绑定面板 -->
                        <div style="margin-top: 25px;">
                            <div style="font-weight: bold; margin-bottom: 10px;">权限绑定</div>
                            <el-collapse>
                                <el-collapse-item v-for="(items, module) in groupedPermissions" :key="module"
                                    :title="module">
                                    <template v-if="checkPerm('role:bind_permission')">
                                        <el-checkbox :indeterminate="isIndeterminate(module)"
                                            v-model="selectAllMap[module]" @change="val => toggleSelectAll(module, val)"
                                            style="margin-bottom: 10px;">
                                            全选
                                        </el-checkbox>
                                        <el-row :gutter="20">
                                            <el-col :span="12" v-for="(chunk, idx) in chunked(items, 2)" :key="idx">
                                                <el-checkbox-group v-model="currentRole.permissions">
                                                    <el-checkbox v-for="perm in chunk" :key="perm.id" :label="perm.id"
                                                        :disabled="!checkPerm('role:bind_permission')">
                                                        {{ perm.name }}
                                                    </el-checkbox>
                                                </el-checkbox-group>
                                            </el-col>
                                        </el-row>
                                    </template>
                                    <template v-else>
                                        <div style="color: #999; font-size: 14px;">暂无权限查看该模块权限</div>
                                    </template>
                                </el-collapse-item>
                            </el-collapse>
                        </div>

                        <div class="footer-btns">
                            <el-button v-has-perm="'role:edit'" @click="cancelEdit">取消</el-button>
                            <el-button v-has-perm="'role:edit'" type="primary" @click="confirmSave">保存</el-button>
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
import { ref, onMounted, computed } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
    getAllRoles, getRoleDetail, updateRole, deleteRole, addRole, updateRoleStatus
} from '@/api/terminal_admin/role'
import { bindPermissions, getGroupedPermissions } from '@/api/terminal_admin/perm'
import { useUserStore } from '@/stores/useUserStore'
import { useRouter } from 'vue-router'
import hasPerm from '@/utils/hasPerm'

const roleList = ref([])
const currentRole = ref(null)
const currentRoleId = ref(null)
const groupedPermissions = ref({})

const loading = ref(false)
const dialogVisible = ref(false)
const addForm = ref({ role_name: '', description: '', permissions: [], status: 0 })
const addFormRef = ref(null)

const rules = {
    role_name: [{ required: true, message: '请输入角色名称', trigger: 'blur' }]
}

const originalRole = ref({})
const userStore = useUserStore()
const router = useRouter()

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
        // console.error('角色加载失败', err)
        ElMessage.error(err?.response?.data?.detail || '您暂无访问角色权限，请联系管理员授权')
    } finally {
        loading.value = false
    }
}

// 加载权限列表
const loadPermissions = async () => {
    try {
        const res = await getGroupedPermissions()
        if (res.data.code === 200) {
            groupedPermissions.value = res.data.data
        } else {
            ElMessage.error(res.data.message || '获取权限失败')
        }
    } catch (err) {
        // console.error('加载权限失败', err)
        ElMessage.error(err?.response?.data?.detail || '您暂无访问权限列表权限，请联系管理员授权')
    }
}

// 两列权限展示
const chunked = (arr, cols) => {
    const mid = Math.ceil(arr.length / cols)
    return [arr.slice(0, mid), arr.slice(mid)]
}

//  判断当前模块是否已全选
const selectAllMap = computed(() => {
    const map = {}
    for (const module in groupedPermissions.value) {
        const perms = groupedPermissions.value[module]?.map(p => p.id) || []
        map[module] = perms.length > 0 && perms.every(p => currentRole.value.permissions.includes(p))
    }
    return map
})

// 判断当前模块是否为半选状态
const isIndeterminate = (module) => {
    const perms = groupedPermissions.value[module]?.map(p => p.id) || []
    const selected = perms.filter(p => currentRole.value.permissions.includes(p))
    return selected.length > 0 && selected.length < perms.length
}

// 全选
const toggleSelectAll = (module, val) => {
    const perms = groupedPermissions.value[module]?.map(p => p.id) || []
    if (val) {
        // 合并当前模块权限到已选权限中
        const newPermissions = new Set([...currentRole.value.permissions, ...perms])
        currentRole.value.permissions = Array.from(newPermissions)
    } else {
        // 从已选权限中移除当前模块的所有权限
        currentRole.value.permissions = currentRole.value.permissions.filter(id => !perms.includes(id))
    }
}

// 选择角色并加载详情
const handleSelectRole = async (roleId) => {
    currentRoleId.value = roleId
    try {
        const res = await getRoleDetail(roleId)
        if (res.data.code === 200) {
            currentRole.value = res.data.data
            originalRole.value = JSON.parse(JSON.stringify(res.data.data)) //拷贝
            currentRole.value.permissions ||= []
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
        // 判断权限是否变更
        const originalPerms = originalRole.value.permissions?.sort().join(',')
        const currentPerms = currentRole.value.permissions?.sort().join(',')
        const permissionsChanged = originalPerms !== currentPerms
        // 更新角色信息
        const res = await updateRole(currentRole.value)
        if (res.data.code !== 200) {
            ElMessage.error(res.data.message || '保存失败')
            return
        }
        // 更新权限
        const bindRes = await bindPermissions({
            role_id: currentRole.value.role_id,
            perm_ids: currentRole.value.permissions
        })
        if (bindRes.data.code !== 200) {
            ElMessage.error(bindRes.data.message || '权限保存失败')
            return
        }
        ElMessage.success('保存成功')

        // 判断是否当前用户改了自己的角色 && 权限有变更
        const currentUserRoleId = userStore.userInfo?.user?.role_id
        const modifiedRoleId = currentRole.value.role_id

        if (currentUserRoleId === modifiedRoleId && permissionsChanged) {
            const confirm = await ElMessageBox.alert(
                '您的权限已更新，请重新登录以生效',
                '提示',
                {
                    confirmButtonText: '确定',
                    type: 'warning'
                }
            ).catch(() => false)

            if (confirm) {
                userStore.logout()
                ElMessage.success('已退出登录')
                router.push('/login')
            }
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
    currentRole.value = {
        role_name: '',
        description: '',
        permissions: [],
        status: 0
    }
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

// 控制权限
const checkPerm = (code) => {
    return userStore.userInfo?.permissions?.includes(code)
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
    display: flex;
    flex-direction: column;
    padding: 20px;
}

.footer-btns {
    display: flex;
    justify-content: center;
    margin-top: 30px;
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
