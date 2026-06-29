<template>
  <div class="archive">
    <PageHeader title="存档管理" subtitle="快照保存、恢复与派生">
      <template #action>
        <el-button type="primary" :disabled="!isActive()" @click="archiveCurrent">生成当前快照</el-button>
      </template>
    </PageHeader>

    <p v-if="!isActive()" class="muted hint">无活动项目，请先在开始页打开一个。</p>
    <p v-else-if="loading" class="muted hint">加载中…</p>

    <!-- 项目卡片 -->
    <section
      v-for="p in projects"
      :key="p.id"
      class="proj-card"
      :class="{ active: p.id === projectId }"
    >
      <!-- 项目头 -->
      <div class="proj-head">
        <div class="proj-info">
          <span class="proj-name">
            {{ p.name }}
            <el-tag v-if="p.id === projectId" size="small" type="primary" effect="plain" round>当前</el-tag>
          </span>
          <span class="muted proj-meta">更新于 {{ p.updated_at }}</span>
        </div>
        <el-dropdown trigger="click" @command="(c: string) => onProjectCmd(c, p)">
          <el-button text size="small" class="more-btn" aria-label="项目操作">
            <Ellipsis :size="16" />
          </el-button>
          <template #dropdown>
            <el-dropdown-menu>
              <el-dropdown-item command="rename">重命名</el-dropdown-item>
              <el-dropdown-item command="delete" divided>删除项目</el-dropdown-item>
            </el-dropdown-menu>
          </template>
        </el-dropdown>
      </div>

      <!-- 快照时间线 -->
      <ul v-if="snapshotsByProject[p.id]?.length" class="timeline">
        <li v-for="snap in snapshotsByProject[p.id]" :key="snap.id" class="snap">
          <span class="snap-dot"></span>
          <div class="snap-body">
            <span class="snap-name">{{ snap.name }}</span>
            <span class="muted snap-meta">{{ snap.created_at }}</span>
          </div>
          <el-dropdown trigger="click" @command="(c: string) => onSnapCmd(c, p.id, snap)">
            <el-button text size="small" class="more-btn" aria-label="快照操作">
              <Ellipsis :size="16" />
            </el-button>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item command="restore">恢复</el-dropdown-item>
                <el-dropdown-item command="fork">Fork 副本</el-dropdown-item>
                <el-dropdown-item command="rename" divided>重命名</el-dropdown-item>
                <el-dropdown-item command="delete">删除快照</el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </li>
      </ul>
      <p v-else class="muted snap-empty">（无快照）</p>
    </section>

    <!-- 空状态 -->
    <section v-if="!projects.length && !loading" class="block">
      <EmptyState
        :icon="emptyIcon"
        title="还没有项目"
        description="存档与历史会随项目自动积累。先在开始页新建一个项目吧。"
      >
        <el-button type="primary" @click="router.push('/')">前往开始页</el-button>
      </EmptyState>
    </section>
  </div>
</template>

<script setup lang="ts">
import { markRaw, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Ellipsis, History } from '@lucide/vue'
import PageHeader from '../components/common/PageHeader.vue'
import EmptyState from '../components/common/EmptyState.vue'
import { useProject } from '../composables/useProject'
import { patchProject, renameSnapshot } from '../api/projects'
import type { ProjectPublic, SnapshotPublic } from '../api/projects'

const emptyIcon = markRaw(History)

const router = useRouter()
const {
  projectId,
  isActive,
  listProjects,
  listSnapshots,
  archive,
  restoreSnapshot,
  forkSnapshot,
  deleteSnapshot,
  deleteProject,
  openProject,
} = useProject()

const projects = ref<ProjectPublic[]>([])
const snapshotsByProject = ref<Record<number, SnapshotPublic[]>>({})
const loading = ref(false)

async function reload(): Promise<void> {
  loading.value = true
  try {
    projects.value = await listProjects()
    const map: Record<number, SnapshotPublic[]> = {}
    for (const p of projects.value) {
      map[p.id] = await listSnapshots(p.id)
    }
    snapshotsByProject.value = map
  } catch {
    ElMessage.error('加载失败')
  } finally {
    loading.value = false
  }
}

async function archiveCurrent(): Promise<void> {
  if (!isActive()) {
    ElMessage.warning('无活动项目，请先在开始页打开一个')
    return
  }
  try {
    const { value } = await ElMessageBox.prompt('归档名称（可留空）', '归档当前项目', {
      confirmButtonText: '归档',
      cancelButtonText: '取消',
    })
    await archive(value.trim() || undefined)
    ElMessage.success('已归档')
    await reload()
  } catch {
    /* 用户取消 */
  }
}

async function restore(pid: number, snap: SnapshotPublic): Promise<void> {
  try {
    await ElMessageBox.confirm('恢复将覆盖该项目当前工作态，确定？', '恢复快照', {
      type: 'warning', confirmButtonText: '恢复', cancelButtonText: '取消',
    })
  } catch {
    return
  }
  try {
    await openProject(pid)
    await restoreSnapshot(snap.id)
    ElMessage.success('已恢复')
    await reload()
  } catch {
    ElMessage.error('恢复失败')
  }
}

