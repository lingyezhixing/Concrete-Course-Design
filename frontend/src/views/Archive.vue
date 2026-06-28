<template>
  <div class="archive">
    <PageHeader title="存档与历史" subtitle="归档 / 恢复 / fork / 管理" />

    <!-- 顶部操作：归档当前 -->
    <section class="toolbar">
      <el-button type="primary" :disabled="!isActive()" @click="archiveCurrent">
        归档当前
      </el-button>
      <span v-if="!isActive()" class="muted-inline">无活动项目，请先在开始页打开一个</span>
    </section>

    <!-- 项目列表 -->
    <section
      v-for="p in projects"
      :key="p.id"
      class="block"
      :class="{ active: p.id === projectId }"
    >
      <div class="proj-head">
        <div class="proj-info">
          <span class="proj-name">
            {{ p.name }}
            <el-tag v-if="p.id === projectId" size="small" type="success">当前</el-tag>
            <el-tag v-if="p.has_uncommitted" size="small" type="warning">未归档</el-tag>
          </span>
          <span class="muted proj-meta">更新于 {{ p.updated_at }}</span>
        </div>
        <div class="proj-actions">
          <el-button size="small" @click="renameProject(p)">重命名</el-button>
          <el-button size="small" type="danger" plain @click="removeProject(p)">删除项目</el-button>
        </div>
      </div>

      <!-- 快照列表 -->
      <ul v-if="snapshotsByProject[p.id]?.length" class="snap-list">
        <li v-for="snap in snapshotsByProject[p.id]" :key="snap.id" class="snap-row">
          <div class="snap-info">
            <span class="snap-name">{{ snap.name }}</span>
            <span class="muted snap-meta">归档于 {{ snap.created_at }}</span>
          </div>
          <div class="snap-actions">
            <el-button size="small" @click="restore(p.id, snap)">恢复</el-button>
            <el-button size="small" @click="fork(p.id, snap)">fork</el-button>
            <el-button size="small" type="danger" plain @click="removeSnapshot(snap)">删除快照</el-button>
          </div>
        </li>
      </ul>
      <p v-else class="muted snap-empty">（无快照）</p>
    </section>

    <!-- 空状态 -->
    <section v-if="!projects.length && !loading" class="block empty">
      <p class="muted">还没有项目</p>
      <el-button type="primary" @click="router.push('/')">前往开始页</el-button>
    </section>
  </div>
</template>

<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import PageHeader from '../components/common/PageHeader.vue'
import { useProject } from '../composables/useProject'
import { patchProject } from '../api/projects'
import type { ProjectPublic, SnapshotPublic } from '../api/projects'

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
      type: 'warning',
      confirmButtonText: '恢复',
      cancelButtonText: '取消',
    })
  } catch {
    return
  }
  try {
    await openProject(pid) // restoreSnapshot 作用于活动项目
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
      confirmButtonText: 'Fork',
      cancelButtonText: '取消',
      inputPattern: /.+/,
      inputErrorMessage: '名称不能为空',
    })
    await forkSnapshot(pid, snap.id, value.trim())
    ElMessage.success('已 fork')
    await reload()
  } catch {
    /* 用户取消 */
  }
}

async function removeSnapshot(snap: SnapshotPublic): Promise<void> {
  try {
    await ElMessageBox.confirm(`删除快照「${snap.name}」？`, '删除快照', {
      type: 'warning',
      confirmButtonText: '删除',
      cancelButtonText: '取消',
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
      confirmButtonText: '保存',
      cancelButtonText: '取消',
      inputValue: p.name,
      inputPattern: /.+/,
      inputErrorMessage: '名称不能为空',
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
      type: 'error',
      confirmButtonText: '删除',
      cancelButtonText: '取消',
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

onMounted(reload)
</script>

<style scoped>
.archive {
  max-width: 720px;
}
.toolbar {
  margin-top: 20px;
  display: flex;
  align-items: center;
  gap: 12px;
}
.muted-inline {
  color: var(--muted-foreground);
  font-size: 13px;
}
.block {
  margin-top: 20px;
  padding: 16px;
  background: var(--card);
  border: 1px solid var(--border);
  border-radius: var(--radius);
}
.block.active {
  border-color: var(--primary);
}
.proj-head {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 12px;
  flex-wrap: wrap;
}
.proj-info {
  display: flex;
  flex-direction: column;
  gap: 4px;
  min-width: 0;
}
.proj-name {
  font-size: 14px;
  font-weight: 600;
  color: var(--foreground);
  display: inline-flex;
  align-items: center;
  gap: 6px;
  flex-wrap: wrap;
}
.proj-meta {
  font-size: 12px;
}
.proj-actions {
  display: flex;
  gap: 8px;
  flex-shrink: 0;
}
.muted {
  margin: 0;
  color: var(--muted-foreground);
  font-size: 13px;
}
.snap-list {
  list-style: none;
  margin: 12px 0 0;
  padding: 0;
  border-top: 1px solid var(--border);
}
.snap-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  padding: 10px 0;
  border-top: 1px solid var(--border);
}
.snap-row:first-child {
  border-top: none;
}
.snap-info {
  display: flex;
  flex-direction: column;
  gap: 2px;
  min-width: 0;
}
.snap-name {
  font-size: 13px;
  color: var(--foreground);
}
.snap-meta {
  font-size: 12px;
}
.snap-actions {
  display: flex;
  gap: 8px;
  flex-shrink: 0;
}
.snap-empty {
  margin: 10px 0 0;
  font-size: 12px;
}
.empty {
  text-align: center;
}
.empty .muted {
  margin-bottom: 14px;
}
</style>
