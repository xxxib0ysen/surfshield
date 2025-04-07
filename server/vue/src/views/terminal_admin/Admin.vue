<template>
  <el-container class="admin-container">
    <el-main>
      <!-- 操作栏 -->
      <el-card shadow="never" class="card-spacing">
        <el-icon size="small">
          <Tickets />
        </el-icon>
        <span> 数据列表</span>
        <el-button size="mini" circle @click="loadData" style="float:right" :loading="loading">
          <el-icon>
            <RefreshRight />
          </el-icon>
        </el-button>
        <el-button size="mini" @click="openAddDialog" style="float:right;margin-right: 15px">新增用户</el-button>
      </el-card>

      <!-- 数据表格 -->
      <el-table v-loading="loading" :data="tableData" border style="width: 100%" :max-height="500">
        <el-table-column prop="admin_name" label="用户名" />
        <el-table-column label="角色">
          <template #default="scope">
            <el-tag size="small" type="info">
              {{ getRoleName(scope.row.role_id) || '未知' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="description" label="说明" />
        <el-table-column label="启用状态" width="140">
          <template #default="scope">
            <el-switch :model-value="scope.row.status" :active-value="1" :inactive-value="0"
              @change="val => confirmToggleStatus(scope.row.admin_id, val)" />
          </template>
        </el-table-column>
        <el-table-column label="操作" width="240">
          <template #default="scope">
            <el-button type="text" icon="Edit" @click="openEditDialog(scope.row)">编辑</el-button>
            <el-button type="text" icon="Refresh" @click="confirmReset(scope.row)">重置密码</el-button>
            <el-button type="text" icon="Delete" @click="confirmDelete(scope.row.admin_id)">删除</el-button>
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
    <el-dialog v-model="dialogVisible" :title="isEdit ? '编辑管理员' : '新增管理员'" width="500px">
      <el-form :model="form" :rules="rules" ref="formRef" label-width="120px">
        <el-form-item label="用户名" prop="admin_name" v-if="!isEdit">
          <el-input v-model="form.admin_name" placeholder="请输入用户名" style="width: 80%;" />
        </el-form-item>
        <el-form-item label="角色" prop="role_id">
          <el-select v-model="form.role_id" placeholder="请选择角色" style="width: 80%;">
            <el-option v-for="item in roleList" :key="item.role_id" :label="item.role_name" :value="item.role_id" />
          </el-select>
        </el-form-item>
        <el-form-item label="说明">
          <el-input type="textarea" v-model="form.description" placeholder="请输入说明" :rows="5" style="width: 80%;" />
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
  getAdminList, addAdmin, updateAdmin,
  resetPassword, deleteAdmin, updateStatus
} from '@/api/terminal_admin/admin'
import { getAllRoles } from '@/api/terminal_admin/role'

const tableData = ref([])
const total = ref(0)
const loading = ref(false)
const query = ref({ page: 1 })

const dialogVisible = ref(false)
const isEdit = ref(false)
const formRef = ref(null)
const form = ref({
  admin_id: null,
  admin_name: '',
  role_id: '',
  description: '',
  status: 0
})

const roleList = ref([])

const rules = {
  admin_name: [{ required: true, message: '请输入用户名', trigger: 'blur' }],
  role_id: [{ required: true, message: '请选择角色', trigger: 'change' }]
}

// 获取管理员列表
const loadData = async () => {
  loading.value = true
  try {
    const res = await getAdminList(query.value)
    if (res.data.code === 200) {
      tableData.value = res.data.data.data
      total.value = res.data.data.total
    } else {
      ElMessage.error(res.data.data.message || '获取列表失败')
    }
  } catch (err) {
    console.error('加载失败：', err)
    ElMessage.error('加载管理员列表失败')
  } finally {
    loading.value = false
  }
}

// 新增管理员
const openAddDialog = () => {
  isEdit.value = false
  dialogVisible.value = true
  form.value = { admin_id: null, admin_name: '', role_id: '', description: '', status: 0 }
  query.value.page = 1
  loadRoleList()
}

// 编辑管理员
const openEditDialog = (row) => {
  isEdit.value = true
  dialogVisible.value = true
  form.value = { ...row }
  loadRoleList()
}

// 保存
const submitForm = () => {
  formRef.value.validate(async (valid) => {
    if (!valid) return
    try {
      const res = isEdit.value
        ? await updateAdmin(form.value.admin_id, form.value)
        : await addAdmin(form.value)
      if (res.data.code === 200) {
        ElMessage.success(res.data.message)
        dialogVisible.value = false
        loadData()
      } else {
        ElMessage.error(res.data.message || '保存失败')
      }
    } catch (err) {
      console.error('提交失败：', err)
      ElMessage.error('保存管理员失败')
    }
  })
}

// 切换状态
const confirmToggleStatus = (id, status) => {
  ElMessageBox.confirm(`确认要${status ? '启用' : '禁用'}该用户吗？`, '提示', {
    type: 'warning'
  }).then(async () => {
    try {
      await updateStatus(id, status)
      ElMessage.success('状态更新成功')
      loadData()
    } catch (err) {
      console.error('切换状态失败：', err)
      ElMessage.error('状态更新失败')
    }
  })
}

// 删除管理员
const confirmDelete = (id) => {
  ElMessageBox.confirm('确认删除该管理员？', '警告', {
    type: 'warning'
  }).then(async () => {
    try {
      const res = await deleteAdmin(id)
      if (res.data.code === 200) {
        ElMessage.success(res.data.message)
        loadData()
      } else {
        ElMessage.error(res.data.message || '删除失败')
      }
    } catch (err) {
      console.error('删除失败：', err)
      ElMessage.error('删除管理员失败')
    }
  })
}

// 重置密码
const confirmReset = (row) => {
  ElMessageBox.confirm('确认将密码重置为默认密码（surfshield）？', '重置密码', {
    type: 'info'
  }).then(async () => {
    try {
      const res = await resetPassword(row.admin_id)
      if (res.data.code === 200) {
        ElMessage.success('密码重置成功')
      } else {
        ElMessage.error(res.data.message || '密码重置失败')
      }
    } catch (err) {
      console.error('重置密码失败：', err)
      ElMessage.error('重置密码失败')
    }
  })
}

// 分页
const handlePageChange = (val) => {
  query.value.page = val
  loadData()
}

// 获取角色下拉列表
const loadRoleList = async () => {
  try {
    const res = await getAllRoles()
    if (res.data.code === 200) {
      roleList.value = res.data.data
    }
  } catch (err) {
    console.error('角色列表加载失败', err)
  }
}

// 显示角色名
const getRoleName = (role_id) => {
  if (!Array.isArray(roleList.value)) return ''
  const role = roleList.value.find(r => r.role_id === role_id)
  return role ? role.role_name : ''
}


onMounted(() => {
  loadRoleList()
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