async function fork(pid: number, snap: SnapshotPublic): Promise<void> {
  try {
    const { value } = await ElMessageBox.prompt('新项目名称', 'Fork 副本', {
      confirmButtonText: 'Fork', cancelButtonText: '取消',
      inputPattern: /.+/, inputErrorMessage: '名称不能为空',
    })
    await forkSnapshot(pid, snap.id, value.trim())
    ElMessage.success('已 fork')
    await reload()
  } catch {
    /* 用户取消 */
  }
}

async function renameSnap(pid: number, snap: SnapshotPublic): Promise<void> {
  try {
    const { value } = await ElMessageBox.prompt('新名称', '重命名快照', {
      confirmButtonText: '保存', cancelButtonText: '取消',
      inputValue: snap.name, inputPattern: /.+/, inputErrorMessage: '名称不能为空',
    })
    await renameSnapshot(pid, snap.id, value.trim())
    ElMessage.success('已重命名')
    await reload()
  } catch {
    /* 用户取消 */
  }
}

async function removeSnapshot(snap: SnapshotPublic): Promise<void> {
  try {
    await ElMessageBox.confirm(`删除快照「${snap.name}」？`, '删除快照', {
      type: 'warning', confirmButtonText: '删除', cancelButtonText: '取消',
    })
  } catch {
    return
  }
  try {
    await deleteSnapshot(snap.id)
    await reload()
  } catch {
    ElMessage.error('删除失败')
  }
}

async function renameProject(p: ProjectPublic): Promise<void> {
  try {
    const { value } = await ElMessageBox.prompt('新名称', '重命名项目', {
      confirmButtonText: '保存', cancelButtonText: '取消',
      inputValue: p.name, inputPattern: /.+/, inputErrorMessage: '名称不能为空',
    })
    await patchProject(p.id, { name: value.trim() })
    ElMessage.success('已重命名')
    await reload()
  } catch {
    /* 用户取消 */
  }
}

async function removeProject(p: ProjectPublic): Promise<void> {
  try {
    await ElMessageBox.confirm(`删除项目「${p.name}」及其全部快照？不可恢复。`, '删除项目', {
      type: 'error', confirmButtonText: '删除', cancelButtonText: '取消',
    })
  } catch {
    return
  }
  try {
    await deleteProject(p.id)
    ElMessage.success('项目已删除')
    await reload()
  } catch {
    ElMessage.error('删除失败')
  }
}

function onProjectCmd(cmd: string, p: ProjectPublic): void {
  if (cmd === 'rename') void renameProject(p)
  else if (cmd === 'delete') void removeProject(p)
}

function onSnapCmd(cmd: string, pid: number, snap: SnapshotPublic): void {
  if (cmd === 'restore') void restore(pid, snap)
  else if (cmd === 'fork') void fork(pid, snap)
  else if (cmd === 'rename') void renameSnap(pid, snap)
  else if (cmd === 'delete') void removeSnapshot(snap)
}

onMounted(reload)
</script>

<style scoped>
.archive {
  width: 100%;
}
.hint {
  margin-top: var(--space-5);
}

/* 项目卡片 */
.proj-card {
  margin-top: var(--space-5);
  padding: var(--space-4) var(--space-5);
  background: var(--card);
  border: 1px solid var(--border);
  border-radius: var(--radius);
}
.proj-card.active {
  border-color: var(--primary);
  box-shadow: 0 0 0 1px var(--primary) inset;
}
.proj-head {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: var(--space-3);
}
.proj-info {
  display: flex;
  flex-direction: column;
  gap: var(--space-1);
  min-width: 0;
}
.proj-name {
  font-size: var(--text-lg);
  font-weight: 600;
  color: var(--foreground);
  display: inline-flex;
  align-items: center;
  gap: var(--space-2);
  flex-wrap: wrap;
}
.proj-meta {
  font-size: var(--text-sm);
}
.more-btn {
  color: var(--muted-foreground);
  padding: var(--space-1);
  flex-shrink: 0;
}
.more-btn:hover {
  color: var(--primary);
}

/* 快照时间线 */
.timeline {
  list-style: none;
  margin: var(--space-4) 0 0;
  padding: 0 0 0 var(--space-2);
  position: relative;
}
.timeline::before {
  content: '';
  position: absolute;
  left: var(--space-3);
  top: 6px;
  bottom: 6px;
  width: 2px;
  background: var(--border);
}
.snap {
  display: flex;
  align-items: center;
  gap: var(--space-3);
  padding: var(--space-2) 0;
  position: relative;
}
.snap-dot {
  width: 10px;
  height: 10px;
  border-radius: 50%;
  background: var(--card);
  border: 2px solid var(--primary);
  flex-shrink: 0;
  margin-left: 3px;
  z-index: 1;
}
.snap-body {
  display: flex;
  flex-direction: column;
  gap: 2px;
  min-width: 0;
  flex: 1;
}
.snap-name {
  font-size: var(--text-base);
  color: var(--foreground);
}
.snap-meta {
  font-size: var(--text-sm);
}
.snap-empty {
  margin: var(--space-3) 0 0;
  font-size: var(--text-sm);
}
</style>
