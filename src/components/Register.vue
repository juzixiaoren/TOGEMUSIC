<template>
  <div class="register-container">
    <el-card class="register-card">
      <template #header>
        <div class="card-header">
          <span>注册</span>
        </div>
      </template>
      <el-form :model="form" :rules="rules" ref="formRef">
        <el-form-item label="用户名" prop="username">
          <el-input v-model="form.username" placeholder="请输入用户名"></el-input>
        </el-form-item>
        <el-form-item label="密码" prop="password">
          <el-input v-model="form.password" type="password" placeholder="请输入密码"></el-input>
        </el-form-item>
        <el-form-item label="确认密码" prop="confirmPassword">
          <el-input v-model="form.confirmPassword" type="password" placeholder="请确认密码"></el-input>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="register" :loading="loading">注册</el-button>
          <el-button @click="goToLogin">登录</el-button>
        </el-form-item>
      </el-form>
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import http from '../utils/http'

const router = useRouter()

const form = reactive({
  username: '',
  password: '',
  confirmPassword: ''
})

const rules = {
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' }
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, message: '密码长度不能少于6位', trigger: 'blur' }
  ],
  confirmPassword: [
    { required: true, message: '请确认密码', trigger: 'blur' },
    {
      validator: (rule, value, callback) => {
        if (value !== form.password) {
          callback(new Error('两次输入密码不一致'))
        } else {
          callback()
        }
      },
      trigger: 'blur'
    }
  ]
}

const formRef = ref()
const loading = ref(false)

const register = async () => {
  try {
    await formRef.value.validate()
    loading.value = true
    await http.post('/reverse/register', {
      username: form.username,
      password: form.password
    })
    router.push('/login')
  } catch (error) {
    console.error(error)
    // Handle error
  } finally {
    loading.value = false
  }
}

const goToLogin = () => {
  router.push('/login')
}
</script>

<style scoped>
.register-container {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100vh;
}

.register-card {
  width: 400px;
}
</style>