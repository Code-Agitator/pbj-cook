<template>
  <view class="tag-input">
    <!-- 已选标签 -->
    <view class="selected-tags" v-if="modelValue.length > 0">
      <view v-for="(tag, idx) in modelValue" :key="idx" class="tag-chip">
        <text>{{ tag }}</text>
        <view class="tag-remove" @tap="removeTag(idx)">
          <Icon icon="X" :size="12"/>
        </view>
      </view>
    </view>

    <!-- 输入框 -->
    <view class="input-wrap" v-if="modelValue.length < maxTags">
      <BaseInput
        v-model="inputText"
        :placeholder="placeholder"
        :maxlength="10"
        @input="onInput"
        @focus="onFocus"
        @blur="onBlur"
        @confirm="onEnter"
      >
        <template #suffix>
          <view class="input-suffix" v-if="inputText && !filteredTags.length" @tap="onEnter">
            <Icon icon="Plus" :size="14"/>
          </view>
        </template>
      </BaseInput>
    </view>

    <!-- 补全提示下拉 -->
    <view class="autocomplete" v-if="showDropdown && (filteredTags.length > 0 || (inputText && !allTags.includes(inputText)))">
      <scroll-view scroll-y class="ac-scroll">
        <view
          v-for="tag in filteredTags"
          :key="tag"
          class="ac-item"
          @tap="selectTag(tag)"
        >
          <Icon icon="Tag" :size="14" class="ac-icon"/>
          <text>{{ tag }}</text>
        </view>
        <view class="ac-item ac-create" v-if="inputText && !allTags.includes(inputText)" @tap="selectTag(inputText)">
          <Icon icon="Plus" :size="14" class="ac-icon"/>
          <text>新建 "{{ inputText }}"</text>
        </view>
      </scroll-view>
    </view>
  </view>
</template>

<script setup lang="js">
import { ref, computed, onMounted } from 'vue'
import Icon from './Icons.vue'
import BaseInput from './BaseInput.vue'

const props = defineProps({
  modelValue: { type: Array, default: () => [] },
  placeholder: { type: String, default: '输入或选择标签' },
  maxTags: { type: Number, default: 3 },
  predefinedTags: { type: Array, default: () => [] }
})

const emit = defineEmits(['update:modelValue'])

const inputText = ref('')
const allTags = ref([])
const showDropdown = ref(false)

const filteredTags = computed(() => {
  const text = inputText.value.trim()
  if (!text) return allTags.value.slice(0, 8)
  return allTags.value.filter(t => t.includes(text)).slice(0, 6)
})

onMounted(() => {
  allTags.value = [...props.predefinedTags]
})

function onInput() {
  showDropdown.value = true
}

function onFocus() {
  showDropdown.value = true
}

function onBlur() {
  setTimeout(() => { showDropdown.value = false }, 150)
}

function onEnter() {
  const text = inputText.value.trim()
  if (!text) return
  if (props.modelValue.length >= props.maxTags) return
  if (props.modelValue.includes(text)) return
  emit('update:modelValue', [...props.modelValue, text])
  inputText.value = ''
  // 同步到 allTags
  if (!allTags.value.includes(text)) {
    allTags.value.push(text)
  }
}

function selectTag(tag) {
  const text = tag.trim()
  if (!text) return
  if (props.modelValue.length >= props.maxTags) return
  if (props.modelValue.includes(text)) return
  emit('update:modelValue', [...props.modelValue, text])
  inputText.value = ''
  showDropdown.value = false
  if (!allTags.value.includes(text)) {
    allTags.value.push(text)
  }
}

function removeTag(idx) {
  const next = [...props.modelValue]
  next.splice(idx, 1)
  emit('update:modelValue', next)
}

// 暴露方法供外部刷新标签
function setTags(tags) {
  allTags.value = [...new Set([...tags, ...props.predefinedTags])]
}

defineExpose({ setTags })
</script>

<style scoped>
.tag-input {
  position: relative;
  width: 100%;
}

.selected-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 12rpx;
  margin-bottom: 16rpx;
}

.tag-chip {
  display: inline-flex;
  align-items: center;
  gap: 8rpx;
  padding: 10rpx 20rpx;
  border-radius: 999px;
  background: rgba(232, 130, 74, 0.08);
  border: 1.5px solid var(--theme-action-primary);
  color: var(--theme-action-primary);
  font-size: 24rpx;
  font-weight: 600;
  flex-direction: row;
}

.tag-remove {
  width: 32rpx;
  height: 32rpx;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(232, 130, 74, 0.15);
  color: var(--theme-action-primary);
  cursor: pointer;
  flex-shrink: 0;
}

.tag-remove:active {
  background: rgba(232, 130, 74, 0.3);
}

.input-wrap {
  position: relative;
  width: 100%;
}

/* BaseInput suffix 在 TagInput 中保持绝对定位 */
.input-wrap :deep(.base-input__suffix) {
  position: absolute;
  right: 8rpx;
  top: 50%;
  transform: translateY(-50%);
  padding-left: 0;
}

.input-suffix {
  width: 44rpx;
  height: 44rpx;
  border-radius: 50%;
  background: var(--theme-action-primary);
  color: #fff;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
}

.autocomplete {
  position: absolute;
  top: 100%;
  left: 0;
  right: 0;
  margin-top: 8rpx;
  background: var(--theme-bg-surface);
  border-radius: 20rpx;
  box-shadow: 0 12rpx 40rpx rgba(25, 34, 28, 0.14);
  z-index: 100;
  overflow: hidden;
  border: 1px solid var(--theme-border-subtle);
}

.ac-scroll {
  max-height: 320rpx;
}

.ac-item {
  display: flex;
  align-items: center;
  gap: 14rpx;
  padding: 20rpx 26rpx;
  font-size: 26rpx;
  color: var(--theme-text-primary);
  flex-direction: row;
  transition: background 0.1s ease;
}

.ac-item:active {
  background: rgba(232, 130, 74, 0.08);
}

.ac-icon {
  color: var(--theme-text-secondary);
  flex-shrink: 0;
}

.ac-create {
  color: var(--theme-action-primary);
  font-weight: 600;
  border-top: 1px dashed var(--theme-border-subtle);
}

.ac-create .ac-icon {
  color: var(--theme-action-primary);
}
</style>
