<template>
    <el-main >
      <el-card style="width: 100%; height: 80vh;">

        <el-alert 
          title="当前是初始密码，为了安全请务必修改密码！" 
          type="warning" 
          show-icon 
          style="margin-bottom: 25px" />

        <el-form  
          :model="form" :rules="rules" ref="formRef" 
          label-width="160px" label-position="right" style="row-gap: 20px">
          <el-form-item label="请输入当前密码:" prop="old_password" >
            <el-input 
              v-model="form.old_password" type="password" 
              prefix-icon="Lock" placeholder="请输入密码" 
              style="width: 35%;" show-password />
          </el-form-item>

          <el-form-item label="请输入新密码:" prop="new_password">
            <el-input 
              v-model="form.new_password" 
              type="password" 
              prefix-icon="Lock"
              placeholder="请输入6到12位同时包含数字、大小写字母的新密码" 
              style="width: 35%; " show-password/>
          </el-form-item>

          <el-form-item label="请再次输入新密码:" prop="confirm_password">
            <el-input 
              v-model="form.confirm_password" 
              type="password" 
              prefix-icon="Lock" 
              placeholder="请输入相同的新密码" 
              style="width: 35%;" show-password />
          </el-form-item>

          <el-form-item style="text-align: center; width: 100%">
            <el-button type="primary" @click="submitForm" style="width: 10%; margin-top: 10px;">修改密码</el-button>
          </el-form-item>
        </el-form>
      </el-card>
    </el-main>
</template>


<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { changePassword } from '@/api/terminal_admin/admin'

const router = useRouter()
const formRef = ref(null)
const form = ref({
  old_password: '',
  new_password: '',
  confirm_password: ''
})

const rules = {
  old_password: [{ required: true, message: '请输入当前密码', trigger: 'blur' }],
  new_password: [
    { required: true, message: '请输入新密码', trigger: 'blur' },
    {
      pattern: /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)[A-Za-z\d]{6,12}$/,
      message: '密码需为6~12位，包含数字、大小写字母',
      trigger: 'blur'
    }
  ],
  confirm_password: [
    { required: true, message: '请再次输入新密码', trigger: 'blur' },
    {
      validator: (rule, value, callback) => {
        if (value !== form.value.new_password) {
          callback(new Error('两次输入密码不一致'))
        } else {
          callback()
        }
      },
      trigger: 'blur'
    }
  ]
}

const submitForm = () => {
  formRef.value.validate(async (valid) => {
    if (!valid) return
    try {
      const res = await changePassword(form.value)
      if (res.data.code === 200) {
        ElMessage.success('密码修改成功，请重新登录')
        localStorage.removeItem('token')
        localStorage.removeItem('user')
        localStorage.removeItem('permissions')
        router.push('/login')
      } else {
        ElMessage.error(res.data.message || '修改失败')
      }
    } catch (err) {
      ElMessage.error(err?.response?.data?.detail || '修改失败')
    }
  })
}
</script>

