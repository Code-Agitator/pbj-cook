<template>
  <view class="page no-tab page-wide">
    <BackButton label="我的" fallback-url="/pages/me/index" />

    <!-- 添加按钮 -->
    <view v-if="isAdmin" class="page-action">
      <view class="btn add" @tap="openAdd"><Icon icon="Plus" :size="18" /> 添加食材</view>
    </view>

    <!-- 搜索框 -->
    <view class="search-wrap">
      <view class="search-box">
        <Icon icon="Search" :size="18" class="search-icon" />
        <input
          v-model="searchKeyword"
          class="search-input"
          placeholder="搜索食材名称或别名（回车搜索服务器）"
          confirm-type="search"
          @input="onSearchInput"
          @confirm="onSearchConfirm"
        />
        <view v-if="searchKeyword" class="search-clear" @tap="clearQuery"><Icon icon="X" :size="16" /></view>
      </view>
    </view>

    <!-- 权限/加载状态 -->
    <view v-if="!isAdmin" class="state panel">仅管理员可管理食材</view>
    <view v-else-if="loading && !ingredients.length" class="state">正在加载食材...</view>
    <view v-else-if="error && !ingredients.length" class="state panel">
      <text>{{ error }}</text>
      <view class="btn tonal" @tap="load">重试</view>
    </view>
    <view v-else-if="!displayItems.length" class="state panel">
      {{ ingredients.length ? '没有符合条件的食材' : '还没有食材，点击右上角添加' }}
    </view>

    <!-- 食材列表 (scroll-view for scrolltolower support) -->
    <scroll-view v-else class="ingredient-list" scroll-y @scrolltolower="loadMore">
      <view v-for="item in displayItems" :key="item.id" class="ingredient-card">
        <view class="card-head">
          <view class="card-title-row">
            <text class="card-title">{{ item.name }}</text>
            <text v-if="item.aliases.length" class="alias-count">{{ item.aliases.length }} 个别名</text>
          </view>
          <view class="card-actions">
            <view class="icon-btn" @tap="openMerge(item)" title="合并">
              <Icon icon="GitMerge" :size="16" />
            </view>
            <view class="icon-btn" @tap="openEdit(item)" title="编辑">
              <Icon icon="Pencil" :size="16" />
            </view>
            <view class="icon-btn danger" @tap="confirmDelete(item)" title="删除">
              <Icon icon="Trash2" :size="16" />
            </view>
          </view>
        </view>
        <view v-if="item.aliases.length" class="alias-list">
          <view v-for="alias in item.aliases" :key="alias.id" class="alias-chip">
            <text>{{ alias.alias }}</text>
          </view>
        </view>
        <view v-else class="alias-empty">暂无别名</view>
      </view>

      <!-- 加载更多指示器 -->
      <view v-if="loadingMore" class="load-more">
        <text>加载中...</text>
      </view>
      <view v-else-if="hasMore && displayItems.length" class="load-more">
        <text>{{ displayItems.length }} / {{ total }} 项，上拉加载更多</text>
      </view>
      <view v-else-if="displayItems.length && !hasMore" class="load-more">
        <text>已加载全部 {{ total }} 项</text>
      </view>
    </scroll-view>

    <!-- 行内错误 -->
    <view v-if="error && ingredients.length" class="inline-error">
      <text>{{ error }}</text>
      <view @tap="load">重试</view>
    </view>

    <!-- 编辑/新增 弹层 -->
    <view v-if="showForm" class="modal-mask" @tap.self="closeForm">
      <view class="sheet">
        <view class="handle" aria-hidden="true" />
        <view class="sheet-head">
          <text class="sheet-title">{{ editing ? '编辑食材' : '添加食材' }}</text>
          <view class="sheet-close" @tap="closeForm"><Icon icon="X" :size="18" /></view>
        </view>

        <view class="form-body">
          <view class="form-group">
            <text class="label">标准名称 <span class="required">*</span></text>
            <input v-model="form.name" class="input" maxlength="30" placeholder="例如：鸡胸肉" />
          </view>

          <view class="form-group">
            <text class="label">别名 <span class="hint-text">点击 × 删除</span></text>
            <view v-if="form.aliases.length" class="alias-edit-list">
              <view v-for="(alias, idx) in form.aliases" :key="idx" class="alias-edit-item">
                <text>{{ alias }}</text>
                <view class="alias-remove" @tap="removeAlias(idx)"><Icon icon="X" :size="14" /></view>
              </view>
            </view>
            <view class="alias-add-row">
              <input
                v-model="aliasInput"
                class="input alias-input"
                maxlength="30"
                placeholder="输入别名后按回车添加"
                @confirm="addAlias"
              />
              <view class="alias-add-btn" @tap="addAlias">添加</view>
            </view>
          </view>
        </view>

        <view class="sheet-footer">
          <view class="btn ghost" @tap="closeForm">取消</view>
          <view class="btn primary" :class="{ disabled: saving }" @tap="save">{{ saving ? '保存中...' : '保存' }}</view>
        </view>
      </view>
    </view>

    <!-- 合并弹层 -->
    <view v-if="showMerge" class="modal-mask" @tap.self="closeMerge">
      <view class="sheet">
        <view class="handle" aria-hidden="true" />
        <view class="sheet-head">
          <text class="sheet-title">合并食材</text>
          <view class="sheet-close" @tap="closeMerge"><Icon icon="X" :size="18" /></view>
        </view>
        <view class="form-body">
          <view class="merge-hint">
            将 <text class="highlight">{{ mergeTarget?.name }}</text> 合并到目标食材，源食材的所有别名会转移到目标食材名下，源食材将被删除。
          </view>
          <view class="form-group">
            <text class="label">选择目标食材</text>
            <view class="merge-target-list">
              <view
                v-for="opt in mergeOptions"
                :key="opt.id"
                class="merge-option"
                :class="{ active: mergeSourceId === opt.id }"
                @tap="mergeSourceId = opt.id"
              >
                <text>{{ opt.name }}</text>
                <text v-if="opt.aliases.length" class="opt-count">{{ opt.aliases.length }} 别名</text>
              </view>
            </view>
          </view>
        </view>
        <view class="sheet-footer">
          <view class="btn ghost" @tap="closeMerge">取消</view>
          <view class="btn primary" :class="{ disabled: !mergeSourceId || merging }" @tap="merge">
            {{ merging ? '合并中...' : '合并' }}
          </view>
        </view>
      </view>
    </view>
  </view>
