<template>
  <el-container class="group-container">
    <el-main>
      <!-- 操作栏 -->
      <el-card shadow="never" class="card-spacing">
        <el-icon size="small">
          <Tickets />
        </el-icon>
        <span> 数据列表 </span>
        <el-button size="mini" circle @click="refresh" style="float:right" :loading="loading">
          <el-icon>
            <RefreshRight />
          </el-icon>
        </el-button>
        <el-button size="mini" @click="openAddDialog()" style="float:right;margin-right: 15px">
          新增分组
        </el-button>
        <el-button size="mini" @click="openInviteDialog" style="float:right;margin-right: 15px">
          管理邀请码
        </el-button>
      </el-card>

      <!-- 数据表 -->
      <el-table 
        v-loading="loading" :data="groupList" row-key="group_id" border 
        :expand-row-keys="expandKeys" :default-expand-all="false"
        :tree-props="{ children: 'children', hasChildren: 'hasChildren' }" style="width: 100%" size="default"
        :row-class-name="({ row }) => row.group_name === '默认分组' ? 'default-row' : ''">
        <el-table-column label="分组名称" prop="group_name" />
        <el-table-column label="说明" prop="description" >
          <template #default="scope">
            <el-tooltip effect="dark" :content="scope.row.description" placement="top">
              <span >{{ scope.row.description }}</span>
            </el-tooltip>
          </template>
        </el-table-column>

        <el-table-column label="操作">
          <template #default="scope">
            <template v-if="scope.row.group_name !== '默认分组'">
              <el-button type="text" icon="Edit" @click="openEditDialog(scope.row)">编辑</el-button>
              <el-button type="text" icon="CirclePlus" @click="openAddDialog(scope.row)">新增子分组</el-button>
              <el-button type="text" icon="Delete" @click="confirmDelete(scope.row)">删除</el-button>
            </template>
            <template v-else></template>
          </template>
        </el-table-column>
      </el-table>
    </el-main>

    <!-- 弹窗表单 -->
    <el-dialog v-model="dialogVisible" :title="isEdit ? '编辑分组' : '新增分组'" width="500px" @close="resetForm">
      <el-form :model="form" :rules="rules" ref="formRef" label-width="100px">
        <el-form-item label="分组名称" prop="group_name">
          <el-input v-model="form.group_name" placeholder="请输入分组名称" style="width: 80%;" />
        </el-form-item>

        <el-form-item label="父分组">
          <el-cascader
            v-model="form.parent_path"
            :options="groupOptions"
            :props="cascaderProps"
            clearable
            placeholder="请选择父分组，空表示顶层"
            style="width: 80%;"
          />
        </el-form-item>

        <el-form-item label="说明">
          <el-input v-model="form.description" type="textarea" :rows="5" placeholder="请输入备注说明" style="width: 80%;" />
        </el-form-item>
      </el-form>

      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="submitForm">保存</el-button>
      </template>
    </el-dialog>

    <!-- 邀请码管理 -->
    <el-dialog v-model="inviteDialogVisible" title="邀请码管理" width="600px" @close="resetInviteForm">
      <el-button @click="openInviteAddDialog" style="margin-bottom: 10px;">
        新增邀请码
      </el-button>

      <el-table :data="inviteList" border >
        <el-table-column label="邀请码" prop="group_code" />
        <el-table-column label="所属分组" prop="group_id">
          <template #default="scope">
            {{ getGroupName(scope.row.group_id) }}
          </template>
        </el-table-column>
        <el-table-column label="状态" prop="status">
          <template #default="scope">
            <el-tag :type="scope.row.status === 1 ? 'success' : 'danger'">
              {{ scope.row.status === 1 ? '启用' : '禁用' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="备注" prop="description" />
        <el-table-column label="操作" width="180">
          <template #default="scope">
            <el-button type="text" @click="openInviteEditDialog(scope.row)">编辑</el-button>
            <el-button type="text" @click="confirmInviteDelete(scope.row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>

      <!-- 邀请码编辑弹窗 -->
      <el-dialog v-model="inviteFormVisible" :title="inviteEditMode ? '编辑邀请码' : '新增邀请码'" width="400px">
        <el-form :model="inviteForm" ref="inviteFormRef" label-width="80px">
          <el-form-item label="邀请码" prop="group_code">
            <el-input v-model="inviteForm.group_code" />
          </el-form-item>
          <el-form-item label="分组" prop="group_id">
            <el-cascader
              v-model="inviteForm.group_id"
              :options="groupOptions"
              :props="cascaderProps"
              clearable
              placeholder="请选择分组"
              style="width: 100%;"
            />
          </el-form-item>
          <el-form-item label="状态" prop="status">
            <el-switch v-model="inviteForm.status" :active-value="1" :inactive-value="0" />
          </el-form-item>
          <el-form-item label="备注">
            <el-input v-model="inviteForm.description" />
          </el-form-item>
        </el-form>
        <template #footer>
          <el-button @click="inviteFormVisible = false">取消</el-button>
          <el-button type="primary" @click="submitInviteForm">保存</el-button>
        </template>
      </el-dialog>
    </el-dialog>
  </el-container>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  getGroupTree,
  getGroupDetail,
  addGroup,
  updateGroup,
  deleteGroup,
  getInviteList,
  addInvite,
  updateInvite,
  deleteInvite
} from '@/api/terminal_admin/group'

const loading = ref(false)
const groupList = ref([])
const dialogVisible = ref(false)
const isEdit = ref(false)
const currentId = ref(null)
const expandKeys = ref([]) 

const formRef = ref()
const form = ref({
  group_name: '',
  description: '',
  parent_path: null
})

const rules = {
  group_name: [{ required: true, message: '请输入分组名称', trigger: 'blur' }]
}

const groupOptions = ref([])

// 获取树结构数据
const loadGroups = async () => {
  loading.value = true
  try {
    const res = await getGroupTree()
    if (res.data.code === 200) {
      groupList.value = res.data.data || []
      groupOptions.value = groupList.value
    } else {
      ElMessage.error(res.data.message || '加载失败')
    }
  } catch (err) {
    ElMessage.error('获取分组失败')
  } finally {
    loading.value = false
  }
}

// 新增分组
const openAddDialog = (parent = null) => {
  isEdit.value = false
  currentId.value = null
  form.value = {
    group_name: '',
    description: '',
    parent_path: parent?.group_id ?? null
  }
  dialogVisible.value = true
}

// 编辑
const openEditDialog = async (row) => {
  isEdit.value = true
  currentId.value = row.group_id
  const res = await getGroupDetail(row.group_id)
  if (res.data.code === 200) {
    form.value = {
      group_name: res.data.data.group_name,
      description: res.data.data.description,
      parent_path: res.data.data.parent_id === 0 ? null : res.data.data.parent_id
    }
    dialogVisible.value = true
  }
}

// 分组下拉框
const cascaderProps = {
  value: 'group_id',
  label: 'group_name',
  children: 'children',
  emitPath: false,
  checkStrictly: true
}

// 提交
const submitForm = () => {

  formRef.value.validate(async (valid) => {
    if (!valid) return

    const parentId = form.value.parent_path || 0

    // 分组名唯一性校验
    const isDuplicate = groupList.value.some(group => {
      return group.group_name === form.value.group_name &&
        (!isEdit.value || group.group_id !== currentId.value)
    })
    if (isDuplicate) {
      ElMessage.warning('该分组名称已存在，请修改')
      return
    }

    // 校验是否选择了自己的子分组作为父级
    if (!isEdit.value && parentId === currentId.value) {
      ElMessage.warning('不能选择自己作为父分组')
      return
    }
    if (isEdit.value && isDescendant(groupList.value, parentId, currentId.value)) {
      ElMessage.warning('不能将子分组设置为父分组！')
      return
    }


    const submitData = {
      ...form.value,
      parent_id: parentId
    }

    try {
      const res = isEdit.value
        ? await updateGroup(currentId.value, submitData)
        : await addGroup(submitData)
      if (res.data.code === 200 || res.data.code === 201) {
        ElMessage.success(res.data.message)
        dialogVisible.value = false
        expandKeys.value = [submitData.parent_id]
        await loadGroups()
      } else {
        ElMessage.error(res.data.message || '保存失败')
      }
    } catch (err) {
      ElMessage.error('保存失败')
    }
  })
}

// 删除
const confirmDelete = (row) => {
  ElMessageBox.confirm('确认删除该分组及其所有子分组和终端？', '警告', { type: 'warning' })
    .then(async () => {
      const res = await deleteGroup(row.group_id)
      if (res.data.code === 200) {
        ElMessage.success(res.data.message)
        loadGroups()
      } else {
        ElMessage.error(res.data.message || '删除失败')
      }
    })
    .catch(() => { })
}

// 刷新
const refresh = () => {
  loadGroups()
}

// 关闭弹窗时重置表单
const resetForm = () => {
  form.value = {
    group_name: '',
    description: '',
    parent_path: null
  }
  currentId.value = null
  isEdit.value = false
}

// 递归判断：检查目标 parent_id 是否是当前 group 的子节点
const isDescendant = (tree, targetId, currentId) => {
  for (const node of tree) {
    if (node.group_id === currentId) {
      return containsId(node, targetId)
    }
    if (node.children) {
      if (isDescendant(node.children, targetId, currentId)) {
        return true
      }
    }
  }
  return false
}

// 递归子节点中是否有父节点
const containsId = (node, targetId) => {
  if (!node.children) return false
  for (const child of node.children) {
    if (child.group_id === targetId || containsId(child, targetId)) {
      return true
    }
  }
  return false
}

// 邀请码相关
const inviteDialogVisible = ref(false)
const inviteFormVisible = ref(false)
const inviteEditMode = ref(false)
const inviteList = ref([])

const inviteFormRef = ref()
const inviteForm = ref({
  group_code: '',
  group_id: null,
  status: 1,
  description: ''
})


// 获取邀请码列表
const loadInviteList = async () => {
  try {
    const res = await getInviteList()
    if (res.data.code === 200) {
      inviteList.value = res.data.data || []
    } else {
      ElMessage.error(res.data.message)
    }
  } catch (err) {
    ElMessage.error('获取邀请码失败')
  }
}

// 打开邀请码管理弹窗
const openInviteDialog = async () => {
  inviteDialogVisible.value = true
  if (groupOptions.value.length === 0) {
    await loadGroups()
  }
  await loadInviteList()
}


// 打开新增邀请码表单
const openInviteAddDialog = () => {
  inviteEditMode.value = false
  inviteForm.value = {
    group_code: '',
    group_id: null,
    status: 1,
    description: ''
  }
  inviteFormVisible.value = true
}

// 打开编辑表单
const openInviteEditDialog = (row) => {
  inviteEditMode.value = true
  inviteForm.value = { ...row }
  inviteFormVisible.value = true
}

// 提交邀请码
const submitInviteForm = () => {
  inviteFormRef.value.validate(async (valid) => {
    if (!valid) return

    try {
      const res = inviteEditMode.value
        ? await updateInvite(inviteForm.value.id, inviteForm.value)
        : await addInvite(inviteForm.value)

      if (res.data.code === 200 || res.data.code === 201) {
        ElMessage.success(res.data.message)
        inviteFormVisible.value = false
        await loadInviteList()
      } else {
        ElMessage.error(res.data.message || '保存失败')
      }
    } catch (err) {
      ElMessage.error('保存失败')
    }
  })
}

// 删除邀请码
const confirmInviteDelete = (row) => {
  ElMessageBox.confirm('确认删除该邀请码？', '提示', { type: 'warning' })
    .then(async () => {
      const res = await deleteInvite(row.id)
      if (res.data.code === 200) {
        ElMessage.success('删除成功')
        await loadInviteList()
      } else {
        ElMessage.error(res.data.message || '删除失败')
      }
    })
    .catch(() => {})
}

// 关闭弹窗时重置表单
const resetInviteForm = () => {
  inviteForm.value = {
    group_code: '',
    group_id: null,
    status: 1,
    description: ''
  }
  inviteFormVisible.value = false
}

// 获取分组名称
const getGroupName = (id) => {
  const findName = (nodes) => {
    for (const node of nodes) {
      if (node.group_id === id) {
        return node.group_name
      }
      if (node.children && node.children.length) {
        const result = findName(node.children)
        if (result) return result
      }
    }
    return null
  }

  const name = findName(groupOptions.value)
  return name || '-'
}



onMounted(loadGroups)
</script>

<style scoped>
.group-container {
  padding: 0 15px;
}

.card-spacing {
  margin-top: 18px;
  margin-bottom: 16px;
}

</style>
