<!-- 把 ReportDoc 树渲染为 A4 打印文档：封面 + 目录 + 各章节块。
     figure 块按 figureKind 映射到具体简图组件。 -->
<template>
  <div class="rp-doc">
    <!-- 封面 -->
    <section class="rp-cover">
      <h1 class="rp-cover-title">钢筋混凝土课程设计计算书</h1>
      <p class="rp-cover-sub">整体式单向板肋形楼盖设计</p>
      <table class="rp-cover-table">
        <tbody>
          <tr><td>学　　院</td><td>{{ cover.college || '　' }}</td></tr>
          <tr><td>专　　业</td><td>{{ cover.major || '　' }}</td></tr>
          <tr><td>姓　　名</td><td>{{ cover.name || '　' }}</td></tr>
          <tr><td>学　　号</td><td>{{ cover.student_id || '　' }}</td></tr>
          <tr><td>指导教师</td><td>{{ cover.advisor || '　' }}</td></tr>
        </tbody>
      </table>
      <p class="rp-cover-date">{{ cover.date || '　' }}</p>
    </section>

    <!-- 目录 -->
    <section class="rp-toc">
      <h2 class="rp-toc-title">目录</h2>
      <ol>
        <li v-for="s in doc.sections" :key="s.id">
          <span class="rp-toc-num">{{ s.number }}</span>
          <span class="rp-toc-dots">．．．．．．．．．．．．．．．．．．．．</span>
          <span class="rp-toc-title-text">{{ s.title }}</span>
        </li>
      </ol>
    </section>

    <!-- 正文 -->
    <section
      v-for="s in doc.sections"
      :key="s.id"
      :id="'rp-sec-' + s.id"
      class="rp-section"
    >
      <h2 class="rp-section-title"><span class="rp-num">{{ s.number }}、</span>{{ s.title }}</h2>
      <template v-for="(b, i) in s.blocks" :key="i">
        <h3 v-if="b.kind === 'heading' && b.level === 3" class="rp-h3">{{ b.text }}</h3>
        <p v-else-if="b.kind === 'paragraph'" class="rp-p">{{ b.text }}</p>
        <div v-else-if="b.kind === 'formula'" class="rp-formula">{{ b.text }}</div>
        <div v-else-if="b.kind === 'note'" class="rp-note" :class="'tone-' + (b.tone || 'info')">{{ b.text }}</div>
        <figure v-else-if="b.kind === 'figure'" class="rp-figure">
          <component :is="figureComp(b.figure)" v-bind="b.props" />
          <figcaption>{{ b.caption }}</figcaption>
        </figure>
        <div v-else-if="b.kind === 'table'" class="rp-table-wrap">
          <p v-if="b.caption" class="rp-table-caption">{{ b.caption }}</p>
          <table class="rp-table">
            <thead>
              <tr><th v-for="(h, hi) in b.headers" :key="hi">{{ h }}</th></tr>
            </thead>
            <tbody>
              <tr v-for="(row, ri) in b.rows" :key="ri">
                <td v-for="(cell, ci) in row" :key="ci">{{ cell }}</td>
              </tr>
            </tbody>
          </table>
        </div>
      </template>
    </section>
  </div>
</template>

<script setup lang="ts">
import { computed, markRaw } from 'vue'
import type { Component } from 'vue'
import type { ReportDoc, FigureKind } from '../../report/types'
import UniformLoadBeamDiagram from '../diagrams/UniformLoadBeamDiagram.vue'
import MainBeamDiagram from '../diagrams/MainBeamDiagram.vue'
import InternalForceDiagram from '../diagrams/InternalForceDiagram.vue'
import SectionRebarDiagram from '../diagrams/SectionRebarDiagram.vue'
import ResistingMomentDiagram from '../diagrams/ResistingMomentDiagram.vue'

const props = defineProps<{ doc: ReportDoc }>()
const cover = computed(() => props.doc.cover)

const REGISTRY: Record<FigureKind, Component> = {
  uniformBeam: markRaw(UniformLoadBeamDiagram),
  mainBeam: markRaw(MainBeamDiagram),
  internalForce: markRaw(InternalForceDiagram),
  sectionRebar: markRaw(SectionRebarDiagram),
  resistingMoment: markRaw(ResistingMomentDiagram),
}
function figureComp(k: FigureKind): Component {
  return REGISTRY[k]
}
</script>

<style scoped>
.rp-doc {
  background: var(--card);
  color: var(--foreground);
  width: 100%;
  max-width: 760px;
  margin: 0 auto;
  padding: var(--space-8) var(--space-10);
  font-size: var(--text-base);
  line-height: 1.7;
}
.rp-cover { text-align: center; padding-top: var(--space-10); min-height: 80vh; }
.rp-cover-title { font-size: 26px; font-weight: 700; margin: var(--space-10) 0 var(--space-3); }
.rp-cover-sub { color: var(--muted-foreground); margin-bottom: var(--space-10); }
.rp-cover-table { margin: 0 auto; border-collapse: collapse; }
.rp-cover-table td { border: 1px solid var(--border); padding: var(--space-2) var(--space-6); }
.rp-cover-date { margin-top: var(--space-10); }

.rp-toc-title { font-size: 18px; margin-bottom: var(--space-3); }
.rp-toc ol { list-style: none; padding: 0; }
.rp-toc li { display: flex; gap: var(--space-2); margin: var(--space-1) 0; }
.rp-toc-num { min-width: 2em; }
.rp-toc-dots { flex: 1; color: var(--border); overflow: hidden; white-space: nowrap; }

.rp-section-title { font-size: 18px; font-weight: 700; margin: var(--space-6) 0 var(--space-2); }
.rp-num { color: var(--primary); }
.rp-h3 { font-size: 15px; font-weight: 600; margin: var(--space-4) 0 var(--space-1); }
.rp-p { margin: var(--space-1) 0; }
.rp-formula { margin: var(--space-1) 0; font-family: var(--font-mono, monospace); }
.rp-note { margin: var(--space-2) 0; padding: var(--space-2) var(--space-3); border-left: 3px solid var(--muted-foreground); background: var(--muted); font-size: var(--text-sm); }
.rp-note.tone-warn { border-left-color: var(--warning); }
.rp-figure { margin: var(--space-3) 0; text-align: center; }
.rp-figure figcaption { font-size: var(--text-sm); color: var(--muted-foreground); margin-top: var(--space-1); }
.rp-table-caption { font-size: var(--text-sm); color: var(--muted-foreground); margin: var(--space-2) 0 var(--space-1); }
.rp-table-wrap { margin: var(--space-2) 0; }
.rp-table { width: 100%; border-collapse: collapse; font-size: var(--text-sm); }
.rp-table th, .rp-table td { border: 1px solid var(--border); padding: var(--space-1) var(--space-2); text-align: center; }
.rp-table th { background: var(--muted); font-weight: 600; }
</style>
