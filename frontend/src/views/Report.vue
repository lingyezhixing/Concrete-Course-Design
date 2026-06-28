<template>
  <div class="report">
    <PageHeader title="计算书" subtitle="自动生成设计计算书" />
    <section class="block">
      <EmptyState
        :icon="icon"
        title="计算书生成功能即将上线"
        description="完成板、次梁、主梁的计算后，可在此一键生成符合课程设计要求的完整计算书。"
      />
    </section>
  </div>
</template>

<script setup lang="ts">
import { markRaw } from 'vue'
import { FileText } from '@lucide/vue'
import PageHeader from '../components/common/PageHeader.vue'
import EmptyState from '../components/common/EmptyState.vue'

const icon = markRaw(FileText)
</script>

<style scoped>
.report {
  width: 100%;
}
</style>
