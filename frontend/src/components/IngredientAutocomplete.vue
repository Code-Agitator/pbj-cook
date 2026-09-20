<template>
  <view class="ing-auto-wrap">
    <input
      :value="modelValue"
      type="text"
      :placeholder="placeholder"
      class="input"
      aria-label="食材名称"
      @input="onInput"
      @focus="onFocus"
      @blur="onBlur"
      @confirm="$emit('confirm')"
    />

    <!-- 下拉建议列表 -->
    <view v-if="showSuggestions && suggestions.length" class="suggestions">
      <scroll-view scroll-y class="suggestion-scroll">
        <view
          v-for="item in suggestions"
          :key="item.id"
          class="suggestion-item"
          @tap="selectItem(item)"
        >
          <view class="suggestion-main">
            <text class="suggestion-name">{{ item.name }}</text>
            <text v-if="item.aliases && item.aliases.length" class="suggestion-aliases">
              也叫：{{ displayAliases(item.aliases) }}
            </text>
          </view>
          <Icon icon="PlusCircle" :size="18" class="suggestion-add" />
        </view>
      </scroll-view>
      <view v-if="loading" class="suggestion-loading">搜索中...</view>
    </view>
  </view>
</template>

<script setup lang="js">
import { ref, watch } from 'vue'
import Icon from './Icons.vue'
import { request } from '../api/client'

const props = defineProps({
  modelValue: { type: String, default: '' },
  placeholder: { type: String, default: '食材' },
})

const emit = defineEmits(['update:modelValue', 'select', 'confirm'])

const suggestions = ref([])
const showSuggestions = ref(false)
const loading = ref(false)
let searchTimer = null

function displayAliases(aliases) {
  if (!aliases || !aliases.length) return ''
  const names = aliases.map(a => typeof a === 'string' ? a : (a.alias || '')).filter(Boolean)
  return names.slice(0, 3).join('、')
}

function onInput(e) {
  const value = e.detail?.value ?? e.target?.value ?? ''
  emit('update:modelValue', value)

  if (searchTimer) clearTimeout(searchTimer)
  searchTimer = setTimeout(() => {
    searchIngredients(value)
  }, 300)
}

function onFocus() {
  if (props.modelValue.trim()) {
    searchIngredients(props.modelValue)
  }
}

function onBlur() {
  // 延迟关闭，让点击事件先处理
  setTimeout(() => {
    showSuggestions.value = false
  }, 200)
}

async function searchIngredients(keyword) {
  const q = (keyword || '').trim()
  if (!q) {
    suggestions.value = []
    showSuggestions.value = false
    return
  }

  loading.value = true
  try {
    // 使用小 page_size 获取少量建议
    const data = await request(`/api/ingredients?q=${encodeURIComponent(q)}&page=1&page_size=8`)
    if (data && data.items) {
      // 格式化别名
      suggestions.value = data.items.map(item => ({
        ...item,
        alias_names: (item.aliases || []).map(a => typeof a === 'string' ? a : a.alias)
      }))
      showSuggestions.value = true
    } else if (Array.isArray(data)) {
      // 兼容旧格式
      suggestions.value = data.map(item => ({
        ...item,
        alias_names: (item.aliases || []).map(a => typeof a === 'string' ? a : a.alias)
      }))
      showSuggestions.value = true
    } else {
      suggestions.value = []
      showSuggestions.value = false
    }
  } catch {
    suggestions.value = []
    showSuggestions.value = false
  } finally {
    loading.value = false
  }
}

function selectItem(item) {
  emit('update:modelValue', item.name)
  emit('select', item)
  showSuggestions.value = false
  suggestions.value = []
}

// 外部清空
watch(() => props.modelValue, (val) => {
  if (!val) {
    suggestions.value = []
    showSuggestions.value = false
  }
})

defineExpose({ close: () => { showSuggestions.value = false } })
</script>

<style scoped>
.ing-auto-wrap {
  position: relative;
  width: 100%;
}

.ing-auto-wrap .input {
  width: 100%;
  padding: 18rpx 18rpx;
  border: 0;
  border-radius: 22rpx;
  background: var(--theme-bg-surface);
  font-size: 26rpx;
  font-family: inherit;
  color: var(--theme-text-primary);
  outline: none;
  display: flex;
  align-items: center;
  box-shadow: 0 4rpx 16rpx rgba(25, 34, 28, 0.06), 0 1px 2rpx rgba(25, 34, 28, 0.04);
}

.ing-auto-wrap .input:focus {
  box-shadow: 0 6rpx 24rpx rgba(232, 130, 74, 0.18), 0 2rpx 4rpx rgba(232, 130, 74, 0.1);
}

.ing-auto-wrap .input::placeholder {
  color: var(--palette-placeholder, #B8AC9C);
}

/* 建议下拉 */
.suggestions {
  position: absolute;
  z-index: 100;
  top: 100%;
  left: 0;
  right: 0;
  margin-top: 8rpx;
  background: var(--theme-bg-surface);
  border-radius: 22rpx;
  box-shadow: 0 12rpx 40rpx rgba(25, 34, 28, 0.18), 0 4rpx 8rpx rgba(25, 34, 28, 0.08);
  overflow: hidden;
}

.suggestion-scroll {
  max-height: 320rpx;
}

.suggestion-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 18rpx 24rpx;
  cursor: pointer;
  transition: background 0.1s ease;
  flex-direction: row;
}

.suggestion-item:active {
  background: var(--theme-bg-subtle);
}

.suggestion-main {
  display: flex;
  flex-direction: column;
  gap: 4rpx;
  flex: 1;
  min-width: 0;
}

.suggestion-name {
  font-size: 28rpx;
  font-weight: 600;
  color: var(--theme-text-primary);
}

.suggestion-aliases {
  font-size: 20rpx;
  color: var(--theme-text-tertiary);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.suggestion-add {
  color: var(--theme-text-secondary);
  flex-shrink: 0;
}

.suggestion-loading {
  padding: 20rpx;
  text-align: center;
  font-size: 22rpx;
  color: var(--theme-text-tertiary);
}
</style>
