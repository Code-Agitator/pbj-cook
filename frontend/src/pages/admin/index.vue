<template>
  <view class="page no-tab"><text class="back" @tap="back">‹ 我的</text><PageHeader title="家庭管理"/>
    <view v-if="loading" class="card state">正在加载家庭设置…</view><view v-else-if="error" class="card state"><text>{{error}}</text><button class="btn block" @tap="load">重试</button></view>
    <template v-else><text class="section-title heading">家庭设置</text><view class="card panel"><view class="form-group"><text class="label">家庭名称</text><input v-model="settings.family_name" class="input" maxlength="20"/></view><view class="row between switch-row"><view><text>允许注册</text><text class="subtle line">关闭后，新成员将无法加入</text></view><switch :checked="settings.registration_open" color="#43a367" @change="settings.registration_open=$event.detail.value"/></view><view class="form-group"><text class="label">注册口令（可选）</text><input v-model="settings.join_code" class="input" placeholder="留空则无需口令"/></view><button class="btn" @tap="saveSettings">保存设置</button></view>
    <view class="row between heading"><text class="section-title">自动饭局</text><button class="chip" @tap="newSchedule">+ 添加</button></view><text class="subtle desc">按规则自动开放点菜、截止并进入做饭，餐后自动完成。</text><view class="schedules"><view v-for="s in schedules" :key="s.id" class="card schedule"><view class="row between"><text class="schedule-name">{{s.name}}</text><switch :checked="s.enabled" color="#43a367" @change="toggleSchedule(s,$event.detail.value)"/></view><text class="subtle line">{{mealLabels[s.meal_type] || '未知餐次'}} · {{s.dining_time || '--:--'}} 开饭 · 提前 {{s.create_lead_hours}} 小时创建</text><view class="row schedule-actions"><button class="chip" @tap="editSchedule(s)">编辑</button><button class="chip danger-chip" @tap="deleteSchedule(s)">删除</button></view></view></view><button class="btn tonal block tick" @tap="tick">立即运行一次自动任务</button><text class="section-title heading">家庭成员（{{members.length}}）</text><view class="card member-list"><view v-for="m in members" :key="m.id" class="member row"><Avatar :name="m.name" :src="assetUrl(m.avatar_path)" :size="74"/><view class="grow"><text>{{m.name}}</text><text v-if="m.is_admin" class="badge">管理员</text></view><button v-if="m.id!==me.id" class="chip" @tap="manageMember(m)">管理</button></view></view></template>
    <view v-if="editing" class="modal-mask" @tap.self="closeEditing"><view class="sheet"><text class="section-title">{{editing.id?'编辑规则':'添加自动饭局'}}</text><view class="form-group top"><text class="label">规则名称</text><input v-model="editing.name" class="input"/></view><view class="types"><view v-for="(label,key) in mealLabels" :key="key" class="chip" :class="{on:editing.meal_type===key}" @tap="editing.meal_type=key">{{label}}</view></view><view class="grid-2"><view><text class="label">用餐时间</text><picker mode="time" :value="editing.dining_time" @change="editing.dining_time=$event.detail.value"><view class="input picker">{{editing.dining_time}}</view></picker></view><view><text class="label">提前创建（小时）</text><input v-model.number="editing.create_lead_hours" type="number" class="input"/></view></view><view class="form-group top"><text class="label">提前截止（分钟）</text><input v-model.number="editing.deadline_lead_minutes" type="number" class="input"/></view><text class="label">生效星期</text><view class="week"><view v-for="d in weekDays" :key="d.v" class="chip" :class="{on:editing.weekdays.includes(d.v)}" @tap="toggleDay(d.v)">{{d.l}}</view></view><view class="row modal-actions"><button class="chip" @tap="closeEditing">取消</button><button class="btn" @tap="saveSchedule">保存规则</button></view></view></view>
  </view>
</template>
<script>
import PageHeader from '../../components/PageHeader.vue'
import Avatar from '../../components/Avatar.vue'
import { assetUrl, currentUser, request, run } from '../../api/client'
import { validateScheduleDraft } from '../../utils/app'

