<template>
  <view class="page no-tab admin-page">
    <BackButton label="我的" fallback-url="/pages/me/index"/>
    <view v-if="loading" class="state">正在加载家庭设置...</view>
    <view v-else-if="error" class="state panel">
      <text>{{ error }}</text>
      <view class="btn tonal" @tap="load">重试</view>
    </view>
    <template v-else>
      <section class="admin-section">
        <text class="section-title">家庭设置</text>
        <view class="section-body">
          <view class="form-group">
            <text class="label">家庭名称</text>
            <input v-model="settings.family_name" class="input" maxlength="20"/></view>
          <view class="switch-row">
            <view>
              <text>允许注册</text>
              <text class="subtle">关闭后，新成员无法加入</text>
            </view>
            <switch :checked="settings.registration_open" :color="NATIVE_SWITCH_COLOR"
                    @change="settings.registration_open=$event.detail.value"/>
          </view>
          <view class="form-group">
            <text class="label">注册口令（可选）</text>
            <input v-model="settings.join_code" class="input" placeholder="留空则无需口令"/></view>
          <view class="btn" :class="{ disabled: settingsSaving }" @tap="saveSettings">
            {{ settingsSaving ? '保存中...' : '保存设置' }}
          </view>
        </view>
      </section>
      <section class="admin-section">
        <view class="section-head">
          <view>
            <text class="section-title">自动饭局</text>
            <text class="subtle">按规则创建饭局并管理状态</text>
          </view>
          <view class="chip" @tap="newSchedule">
            <Icon icon="Plus" :size="15"/>
            添加
          </view>
        </view>
        <view class="schedule-list">
          <view v-for="schedule in schedules" :key="schedule.id" class="schedule-row">
            <view class="schedule-main">
              <view class="schedule-title">
                <text>{{ schedule.name }}</text>
                <switch :checked="schedule.enabled" :color="NATIVE_SWITCH_COLOR"
                        @change="toggleSchedule(schedule,$event.detail.value)"/>
              </view>
              <text class="subtle">{{ mealLabels[schedule.meal_type] || '未知餐次' }} ·
                {{ schedule.dining_time || '--:--' }} 开饭 · 提前 {{ schedule.create_lead_hours }} 小时创建
              </text>
              <view class="row-actions">
                <view @tap="editSchedule(schedule)">编辑</view>
                <view class="danger" @tap="deleteSchedule(schedule)">删除</view>
              </view>
            </view>
          </view>
          <view v-if="!schedules.length" class="state compact">还没有自动饭局规则</view>
        </view>
        <view class="btn tonal block tick" :class="{ disabled: tickSaving }" @tap="tick">立即运行一次自动任务</view>
      </section>
      <section class="admin-section">
        <view class="section-head">
          <text class="section-title">家庭成员</text>
          <text class="count">{{ members.length }} 人</text>
        </view>
        <view class="member-list">
          <view v-for="member in members" :key="member.id" class="member-row">
            <Avatar :name="member.name" :src="assetUrl(member.avatar_path)" :size="72"/>
            <view class="member-copy">
              <text>{{ member.name }}</text>
              <text v-if="member.is_admin" class="subtle">管理员</text>
            </view>
            <view v-if="member.id!==me.id" class="manage" @tap="manageMember(member)">管理</view>
          </view>
        </view>
      </section>
    </template>
    <view v-if="editing" class="modal-mask" @tap.self="closeEditing">
      <view class="sheet">
        <view class="sheet-head">
          <text class="section-title">{{ editing.id ? '编辑规则' : '添加自动饭局' }}</text>
          <view class="close" @tap="closeEditing">
            <Icon icon="X" :size="18"/>
          </view>
        </view>
        <view class="form-group top">
          <text class="label">规则名称</text>
          <input v-model="editing.name" class="input"/></view>
        <view class="types">
          <view v-for="(label,key) in mealLabels" :key="key" class="chip" :class="{on:editing.meal_type===key}"
                @tap="editing.meal_type=key">{{ label }}
          </view>
        </view>
        <view class="form-grid">
          <view>
            <text class="label">用餐时间</text>
            <picker mode="time" :value="editing.dining_time" @change="editing.dining_time=$event.detail.value">
              <view class="input picker">{{ editing.dining_time }}</view>
            </picker>
          </view>
          <view>
            <text class="label">提前创建（小时）</text>
            <input v-model.number="editing.create_lead_hours" type="number" class="input"/></view>
        </view>
        <view class="form-group top">
          <text class="label">提前截止（分钟）</text>
          <input v-model.number="editing.deadline_lead_minutes" type="number" class="input"/></view>
        <text class="label">生效星期</text>
        <view class="week">
          <view v-for="day in weekDays" :key="day.v" class="chip" :class="{on:editing.weekdays.includes(day.v)}"
                @tap="toggleDay(day.v)">{{ day.l }}
          </view>
        </view>
        <view class="btn block" :class="{ disabled: scheduleSaving }" @tap="saveSchedule">
          {{ scheduleSaving ? '保存中...' : '保存规则' }}
        </view>
      </view>
    </view>
  </view>
