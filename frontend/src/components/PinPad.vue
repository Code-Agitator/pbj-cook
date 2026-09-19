<template>
  <view class="pin-wrap">
    <view class="dots">
      <view v-for="n in 6" :key="n" class="dot" :class="{ filled: modelValue.length >= n, error }"/>
    </view>
    <view class="pad">
      <button v-for="n in nums" :key="n" class="key" :disabled="disabled" @tap="press(String(n))">{{ n }}</button>
      <view/>
      <button class="key" :disabled="disabled" @tap="press('0')">0</button>
      <button class="key icon" :disabled="disabled" @tap="erase">⌫</button>
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
  width: 100%;
  max-width: 560rpx;
  flex-direction: column
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
  grid-template-columns:repeat(3, 1fr);
  gap: 12rpx
}

.key {
  width: 100%;
  height: 88rpx;
  min-height: 88rpx;
  margin: 0;
  padding: 0;
  border: 1px solid var(--theme-border-subtle);
  border-radius: 10rpx;
  background: var(--theme-bg-surface);
  color: var(--theme-text-primary);
  font-size: 34rpx
}

.key.icon {
  border-color: transparent;
  background: transparent;
  color: var(--theme-text-secondary)
}
</style>
