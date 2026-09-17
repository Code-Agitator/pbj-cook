<template><view class="avatar" :style="containerStyle"><image v-if="src" :src="src" mode="aspectFill" /><text v-else>{{ firstChar }}</text></view></template>
<script>
export default {
  name: 'Avatar',
  props: { name: String, src: String, size: { type: Number, default: 84 } },
  computed: {
    containerStyle() {
      return { width: this.size + 'rpx', height: this.size + 'rpx', fontSize: this.size * 0.4 + 'rpx' }
    },
    firstChar() { return this.name ? this.name.slice(0, 1) : '' }
  }
}
</script>