</template>
<script setup lang="js">
import {onMounted, reactive, ref} from 'vue';
import Avatar from '../../components/Avatar.vue';
import BackButton from '../../components/BackButton.vue';
import Icon from '../../components/Icons.vue';
import PageHeader from '../../components/PageHeader.vue';
import {assetUrl, currentUser, request, run} from '../../api/client';
import {validateScheduleDraft} from '../../utils/app'

const NATIVE_SWITCH_COLOR = '#234c35'
const me = currentUser() || {}, settings = reactive({family_name: '', registration_open: true, join_code: ''}),
    schedules = ref([]), members = ref([]), editing = ref(null), loading = ref(false), error = ref(''),
    settingsSaving = ref(false), scheduleSaving = ref(false), tickSaving = ref(false), operationIds = ref(new Set())
const mealLabels = {breakfast: '早餐', lunch: '午餐', dinner: '晚餐'},
    weekDays = [{v: 1, l: '一'}, {v: 2, l: '二'}, {v: 3, l: '三'}, {v: 4, l: '四'}, {v: 5, l: '五'}, {
      v: 6,
      l: '六'
    }, {v: 0, l: '日'}]

function showError(value) {
  uni.showToast({title: value?.message || '操作失败', icon: 'none'})
}

async function load() {
  if (loading.value) return;
  loading.value = true;
  error.value = '';
  try {
    const data = await request('/api/admin');
    Object.assign(settings, data?.settings || {});
    schedules.value = Array.isArray(data?.schedules) ? data.schedules : [];
    members.value = Array.isArray(data?.members) ? data.members : []
  } catch (loadError) {
    error.value = loadError?.message || '家庭管理加载失败'
  } finally {
    loading.value = false
  }
}

async function saveSettings() {
  if (settingsSaving.value) return;
  const name = typeof settings.family_name === 'string' ? settings.family_name.trim() : '';
  if (!name) return uni.showToast({title: '请输入家庭名称', icon: 'none'});
  settingsSaving.value = true;
  try {
    await run(() => request('/api/admin/settings', {
      method: 'PUT',
      data: {...settings, family_name: name}
    }), '设置已保存');
    await load()
  } catch {
  } finally {
    settingsSaving.value = false
  }
}

function blank() {
  return {
    name: '新饭局',
    meal_type: 'dinner',
    enabled: true,
    dining_time: '18:30',
    create_lead_hours: 10,
    deadline_lead_minutes: 120,
    weekdays: [0, 1, 2, 3, 4, 5, 6]
  }
}

function newSchedule() {
  if (!scheduleSaving.value) editing.value = blank()
}

function editSchedule(schedule) {
  if (!scheduleSaving.value) editing.value = JSON.parse(JSON.stringify(schedule))
}

function closeEditing() {
  if (!scheduleSaving.value) editing.value = null
}

function toggleDay(value) {
  if (!editing.value) return;
  const index = editing.value.weekdays.indexOf(value);
  index >= 0 ? editing.value.weekdays.splice(index, 1) : editing.value.weekdays.push(value)
}

async function saveSchedule() {
  if (scheduleSaving.value || !editing.value) return;
  const current = editing.value, draft = {
    ...current,
    name: typeof current.name === 'string' ? current.name.trim() : '',
    create_lead_hours: Number(current.create_lead_hours),
    deadline_lead_minutes: Number(current.deadline_lead_minutes)
  };
  const validation = validateScheduleDraft(draft);
  if (validation) return uni.showToast({title: validation, icon: 'none'});
  scheduleSaving.value = true;
  try {
    await run(() => request(current.id ? `/api/admin/schedules/${current.id}` : '/api/admin/schedules', {
      method: current.id ? 'PUT' : 'POST',
      data: draft
    }), '规则已保存');
    editing.value = null;
    await load()
  } catch {
  } finally {
    scheduleSaving.value = false
  }
}

function busy(key, value) {
  const next = new Set(operationIds.value);
  value ? next.add(key) : next.delete(key);
  operationIds.value = next
}

async function toggleSchedule(schedule, value) {
  const key = `toggle:${schedule.id}`;
  if (operationIds.value.has(key)) return;
  busy(key, true);
  try {
    await request(`/api/admin/schedules/${schedule.id}`, {method: 'PUT', data: {...schedule, enabled: value}});
    schedule.enabled = value
  } catch (toggleError) {
    showError(toggleError)
  } finally {
    busy(key, false)
  }
}

