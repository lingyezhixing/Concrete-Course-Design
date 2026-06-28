import { beforeEach, describe, expect, it, vi } from 'vitest'

// mock 整个 api 模块
vi.mock('../api/projects', () => {
  const state: { patched: number; calcResult: Record<string, unknown> } = {
    patched: 0,
    calcResult: { sections: [{ name: 'M1' }] },
  }
  const emptyData = () => ({
    structure: {
      L1: null, L2: null, slab_thickness: null,
      beam_width: null, beam_height: null,
      main_beam_width: null, main_beam_height: null,
      column_width: null,
      slab_spans: null, beam_spans: null, main_beam_spans: null,
      beam_stirrup_diameter: null, main_beam_stirrup_diameter: null,
    },
    materials: { fc: 9.6, fy_slab: 270, fy_beam: 300, gamma_d: 1.2 },
    loads: {
      reinforced_concrete_weight: null, terrazzo_surface: null,
      plaster_thickness: null, plaster_weight: null, live_load: null,
      dead_load_factor: 1.05, live_load_factor: 1.2,
    },
    slab: { result: null, initialized: false },
    beam: { result: null, initialized: false },
    main_beam: { result: null, initialized: false },
  })
  return {
    emptyProjectData: emptyData,
    listProjects: vi.fn(async () => []),
    createProject: vi.fn(async (name: string) => ({
      id: 1, name, data: emptyData(),
      created_at: 't', updated_at: 't', last_opened_at: null, has_uncommitted: false,
    })),
    getProject: vi.fn(async (id: number) => ({
      id, name: 'p', data: {
        ...emptyData(),
        materials: { fc: 9.6, fy_slab: 270, fy_beam: 300, gamma_d: 1.2 },
      },
      created_at: 't', updated_at: 't', last_opened_at: null, has_uncommitted: false,
    })),
    patchProject: vi.fn(async (id: number, payload: { data?: unknown }) => {
      state.patched += 1
      return {
        id, name: 'p',
        data: (payload.data as any) ?? emptyData(),
        created_at: 't', updated_at: 't2', last_opened_at: null, has_uncommitted: true,
      }
    }),
    deleteProject: vi.fn(async () => undefined),
    calculate: vi.fn(async () => state.calcResult),
    listSnapshots: vi.fn(async () => []),
    createSnapshot: vi.fn(async (_pid: number, name?: string) => ({
      id: 10, project_id: 1, name: name ?? 's', data: {}, created_at: 't',
    })),
    restoreSnapshot: vi.fn(async (pid: number) => ({
      id: pid, name: 'p', data: {
        ...emptyData(),
        materials: { fc: 9.6, fy_slab: 270, fy_beam: 300, gamma_d: 1.2 },
        slab: { result: { x: 1 }, initialized: true },
      },
      created_at: 't', updated_at: 't', last_opened_at: null, has_uncommitted: false,
    })),
    forkSnapshot: vi.fn(async () => ({
      id: 2, name: 'fork', data: {}, created_at: 't', updated_at: 't', last_opened_at: null, has_uncommitted: true,
    })),
    deleteSnapshot: vi.fn(async () => undefined),
    __state: state,
  }
})

import { useProject } from './useProject'
import * as projectsApi from '../api/projects'

describe('useProject', () => {
  beforeEach(() => {
    // 每个用例重置单例
    const { closeProject } = useProject()
    closeProject()
    vi.clearAllMocks()
  })

  it('openProject sets active project + data', async () => {
    const { openProject, projectId, data, isActive } = useProject()
    expect(isActive()).toBe(false)
    await openProject(1)
    expect(projectId.value).toBe(1)
    expect(isActive()).toBe(true)
    expect(data.value?.materials.fc).toBe(9.6)
    expect(projectsApi.getProject).toHaveBeenCalledWith(1)
  })

  it('editing data triggers debounced save', async () => {
    vi.useFakeTimers()
    try {
      const { openProject, data } = useProject()
      await openProject(1)
      ;(projectsApi.patchProject as any).mockClear()

      // 模拟编辑结构参数
      data.value!.structure.L1 = 30
      // 防抖未到，不应已保存
      expect(projectsApi.patchProject).not.toHaveBeenCalled()

      await vi.advanceTimersByTimeAsync(800)
      expect(projectsApi.patchProject).toHaveBeenCalledTimes(1)
    } finally {
      vi.useRealTimers()
    }
  })

  it('calculate flushes save, calls /calculate, writes result + initialized', async () => {
    const { openProject, calculate, data } = useProject()
    await openProject(1)
    await calculate('slab')
    // 先 flush save（patchProject 被调用）
    expect(projectsApi.patchProject).toHaveBeenCalled()
    // calculate 被调用
    expect(projectsApi.calculate).toHaveBeenCalledWith(1, 'slab')
    // 结果写回
    expect(data.value?.slab.initialized).toBe(true)
    expect((data.value?.slab.result as any)?.sections?.[0]?.name).toBe('M1')
  })

  it('restoreSnapshot updates data from response', async () => {
    const { openProject, restoreSnapshot, data } = useProject()
    await openProject(1)
    await restoreSnapshot(10)
    expect(data.value?.slab.initialized).toBe(true)
    expect((data.value?.slab.result as any)?.x).toBe(1)
  })

  it('closeProject clears state', async () => {
    const { openProject, closeProject, projectId, data, isActive } = useProject()
    await openProject(1)
    closeProject()
    expect(isActive()).toBe(false)
    expect(projectId.value).toBeNull()
    expect(data.value).toBeNull()
  })
})
