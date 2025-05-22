<template>
  <el-container class="terminal-container">
    <el-main>
    <el-row gutter="20">
      <!-- 左侧 -->
      <el-col :span="4">
        <el-card shadow="never">
          <el-tree
            class="group-tree"
            :data="groupList"
            :props="defaultProps"
            node-key="group_id"
            default-expand-all
            accordion
            highlight-current
            :current-node-key="selectedGroupId"
            :filter-node-method="filterGroup"
            @node-click="handleGroupClick"
          />
        </el-card>
      </el-col>

      <!-- 右侧 -->
      <el-col :span="20">
        <!-- 筛选区域 -->
        <el-card shadow="never" class="mb-2 filter-card">
          <el-form :model="filters" label-position="left" >
            <el-row :gutter="20">
              <template v-for="item in visibleFields" :key="item.prop">
                <el-col :span="8">
                  <el-form-item :label="item.label">
                    <template v-if="item.prop === 'status'">
                      <el-select v-model="filters.status" placeholder="请选择" clearable style="width: 100%" @change="handleSearch">
                        <el-option label="在线" :value="1" />
                        <el-option label="离线" :value="0" />
                      </el-select>
                    </template>
                    <template v-else>
                      <el-input v-model="filters[item.prop]" placeholder="请输入" clearable @change="handleSearch"/>
                    </template>
                  </el-form-item>
                </el-col>
              </template>
              <template v-for="n in emptySlots" :key="'empty-' + n">
                <el-col :span="8" />
              </template>

              <!-- 按钮 -->
              <el-col :span="8" > 
                <el-form-item>
                  <div style="display: flex; justify-content: flex-end; align-items: center;">
                    <el-switch
                      v-model="filters.fuzzy"
                      @change="handleSearch"
                      active-text="模糊匹配"
                      style="margin-right: 10px"
                    />
                    <el-button type="primary" @click="handleSearch">
                      <el-icon><Search /></el-icon> 搜索
                    </el-button>
                    <el-button @click="handleReset">
                      <el-icon><Delete /></el-icon> 重置
                    </el-button>
                    <el-button @click="toggleExpand" type="text" style="margin-left: 10px;">
                      <el-icon><component :is="expand ? 'ArrowUp' : 'ArrowDown'" /></el-icon>
                    </el-button>
                  </div>
                </el-form-item>
              </el-col>

            </el-row>
          </el-form>
        </el-card>

        <!-- 终端列表 -->
        <el-card shadow="never">
          <!-- 操作按钮 -->
          <div class="mb-2">
            <el-button 
              type="primary" 
              icon="Edit" @click="openMoveDialog()" 
              :disabled="selectedRows.length === 0">
              移动到分组</el-button>
            <el-button circle @click="showColumnDialog=true" style="float:right">
              <el-icon><Operation /></el-icon>
            </el-button>
            <el-button circle @click="handleRefresh" style="float:right" >
              <el-icon><Refresh /></el-icon>
            </el-button>
          </div>
          <!-- 表格 -->
          <el-table :data="tableData" border style="width: 100%" @selection-change="handleSelectionChange">
            <el-table-column type="selection" width="55" />
            <template v-for="col in columnOptions" :key="col.prop">
              <el-table-column
                v-if="col.show"
                :prop="col.prop"
                :label="col.label"
              >
                <template v-if="col.prop === 'username'" #default="scope">
                  <el-link :underline="false" @click="viewDetail(scope.row)">
                    {{ scope.row.username }}
                  </el-link>
                </template>

                <template v-else-if="col.prop === 'status'" #default="scope">
                  <el-tag :type="scope.row.status === 1 ? 'success' : 'info'">
                    {{ scope.row.status === 1 ? '在线' : '离线' }}
                  </el-tag>
                </template>

                <template v-else-if="col.prop === 'is_64bit'" #default="scope">
                  <el-tag :type="scope.row.is_64bit === 1 ? 'success' : 'info'">
                    {{ scope.row.is_64bit === 1 ? '64位' : '32位' }}
                  </el-tag>
                </template>

                <template v-else #default="scope">
                  {{ scope.row[col.prop] }}
                </template>

              </el-table-column>
            </template>
          </el-table>

          <!-- 分页 -->
          <div class="pagination-container">
            <el-pagination background
            layout="total, prev, pager, next, jumper"
            :total="total"
            :page-size="pageSize"
            :current-page="pageNum"
            @current-change="handlePageChange"
            />
          </div>
          
        </el-card>
      </el-col>
    </el-row>

    <!-- 移动分组弹窗 -->
    <el-dialog v-model="showMoveDialog" title="移动终端到分组" width="30%">
      <el-form>
        <el-form-item label="目标分组">
          <el-cascader
            v-model="targetGroupId"
            :options="groupList"
            :props="cascaderProps"
            placeholder="请选择目标分组"
            clearable
            expand-trigger="hover"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showMoveDialog = false">取消</el-button>
        <el-button type="primary" @click="confirmMove">确定</el-button>
      </template>
    </el-dialog>

    <!-- 自定义列 -->
    <el-dialog v-model="showColumnDialog" title="列设置" width="400px">
      <el-table :data="columnOptions.filter(col => !col.force)" border>
        <el-table-column prop="label" label="列名" />
        <el-table-column label="显示" width="100">
          <template #default="scope">
            <el-switch
              v-model="scope.row.show"
              :disabled="scope.row.force"
              @change="updateVisibleColumns"
            />
          </template>
        </el-table-column>
      </el-table>
    </el-dialog>

    </el-main>
  </el-container>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { getTerminalList, moveTerminalToGroup, getTerminalColumns } from '@/api/terminal_admin/terminal'
