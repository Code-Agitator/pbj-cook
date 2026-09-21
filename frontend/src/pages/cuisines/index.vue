<template>
  <view class="page no-tab page-wide">
    <BackButton label="我的" fallback-url="/pages/me/index"/>

    <!-- 添加按钮 -->
    <view v-if="isAdmin" class="page-action">
      <AppButton variant="primary" size="md" icon="Plus" block @tap="openAdd">
        添加菜系
      </AppButton>
    </view>

    <!-- 搜索框 -->
    <view class="search-wrap">
      <BaseInput
          v-model="searchKeyword"
          prefix-icon="Search"
          placeholder="搜索菜系名称"
          confirm-type="search"
          @confirm="onSearchConfirm"
      >
        <template #suffix>
          <view v-if="searchKeyword" class="search-clear" @tap="clearQuery">
            <Icon icon="X" :size="16"/>
          </view>
        </template>
      </BaseInput>
    </view>

    <!-- 权限/加载状态 -->
    <view v-if="!isAdmin" class="state panel">仅管理员可管理菜系</view>
    <view v-else-if="loading && !cuisines.length" class="state">正在加载菜系...</view>
    <view v-else-if="error && !cuisines.length" class="state panel">
      <text>{{ error }}</text>
      <AppButton variant="tonal" size="sm" @tap="load">重试</AppButton>
    </view>
    <view v-else-if="!displayItems.length" class="state panel">
      {{ cuisines.length ? '没有符合条件的菜系' : '还没有菜系，点击上方添加' }}
    </view>

    <!-- 菜系列表 -->
    <scroll-view v-else class="cuisine-list" scroll-y>
      <view v-for="item in displayItems" :key="item.id" class="cuisine-card">
        <view class="card-head">
          <view class="card-title-row">
            <text class="cuisine-emoji">{{ item.emoji || '🍽️' }}</text>
            <text class="card-title">{{ item.name }}</text>
            <text v-if="item.dish_count" class="dish-count">{{ item.dish_count }} 道菜</text>
          </view>
          <view class="card-actions">
            <view class="icon-btn" @tap="openEdit(item)" title="编辑">
              <Icon icon="Pencil" :size="16"/>
            </view>
            <view class="icon-btn danger" @tap="confirmDelete(item)" title="删除">
              <Icon icon="Trash2" :size="16"/>
            </view>
          </view>
        </view>
      </view>
    </scroll-view>

    <!-- 行内错误 -->
    <view v-if="error && cuisines.length" class="inline-error">
      <text>{{ error }}</text>
      <view @tap="load">重试</view>
    </view>

    <!-- 编辑/新增 弹层 -->
    <view v-if="showForm" class="modal-mask" @tap.self="closeForm">
      <view class="sheet">
        <view class="handle" aria-hidden="true"/>
        <view class="sheet-head">
          <text class="sheet-title">{{ editing ? '编辑菜系' : '添加菜系' }}</text>
          <view class="sheet-close" @tap="closeForm">
            <Icon icon="X" :size="18"/>
          </view>
        </view>

        <view class="form-body">
          <view class="form-group">
            <text class="label">菜系名称 <span class="required">*</span></text>
            <BaseInput v-model="form.name" maxlength="12" placeholder="例如：川菜"/>
          </view>

          <view class="form-group">
            <text class="label">表情符号</text>
            <view class="emoji-row">
              <BaseInput v-model="form.emoji" maxlength="4" placeholder="例如：🌶️" class="emoji-input"/>
              <text class="emoji-preview">{{ form.emoji || '🍽️' }}</text>
            </view>
          </view>
        </view>

        <view class="sheet-footer">
          <AppButton variant="ghost" block @tap="closeForm">取消</AppButton>
          <AppButton variant="primary" block :disabled="saving" @tap="save">{{
              saving ? '保存中...' : '保存'
            }}
          </AppButton>
        </view>
      </view>
    </view>
  </view>
</template>

