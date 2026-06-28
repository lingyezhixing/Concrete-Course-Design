<template>
  <div class="overview">
    <PageHeader
      title="工作台"
      :subtitle="currentUser ? `${currentUser.username} 的项目概览` : '项目概览'"
    />

    <h3 v-if="projects.length || loading" class="grid-title">所有项目</h3>

    <!-- 加载骨架 -->
    <div v-if="loading" class="grid">
      <div v-for="i in 3" :key="i" class="proj-card skeleton-card">
        <div class="proj-card-inner">
          <Skeleton height="16px" width="60%" />
          <Skeleton height="12px" width="40%" />
        </div>
      </div>
    </div>

    <!-- 项目网格 -->
    <div v-else-if="projects.length" class="grid">
      <button
        v-for="p in projects"
        :key="p.id"
        class="proj-card"
        :class="{ active: p.id === projectId }"
        @click="open(p)"
      >
        <div class="proj-card-inner">
          <div class="proj-card-top">
            <span class="proj-card-name">{{ p.name }}</span>
            <el-tag v-if="p.id === projectId" size="small" type="primary" effect="light" round>当前</el-tag>
          </div>
          <span class="muted proj-card-meta">更新于 {{ p.updated_at }}</span>
        </div>
      </button>

      <button class="proj-card new-card" @click="newProject">
        <Plus :size="22" class="new-icon" />
        <span class="new-label">新建项目</span>
      </button>
    </div>

    <!-- 空状态 -->
    <section v-else class="block">
      <EmptyState
        :icon="emptyIcon"
        title="还没有项目"
        description="新建一个项目，开始板、次梁、主梁的配筋计算。"
      >
        <el-button type="primary" @click="newProject">新建项目</el-button>
      </EmptyState>
    </section>
  </div>
</template>

<script setup lang="ts">
import { markRaw, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, FolderOpen } from '@lucide/vue'
import PageHeader from '../components/common/PageHeader.vue'
import EmptyState from '../components/common/EmptyState.vue'
import Skeleton from '../components/common/Skeleton.vue'
import { useProject } from '../composables/useProject'
import { useAuth } from '../composables/useAuth'
import type { ProjectPublic } from '../api/projects'

const emptyIcon = markRaw(FolderOpen)

const router = useRouter()
const { currentUser } = useAuth()
const { projectId, listProjects, openProject, createAndOpen } = useProject()

const projects = ref<ProjectPublic[]>([])
const loading = ref(false)

async function reload(): Promise<void> {
  loading.value = true
  try {
    projects.value = await listProjects()
  } catch {
    ElMessage.error('加载项目列表失败')
  } finally {
    loading.value = false
  }
}

async function open(p: ProjectPublic): Promise<void> {
  try {
    await openProject(p.id)
    router.push('/params')
  } catch {
    ElMessage.error('打开项目失败')
  }
}

async function newProject(): Promise<void> {
  try {
    const { value } = await ElMessageBox.prompt('输入项目名称', '新建项目', {
      confirmButtonText: '创建',
      cancelButtonText: '取消',
      inputPattern: /.+/,
      inputErrorMessage: '名称不能为空',
    })
    await createAndOpen(value.trim())
    router.push('/params')
  } catch {
    /* 用户取消 */
  }
}

onMounted(reload)
</script>

<style scoped>
.overview {
  width: 100%;
}
.grid-title {
  margin: var(--space-5) 0 var(--space-3);
  font-size: var(--text-md);
  font-weight: 600;
  color: var(--foreground);
}
.grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(220px, 1fr));
  gap: var(--space-3);
}
.proj-card {
  text-align: left;
  padding: 0;
  background: var(--card);
  border: 1px solid var(--border);
  border-left: 3px solid transparent;
  border-radius: var(--radius);
  cursor: pointer;
  font: inherit;
  color: inherit;
  transition:
    box-shadow var(--duration),
    transform var(--duration),
    border-color var(--duration);
}
.proj-card:hover {
  box-shadow: var(--el-box-shadow-dark);
  transform: translateY(-2px);
  border-color: var(--border);
  border-left-color: var(--primary);
}
.proj-card.active {
  border-left-color: var(--primary);
  background: color-mix(in srgb, var(--primary) 6%, var(--card));
}
.proj-card.active:hover {
  border-color: var(--primary);
}
.proj-card-inner {
  padding: var(--space-4) var(--space-5);
  display: flex;
  flex-direction: column;
  gap: var(--space-2);
}
.proj-card-top {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: var(--space-2);
}
.proj-card-name {
  font-size: var(--text-lg);
  font-weight: 600;
  color: var(--foreground);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.proj-card-meta {
  font-size: var(--text-sm);
}
.skeleton-card {
  border-left: 3px solid var(--border);
}

/* 新建卡片 */
.new-card {
  display: flex;
  align-items: center;
  justify-content: center;
  border-style: dashed;
  color: var(--muted-foreground);
  min-height: 76px;
}
.new-card:hover {
  border-color: var(--primary);
  color: var(--primary);
}
.new-icon {
  margin-bottom: 2px;
}
.new-label {
  font-size: var(--text-base);
  font-weight: 500;
}
</style>
