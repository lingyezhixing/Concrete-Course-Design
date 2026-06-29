<template>
  <div class="login-page">
    <div class="login-card">
      <div class="brand">
        <img src="/logo.ico" class="brand-logo" alt="logo" />
      </div>
      <h1 class="title">混凝土课程设计计算平台</h1>
      <p class="subtitle">
        {{ mode === 'login' ? '欢迎回来，请登录以继续' : '创建账户即可开始使用' }}
      </p>

      <el-form
        ref="formRef"
        :model="form"
        :rules="rules"
        label-position="top"
        @submit.prevent="submit"
      >
        <el-form-item prop="username">
          <el-input
            v-model="form.username"
            size="large"
            placeholder="用户名（3-32 位字母/数字/下划线）"
          />
        </el-form-item>
        <el-form-item prop="password">
          <el-input
            v-model="form.password"
            size="large"
            type="password"
            show-password
            placeholder="密码（至少 6 位）"
          />
        </el-form-item>
        <el-form-item v-if="mode === 'register'" prop="confirm">
          <el-input
            v-model="form.confirm"
            size="large"
            type="password"
            show-password
            placeholder="确认密码"
          />
        </el-form-item>
        <el-button
          type="primary"
          size="large"
          :loading="loading"
          class="submit"
          @click="submit"
        >
          {{ mode === 'login' ? '登录' : '注册' }}
        </el-button>
      </el-form>

      <div class="switch">
        <span class="switch-text">
          {{ mode === 'login' ? '还没有账户？' : '已有账户？' }}
        </span>
        <a class="switch-link" @click="toggleMode">
          {{ mode === 'login' ? '去注册' : '去登录' }}
        </a>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { reactive, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage, type FormInstance, type FormRules } from 'element-plus'
import { useAuth } from '../composables/useAuth'

type Mode = 'login' | 'register'

const route = useRoute()
const router = useRouter()
const { login, register } = useAuth()

const mode = ref<Mode>('login')
const loading = ref(false)
const formRef = ref<FormInstance>()

const form = reactive({
  username: '',
  password: '',
  confirm: '',
})

const rules: FormRules = {
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' },
    {
      pattern: /^[A-Za-z0-9_]{3,32}$/,
      message: '3-32 位字母/数字/下划线',
      trigger: 'blur',
    },
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, message: '至少 6 位', trigger: 'blur' },
  ],
  confirm: [
    {
      validator: (_r, value, cb) => {
        if (mode.value === 'register' && value !== form.password) {
          cb(new Error('两次密码不一致'))
        } else {
          cb()
        }
      },
      trigger: 'blur',
    },
  ],
}

function toggleMode(): void {
  mode.value = mode.value === 'login' ? 'register' : 'login'
  form.password = ''
  form.confirm = ''
  formRef.value?.clearValidate()
}

async function submit(): Promise<void> {
  if (!formRef.value) return
  try {
    await formRef.value.validate()
  } catch {
    return
  }
  loading.value = true
  try {
    if (mode.value === 'login') {
      await login(form.username, form.password)
      const redirect = (route.query.redirect as string) || '/'
      router.replace(redirect)
    } else {
      // 注册成功后不自动登录：切回登录页，保留用户名、清空密码
      await register(form.username, form.password)
      ElMessage.success('注册成功，请登录')
      form.password = ''
      form.confirm = ''
      mode.value = 'login'
      formRef.value?.clearValidate()
    }
  } catch (e: unknown) {
    const detail = (e as { response?: { data?: { detail?: string } } })?.response?.data?.detail
    ElMessage.error(detail ?? '操作失败，请重试')
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.login-page {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 24px;
  background: var(--background);
  color: var(--foreground);
}
.login-card {
  width: 100%;
  max-width: 400px;
  padding: 44px 40px 36px;
  background: var(--card);
  border: 1px solid var(--border);
  border-radius: 16px;
  box-shadow: 0 16px 48px rgba(0, 0, 0, 0.16);
}
.brand {
  width: 52px;
  height: 52px;
  margin: 0 auto 20px;
  display: flex;
  align-items: center;
  justify-content: center;
}
.brand-logo {
  width: 100%;
  height: 100%;
}
.title {
  margin: 0;
  font-size: 20px;
  font-weight: 700;
  letter-spacing: -0.01em;
  line-height: 1.3;
  text-align: center;
}
.subtitle {
  margin: 8px 0 30px;
  font-size: 13px;
  color: var(--muted-foreground);
  text-align: center;
}
.submit {
  width: 100%;
  height: 44px;
  margin-top: 4px;
  font-size: 15px;
  font-weight: 600;
  border-radius: 10px;
}
.switch {
  margin-top: 22px;
  text-align: center;
  font-size: 13px;
}
.switch-text {
  color: var(--muted-foreground);
}
.switch-link {
  margin-left: 4px;
  color: var(--primary);
  font-weight: 500;
  cursor: pointer;
  user-select: none;
}
.switch-link:hover {
  text-decoration: underline;
}
:deep(.el-input__wrapper) {
  border-radius: 10px;
}
:deep(.el-form-item) {
  margin-bottom: 18px;
}
</style>
