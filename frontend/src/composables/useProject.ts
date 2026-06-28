import { ref, watch } from 'vue'

import * as projectsApi from '../api/projects'
import type {
  CalcPage,
  ProjectData,
  SnapshotPublic,
} from '../api/projects'

// 模块级单例状态（跨组件共享）
const projectId = ref<number | null>(null)
const projectName = ref<string>('')
const data = ref<ProjectData | null>(null)
const loading = ref(false)
const saving = ref(false)

let saveTimer: ReturnType<typeof setTimeout> | null = null
const SAVE_DEBOUNCE_MS = 800

/** 是否有活动项目。 */
function isActive(): boolean {
  return projectId.value !== null && data.value !== null
}

/** 立即保存当前 data（取消待执行的防抖）。无活动项目则跳过。 */
async function saveNow(): Promise<void> {
  if (saveTimer) {
    clearTimeout(saveTimer)
    saveTimer = null
  }
  if (!isActive()) return
  saving.value = true
  try {
    // 不回写 res.data：后端不对前端需要的字段做规范化，回写会重新触发深度 watcher
    // → 再排一次防抖保存 → 每 800ms 空转 PATCH。前端 data 即权威。
    await projectsApi.patchProject(projectId.value!, { data: data.value! })
  } finally {
    saving.value = false
  }
}

/** 防抖保存：data 改动后延时整体 PATCH。 */
function scheduleSave(): void {
  if (!isActive()) return
  if (saveTimer) clearTimeout(saveTimer)
  saveTimer = setTimeout(() => {
    saveTimer = null
    void saveNow()
  }, SAVE_DEBOUNCE_MS)
}

async function openProject(id: number): Promise<void> {
  loading.value = true
  try {
    const res = await projectsApi.getProject(id)
    projectId.value = res.id
    projectName.value = res.name
    data.value = res.data
  } finally {
    loading.value = false
  }
}

async function createAndOpen(name: string): Promise<void> {
  loading.value = true
  try {
    const res = await projectsApi.createProject(name)
    projectId.value = res.id
    projectName.value = res.name
    data.value = res.data
  } finally {
    loading.value = false
  }
}

function closeProject(): void {
  if (saveTimer) {
    clearTimeout(saveTimer)
    saveTimer = null
  }
  projectId.value = null
  projectName.value = ''
  data.value = null
}

/**
 * 计算某页：先 flush 保存（确保后端读到最新 structure/loads）→ POST /calculate
 * → 用返回结果更新 data[P].result + initialized。
 */
async function calculate(page: CalcPage): Promise<void> {
  if (!isActive()) return
  await saveNow() // 先把待存的参数落库
  const result = await projectsApi.calculate(projectId.value!, page)
  if (data.value) {
    data.value[page].result = result
    data.value[page].initialized = true
  }
}

async function archive(name?: string): Promise<SnapshotPublic> {
  if (!isActive()) throw new Error('无活动项目')
  await saveNow()
  return projectsApi.createSnapshot(projectId.value!, name)
}

async function restoreSnapshot(snapshotId: number): Promise<void> {
  if (!isActive()) return
  const res = await projectsApi.restoreSnapshot(projectId.value!, snapshotId)
  data.value = res.data
}

// 自动保存：data 深度改动 → 防抖 PATCH（仅在有活动项目时）
watch(
  data,
  () => scheduleSave(),
  { deep: true },
)

export function useProject() {
  return {
    // 状态
    projectId,
    projectName,
    data,
    loading,
    saving,
    // 方法
    isActive,
    openProject,
    createAndOpen,
    closeProject,
    saveNow,
    calculate,
    archive,
    restoreSnapshot,
    // 透传列表/快照管理（页面按需调用）
    listProjects: projectsApi.listProjects,
    listSnapshots: projectsApi.listSnapshots,
    forkSnapshot: projectsApi.forkSnapshot,
    deleteSnapshot: projectsApi.deleteSnapshot,
    deleteProject: projectsApi.deleteProject,
  }
}
