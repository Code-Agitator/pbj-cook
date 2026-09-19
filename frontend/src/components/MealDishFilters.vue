<template>
  <view class="meal-filters">
    <view class="search-wrap">
      <Icon icon="Search" :size="18"/>
      <input
          class="search-input"
          :value="query"
          placeholder="搜索菜名、口味或标签"
          confirm-type="search"
          @input="emit('update:query', $event.detail.value)"
      />
      <button v-if="query" class="icon-button" aria-label="清除搜索" @tap="emit('update:query', '')">
        <Icon icon="X" :size="16"/>
      </button>
    </view>

    <scroll-view scroll-x class="filter-scroll" :show-scrollbar="false">
      <view class="filter-line">
        <view class="chip" :class="{ on: !cuisineId }" @tap="emit('update:cuisineId', null)">全部</view>
        <view
            v-for="cuisine in cuisines"
            :key="cuisine.id"
            class="chip"
            :class="{ on: cuisineId === cuisine.id }"
            @tap="emit('update:cuisineId', cuisine.id)"
        >{{ cuisine.emoji || '' }} {{ cuisine.name || '未命名菜系' }}
        </view>
      </view>
    </scroll-view>

    <scroll-view scroll-x class="filter-scroll tag-scroll" :show-scrollbar="false">
      <view class="filter-line">
        <view v-if="showSelectedOnly" class="chip mine" :class="{ on: hasTag('__mine__') }"
                @tap="emit('toggle-tag', '__mine__')">
          只看我点的 {{ selectedCount }}
        </view>
        <view
            v-for="tag in availableTags"
            :key="tag"
            class="chip"
            :class="{ on: hasTag(tag) }"
            @tap="emit('toggle-tag', tag)"
        >{{ tag }}
        </view>
      </view>
    </scroll-view>

    <view class="filter-meta">
      <text>共 {{ resultCount }} 道</text>
      <view v-if="hasFilters" class="reset" @tap="emit('reset')">清除筛选</view>
    </view>
  </view>
</template>

<script setup lang="js">
import {computed} from 'vue'
import Icon from './Icons.vue'

const props = defineProps({
  query: {type: String, default: ''},
  cuisines: {type: Array, default: () => []},
  cuisineId: {type: String, default: null},
  tags: {type: Object, default: () => new Set()},
  availableTags: {type: Array, default: () => []},
  selectedCount: {type: Number, default: 0},
  showSelectedOnly: {type: Boolean, default: true},
  resultCount: {type: Number, default: 0}
})

const emit = defineEmits(['update:query', 'update:cuisineId', 'toggle-tag', 'reset'])
const hasTag = (tag) => props.tags instanceof Set && props.tags.has(tag)
const hasFilters = computed(() => Boolean(props.query.trim() || props.cuisineId || (props.tags instanceof Set && props.tags.size)))
</script>

<style scoped>
.meal-filters {
  padding: 28rpx 0 0 0;
}

.search-wrap {
  display: flex;
  min-height: 82rpx;
  padding: 0 18rpx 0 24rpx;
  align-items: center;
  border: 1px solid var(--theme-border-subtle);
  border-radius: var(--radius-control);
  background: var(--theme-bg-surface);
  color: var(--theme-text-secondary);
}

.search-input {
  flex: 1;
  height: 80rpx;
  margin-left: 16rpx;
  color: var(--theme-text-primary);
  font-size: 27rpx;
}

.icon-button {
  display: flex;
  width: 58rpx;
  height: 58rpx;
  min-height: 58rpx;
  padding: 0;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  background: transparent;
  color: var(--theme-text-secondary);
}

.filter-scroll {
  width: 100%;
  margin-top: 18rpx;
  white-space: nowrap;
}

.tag-scroll {
  margin-top: 12rpx;
}

.filter-line {
  display: inline-flex;
  min-width: 100%;
  flex-direction: row;
  overflow: scroll;

  gap: var(--space-1);
}

.filter-line .chip {
  flex: none;
}

.mine text {
  margin-left: 8rpx;
  opacity: .8;
}

.filter-meta {
  display: flex;
  min-height: 58rpx;
  margin-top: 10rpx;
  align-items: center;
  justify-content: space-between;
  color: var(--theme-text-secondary);
  font-size: 22rpx;
}

.reset {
  min-height: 58rpx;
  padding: 0;
  background: transparent;
  color: var(--theme-text-action);
  font-size: 23rpx;
}

.search-wrap,
.filter-meta {
  flex-direction: row;
}
</style>
