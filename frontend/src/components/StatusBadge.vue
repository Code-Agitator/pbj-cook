<template>
  <text class="status-badge" :class="status">{{ label }}</text>
</template>

<script setup lang="js">
import { computed } from 'vue'

const props = defineProps({
  status: { type: String, default: '' },
})

const labels = {
  ordering: '点菜中',
  cooking: '做饭中',
  done: '已完成',
  cancelled: '已取消',
}

const label = computed(() => labels[props.status] || '状态未知')
</script>

<style scoped>
.status-badge {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-height: 36rpx;
  padding: 4rpx 14rpx;
  border-radius: 6rpx;
  background: transparent;
  border: 1px solid currentColor;
  font-size: 20rpx;
  font-weight: 500;
  line-height: 1.4;
  white-space: nowrap;
}

.status-badge.ordering {
  color: var(--palette-amber-600);
}

.status-badge.cooking {
  color: var(--palette-moss-600);
}

.status-badge.done {
  color: var(--palette-forest-700);
}

.status-badge.cancelled {
  color: var(--palette-text-650);
}
</style>
