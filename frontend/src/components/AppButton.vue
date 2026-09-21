<template>
  <view
    class="app-btn"
    :class="[
      `app-btn--${variant}`,
      `app-btn--${size}`,
      { 'app-btn--block': block, 'app-btn--circle': circle, 'app-btn--icon-only': icon && !$slots.default, 'app-btn--disabled': disabled, 'app-btn--loading': loading }
    ]"
    @tap="onClick"
  >
    <slot name="prefix"></slot>
    <view v-if="loading" class="app-btn__spinner"/>
    <Icon v-else-if="icon" :icon="icon" :size="iconSize" class="app-btn__icon"/>
    <text class="app-btn__label">
      <slot/>
    </text>
    <slot name="suffix"></slot>
  </view>
</template>

<script setup lang="js">
import { computed } from 'vue'
import Icon from './Icons.vue'

const props = defineProps({
  variant: { type: String, default: 'primary' },
  size: { type: String, default: 'lg' },
  icon: { type: String, default: '' },
  block: { type: Boolean, default: false },
  circle: { type: Boolean, default: false },
  disabled: { type: Boolean, default: false },
  loading: { type: Boolean, default: false }
})

const emit = defineEmits(['tap'])

const iconSize = computed(() => {
  if (props.size === 'sm') return 16
  if (props.size === 'md') return 20
  return 22
})

function onClick() {
  if (props.disabled || props.loading) return
  emit('tap')
}
</script>

<style scoped>
.app-btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  flex-direction: row;
  gap: 12rpx;
  border: 0;
  cursor: pointer;
  font-family: inherit;
  transition: transform 0.1s ease, background 0.15s ease, box-shadow 0.15s ease, opacity 0.15s ease;
  position: relative;
  overflow: hidden;
}

.app-btn::after {
  content: '';
  position: absolute;
  inset: 0;
  border-radius: inherit;
  background: linear-gradient(to bottom, rgba(255, 255, 255, 0.18) 0%, rgba(255, 255, 255, 0) 45%);
  pointer-events: none;
}

.app-btn:active {
  transform: scale(0.97);
}

/* ---------- Primary（开饭局风格） ---------- */
.app-btn--primary {
  background: #E05A3A;
  color: #fff;
  box-shadow: 0 16rpx 40rpx rgba(224, 90, 58, 0.3);
}

.app-btn--primary:active {
  background: #C84A2A;
  box-shadow: 0 8rpx 24rpx rgba(224, 90, 58, 0.24);
}

/* ---------- Secondary（次操作） ---------- */
.app-btn--secondary {
  background: rgba(224, 90, 58, 0.08);
  color: #E05A3A;
  box-shadow: none;
}

.app-btn--secondary::after {
  display: none;
}

.app-btn--secondary:active {
  background: rgba(224, 90, 58, 0.14);
}

/* ---------- Outline Dashed（虚线边框） ---------- */
.app-btn--outline-dashed {
  background: transparent;
  color: var(--theme-action-primary);
  border: 2rpx dashed var(--theme-action-primary);
  box-shadow: none;
}

.app-btn--outline-dashed::after {
  display: none;
}

.app-btn--outline-dashed:active {
  background: rgba(224, 90, 58, 0.06);
}

/* ---------- Ghost（轻量操作） ---------- */
.app-btn--ghost {
  background: var(--theme-action-on-primary);
  box-shadow: none;
}

.app-btn--ghost::after {
  display: none;
}

.app-btn--ghost:active {
  background: rgba(25, 34, 28, 0.04);
}

/* ---------- Tonal（瓷色系） ---------- */
.app-btn--tonal {
  background: var(--theme-bg-surface);
  box-shadow: 0 2px 6rpx rgba(25, 34, 28, 0.06);
}

.app-btn--tonal::after {
  background: linear-gradient(to bottom, rgba(255, 255, 255, 0.25) 0%, rgba(255, 255, 255, 0) 50%);
}

.app-btn--tonal:active {
  background: var(--theme-bg-subtle);
}

/* ---------- Sizes ---------- */
.app-btn--lg {
  padding: var(--space-2) var(--space-4);
  border-radius: 36rpx;
  font-size: 32rpx;
  font-weight: 700;
  min-height: 88rpx;
}

.app-btn--md {
  padding: 18rpx;
  border-radius: 28rpx;
  font-size: 28rpx;
  font-weight: 650;
  min-height: 72rpx;
}

.app-btn--sm {
  padding: 12rpx;
  border-radius: 22rpx;
  font-size: 24rpx;
  font-weight: 600;
  min-height: 56rpx;
}

/* ---------- Block ---------- */
.app-btn--block {
  display: flex;
  width: 100%;
}

/* ---------- Circle (圆形图标按钮) ---------- */
.app-btn--circle {
  border-radius: 50%;
  padding: 0;
  aspect-ratio: 1;
}

.app-btn--circle.app-btn--lg {
  width: 88rpx;
  height: 88rpx;
}

.app-btn--circle.app-btn--md {
  width: 72rpx;
  height: 72rpx;
}

.app-btn--circle.app-btn--sm {
  width: 56rpx;
  height: 56rpx;
}

/* ---------- Icon Only（无文字时居中图标） ---------- */
.app-btn--icon-only .app-btn__icon {
  margin: 0;
}

.app-btn--icon-only .app-btn__label {
  display: none;
}

/* ---------- Disabled ---------- */
.app-btn--disabled {
  opacity: 0.48;
  pointer-events: none;
  box-shadow: none;
}

.app-btn--disabled::after {
  display: none;
}

/* ---------- Loading ---------- */
.app-btn--loading {
  pointer-events: none;
  opacity: 0.72;
}

.app-btn__spinner {
  width: 32rpx;
  height: 32rpx;
  border: 3rpx solid rgba(255, 255, 255, 0.3);
  border-top-color: #fff;
  border-radius: 50%;
  animation: app-btn-spin 0.6s linear infinite;
}

.app-btn--secondary .app-btn__spinner,
.app-btn--tonal .app-btn__spinner {
  border-color: rgba(224, 90, 58, 0.2);
  border-top-color: #E05A3A;
}

.app-btn--ghost .app-btn__spinner {
  border-color: rgba(25, 34, 28, 0.15);
  border-top-color: var(--theme-text-secondary);
}

@keyframes app-btn-spin {
  to { transform: rotate(360deg); }
}

/* ---------- Icon ---------- */
.app-btn__icon {
  flex-shrink: 0;
}

.app-btn__label {
  line-height: 1;
}

/* ---------- Hover ---------- */
@media (hover: hover) {
  .app-btn--primary:hover {
    background: #D24E2E;
    box-shadow: 0 20rpx 48rpx rgba(224, 90, 58, 0.36);
  }

  .app-btn--secondary:hover {
    background: rgba(224, 90, 58, 0.12);
  }

  .app-btn--ghost:hover {
    background: rgba(25, 34, 28, 0.03);
  }

  .app-btn--tonal:hover {
    background: var(--theme-bg-subtle);
  }
}
</style>