</template>

<script setup lang="js">
import { computed, onActivated, onMounted, reactive, ref } from 'vue'
import BackButton from '../../components/BackButton.vue'
import Icon from '../../components/Icons.vue'
import { currentUser, request, run } from '../../api/client'

const me = ref(currentUser())
const isAdmin = computed(() => me.value?.is_admin === true)

// 分页数据
const ingredients = ref([])
const total = ref(0)
const page = ref(1)
const pageSize = 50
const hasMore = ref(false)
const loadingMore = ref(false)

const query = ref('')
const loading = ref(false)
const error = ref('')

// 弹层状态
const showForm = ref(false)
const showMerge = ref(false)
const editing = ref(null)
const mergeTarget = ref(null)
const mergeSourceId = ref('')

// 表单状态
const form = reactive({ name: '', aliases: [] })
const aliasInput = ref('')
const saving = ref(false)
const merging = ref(false)

// 搜索时在前端过滤已加载数据，非搜索时显示全部已加载数据
const searchKeyword = ref('')
const displayItems = computed(() => {
  if (!searchKeyword.value.trim()) return ingredients.value
  const kw = searchKeyword.value.trim().toLowerCase()
  return ingredients.value.filter(item =>
    item.name.toLowerCase().includes(kw) ||
    (item.alias_names || []).some(a => a.toLowerCase().includes(kw))
  )
})

