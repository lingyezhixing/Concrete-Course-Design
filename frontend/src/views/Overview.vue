<template>
  <div class="overview">
    <PageHeader
      title="开始"
      :subtitle="currentUser ? `${currentUser.username} 的设计工作台` : '设计工作台'"
    />

    <!-- 所有项目 -->
    <section class="grid-section">
      <h3 class="grid-title" v-if="projects.length">所有项目</h3>
      <div class="grid">
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
    </section>
  </div>
</template>

<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus } from '@lucide/vue'
import PageHeader from '../components/common/PageHeader.vue'
import { useProject } from '../composables/useProject'
import { useAuth } from '../composables/useAuth'
import type { ProjectPublic } from '../api/projects'

const router = useRouter()
const { currentUser } = useAuth()
const { projectId, listProjects, openProject, createAndOpen } = useProject()

const projects = ref<ProjectPublic[]>([])

async function reload(): Promise<void> {
  try {
    projects.value = await listProjects()
  } catch {
    ElMessage.error('加载项目列表失败')
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
.muted {
  color: var(--muted-foreground);
  font-size: 13px;
}
.grid-section {
  margin-top: 20px;
}
.grid-title {
  margin: 0 0 12px;
  font-size: 14px;
  font-weight: 600;
  color: var(--foreground);
}
.grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(220px, 1fr));
  gap: 14px;
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
  transition: box-shadow 0.2s, transform 0.2s, border-color 0.2s;
}
.proj-card:hover {
  box-shadow: 0 3px 12px rgba(0, 0, 0, 0.1);
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
  padding: 18px 20px;
  display: flex;
  flex-direction: column;
  gap: 8px;
}
.proj-card-top {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 10px;
}
.proj-card-name {
  font-size: 15px;
  font-weight: 600;
  color: var(--foreground);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.proj-card-meta {
  font-size: 12px;
}

/* 新建卡片 */
.new-card {
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
  font-size: 13px;
  font-weight: 500;
}
</style>
