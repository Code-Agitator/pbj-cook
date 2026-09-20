<template>
  <view class="pin-wrap">
    <view class="pin-inner">
      <view class="dots">
        <view v-for="n in 6" :key="n" class="dot" :class="{ filled: modelValue.length >= n, error }"/>
      </view>
      <view class="pad">
        <view v-for="n in nums" :key="n" class="key" :class="{ disabled }" @tap="press(String(n))">{{ n }}</view>
        <view/>
        <view class="key" :class="{ disabled }" @tap="press('0')">0</view>
        <view class="key icon" :class="{ disabled }" @tap="erase">⌫</view>
      </view>
    </view>
  </view>
</template>
<script setup lang="js">
const props = defineProps({
  modelValue: {type: String, default: ''},
  error: {type: Boolean, default: false},
  disabled: {type: Boolean, default: false}
})
const emit = defineEmits(['update:modelValue', 'complete'])
const nums = [1, 2, 3, 4, 5, 6, 7, 8, 9]

function press(number) {
  if (props.disabled || props.modelValue.length >= 6) return;
  const next = props.modelValue + number;
  emit('update:modelValue', next);
  if (next.length === 6) emit('complete', next)
}

function erase() {
  if (!props.disabled) emit('update:modelValue', props.modelValue.slice(0, -1))
}
</script>
<style scoped>
.pin-wrap {
  display: flex;
  width: 100%;
  flex-direction: column;
  box-sizing: border-box;
}

.pin-inner {
  width: 100%;
  display: flex;
  flex-direction: column;
}

.dots {
  display: flex;
  justify-content: center;
  flex-direction: row;
  margin-bottom: 34rpx;
  gap: 22rpx
}

.dot {
  width: 18rpx;
  height: 18rpx;
  border: 2rpx solid var(--theme-border-strong);
  border-radius: 50%
}

.dot.filled {
  border-color: var(--theme-action-primary);
  background: var(--theme-action-primary)
}

.dot.error {
  border-color: var(--theme-danger)
}

.pad {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 12rpx;
  width: 100%;
}

.key {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 100%;
  height: 88rpx;
  min-height: 88rpx;
  margin: 0;
  padding: 0;
  border-radius: 16rpx;
  background: var(--theme-bg-surface);
  color: var(--theme-text-primary);
  font-size: 34rpx;
  font-weight: 700;
  box-shadow: 0 2px 6rpx rgba(25, 34, 28, 0.08), 0 1px 2rpx rgba(25, 34, 28, 0.06);
  transition: transform 0.1s ease, box-shadow 0.1s ease, background 0.1s ease;
  position: relative;
}

.key::after {
  content: '';
  position: absolute;
  inset: 0;
  border-radius: inherit;
  background: linear-gradient(to bottom, rgba(255, 255, 255, 0.18) 0%, rgba(255, 255, 255, 0) 50%);
  pointer-events: none;
}

.key:active {
  transform: translateY(2rpx);
  box-shadow: 0 1px 3rpx rgba(25, 34, 28, 0.06), 0 1px 1rpx rgba(25, 34, 28, 0.04);
  background: var(--palette-green-050, #e7ebe4);
}

.key:active::after {
  background: linear-gradient(to bottom, rgba(0, 0, 0, 0.06) 0%, rgba(0, 0, 0, 0) 50%);
}

.key.icon {
  border-color: transparent;
  background: transparent;
  color: var(--theme-text-secondary);
  box-shadow: none;
}

.key.icon::after {
  display: none;
}

.key.icon:active {
  transform: translateY(2rpx);
  background: var(--palette-green-050, #e7ebe4);
}
</style>
