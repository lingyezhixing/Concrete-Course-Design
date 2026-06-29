<template>
  <div class="settings">
    <PageHeader title="系统设置" subtitle="主题外观与账户管理" />

    <section class="block">
      <h2 class="block-title">主题外观</h2>
      <div class="theme-options">
        <button
          v-for="opt in OPTIONS"
          :key="opt.value"
          type="button"
          class="opt"
          :class="{ active: theme === opt.value }"
          @click="setTheme(opt.value)"
        >
          {{ opt.label }}
        </button>
      </div>
    </section>

    <section class="block">
      <h2 class="block-title">账户</h2>
      <p class="muted">当前用户：{{ currentUser?.username ?? '未登录' }}</p>
    </section>

    <section v-if="currentUser" class="block danger">
      <h2 class="block-title danger-title">注销账户</h2>
      <p class="muted">注销将永久删除你的账户及全部数据，操作不可恢复。</p>
      <el-button type="danger" plain :loading="deleting" @click="confirmDelete">
        注销账户
      </el-button>
    </section>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import PageHeader from '../components/common/PageHeader.vue'
import { useTheme, type Theme } from '../composables/useTheme'
import { useAuth } from '../composables/useAuth'

const OPTIONS: ReadonlyArray<{ value: Theme; label: string }> = [
  { value: 'dark', label: '深色' },
  { value: 'light', label: '浅色' },
  { value: 'warm', label: '暖灰' },
]

const router = useRouter()
const { theme, setTheme } = useTheme()
const { currentUser, deleteAccount } = useAuth()

const deleting = ref(false)

async function confirmDelete(): Promise<void> {
  // 第一次确认
  try {
    await ElMessageBox.confirm(
      '注销将永久删除你的账户及全部数据，确定继续吗？',
      '注销账户（1/2）',
      { type: 'warning', confirmButtonText: '继续', cancelButtonText: '取消' },
    )
  } catch {
    return
  }
  // 第二次确认
  try {
    await ElMessageBox.confirm(
      '这是最后确认：账户一旦注销将无法恢复。真的要删除吗？',
      '注销账户（2/2）',
      { type: 'error', confirmButtonText: '确认注销', cancelButtonText: '取消' },
    )
  } catch {
    return
  }
  deleting.value = true
  try {
    await deleteAccount()
    ElMessage.success('账户已注销')
    router.replace('/login')
  } catch (e: unknown) {
    const detail = (e as { response?: { data?: { detail?: string } } })?.response?.data?.detail
    ElMessage.error(detail ?? '注销失败，请重试')
  } finally {
    deleting.value = false
  }
}
</script>

<style scoped>
.settings {
  width: 100%;
}
/* .muted 全局已提供颜色与字号，此处仅补段落间距 */
.muted {
  margin: 0 0 var(--space-3);
}
.theme-options {
  display: flex;
  gap: var(--space-2);
  flex-wrap: wrap;
}
.opt {
  height: 32px;
  padding: 0 var(--space-4);
  font-size: var(--text-base);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  background: transparent;
  color: var(--muted-foreground);
  cursor: pointer;
  transition:
    background-color var(--duration-fast),
    color var(--duration-fast),
    border-color var(--duration-fast);
}
.opt:hover {
  background: var(--muted);
  color: var(--foreground);
}
.opt.active {
  background: var(--primary);
  border-color: var(--primary);
  color: var(--primary-foreground);
}
.danger {
  border-color: var(--destructive);
}
.danger-title {
  color: var(--destructive);
}
</style>