const mergeOptions = computed(() =>
  ingredients.value.filter(item => item.id !== mergeTarget.value?.id)
)

async function load(reset = true) {
  me.value = currentUser()
  if (!isAdmin.value) return
  if (reset) {
    page.value = 1
    ingredients.value = []
    loading.value = true
  }
  error.value = ''

  try {
    const q = query.value.trim()
    const data = await request(
      `/api/ingredients?q=${encodeURIComponent(q)}&page=${page.value}&page_size=${pageSize}`
    )
    if (data && data.items) {
      // 标准化别名格式：确保每项都有 alias_names 字符串数组
      const normalized = data.items.map(item => ({
        ...item,
        alias_names: (item.aliases || []).map(a => typeof a === 'string' ? a : a.alias)
      }))
      if (reset) {
        ingredients.value = normalized
      } else {
        // 合并新数据，避免重复
        const existingIds = new Set(ingredients.value.map(i => i.id))
        const newItems = normalized.filter(i => !existingIds.has(i.id))
        ingredients.value = [...ingredients.value, ...newItems]
      }
      total.value = data.total || 0
      hasMore.value = ingredients.value.length < total.value
    } else {
      // 兼容旧的平铺数组返回格式
      ingredients.value = (Array.isArray(data) ? data : []).map(item => ({
        ...item,
        alias_names: (item.aliases || []).map(a => typeof a === 'string' ? a : a.alias)
      }))
      total.value = ingredients.value.length
      hasMore.value = false
    }
  } catch (e) {
    error.value = e?.message || '食材加载失败'
  } finally {
    loading.value = false
    loadingMore.value = false
  }
}

async function loadMore() {
  if (loadingMore.value || !hasMore.value || loading.value) return
  // 搜索模式下不触发搜索更多（因为后端搜索已经返回全部结果）
  if (searchKeyword.value.trim()) return
  loadingMore.value = true
  page.value += 1
  await load(false)
}

function clearQuery() {
  query.value = ''
  searchKeyword.value = ''
  load(true)
}

// 搜索输入时做本地过滤，同时防抖发送服务器搜索
let searchTimer = null
function onSearchInput() {
  if (searchTimer) clearTimeout(searchTimer)
  searchTimer = setTimeout(() => {
    query.value = searchKeyword.value
    load(true)
  }, 500)
}

function onSearchConfirm() {
  if (searchTimer) clearTimeout(searchTimer)
  query.value = searchKeyword.value
  load(true)
}

// === 表单操作 ===
function openAdd() {
  editing.value = null
  form.name = ''
  form.aliases = []
  aliasInput.value = ''
  showForm.value = true
}

function openEdit(item) {
  editing.value = item
  form.name = item.name
  form.aliases = [...(item.alias_names || [])]
  aliasInput.value = ''
  showForm.value = true
}

function closeForm() {
  if (saving.value) return
  showForm.value = false
}

function addAlias() {
  const val = aliasInput.value.trim()
  if (!val) return
  if (val === form.name) {
    uni.showToast({ title: '别名不能与标准名相同', icon: 'none' })
    return
  }
  if (form.aliases.includes(val)) {
    uni.showToast({ title: '该别名已存在', icon: 'none' })
    return
  }
  form.aliases.push(val)
  aliasInput.value = ''
}

function removeAlias(idx) {
  form.aliases.splice(idx, 1)
}

async function save() {
  if (saving.value || !form.name.trim()) {
    if (!form.name.trim()) uni.showToast({ title: '请填写标准名称', icon: 'none' })
    return
  }
  saving.value = true
  try {
    const payload = { name: form.name.trim(), aliases: form.aliases }
    if (editing.value) {
      await run(() => request(`/api/ingredients/${editing.value.id}`, { method: 'PUT', data: payload }), '已更新')
    } else {
      await run(() => request('/api/ingredients', { method: 'POST', data: payload }), '已添加')
    }
    showForm.value = false
    load()
  } catch {} finally {
    saving.value = false
  }
}

