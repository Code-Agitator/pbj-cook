<template>
  <view class="pin-wrap">
    <view class="dots"><view v-for="n in 6" :key="n" class="dot" :class="{ filled: modelValue.length >= n, error }" /></view>
    <view class="pad">
      <button v-for="n in nums" :key="n" class="key" :disabled="disabled" @tap="press(String(n))">{{ n }}</button>
      <view /><button class="key" :disabled="disabled" @tap="press('0')">0</button><button class="key icon" :disabled="disabled" @tap="erase">⌫</button>
    </view>
  </view>
</template>
<script>
export default {
  name: 'PinPad',
  props: { modelValue: { type: String, default: '' }, error: Boolean, disabled: Boolean },
  data() { return { nums: [1, 2, 3, 4, 5, 6, 7, 8, 9] } },
  methods: {
    press(n) {
      if (this.disabled || this.modelValue.length >= 6) return
      const next = this.modelValue + n
      this.$emit('update:modelValue', next)
      if (next.length === 6) this.$emit('complete', next)
    },
    erase() {
      if (this.disabled) return
      this.$emit('update:modelValue', this.modelValue.slice(0, -1))
    }
  }
}
</script>
<style scoped>
.pin-wrap { width: 100%; max-width: 600rpx; flex-direction: column; }.dots { display: flex; flex-direction: row; justify-content: center; margin-bottom: 35rpx; }.dot { width: 22rpx; height: 22rpx; border: 3rpx solid #a8b2ab; border-radius: 50%; }.dot.filled { border-color: #43a367; background: #43a367; }.dot.error { border-color: #d95353; }.pad { display: flex; flex-direction: row; flex-wrap: wrap; }.key { width: 30%; margin: 8rpx 1.5%; height: 90rpx; line-height: 90rpx; padding: 0; border-radius: 30rpx; background: white; color: #1d2a22; font-size: 36rpx; box-shadow: 0 2rpx 6rpx rgba(30,50,38,.06); }.key.icon { background: transparent; box-shadow: none; color: #68756e; }
</style>
