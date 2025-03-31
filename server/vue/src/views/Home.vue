<template>
    <div class="card-row">
      <!-- 终端概况 -->
      <el-card class="sub-card">
        <div class="card-header">
          <span class="card-title">终端概况</span>
          <el-button type="primary" size="mini" @click="deployTerminals" icon="Monitor">部署终端</el-button>
        </div>
        <div ref="terminalChartRef" class="chart-box"></div>
      </el-card>
  
      <!-- 终端操作系统分布 -->
      <el-card class="sub-card">
        <div class="card-header">
          <span class="card-title">终端操作系统分布</span>
        </div>
        <div ref="osChartRef" class="chart-box"></div>
      </el-card>
    </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import * as echarts from 'echarts'
import { ElMessage } from 'element-plus'

// 模拟
const terminalChartRef = ref(null)
const osChartRef = ref(null)

const deployTerminals = () => {
ElMessage.warning("点击部署终端")
// TODO: 部署终端
}

onMounted(() => {
const terminalChart = echarts.init(terminalChartRef.value)
terminalChart.setOption({
    title: {
    text: '终端总数',
    left: 'center',
    top: '45%',
    textStyle: {
        fontSize: 14,
        color: '#999',
    }
    },
    tooltip: {
    trigger: 'item',
    },
    legend: {
    top: 20,
    left: 'left'
    },
    series: [
    {
        name: '终端状态',
        type: 'pie',
        radius: ['50%', '70%'],
        avoidLabelOverlap: false,
        label: {
        show: true,
        formatter: '{b} ({c})',
        },
        data: [
        { value: 3, name: '在线终端', itemStyle: { color: '#67C23A' } },
        { value: 2, name: '离线终端', itemStyle: { color: '#F56C6C' } }
        ]
    }
    ]
})

const osChart = echarts.init(osChartRef.value)
osChart.setOption({
    title: {
    text: '操作系统分布',
    left: 'center',
    top: '45%',
    textStyle: {
        fontSize: 14,
        color: '#ccc',
    }
    },
    tooltip: {
    trigger: 'item'
    },
    legend: {
    top: 20,
    left: 'left'
    },
    series: [
    {
        name: '操作系统',
        type: 'pie',
        radius: ['50%', '70%'],
        avoidLabelOverlap: false,
        label: {
        show: true,
        formatter: '{b} ({c})',
        },
        data: [
        { value: 2, name: 'Windows' },
        { value: 1, name: 'MacOS' },
        { value: 2, name: 'Linux' }
        ]
    }
    ]
})
})
</script>

<style scoped>
.card-row {
display: flex;
gap: 20px;
width: 100%;
box-sizing: border-box;
}

.sub-card {
flex: 1;
box-sizing: border-box;
padding-bottom: 20px;
}

.card-header {
display: flex;
justify-content: space-between;
align-items: center;
margin-bottom: 12px;
}

.card-title {
font-weight: bold;
font-size: 16px;
}

.chart-box {
width: 100%;
height: 300px;
}
</style>
