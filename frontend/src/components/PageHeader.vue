<template><view class="head"><view><text class="title">{{ title }}</text><text v-if="subtitle" class="subtle sub">{{ subtitle }}</text></view><slot /></view></template>
<script>
export default {
  name: 'PageHeader',
  props: { title: String, subtitle: String }
}
</script>
<style scoped>.head{display:flex;flex-direction:row;align-items:center;justify-content:space-between;margin-bottom:40rpx}.sub{display:block;margin-top:8rpx}</style>
