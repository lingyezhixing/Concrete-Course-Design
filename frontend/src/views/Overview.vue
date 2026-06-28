<template>
  <div class="overview">
    <PageHeader
      title="开始"
      :subtitle="currentUser ? `${currentUser.username} 的项目与设计参数总览` : '项目与设计参数总览'"
    />

    <!-- 首次使用：0 项目且未关闭 -->
    <section v-if="showFirstUse" class="block first-use">
      <h2 class="block-title">创建你的第一个项目</h2>
      <p class="muted">还没有项目。新建一个开始你的混凝土课程设计计算。</p>
      <div class="actions">
        <el-button type="primary" @click="newProject">创建</el-button>
        <el-button text @click="firstUseDismissed = true">×关闭</el-button>
      </div>
    </section>

    <!-- 未归档恢复横幅（非阻塞，页面顶部） -->
    <section v-if="active && active.has_uncommitted" class="banner">
      <span class="banner-text">『{{ active.name }}』有未归档的改动</span>
      <div class="banner-actions">
        <el-button size="small" type="primary" plain @click="continueProject(active)">
          继续
        </el-button>
        <el-button size="small" type="danger" plain :loading="discardingId === active.id" @click="discard(active)">
          丢弃
        </el-button>
      </div>
    </section>

    <!-- 继续：最近项目 -->
    <section v-if="active && !isEmpty" class="block continue">
      <div class="continue-main">
        <h2 class="block-title">继续：{{ active.name }}</h2>
        <p class="muted">更新于 {{ active.updated_at }}</p>
      </div>
      <el-button type="primary" @click="continueProject(active)">继续工作</el-button>
    </section>

    <!-- 操作区：新建项目 -->
    <section v-if="!isEmpty" class="toolbar">
      <el-button type="primary" @click="newProject">新建项目</el-button>
    </section>

    <!-- 项目列表 -->
    <section v-if="!isEmpty" class="block">
      <h2 class="block-title">全部项目</h2>
      <ul class="proj-list">
        <li v-for="p in projects" :key="p.id" class="proj-row">
          <div class="proj-info">
            <span class="proj-name">
              {{ p.name }}
              <span v-if="p.has_uncommitted" class="dot" title="有未归档改动"></span>
            </span>
            <span class="muted proj-meta">更新于 {{ p.updated_at }}</span>
          </div>
          <el-button size="small" @click="continueProject(p)">打开</el-button>
        </li>
      </ul>
      <div class="archive-link">
        <el-button link type="primary" @click="router.push('/archive')">查看全部历史 →</el-button>
      </div>
    </section>

    <!-- 空状态（首次提示已关闭） -->
    <section v-if="isEmpty && !showFirstUse" class="block empty">
      <p class="muted">还没有项目</p>
      <el-button type="primary" @click="newProject">新建项目</el-button>
    </section>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import PageHeader from '../components/common/PageHeader.vue'
import { useProject } from '../composables/useProject'
import { useAuth } from '../composables/useAuth'
import type { ProjectPublic } from '../api/projects'

const router = useRouter()
const { currentUser } = useAuth()
const {
  listProjects,
  openProject,
  createAndOpen,
  listSnapshots,
  restoreSnapshot,
  deleteProject,
} = useProject()

const projects = ref<ProjectPublic[]>([])
const loading = ref(false)
const firstUseDismissed = ref(false)
/** 正在执行丢弃的项目 id（按钮 loading 态）。null=无。 */
const discardingId = ref<number | null>(null)

const isEmpty = computed(() => projects.value.length === 0)
const showFirstUse = computed(() => isEmpty.value && !firstUseDismissed.value)
/** 最近打开的项目（列表按 last_opened_at DESC 排序，故 [0] 即最近）。 */
const active = computed<ProjectPublic | null>(() => projects.value[0] ?? null)

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

async function continueProject(p: ProjectPublic): Promise<void> {
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
    /* 用户取消，忽略 */
  }
}

async function discard(p: ProjectPublic): Promise<void> {
  discardingId.value = p.id
  try {
    const snaps = await listSnapshots(p.id)
    if (snaps.length > 0) {
      // 有归档：回滚到最近一次归档（恢复工作状态）。
      // useProject.restoreSnapshot 作用于当前活动项目，故先打开目标项目。
      await openProject(p.id)
      await restoreSnapshot(snaps[0].id)
      ElMessage.success(`已回滚「${p.name}」到最近归档`)
    } else {
      // 无归档：丢弃等于删除整个项目（不可恢复）。
      try {
        await ElMessageBox.confirm(
          `「${p.name}」从未归档，丢弃将删除整个项目，确定？`,
          '丢弃（不可恢复）',
          { type: 'warning', confirmButtonText: '删除项目', cancelButtonText: '取消' },
        )
      } catch {
        return // 取消确认
      }
      await deleteProject(p.id)
      ElMessage.success('项目已删除')
    }
    await reload()
  } catch {
    ElMessage.error('操作失败，请重试')
  } finally {
    discardingId.value = null
  }
}

onMounted(reload)
</script>

<style scoped>
.overview {
  max-width: 720px;
}
.block {
  margin-top: 20px;
  padding: 16px;
  background: var(--card);
  border: 1px solid var(--border);
  border-radius: var(--radius);
}
.block-title {
  margin: 0 0 12px;
  font-size: 14px;
  font-weight: 600;
  color: var(--foreground);
}
.muted {
  margin: 0;
  color: var(--muted-foreground);
  font-size: 13px;
}
.actions {
  display: flex;
  gap: 8px;
  margin-top: 14px;
}

/* 未归档恢复横幅（非阻塞，顶部，强调色边框） */
.banner {
  margin-top: 20px;
  padding: 12px 16px;
  background: var(--card);
  border: 1px solid var(--border);
  border-left: 3px solid var(--warning);
  border-radius: var(--radius);
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
}
.banner-text {
  font-size: 13px;
  color: var(--foreground);
}
.banner-actions {
  display: flex;
  gap: 8px;
  flex-shrink: 0;
}

/* 继续：最近项目 */
.continue {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
}
.continue-main {
  min-width: 0;
}
.continue-main .block-title {
  margin-bottom: 4px;
  font-size: 15px;
}

/* 操作区 */
.toolbar {
  margin-top: 20px;
}

/* 项目列表 */
.proj-list {
  list-style: none;
  margin: 0;
  padding: 0;
}
.proj-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  padding: 10px 0;
  border-top: 1px solid var(--border);
}
.proj-row:first-child {
  border-top: none;
}
.proj-info {
  display: flex;
  flex-direction: column;
  gap: 2px;
  min-width: 0;
}
.proj-name {
  font-size: 14px;
  color: var(--foreground);
  display: inline-flex;
  align-items: center;
  gap: 6px;
}
.proj-meta {
  font-size: 12px;
}
.dot {
  width: 7px;
  height: 7px;
  border-radius: 50%;
  background: var(--warning);
  display: inline-block;
  flex-shrink: 0;
}
.archive-link {
  margin-top: 12px;
}

/* 空状态 */
.empty {
  text-align: center;
}
.empty .muted {
  margin-bottom: 14px;
}
</style>