function deleteSchedule(schedule) {
  uni.showModal({
    title: `删除“${schedule.name}”？`, content: '删除后无法恢复', success: async result => {
      if (!result?.confirm) return;
      const key = `delete:${schedule.id}`;
      if (operationIds.value.has(key)) return;
      busy(key, true);
      try {
        await run(() => request(`/api/admin/schedules/${schedule.id}`, {method: 'DELETE'}), '已删除');
        await load()
      } catch {
      } finally {
        busy(key, false)
      }
    }
  })
}

async function tick() {
  if (tickSaving.value) return;
  tickSaving.value = true;
  try {
    const result = await run(() => request('/api/admin/tick', {method: 'POST'}));
    uni.showModal({
      title: '任务已运行',
      content: `新建 ${result?.created || 0} 场，开始准备 ${result?.started || 0} 场，完成 ${result?.finished || 0} 场`,
      showCancel: false
    })
  } catch {
  } finally {
    tickSaving.value = false
  }
}

function manageMember(member) {
  uni.showActionSheet({
    itemList: [member.is_admin ? '取消管理员' : '设为管理员', '移除成员'], success: result => {
      const action = result?.tapIndex === 0 ? (member.is_admin ? 'demote' : 'promote') : result?.tapIndex === 1 ? 'remove' : '';
      if (!action) return;
      const execute = async () => {
        const key = `member:${member.id}:${action}`;
        if (operationIds.value.has(key)) return;
        busy(key, true);
        try {
          await run(() => request(`/api/admin/members/${member.id}`, {
            method: action === 'remove' ? 'DELETE' : 'PATCH',
            data: action === 'remove' ? undefined : {is_admin: action === 'promote'}
          }), action === 'remove' ? '成员已移除' : '权限已更新');
          await load()
        } catch {
        } finally {
          busy(key, false)
        }
      };
      if (action === 'remove') uni.showModal({
        title: '确认移除成员？', content: member.name || '', success: confirm => {
          if (confirm?.confirm) execute()
        }
      }); else execute()
    }
  })
}

onMounted(load)
</script>
<style scoped>.admin-page {
  max-width: 820px
}

.admin-section {
  display: block;
  padding: 46rpx 24rpx;
  border-top: 1px solid var(--theme-border-subtle)
}

.admin-section:first-of-type {
  border-top: 0
}

.section-body {
  margin-top: 28rpx;
  display: flex;
  flex-direction: column
}

.switch-row {
  display: flex;
  min-height: 96rpx;
  margin-bottom: 24rpx;
  align-items: center;
  justify-content: space-between
}

.switch-row > view {
  display: flex;
  flex-direction: column
}

.section-head {
  display: flex;
  align-items: flex-start;
  justify-content: space-between
}

.section-head > view {
  display: flex;
  flex-direction: column
}

.section-head .chip {
  gap: 6rpx
}

.schedule-list, .member-list {
  margin-top: 22rpx;
  border-top: 1px solid var(--theme-border-subtle)
}

.schedule-row {
  padding: 26rpx 24rpx;
  border-bottom: 1px solid var(--theme-border-subtle)
}

.schedule-title {
  display: flex;
  align-items: center;
  justify-content: space-between;
  font-size: 29rpx;
  font-weight: 620
}

.row-actions {
  display: flex;
  margin-top: 12rpx;
  gap: 24rpx
}

.row-actions view {
  min-height: 56rpx;
  padding: 0;
  background: transparent;
  color: var(--theme-text-action);
  font-size: 23rpx
}

.row-actions .danger {
  color: var(--theme-danger)
}

.tick {
  margin-top: 24rpx
}

.member-row {
  display: flex;
  min-height: 108rpx;
  padding: 0 24rpx;
  align-items: center;
  border-bottom: 1px solid var(--theme-border-subtle)
}

.member-copy {
  display: flex;
  margin-left: 18rpx;
  flex: 1;
  flex-direction: column
}

.manage {
  min-height: 60rpx;
  padding: 0 10rpx;
  background: transparent;
  color: var(--theme-text-action);
  font-size: 23rpx
}

.count {
  color: var(--theme-text-secondary);
  font-size: 22rpx
}

.state .btn {
  margin-top: 18rpx
}

.state.compact {
  padding: 40rpx 24rpx
}

.sheet-head {
  display: flex;
  align-items: center;
  justify-content: space-between
}

.close {
  display: flex;
  width: 62rpx;
  height: 62rpx;
  min-height: 62rpx;
  padding: 0;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  background: var(--theme-control-subtle);
  color: var(--theme-text-primary)
}

.top {
  margin-top: 26rpx
}

.types, .week {
  display: flex;
  margin: 20rpx 0;
  flex-wrap: wrap;
  gap: 10rpx
}

.form-grid {
  display: grid;
  grid-template-columns:1fr 1fr;
  gap: 16rpx
}

.picker {
  display: flex;
  align-items: center
}</style>
