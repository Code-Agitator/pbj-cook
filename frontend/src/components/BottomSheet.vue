<template>
  <view v-if="modelValue" class="sheet-mask" catchtouchmove="noop" @click.stop="onMaskClick">
    <view class="sheet-body" :style="{ maxHeight: maxHeight }" @click.stop>
      <view class="sheet-handle" aria-hidden="true"></view>
      <scroll-view scroll-y class="sheet-scroll">
        <slot />
      </scroll-view>
    </view>
  </view>
</template>

<script setup lang="js">
const props = defineProps({
  modelValue: { type: Boolean, default: false },
  maxHeight: { type: String, default: '60vh' },
  closeOnMaskTap: { type: Boolean, default: true }
})

const emit = defineEmits(['update:modelValue', 'close'])

function onMaskClick() {
  if (props.closeOnMaskTap) {
    emit('update:modelValue', false)
    emit('close')
  }
}
</script>

<style scoped>
.sheet-mask {
  position: fixed;
  z-index: 90;
  inset: 0;
  display: flex;
  align-items: flex-end;
  justify-content: center;
  background: rgba(39, 33, 26, 0.45);
  animation: fadeIn 0.25s ease;
}

@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

.sheet-body {
  width: 100%;
  max-width: 960rpx;
  background: #FAF7F1;
  background: var(--theme-bg-surface, #FAF7F1);
  border-radius: 56rpx 56rpx 0 0;
  padding: 24rpx;
  display: flex;
  flex-direction: column;
  animation: slideUp 0.32s cubic-bezier(0.32, 0.72, 0, 1);
}

@keyframes slideUp {
  from { transform: translateY(100%); }
  to { transform: translateY(0); }
}

.sheet-handle {
  width: 80rpx;
  height: 8rpx;
  border-radius: 4rpx;
  background: #EFE5D8;
  background: var(--theme-border-subtle, #EFE5D8);
  margin: 0 auto 24rpx;
  flex-shrink: 0;
}

.sheet-scroll {
  flex: 1;
  min-height: 0;
  max-height: calc(60vh - 104rpx);
  overflow-y: auto;
  scrollbar-width: none;
  -ms-overflow-style: none;
}
.sheet-scroll::-webkit-scrollbar {
  display: none;
}
</style>
