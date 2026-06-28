import api from './index'

export interface Materials {
  fc: number | null
  fy_slab: number | null
  fy_beam: number | null
  gamma_d: number | null
}

export interface Structure {
  L1: number | null
  L2: number | null
  slab_thickness: number | null
  beam_width: number | null
  beam_height: number | null
  main_beam_width: number | null
  main_beam_height: number | null
  column_width: number | null
  slab_spans: number | null
  beam_spans: number | null
  main_beam_spans: number | null
}

export interface Loads {
  reinforced_concrete_weight: number | null
  terrazzo_surface: number | null
  plaster_thickness: number | null
  plaster_weight: number | null
  live_load: number | null
  dead_load_factor: number
  live_load_factor: number
}

export interface ComponentState {
  result: Record<string, unknown> | null
  initialized: boolean
}

export interface ProjectData {
  structure: Structure
  materials: Materials
  loads: Loads
  slab: ComponentState
  beam: ComponentState
  main_beam: ComponentState
}

export interface ProjectPublic {
  id: number
  name: string
  data: ProjectData
  created_at: string
  updated_at: string
  last_opened_at: string | null
  has_uncommitted: boolean
}

export interface SnapshotPublic {
  id: number
  project_id: number
  name: string
  data: ProjectData
  created_at: string
}

export interface CheckItem {
  name: string
  status: 'pass' | 'review' | 'fail'
  clause: string
  detail: string
}

export type CalcPage = 'slab' | 'beam' | 'main_beam'

export interface ChecksResponse {
  slab: CheckItem[]
}

/** 空数据骨架（与后端 empty_data 一致），供前端初始化用。 */
export function emptyProjectData(): ProjectData {
  const comp = (): ComponentState => ({ result: null, initialized: false })
  return {
    structure: {
      L1: null, L2: null, slab_thickness: null,
      beam_width: null, beam_height: null,
      main_beam_width: null, main_beam_height: null,
      column_width: null,
      slab_spans: null, beam_spans: null, main_beam_spans: null,
    },
    materials: { fc: 9.6, fy_slab: 270, fy_beam: 300, gamma_d: 1.2 },
    loads: {
      reinforced_concrete_weight: null, terrazzo_surface: null,
      plaster_thickness: null, plaster_weight: null, live_load: null,
      dead_load_factor: 1.05, live_load_factor: 1.2,
    },
    slab: comp(),
    beam: comp(),
    main_beam: comp(),
  }
}

export async function listProjects(): Promise<ProjectPublic[]> {
  const { data } = await api.get<ProjectPublic[]>('/projects')
  return data
}

export async function createProject(name: string): Promise<ProjectPublic> {
  const { data } = await api.post<ProjectPublic>('/projects', { name })
  return data
}

export async function getProject(id: number): Promise<ProjectPublic> {
  const { data } = await api.get<ProjectPublic>(`/projects/${id}`)
  return data
}

export async function patchProject(
  id: number,
  payload: { name?: string; data?: ProjectData },
): Promise<ProjectPublic> {
  const { data } = await api.patch<ProjectPublic>(`/projects/${id}`, payload)
  return data
}

export async function deleteProject(id: number): Promise<void> {
  await api.delete(`/projects/${id}`)
}

/** 返回该页的计算结果（后端已持久化 result+initialized）。 */
export async function calculate(
  id: number,
  page: CalcPage,
): Promise<Record<string, unknown>> {
  const { data } = await api.post<Record<string, unknown>>(`/projects/${id}/calculate`, { page })
  return data
}

export async function getChecks(id: number): Promise<ChecksResponse> {
  const { data } = await api.get<ChecksResponse>(`/projects/${id}/checks`)
  return data
}

export async function listSnapshots(projectId: number): Promise<SnapshotPublic[]> {
  const { data } = await api.get<SnapshotPublic[]>(`/projects/${projectId}/snapshots`)
  return data
}

export async function createSnapshot(
  projectId: number,
  name?: string,
): Promise<SnapshotPublic> {
  const { data } = await api.post<SnapshotPublic>(`/projects/${projectId}/snapshots`, { name })
  return data
}

export async function restoreSnapshot(
  projectId: number,
  snapshotId: number,
): Promise<ProjectPublic> {
  const { data } = await api.post<ProjectPublic>(
    `/projects/${projectId}/snapshots/${snapshotId}/restore`,
  )
  return data
}

export async function forkSnapshot(
  projectId: number,
  snapshotId: number,
  name?: string,
): Promise<ProjectPublic> {
  const { data } = await api.post<ProjectPublic>(
    `/projects/${projectId}/snapshots/${snapshotId}/fork`,
    { name },
  )
  return data
}

export async function deleteSnapshot(snapshotId: number): Promise<void> {
  await api.delete(`/snapshots/${snapshotId}`)
}
