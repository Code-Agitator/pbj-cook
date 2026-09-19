<template><view class="avatar" :style="containerStyle"><image v-if="src" :src="src" mode="aspectFill" /><text v-else>{{ firstChar }}</text></view></template>
<script setup lang="js">
import { computed } from 'vue'
const props = defineProps({ name: { type: String, default: '' }, src: { type: String, default: '' }, size: { type: Number, default: 84 } })
const containerStyle = computed(() => ({ width: `${props.size}rpx`, height: `${props.size}rpx`, fontSize: `${props.size * .4}rpx` }))
const firstChar = computed(() => props.name ? props.name.slice(0, 1) : '')
</script>
