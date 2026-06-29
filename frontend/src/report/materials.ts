// 镜像 backend/app/materials.py（单一来源在后端；此处供前端计算书/简图使用，改动需同步）。
// γG/γQ 在后端固定（solvers/derive.py），此处一并镜像。

/** C20 混凝土轴心抗压强度设计值 (N/mm²) */
export const FC = 9.6
/** C20 混凝土轴心抗拉强度设计值 (N/mm²) */
export const FT = 1.10
/** 板受力筋 HPB300 抗拉强度设计值 (N/mm²) */
export const FY_SLAB = 270
/** 梁纵筋 HRB335 抗拉强度设计值 (N/mm²) */
export const FY_BEAM = 300
/** 箍筋/构造筋抗拉强度设计值（HPB300，同 FY_SLAB）(N/mm²) */
export const FYV = 270
/** 结构系数 γd（SL 191-2008） */
export const GAMMA_D = 1.2
/** 恒载分项系数 γG（后端固定） */
export const GAMMA_G = 1.05
/** 活载分项系数 γQ（后端固定） */
export const GAMMA_Q = 1.2