<script setup lang="js">
import {computed, onActivated, onMounted, reactive, ref} from 'vue'
import BackButton from '../../components/BackButton.vue'
import AppButton from '../../components/AppButton.vue'
import BaseInput from '../../components/BaseInput.vue'
import Icon from '../../components/Icons.vue'
import {currentUser, request, run} from '../../api/client'

const me = ref(currentUser())
const isAdmin = computed(() => me.value?.is_admin === true)

const cuisines = ref([])
const loading = ref(false)
const error = ref('')

// 弹层状态
const showForm = ref(false)
const editing = ref(null)

// 表单状态
const form = reactive({name: '', emoji: ''})
const saving = ref(false)

// 搜索
const searchKeyword = ref('')

const displayItems = computed(() => {
  if (!searchKeyword.value.trim()) return cuisines.value
  const kw = searchKeyword.value.trim().toLowerCase()
  return cuisines.value.filter(item =>
      (item.name || '').toLowerCase().includes(kw)
  )
})

async function load() {
  me.value = currentUser()
  if (!isAdmin.value) return
  loading.value = true
  error.value = ''

  try {
    const [data, dishesData] = await Promise.all([
      request('/api/cuisines'),
      request('/api/dishes?page_size=1000').catch(() => [])
    ])
    const cuisineList = Array.isArray(data) ? data : []
    // 统计每个菜系的菜品数量
    const dishCountMap = {}
    if (Array.isArray(dishesData)) {
      dishesData.forEach(dish => {
        if (dish.cuisine_id) {
          dishCountMap[dish.cuisine_id] = (dishCountMap[dish.cuisine_id] || 0) + 1
        }
      })
    }
    cuisines.value = cuisineList.map(c => ({
      ...c,
      dish_count: dishCountMap[c.id] || 0
    }))
  } catch (e) {
    error.value = e?.message || '菜系加载失败'
  } finally {
    loading.value = false
  }
}

function clearQuery() {
  searchKeyword.value = ''
}

function onSearchConfirm() {
  // 搜索结果由 displayItems 计算属性处理
}

// === 表单操作 ===
function openAdd() {
  editing.value = null
  form.name = ''
  form.emoji = ''
  showForm.value = true
}

function openEdit(item) {
  editing.value = item
  form.name = item.name || ''
  form.emoji = item.emoji || ''
  showForm.value = true
}

function closeForm() {
  if (saving.value) return
  showForm.value = false
}

async function save() {
  if (saving.value) return
  if (!form.name.trim()) {
    uni.showToast({title: '请填写菜系名称', icon: 'none'})
    return
  }
  saving.value = true
  try {
    const payload = {name: form.name.trim(), emoji: form.emoji.trim()}
    if (editing.value) {
      await run(() => request(`/api/cuisines/${editing.value.id}`, {method: 'PUT', data: payload}), '已更新')
    } else {
      await run(() => request('/api/cuisines', {method: 'POST', data: payload}), '已添加')
    }
    showForm.value = false
    load()
  } catch {
  } finally {
    saving.value = false
  }
}

// === 删除 ===
function confirmDelete(item) {
  uni.showModal({
    title: '删除菜系',
    content: `确定删除「${item.name}」吗？${item.dish_count ? '该菜系下仍有菜品，无法删除。' : ''}`,
    success: async result => {
      if (!result?.confirm) return
      try {
        await run(() => request(`/api/cuisines/${item.id}`, {method: 'DELETE'}), '已删除')
        load()
      } catch {
      }
    },
  })
}

onMounted(load)
onActivated(load)
</script>

<style scoped>
.page-wide {
  max-width: 820px;
  padding-bottom: 60rpx;
}

/* 添加按钮 */
.page-action {
  display: flex;
  justify-content: flex-end;
  margin: var(--space-4) 0;
}

/* 搜索框 */
.search-wrap {
  margin-bottom: var(--space-4);
}

.search-clear {
  width: 40rpx;
  height: 40rpx;
  border-radius: 50%;
  background: var(--theme-control-subtle);
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--theme-text-secondary);
  cursor: pointer;
  flex-shrink: 0;
}

/* 状态面板 */
.state .app-btn {
  margin-top: 20rpx;
}

