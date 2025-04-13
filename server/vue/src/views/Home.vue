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
import { getTerminalStatusCount, getTerminalOSDistribution } from '@/api/terminal_admin/terminal'


const terminalChartRef = ref(null)
const osChartRef = ref(null)

// 终端状态
const renderTerminalStatusChart = async () => {
  const chart = echarts.init(terminalChartRef.value)
  try {
    const res = await getTerminalStatusCount()
    const { online, offline } = res.data

    chart.setOption({
      title: {
        text: '终端总数',
        left: 'center',
        top: '45%',
        textStyle: {
          fontSize: 14,
          color: '#999'
        }
      },
      tooltip: { trigger: 'item' },
      legend: { top: 20, left: 'left' },
      series: [
        {
          name: '终端状态',
          type: 'pie',
          radius: ['50%', '70%'],
          avoidLabelOverlap: false,
          label: { show: true, formatter: '{b} ({c})' },
          data: [
            { value: online, name: '在线终端', itemStyle: { color: '#67C23A' } },
            { value: offline, name: '离线终端', itemStyle: { color: '#F56C6C' } }
          ]
        }
      ]
    })
  } catch (err) {
    ElMessage.error('获取终端状态统计失败')
  }
}

// 操作系统分布
const renderOSChart = async () => {
  const chart = echarts.init(osChartRef.value)
  try {
    const res = await getTerminalOSDistribution()
    const osData = res.data.map(item => ({
      name: item.name,
      value: item.count
    }))

    chart.setOption({
      title: {
        text: '操作系统分布',
        left: 'center',
        top: '45%',
        textStyle: {
          fontSize: 14,
          color: '#ccc'
        }
      },
      tooltip: { trigger: 'item' },
      legend: { top: 20, left: 'left' },
      series: [
        {
          name: '操作系统',
          type: 'pie',
          radius: ['50%', '70%'],
          avoidLabelOverlap: false,
          label: { show: true, formatter: '{b} ({c})' },
          data: osData
        }
      ]
    })
  } catch (err) {
    ElMessage.error('获取操作系统分布失败')
  }
}

const deployTerminals = () => {
ElMessage.warning("点击部署终端")
// TODO: 部署终端
}

onMounted(() => {
  renderTerminalStatusChart()
  renderOSChart()
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
