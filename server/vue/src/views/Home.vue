<template>
  <div class="card-row">
    <!-- 终端概况 -->
    <el-card class="sub-card">
      <div class="card-header">
        <span class="card-title">终端概况</span>
        <el-button type="primary" size="mini" @click="deployTerminals" icon="Monitor">部署终端</el-button>
      </div>
      <div class="chart-container">
        <div ref="terminalChartRef" class="chart-box"></div>
      </div>
    </el-card>

    <!-- 终端操作系统分布 -->
    <el-card class="sub-card">
      <div class="card-header">
        <span class="card-title">终端操作系统分布</span>
      </div>
      <div class="chart-container">
        <div ref="osChartRef" class="chart-box"></div>
      </div>
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

// 渲染通用圆环图
const renderRingChart = (chartDom, dataList, centerText = '') => {
  const chart = echarts.init(chartDom)
  chart.setOption({
    tooltip: {
      trigger: 'item',
      formatter: '{b}: {c} 台 ({d}%)'
    },
    legend: {
      orient: 'vertical',
      left: 10,
      top: 'center',
      itemWidth: 14,
      itemHeight: 14,
      textStyle: {
        fontSize: 12
      }
    },
    series: [
      {
        type: 'pie',
        radius: '70%',
        center: ['65%', '50%'],
        avoidLabelOverlap: false,
        label: { show: false },
        labelLine: { show: false },
        emphasis: {
          label: { show: false } 
        },
        data: dataList
      }
    ]
  })
}


// 渲染终端状态图表
const renderTerminalStatusChart = async () => {
  try {
    const res = await getTerminalStatusCount()
    const { online, offline } = res.data
    const data = [
      { value: online, name: '在线终端', itemStyle: { color: '#67C23A' } },
      { value: offline, name: '离线终端', itemStyle: { color: '#F56C6C' } }
    ]
    renderRingChart(terminalChartRef.value, data)
  } catch (err) {
    ElMessage.error('获取终端状态统计失败')
  }
}

// 渲染操作系统分布图表
const renderOSChart = async () => {
  try {
    const res = await getTerminalOSDistribution()
    const data = res.data.map(item => ({
      name: item.name,
      value: item.count
    }))
    renderRingChart(osChartRef.value, data)
  } catch (err) {
    ElMessage.error('获取操作系统分布失败')
  }
}

const deployTerminals = () => {
  ElMessage.warning('点击部署终端')
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

.chart-container {
  display: flex;
  flex-direction: row;
  justify-content: space-between;
  align-items: center;
  height: 420px;
  padding-right: 10px;
}

.chart-box {
  flex: 1;
  height: 100%;
}
</style>
