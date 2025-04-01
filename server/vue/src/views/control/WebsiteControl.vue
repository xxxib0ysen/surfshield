<template>
    <el-container class="website-control-container">
        <el-main>
            <!-- 操作栏 -->
            <el-card shadow="never" class="card-spacing">
                <el-icon size="small">
                    <Tickets />
                </el-icon>
                <span> 数据列表</span>
                <el-button size="mini" circle @click="loadAll" style="float:right" :loading="loading">
                    <el-icon>
                        <RefreshRight />
                    </el-icon>
                </el-button>
                <el-button size="mini" @click="openAddRuleDialog" style="float:right;margin-right: 15px">添加</el-button>
                <el-button type="primary" size="mini" @click="openTypeDialog"
                    style="float:right;margin-right: 15px">网站类型</el-button>
            </el-card>
            <!-- 数据表 -->
            <el-collapse v-model="activePanels" accordion style="margin-top: 28px;">
                <el-collapse-item v-for="type in websiteTypes" :key="type.type_id" :name="type.type_id">
                    <template #title>
                        <el-icon style="font-size: 18px; margin-right: 10px;">
                            <CircleCheck />
                        </el-icon>
                        <span style="font-weight:bold;font-size: 14px;">{{ type.type_name }}</span>
                        <span style="margin-left: 20px; font-size: 12px; color: gray;">更新于 {{ type.last_modified
                            }}</span>
                        <el-switch
                            :model-value="type.status"
                            :active-value="1"
                            :inactive-value="0"
                            @click.stop
                            @change="handleTypeStatusChange(type, $event)"
                            size="small"
                            style="margin-left: 40px;"
                        />
                    </template>
                    <el-scrollbar max-height="250px">
                        <el-table :data="rules[type.type_id] || []" style="width: 100%;" border>
                            <el-table-column prop="website_url" label="网址" />
                            <el-table-column label="状态">
                                <template #default="{ row }">
                                    <el-switch v-model="row.status" :active-value="1" :inactive-value="0" :disabled="type.status === 0"
                                        @change="changeStatus(row)" />
                                </template>
                            </el-table-column>
                            <el-table-column label="操作">
                                <template #default="{ row }">
                                    <el-button type="text" size="mini" :disabled="type.status === 0"
                                        @click="deleteRule(row.website_id)">删除</el-button>
                                </template>
                            </el-table-column>
                        </el-table>
                    </el-scrollbar>
                </el-collapse-item>
            </el-collapse>
        </el-main>

        <!-- 添加规则 -->
        <el-dialog v-model="showAddRuleDialog" title="添加网站规则" width="500px">
            <el-form :model="newRule" label-width="120px">
                <el-form-item label="类型">
                    <el-select v-model="newRule.type_id" placeholder="请选择网站类型" style="width: 75%;">
                        <el-option v-for="type in websiteTypes" :key="type.type_id" :label="type.type_name"
                            :value="type.type_id" />
                    </el-select>
                </el-form-item>
                <el-form-item label="网址">
                    <el-input v-model="newRule.website_url" type="textarea" :rows="5"
                        placeholder="多个网址以换行分隔，支持通配符 * 和 > (必填)" style="width: 75%;" />
                </el-form-item>
                <el-form-item label="启用">
                    <el-radio-group v-model="newRule.status">
                        <el-radio :label="1">是</el-radio>
                        <el-radio :label="0">否</el-radio>
                    </el-radio-group>
                </el-form-item>
            </el-form>
            <template #footer>
                <el-button @click="showAddRuleDialog = false">取消</el-button>
                <el-button type="primary" @click="submitRule">提交</el-button>
            </template>
        </el-dialog>

        <!-- 网站类型管理 -->
        <el-dialog v-model="showTypeDialog" title="网站类型管理" width="500px">
            <el-table :data="websiteTypes" size="mini">
                <el-table-column prop="type_name" label="类型名称" />
                <el-table-column label="操作">
                    <template #default="{ row }">
                        <el-button type="text" size="mini" @click="deleteType(row.type_id)">删除</el-button>
                    </template>
                </el-table-column>
            </el-table>
            <el-form :model="newType" label-width="80px" style="margin-top: 15px;">
                <el-form-item label="新增类型">
                    <el-input v-model="newType.type_name" placeholder="请输入类型名称" clearable style="width: 75%;" />
                    <el-button @click="submitType" style="margin-left: 10px;">添加</el-button>
                </el-form-item>
            </el-form>
        </el-dialog>
    </el-container>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
    getWebsiteType, addWebsiteType, deleteWebsiteType,updateWebsiteTypeStatus ,
    getWebsiteRule, addWebsiteRule, deleteWebsiteRule, updateWebsiteStatus
} from '@/api/control/website_control'