.inline-error {
  display: flex;
  margin: 22rpx 24rpx 0;
  padding: 18rpx 20rpx;
  align-items: center;
  justify-content: space-between;
  border-left: 4rpx solid var(--theme-danger);
  background: var(--theme-danger-surface);
  color: var(--theme-danger);
  font-size: 23rpx;
  flex-direction: row;
}

.inline-error view {
  min-height: 56rpx;
  background: transparent;
  color: var(--theme-danger);
  cursor: pointer;
  display: flex;
  align-items: center;
}

/* 菜系列表 */
.cuisine-list {
  display: flex;
  flex-direction: column;
  gap: 18rpx;
  height: calc(100vh - 280rpx);
  overflow-y: auto;
  -webkit-overflow-scrolling: touch;
}

.cuisine-card {
  background: var(--theme-bg-surface);
  border-radius: 28rpx;
  padding: 16rpx;
  box-shadow: 0 4rpx 16rpx rgba(25, 34, 28, 0.06), 0 1px 2rpx rgba(25, 34, 28, 0.04);
  margin-bottom: 12rpx;
}

.card-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16rpx;
  flex-direction: row;
}

.card-title-row {
  display: flex;
  align-items: center;
  gap: 16rpx;
  flex: 1;
  min-width: 0;
  flex-direction: row;
}

.cuisine-emoji {
  font-size: 48rpx;
  line-height: 1;
}

.card-title {
  font-size: 32rpx;
  font-weight: 700;
  color: var(--theme-text-primary);
}

.dish-count {
  font-size: 22rpx;
  color: var(--theme-text-tertiary);
  font-weight: 500;
}

.card-actions {
  display: flex;
  gap: 8rpx;
  flex-direction: row;
}

.icon-btn {
  width: 60rpx;
  height: 60rpx;
  border-radius: 50%;
  background: var(--theme-control-subtle);
  color: var(--theme-text-secondary);
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  flex-shrink: 0;
}

.icon-btn:active {
  transform: scale(0.94);
}

.icon-btn.danger {
  color: var(--theme-danger);
  background: rgba(181, 71, 71, 0.08);
}

/* ---------- 弹层 ---------- */
.modal-mask {
  position: fixed;
  z-index: 100;
  inset: 0;
  display: flex;
  align-items: flex-end;
  justify-content: center;
  background: var(--theme-modal-scrim);
}

.handle {
  width: 70rpx;
  height: 8rpx;
  border-radius: 4rpx;
  background: var(--theme-control-neutral);
  margin: 0 auto 32rpx;
}

.sheet {
  width: 100%;
  max-width: 820px;
  padding: var(--space-4, 32rpx) 48rpx calc(var(--space-6, 48rpx) + env(safe-area-inset-bottom));
  border-radius: 52rpx 52rpx 0 0;
  background: var(--theme-bg-surface);
  display: flex;
  flex-direction: column;
}

.sheet-head {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 32rpx;
  flex-direction: row;
}

.sheet-title {
  font-size: 38rpx;
  font-weight: 700;
  color: var(--theme-text-primary);
}

.sheet-close {
  width: 60rpx;
  height: 60rpx;
  min-height: 60rpx;
  padding: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  border: 0;
  border-radius: 50%;
  background: var(--theme-control-subtle);
  color: var(--theme-text-primary);
  cursor: pointer;
}

/* 表单 */
.form-body {
  display: flex;
  flex-direction: column;
  gap: 32rpx;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 12rpx;
}

.label {
  font-size: 26rpx;
  font-weight: 600;
  color: var(--theme-text-primary);
  display: flex;
  align-items: center;
  gap: 8rpx;
  flex-direction: row;
}

.required {
  color: var(--theme-danger);
}

.emoji-row {
  display: flex;
  align-items: center;
  gap: 16rpx;
  flex-direction: row;
}

.emoji-input {
  flex: 1;
}

.emoji-preview {
  font-size: 64rpx;
  line-height: 1;
}

.sheet-footer {
  display: flex;
  gap: 16rpx;
  margin-top: 40rpx;
  flex-direction: row;
}

.sheet-footer .app-btn {
  flex: 1;
}
</style>
