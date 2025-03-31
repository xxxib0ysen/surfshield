<template>
    <el-container>
      <el-main>
        <el-card class="main-card" shadow="never">
          <!-- 横向卡片，宽度不足时自动换行 -->
          <el-space
            :size="20"
            wrap
            alignment="start"
            direction="horizontal"
            class="responsive-space"
          >
            <!-- 终端概况 -->
            <el-card class="sub-card">
              <template #header>
                <div class="card-header">
                  <span>终端概况</span>
                  <el-button size="small" type="primary">部署终端</el-button>
                </div>
              </template>
              <div ref="terminalChart" class="chart-box"></div>
            </el-card>
  
            <!-- 操作系统分布 -->
            <el-card class="sub-card">
              <template #header>
                <span>终端操作系统分布</span>
              </template>
              <div ref="osChart" class="chart-box"></div>
            </el-card>
          </el-space>
        </el-card>
      </el-main>
    </el-container>
  </template>
  
  <script setup>
  import { ref, onMounted } from 'vue'
  import * as echarts from 'echarts'
  
  const terminalChart = ref(null)
  const osChart = ref(null)
  
  onMounted(() => {
    echarts.init(terminalChart.value).setOption({
      tooltip: { trigger: 'item' },
      series: [
        {
          type: 'pie',
          radius: ['40%', '70%'],
          data: [
            { value: 5, name: '在线终端', itemStyle: { color: '#67C23A' } },
            { value: 3, name: '离线终端', itemStyle: { color: '#F56C6C' } }
          ]
        }
      ]
    })
  
    echarts.init(osChart.value).setOption({
      tooltip: { trigger: 'item' },
      series: [
        {
          type: 'pie',
          radius: ['40%', '70%'],
          data: [
            { value: 4, name: 'Windows' },
            { value: 4, name: 'Linux' }
          ]
        }
      ]
    })
  })
  </script>
  
  <style scoped>
  .main-card {
    max-width: 1200px;
    margin: 20px auto;
    padding: 20px;
  }
  
  .sub-card {
    flex: 1 1 500px; /* 自适应宽度 + 最小宽度 */
    min-width: 300px;
    box-sizing: border-box;
  }
  
  .chart-box {
    height: 280px;
  }
  
  .card-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
  }
  </style>
  