export default {
  components: { PageHeader, Avatar },
  created() {
    this.assetUrl = assetUrl
  },
  data() {
    return {
      me: currentUser() || {},
      settings: { family_name: '', registration_open: true, join_code: '' },
      schedules: [],
      members: [],
      editing: null,
      loading: false,
      error: '',
      settingsSaving: false,
      scheduleSaving: false,
      tickSaving: false,
      operationIds: new Set(),
      mealLabels: { breakfast: '早餐', lunch: '午餐', dinner: '晚餐' },
      weekDays: [{ v: 1, l: '一' }, { v: 2, l: '二' }, { v: 3, l: '三' }, { v: 4, l: '四' }, { v: 5, l: '五' }, { v: 6, l: '六' }, { v: 0, l: '日' }]
    }
  },
  mounted() { this.load() },
  methods: {
    back() { uni.navigateBack() },
    saveError(e) { uni.showToast({ title: (e && e.message) || '操作失败', icon: 'none' }) },
    async load() {
      if (this.loading) return
      this.loading = true
      this.error = ''
      try {
        const d = await request('/api/admin')
        Object.assign(this.settings, d && d.settings || {})
        this.schedules = Array.isArray(d && d.schedules) ? d.schedules : []
        this.members = Array.isArray(d && d.members) ? d.members : []
      } catch (e) {
        this.error = (e && e.message) || '家庭管理加载失败'
      } finally {
        this.loading = false
      }
    },
    async saveSettings() {
      if (this.settingsSaving) return
      const name = typeof this.settings.family_name === 'string' ? this.settings.family_name.trim() : ''
      if (!name) { uni.showToast({ title: '请输入家庭名称', icon: 'none' }); return }
      this.settingsSaving = true
      try {
        await run(() => request('/api/admin/settings', { method: 'PUT', data: Object.assign({}, this.settings, { family_name: name }) }), '设置已保存')
        const d = await request('/api/admin')
        Object.assign(this.settings, d && d.settings || {})
      } catch (e) {
        // run already showed error
      } finally {
        this.settingsSaving = false
      }
    },
    blank() {
      return { name: '新饭局', meal_type: 'dinner', enabled: true, dining_time: '18:30', create_lead_hours: 10, deadline_lead_minutes: 120, weekdays: [0, 1, 2, 3, 4, 5, 6] }
    },
    newSchedule() { if (!this.scheduleSaving) this.editing = this.blank() },
    editSchedule(s) { if (!this.scheduleSaving) this.editing = JSON.parse(JSON.stringify(s)) },
    closeEditing() { if (!this.scheduleSaving) this.editing = null },
    toggleDay(v) {
      if (!this.editing) return
      const a = this.editing.weekdays
      const i = a.indexOf(v)
      i >= 0 ? a.splice(i, 1) : a.push(v)
    },
    async saveSchedule() {
      if (this.scheduleSaving || !this.editing) return
      const x = this.editing
      const draft = Object.assign({}, x, {
        name: typeof x.name === 'string' ? x.name.trim() : '',
        create_lead_hours: Number(x.create_lead_hours),
        deadline_lead_minutes: Number(x.deadline_lead_minutes)
      })
      const validation = validateScheduleDraft(draft)
      if (validation) { uni.showToast({ title: validation, icon: 'none' }); return }
      this.scheduleSaving = true
      try {
        const path = x.id ? `/api/admin/schedules/${x.id}` : '/api/admin/schedules'
        await run(() => request(path, { method: x.id ? 'PUT' : 'POST', data: draft }), '规则已保存')
        this.editing = null
        await this.load()
      } catch (e) {
        // run already showed error
      } finally {
        this.scheduleSaving = false
      }
    },
    async toggleSchedule(s, value) {
      const key = `toggle:${s.id}`
      if (this.operationIds.has(key)) return
      this.operationIds.add(key)
      try {
        await request(`/api/admin/schedules/${s.id}`, { method: 'PUT', data: Object.assign({}, s, { enabled: value }) })
        s.enabled = value
      } catch (e) { this.saveError(e) } finally {
        this.operationIds.delete(key)
      }
    },
    deleteSchedule(s) {
      try {
        uni.showModal({
          title: `删除"${s.name}"？`,
          success: (r) => {
            try {
              if (!r || !r.confirm) return
              uni.showModal({
                title: '再次确认删除', content: '删除后无法恢复',
                success: async (second) => {
                  try {
                    if (!second || !second.confirm) return
                    const key = `delete:${s.id}`
                    if (this.operationIds.has(key)) return
                    this.operationIds.add(key)
                    await run(() => request(`/api/admin/schedules/${s.id}`, { method: 'DELETE' }), '已删除')
                    await this.load()
                  } catch (e) {} finally {
                    this.operationIds.delete(`delete:${s.id}`)
                  }
                }
              })
            } catch (e) {}
          }
        })
      } catch (e) {}
    },
    async tick() {
      if (this.tickSaving) return
      this.tickSaving = true
      try {
        const r = await run(() => request('/api/admin/tick', { method: 'POST' }))
        uni.showModal({ title: '任务已运行', content: `新建 ${r && r.created || 0} 场，开始做饭 ${r && r.started || 0} 场，完成 ${r && r.finished || 0} 场`, showCancel: false })
      } catch (e) {
        // run already showed error
      } finally {
        this.tickSaving = false
      }
    },
    manageMember(m) {
      try {
        uni.showActionSheet({
          itemList: [m.is_admin ? '取消管理员' : '设为管理员', '移除成员'],
          success: (r) => {
            try {
              const action = (r && r.tapIndex) === 0 ? (m.is_admin ? 'demote' : 'promote') : (r && r.tapIndex) === 1 ? 'remove' : ''
              if (!action) return
              const confirmAction = async () => {
                const key = `member:${m.id}:${action}`
                if (this.operationIds.has(key)) return
                this.operationIds.add(key)
                try {
                  const method = action === 'remove' ? 'DELETE' : 'PATCH'
                  const data = action === 'remove' ? undefined : { is_admin: action === 'promote' }
                  await run(() => request(`/api/admin/members/${m.id}`, { method, data }), action === 'remove' ? '成员已移除' : '权限已更新')
                  await this.load()
                } catch (e) {} finally {
                  this.operationIds.delete(key)
                }
              }
              if (action === 'remove') {
                uni.showModal({
                  title: '确认移除成员？', content: m.name || '',
                  success: (c) => { try { if (c && c.confirm) confirmAction() } catch (e) {} }
                })
              } else {
                confirmAction()
              }
            } catch (e) {}
          }
        })
      } catch (e) {}
    }
  }
}
</script>
<style scoped>.heading{display:flex;flex-direction:row;margin:35rpx 0 20rpx}.panel{padding:30rpx}.switch-row{margin:30rpx 4rpx}.line{display:block;margin-top:6rpx}.desc{display:block;margin:-6rpx 0 20rpx}.schedules{display:flex;flex-direction:column}.schedule{padding:28rpx;margin-bottom:18rpx}.schedule-name{font-size:31rpx;font-weight:750}.schedule-actions{display:flex;flex-direction:row;margin-top:22rpx}.schedule-actions .btn{margin-right:14rpx}.danger-chip{color:#d95353}.tick{margin-top:20rpx}.member-list{padding:0 28rpx}.member{min-height:112rpx;display:flex;flex-direction:row;border-bottom:1px solid #edf0ed}.member:last-child{border:0}.grow{flex:1;display:flex;flex-direction:row;align-items:center;margin-left:18rpx}.top{margin-top:28rpx}.types,.week{display:flex;flex-direction:row;flex-wrap:wrap;margin:22rpx 0}.types .chip,.week .chip{margin-right:12rpx}.picker{display:flex;flex-direction:row;align-items:center}.state{padding:28rpx;margin-top:20rpx}.state .btn{margin-top:18rpx}.modal-actions{display:flex;flex-direction:row;justify-content:flex-end}.modal-actions .btn{margin-left:18rpx}</style>