const loading = ref(false)
const websiteTypes = ref([])
const rules = ref({})
const activePanels = ref([])

const showAddRuleDialog = ref(false)
const showTypeDialog = ref(false)

const newRule = ref({ website_url: '', type_id: null, status: 1 })
const newType = ref({ type_name: '' })

onMounted(() => {
    loadAll()
})

// 加载所有数据
const loadAll = async () => {
    loading.value = true
    try {
        const resType = await getWebsiteType()
        //   console.log('类型接口返回:', resType)

        if (resType.data.code === 200 && Array.isArray(resType.data.data)) {
            websiteTypes.value = resType.data.data
            activePanels.value = []
        } else {
            ElMessage.warning('网站类型接口异常')
        }

        const resRules = await getWebsiteRule()
        //   console.log('分组规则返回:', resRules)

        if (resRules.data.code === 200 && Array.isArray(resRules.data.data)) {
            const map = {}
            resRules.data.data.forEach(group => {
                map[group.type_id] = group.rules
            })
            rules.value = map
        } else {
            ElMessage.warning('规则数据异常')
        }
    } catch (err) {
        ElMessage.error('加载失败')
        console.error(err)
    } finally {
        loading.value = false
    }
}

// 添加规则
const openAddRuleDialog = () => {
    const currentTypeId = activePanels.value[0]
    const currentType = websiteTypes.value.find(t => t.type_id === currentTypeId)
    if (currentType?.status === 0) {
        return ElMessage.warning('该类型已禁用，无法添加规则')
    }
    newRule.value = { website_url: '', type_id: null, status: 1 }
    showAddRuleDialog.value = true
}

// 类型管理
const openTypeDialog = () => {
    showTypeDialog.value = true
}

// 提交规则
const submitRule = async () => {
    const { type_id, website_url } = newRule.value
    if (!type_id || !website_url.trim()) {
        return ElMessage.warning('请填写完整内容')
    }
    const res = await addWebsiteRule(newRule.value)
    if (res.data.code === 200) {
        ElMessage.success('添加成功')
        showAddRuleDialog.value = false
        await loadAll()
    } else {
        ElMessage.error(res.data.message || '添加失败')
    }
}

// 删除规则
const deleteRule = async (website_id) => {
    try {
        await ElMessageBox.confirm('确定删除该规则？', '提示', { type: 'warning' })
        const res = await deleteWebsiteRule(website_id)
        if (res.data.code === 200) {
            ElMessage.success('删除成功')
            await loadAll()
        } else {
            ElMessage.error(res.data.message || '删除失败')
        }
    } catch (e) { }
}

// 更新网站状态
const changeStatus = async (row) => {
    const res = await updateWebsiteStatus(row.website_id, row.status)
    if (res.data.code === 200) {
        ElMessage.success('状态更新成功')
    } else {
        ElMessage.error(res.data.message || '状态更新失败')
    }
}

// 更新类型状态
const handleTypeStatusChange = async (type, nextStatus) => {
  const originalStatus = type.status
  const action = nextStatus === 1 ? '启用' : '禁用'

  try {
    await ElMessageBox.confirm(`确定要${action}该网站类型？`, '确认操作', {
      type: 'warning'
    })

    const res = await updateWebsiteTypeStatus(type.type_id, nextStatus)
    if (res.data.code === 200) {
      ElMessage.success(`类型已${action}`)
      type.status = nextStatus  
      await loadAll()
    } else {
      ElMessage.error(res.data.message || `类型${action}失败`)
      type.status = originalStatus 
    }
  } catch (e) {
    type.status = originalStatus 
  }
}


// 删除类型
const deleteType = async (type_id) => {
    try {
        await ElMessageBox.confirm('确定删除该类型及其规则？', '提示', { type: 'warning' })
        const res = await deleteWebsiteType(type_id)
        if (res.data.code === 200) {
            ElMessage.success('类型删除成功')
            await loadAll()
        } else {
            ElMessage.error(res.data.message || '删除失败')
        }
    } catch (e) { }
}

// 提交类型
const submitType = async () => {
    if (!newType.value.type_name.trim()) {
        return ElMessage.warning('请输入类型名称')
    }
    const res = await addWebsiteType(newType.value.type_name.trim())
    if (res.data.code === 200) {
        ElMessage.success('添加成功')
        newType.value.type_name = ''
        await loadAll()
    } else {
        ElMessage.error(res.data.message || '添加失败')
    }
}
</script>

<style scoped>
.website-control-container {
    padding: -1px 15px 15px;
}

.card-spacing {
    margin-bottom: 16px;
    margin-top: 18px;
    height: auto;
}

.el-collapse-item__header.is-active {
  color: inherit !important;   
  font-weight: normal;        
}
</style>