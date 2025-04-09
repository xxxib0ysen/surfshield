<template>
    <el-dialog v-model="visible" :title="terminal.username" width="800px" @close="$emit('close')">
        <el-tabs>
            <el-tab-pane label="终端信息">
                <el-descriptions :column="2" border>
                    <el-descriptions-item label="ID">{{ terminal.id }}</el-descriptions-item>
                    <el-descriptions-item label="创建时间">{{ terminal.createdon }}</el-descriptions-item>
                    <el-descriptions-item label="用户名">{{ terminal.username }}</el-descriptions-item>
                    <el-descriptions-item label="唯一标识符">{{ terminal.uuid }}</el-descriptions-item>
                    <el-descriptions-item label="计算机名">{{ terminal.hostname }}</el-descriptions-item>
                    <el-descriptions-item label="MAC">{{ terminal.mac_address }}</el-descriptions-item>
                    <el-descriptions-item label="本地IP">{{ terminal.local_ip }}</el-descriptions-item>
                    <el-descriptions-item label="公网IP">{{ terminal.ip_address }}</el-descriptions-item>
                    <el-descriptions-item label="操作系统">{{ terminal.os_name }}</el-descriptions-item>
                    <el-descriptions-item label="系统版本">{{ terminal.os_version }}</el-descriptions-item>
                    <el-descriptions-item label="系统安装时间">{{ terminal.install_time }}</el-descriptions-item>
                    <el-descriptions-item label="是否64位">{{ terminal['64bit'] ? '是' : '否' }}</el-descriptions-item>
                    <el-descriptions-item label="在线状态">
                        <el-tag :type="terminal.status === 1 ? 'success' : 'info'">
                            {{ terminal.status === 1 ? '在线' : '离线' }}
                        </el-tag>
                    </el-descriptions-item>
                    <el-descriptions-item label="最后在线时间">{{ terminal.last_login }}</el-descriptions-item>
                    <el-descriptions-item label="所在分组">{{ terminal.group_name }}</el-descriptions-item>
                    <el-descriptions-item label="分组ID">{{ terminal.group_id }}</el-descriptions-item>
                </el-descriptions>
            </el-tab-pane>
        </el-tabs>
    </el-dialog>
</template>

<script setup>
const props = defineProps({
    terminal: Object
})
const visible = defineModel({ type: Boolean })
</script>

<style scoped>
.el-descriptions__label {
    width: 120px;
}
</style>