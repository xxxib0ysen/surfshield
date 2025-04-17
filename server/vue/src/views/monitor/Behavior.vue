<template>
    <el-container class="behavior-monitor-container">
        <el-main>
            <!-- 搜索栏 -->
            <el-card shadow="never" class="mb-3">
                <el-autocomplete v-model="filters.username" :fetch-suggestions="searchSuggestions"
                    placeholder="请输入终端用户名" clearable class="custom-search-input" @select="handleSelect"
                    @clear="handleClear" @keyup.enter.native="handleSearch" :trigger-on-focus="true">
                    <template #suffix>
                        <el-icon class="search-icon" @click="handleSearch">
                            <Search />
                        </el-icon>
                    </template>
                </el-autocomplete>
            </el-card>

            <!-- 标签页 -->
            <el-card shadow="never">
                <el-tabs v-model="activeTab">
                    <el-tab-pane label="网页访问记录" name="web">
                        <el-table :data="webData" border v-loading="loading" height="550">
                            <el-table-column prop="username" label="用户名" />
                            <el-table-column prop="title" label="网站名称" />
                            <el-table-column prop="url" label="网址" />
                            <el-table-column prop="browser" label="浏览器" />
                            <el-table-column prop="visit_time" label="访问时间" sortable />
                        </el-table>
                    </el-tab-pane>

                    <el-tab-pane label="搜索关键词记录" name="search">
                        <el-table :data="searchData" border v-loading="loading" height="550">
                            <el-table-column prop="username" label="用户名" />
                            <el-table-column prop="keyword" label="关键词" />
                            <el-table-column prop="engine" label="搜索引擎" />
                            <el-table-column prop="search_time" label="搜索时间" sortable />
                        </el-table>
                    </el-tab-pane>
                </el-tabs>
            </el-card>
        </el-main>
    </el-container>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { ElMessage } from 'element-plus'
import { getWebBehavior, getSearchBehavior, getTerminalUserList } from '@/api/monitor/behavior'

const filters = ref({ username: '' })
const webData = ref([])
const searchData = ref([])
const loading = ref(false)
const activeTab = ref('web')

const userList = ref([])

// 下拉在线用户
const searchSuggestions = (query, cb) => {
    const results = userList.value.filter(item => item.value.includes(query))
    cb(results)
}

// 用户名选择
const handleSelect = (item) => {
    filters.value.username = item.value
    handleSearch()
}

// 清除搜索
const handleClear = () => {
    filters.value.username = ''
    handleSearch()
}

// 查询行为记录
const handleSearch = async () => {
    loading.value = true
    try {
        if (activeTab.value === 'web') {
            const res = await getWebBehavior(filters.value.username || undefined)
            if (res.data.code === 200) {
                webData.value = res.data.data
            }
        } else {
            const res = await getSearchBehavior(filters.value.username || undefined)
            if (res.data.code === 200) {
                searchData.value = res.data.data
            }
        }
    } catch (e) {
        ElMessage.error('加载失败')
    } finally {
        loading.value = false
    }
}

// 自动刷新
let timer = null
const startTimer = () => {
    timer = setInterval(() => {
        handleSearch()
    }, 30000)
}
const stopTimer = () => {
    if (timer) clearInterval(timer)
}

// 初始化加载
const loadUserList = async () => {
    try {
        const res = await getTerminalUserList()
        if (res.data.code === 200 && Array.isArray(res.data.data)) {
            userList.value = res.data.data
                .map(name => ({ value: name }))
                .sort((a, b) => a.value.localeCompare(b.value))
        }
    } catch (e) {
        console.warn('终端用户加载失败')
    }
}

onMounted(() => {
    loadUserList()
    handleSearch()
    startTimer()
})

onUnmounted(() => {
    stopTimer()
})
</script>

<style scoped>
.behavior-monitor-container {
    padding: 0 15px;
}

.mb-3 {
    margin-bottom: 16px;
}

.custom-search-input {
    width: 350px;
}

.search-icon {
    cursor: pointer;
    color: #909399;
}

.search-icon:hover {
    color: #409EFF;
}
</style>