import { getGroupTree } from '@/api/terminal_admin/group'

const router = useRouter()

const expand = ref(false)
const toggleExpand = () => (expand.value = !expand.value)

// 筛选项
const filters = ref({
  username: '',
  status: null,
  hostname: '',
  os_name: '',
  os_version: '',
  ip_address: '',
  uuid: '',
  fuzzy: false,
  group_id: null
})
// 未展开
const baseFields = [
  { label: '用户名：', prop: 'username' },
  { label: '在线状态：', prop: 'status' }
]
// 展开
const expandFields = [
  { label: '计算机名：', prop: 'hostname' },
  { label: '操作系统：', prop: 'os_name' },
  { label: '操作系统版本：', prop: 'os_version' },
  { label: 'IP：', prop: 'ip_address' },
  { label: '唯一标识符：', prop: 'uuid' }
]

const visibleFields = computed(() => expand.value ? [...baseFields, ...expandFields] : baseFields)
// 空位
const totalFieldCount = computed(() => visibleFields.value.length + 1)
const emptySlots = computed(() => {
  const mod = totalFieldCount.value % 3
  return mod === 0 ? 0 : 3 - mod
})

// 级联配置选项
const cascaderProps = {
  label: 'group_name',
  value: 'group_id',
  children: 'children'
}

const pageNum = ref(1)
const pageSize = ref(6)
const total = ref(0)
const tableData = ref([])

// 加载终端列表
const loadTableData = async () => {
  try {
    const params = {
      ...filters.value,
      page: pageNum.value,
      page_size: pageSize.value
    }

    const res = await getTerminalList(params)
    if (res.data.code === 200) {
      tableData.value = res.data.data.data || []
      total.value = res.data.data.total || 0
      // console.log("当前 group_id：", filters.value.group_id)
      // console.log("加载参数：", params)
      // console.log("返回数据：", res.data.data)
    } else {
      ElMessage.error(res.data.message || '终端数据加载失败')
    }
  } catch (err) {
    ElMessage.error(err.message || '终端列表加载异常')
  }
}

// 页码变更
const handlePageChange = (val) => {
  pageNum.value = val
  loadTableData()
}

// 搜索
const handleSearch = () => {
  pageNum.value = 1
  loadTableData()
}