// === 删除 ===
function confirmDelete(item) {
  uni.showModal({
    title: '删除食材',
    content: `确定删除「${item.name}」吗？`,
    success: async result => {
      if (!result?.confirm) return
      try {
        await run(() => request(`/api/ingredients/${item.id}`, { method: 'DELETE' }), '已删除')
        load()
      } catch {}
    },
  })
}

// === 合并 ===
function openMerge(item) {
  mergeTarget.value = item
  mergeSourceId.value = ''
  showMerge.value = true
}

function closeMerge() {
  if (merging.value) return
  showMerge.value = false
  mergeTarget.value = null
  mergeSourceId.value = ''
}

async function merge() {
  if (!mergeSourceId.value || merging.value) return
  merging.value = true
  try {
    await run(
      () => request(`/api/ingredients/${mergeTarget.value.id}/merge`, {
        method: 'POST',
        data: { source_id: mergeSourceId.value },
      }),
      '已合并'
    )
    showMerge.value = false
    mergeTarget.value = null
    mergeSourceId.value = ''
    load()
  } catch {} finally {
    merging.value = false
  }
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
  padding: 0 24rpx 12rpx;
}
.add {
  min-height: 70rpx;
  padding: 0 22rpx;
  gap: 8rpx;
}

/* 搜索框 */
.search-wrap {
  padding: 0 24rpx 12rpx;
}
.search-box {
  display: flex;
  align-items: center;
  gap: 12rpx;
  padding: 16rpx 24rpx;
  background: var(--theme-bg-surface);
  border-radius: 28rpx;
  box-shadow: 0 4rpx 16rpx rgba(25, 34, 28, 0.06), 0 1px 2rpx rgba(25, 34, 28, 0.04);
  flex-direction: row;
}
.search-icon {
  color: var(--theme-text-tertiary);
  flex-shrink: 0;
}
.search-input {
  flex: 1;
  border: 0;
  background: transparent;
  font-size: 28rpx;
  font-family: inherit;
  color: var(--theme-text-primary);
  outline: none;
  padding: 0;
}
.search-input::placeholder {
  color: var(--palette-placeholder, #B8AC9C);
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
.state .btn {
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

/* 食材列表 - 可滚动容器 */
.ingredient-list {
  padding: 0 24rpx;
  display: flex;
  flex-direction: column;
  gap: 18rpx;
  height: calc(100vh - 280rpx);
  overflow-y: auto;
  -webkit-overflow-scrolling: touch;
}

/* 加载更多指示器 */
.load-more {
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 32rpx 0;
  font-size: 24rpx;
  color: var(--theme-text-tertiary);
  gap: 16rpx;
  flex-direction: row;
}
.load-more::before,
.load-more::after {
  content: '';
  width: 60rpx;
  height: 2rpx;
  background: var(--theme-border-subtle);
}

.ingredient-card {
  background: var(--theme-bg-surface);
  border-radius: 28rpx;
  padding: 28rpx;
  box-shadow: 0 4rpx 16rpx rgba(25, 34, 28, 0.06), 0 1px 2rpx rgba(25, 34, 28, 0.04);
}

.card-head {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 16rpx;
  flex-direction: row;
}

.card-title-row {
  display: flex;
  align-items: baseline;
  gap: 16rpx;
  flex: 1;
  min-width: 0;
  flex-direction: row;
}

.card-title {
  font-size: 32rpx;
  font-weight: 700;
  color: var(--theme-text-primary);
}

.alias-count {
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

/* 别名列表 */
.alias-list {
  display: flex;
  flex-wrap: wrap;
  gap: 10rpx;
  margin-top: 20rpx;
  flex-direction: row;
}

.alias-chip {
  padding: 8rpx 20rpx;
  border-radius: 999rpx;
  background: var(--theme-bg-subtle);
  color: var(--theme-text-secondary);
  font-size: 24rpx;
}

.alias-empty {
  margin-top: 16rpx;
  font-size: 24rpx;
  color: var(--theme-text-tertiary);
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
.hint-text {
  font-size: 22rpx;
  color: var(--theme-text-tertiary);
  font-weight: 500;
}

.input {
  width: 100%;
  padding: 26rpx 30rpx;
  border: 0;
  border-radius: 28rpx;
  background: var(--theme-bg-base);
  font-size: 30rpx;
  font-family: inherit;
  color: var(--theme-text-primary);
  outline: none;
  box-shadow: inset 0 0 0 2rpx var(--theme-border-subtle);
}
.input:focus {
  box-shadow: inset 0 0 0 2rpx var(--theme-action-primary);
}

/* 别名编辑列表 */
.alias-edit-list {
  display: flex;
  flex-wrap: wrap;
  gap: 10rpx;
  flex-direction: row;
}
.alias-edit-item {
  display: inline-flex;
  align-items: center;
  gap: 8rpx;
  padding: 10rpx 16rpx 10rpx 20rpx;
  border-radius: 999rpx;
  background: rgba(232, 130, 74, 0.08);
  color: var(--theme-action-primary);
  font-size: 26rpx;
  flex-direction: row;
}
.alias-remove {
  width: 36rpx;
  height: 36rpx;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(232, 130, 74, 0.15);
  cursor: pointer;
  flex-shrink: 0;
}
.alias-remove:active {
  transform: scale(0.9);
}

.alias-add-row {
  display: flex;
  gap: 12rpx;
  flex-direction: row;
}
.alias-input {
  flex: 1;
}
.alias-add-btn {
  min-width: 100rpx;
  padding: 0 24rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 28rpx;
  background: var(--theme-action-primary);
  color: var(--theme-action-on-primary);
  font-size: 28rpx;
  font-weight: 600;
  cursor: pointer;
  flex-shrink: 0;
}
.alias-add-btn:active {
  transform: scale(0.97);
}

/* Sheet footer */
.sheet-footer {
  display: flex;
  gap: 16rpx;
  margin-top: 40rpx;
  flex-direction: row;
}
.btn {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8rpx;
  min-height: 88rpx;
  border: 0;
  border-radius: 28rpx;
  font-size: 30rpx;
  font-weight: 600;
  cursor: pointer;
  flex: 1;
  flex-direction: row;
}
.btn.primary {
  background: var(--theme-action-primary);
  color: var(--theme-action-on-primary);
  box-shadow: 0 8rpx 24rpx rgba(232, 130, 74, 0.2);
}
.btn.primary:active {
  transform: scale(0.98);
}
.btn.ghost {
  background: var(--theme-control-subtle);
  color: var(--theme-text-primary);
}
.btn.tonal {
  background: var(--theme-bg-subtle);
  color: var(--theme-action-primary);
}
.btn.disabled {
  opacity: 0.5;
  pointer-events: none;
}

/* 合并弹层 */
.merge-hint {
  font-size: 26rpx;
  color: var(--theme-text-secondary);
  line-height: 1.6;
}
.merge-hint .highlight {
  color: var(--theme-action-primary);
  font-weight: 700;
}

.merge-target-list {
  display: flex;
  flex-direction: column;
  gap: 12rpx;
  max-height: 400rpx;
  overflow-y: auto;
}
.merge-option {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 20rpx 24rpx;
  border-radius: 22rpx;
  background: var(--theme-bg-base);
  box-shadow: inset 0 0 0 2rpx var(--theme-border-subtle);
  font-size: 28rpx;
  color: var(--theme-text-primary);
  cursor: pointer;
  transition: all 0.15s ease;
  flex-direction: row;
}
.merge-option:active {
  transform: scale(0.99);
}
.merge-option.active {
  box-shadow: inset 0 0 0 3rpx var(--theme-action-primary);
  background: rgba(232, 130, 74, 0.06);
}
.opt-count {
  font-size: 22rpx;
  color: var(--theme-text-tertiary);
}
</style>
