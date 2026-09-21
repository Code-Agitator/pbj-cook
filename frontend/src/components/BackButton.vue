<template>
  <AppButton variant="tonal" size="lg" @tap="goBack" icon="ChevronLeft">
    {{ label }}
  </AppButton>
</template>

<script setup lang="js">
import AppButton from './AppButton.vue'

const props = defineProps({
  label: { type: String, default: '返回' },
  fallbackUrl: { type: String, default: '' },
})

function goBack() {
  try {
    if (typeof getCurrentPages === 'function' && getCurrentPages().length > 1) {
      return uni.navigateBack()
    }
  } catch {}
  if (props.fallbackUrl) {
    uni.reLaunch({ url: props.fallbackUrl })
  } else {
    uni.reLaunch({ url: '/pages/home/index' })
  }
}
</script>

<style scoped>
.back-arrow {
  font-size: 44rpx;
  font-weight: 700;
  color: var(--theme-text-primary, #27211A);
  line-height: 1;
  margin-right: 4rpx;
}
</style>