// 重置
const handleReset = () => {
  Object.assign(filters.value, {
    username: '',
    status: null,
    hostname: '',
    os_name: '',
    os_version: '',
    ip_address: '',
    uuid: '',
    fuzzy: false,
    group_id: selectedGroupId.value === 0 ? null : selectedGroupId.value
  })
  handleSearch()
}

// 查看终端详情
const viewDetail = (row) => {
  router.push(`/management/terminal/detail/${row.id || 1}`)
}

const groupList = ref([])
const selectedGroupId = ref(0)
const showMoveDialog = ref(false)
const targetGroupId = ref(null)

// 分组
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

// 递归获取所有子 group_id
const getAllGroupIds = (node) => {
  const ids = [node.group_id]
  const traverse = (children) => {
    if (!children) return
    children.forEach(child => {
      ids.push(child.group_id)
      traverse(child.children)
    })
  }
  traverse(node.children)
  return ids
}

// 分组筛选
const defaultProps = { children: 'children', label: 'group_name' }
const filterGroup = (value, data) => data.group_name.includes(value)
const handleGroupClick = (node) => {
  selectedGroupId.value = node.group_id
  if (node.group_id === 0) {
    filters.value.group_id = null 
  } else {
    filters.value.group_id = getAllGroupIds(node).join(',')
  }
  pageNum.value = 1
  loadTableData()
}

// 移动分组
const selectedRows = ref([])
const handleSelectionChange = (val) => {
  selectedRows.value = val
}
const openMoveDialog = () => {
  targetGroupId.value = null
  showMoveDialog.value = true
}
const confirmMove = async () => {
  if (selectedRows.value.length === 0) {
    return ElMessage.warning('请选择要移动的终端')
  }
  if (!targetGroupId.value) {
    return ElMessage.warning('请选择目标分组')
  }
  try {
    await ElMessageBox.confirm(
      `确认将 ${selectedRows.value.length} 个终端移动到指定分组？`,
      '操作确认',
      { type: 'warning' }
    )
    const res = await moveTerminalToGroup({
      ids: selectedRows.value.map(i => i.id),
      group_id: targetGroupId.value?.slice(-1)[0]  
    })
    if (res.data.code === 200) {
      ElMessage.success('移动成功')
      showMoveDialog.value = false
      selectedRows.value = []
      handleRefresh()
    } else {
      ElMessage.error(res.data.message || '移动失败')
    }
  } catch {}
}


// 列设置
const showColumnDialog = ref(false)
const columnOptions = ref([])  
const visibleColumns = ref([]) 
const forcedColumns = ['username', 'status', 'hostname', 'os_name', 'ip_address']
// 获取自定义列配置
const loadColumnOptions = async () => {
  const res = await getTerminalColumns()
  if (res.data.code === 200) {
    columnOptions.value = res.data.data.map(col => {
      const isForced = forcedColumns.includes(col.prop)
      return {
        ...col,
        show: isForced ? true : col.default,
        force: isForced
      }
    })
    updateVisibleColumns()
  } else {
    ElMessage.error(res.data.message || '获取列配置失败')
  }
}
// 启用/禁用
const updateVisibleColumns = () => {
  visibleColumns.value = columnOptions.value
    .filter(col => col.show)
    .map(col => col.prop)
}

// 刷新
const handleRefresh = () => {
  loadTableData()
  loadGroupTree()
  loadColumnOptions()
  ElMessage.success('刷新成功')
}

// 初始化加载
onMounted(() => {
  selectedGroupId.value = 0
  loadTableData()
  loadGroupTree()
  loadColumnOptions()
})

</script>


<style scoped>
.terminal-container {
  padding: 0 15px;
}

.mb-2 {
  margin-bottom: 15px;
}

.el-space {
  flex-wrap: wrap;
  justify-content: flex-end;
}

.pagination-container {
  display: flex;
  justify-content: flex-end;
  padding: 10px 20px;
  margin-top: 20px;
}

</style>