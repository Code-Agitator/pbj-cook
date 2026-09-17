<template><view class="page"><PageHeader title="我的"/><view class="hero profile" @tap="openProfile"><Avatar :name="me && me.name" :src="assetUrl(me && me.avatar_path)" :size="120"/><view class="profile-meta"><view class="row"><text class="name">{{(me && me.name) || '未设置昵称'}}</text><text v-if="me && me.is_admin" class="badge">管理员</text></view><text class="subtle">{{settings.family_name || ''}}</text></view><Icon icon="Pencil" :size="22"/></view><view v-if="loadError" class="card state"><text>{{loadError}}</text><button class="btn block" @tap="load">重试</button></view><view class="card menu"><view class="menu-row" @tap="changePin"><view class="menu-icon"><Icon icon="KeyRound" :size="21"/></view><text>修改密码</text><text>›</text></view><view v-if="me && me.is_admin" class="menu-row" @tap="goAdmin"><view class="menu-icon"><Icon icon="Settings" :size="21"/></view><text>家庭管理</text><text>›</text></view><view class="menu-row" @tap="editServer"><view class="menu-icon"><Icon icon="Server" :size="21"/></view><text>服务器设置</text><text>›</text></view><view class="menu-row logout" @tap="logout"><view class="menu-icon"><Icon icon="LogOut" :size="21"/></view><text>退出登录</text><text/></view></view><AppTabBar active="me"/><view v-if="showProfile" class="modal-mask" @tap.self="closeProfile"><view class="sheet"><text class="section-title">编辑个人资料</text><view class="avatar-edit" @tap="chooseAvatar"><Avatar :name="profile.name" :src="profilePreview" :size="140"/><text>更换头像</text></view><view class="form-group"><text class="label">昵称</text><input v-model="profile.name" class="input" maxlength="12"/></view><view class="row modal-actions"><button class="chip" @tap="closeProfile">取消</button><button class="btn" @tap="saveProfile">保存</button></view></view></view></view></template>
<script>
import Icon from '../../components/Icons.vue'
import AppTabBar from '../../components/AppTabBar.vue'
import PageHeader from '../../components/PageHeader.vue'
import Avatar from '../../components/Avatar.vue'
import { apiBase, assetUrl, bootstrap, clearSession, currentUser, request, run, setApiBase, uploadImage } from '../../api/client'
import { validatePin, validateProfileName } from '../../utils/app'

export default {
  components: { Icon, AppTabBar, PageHeader, Avatar },
  created() {
    this.assetUrl = assetUrl
  },
  data() {
    return {
      me: currentUser(),
      settings: {},
      showProfile: false,
      loadError: '',
      savingProfile: false,
      loggingOut: false,
      profile: { name: '', avatar_path: null },
      profilePreview: '',
      localAvatar: ''
    }
  },
  onShow() { this.load() },
  methods: {
    async load() {
      this.loadError = ''
      try {
        const [b, u] = await Promise.all([bootstrap(), request('/api/me')])
        this.settings = (b && b.settings) || {}
        this.me = u
        uni.setStorageSync('dacook_user', u)
      } catch (e) {
        this.loadError = (e && e.message) || '个人资料加载失败'
      }
    },
    goAdmin() { uni.navigateTo({ url: '/pages/admin/index' }) },
    openProfile() {
      const saved = this.me || {}
      this.profile.name = saved.name || ''
      this.profile.avatar_path = saved.avatar_path || null
      this.localAvatar = ''
      this.profilePreview = assetUrl(this.profile.avatar_path)
      this.showProfile = true
    },
    closeProfile() { if (!this.savingProfile) this.showProfile = false },
    chooseAvatar() {
      try {
        uni.chooseImage({
          count: 1,
          sizeType: ['compressed'],
          success: (r) => {
            try {
              const path = r && r.tempFilePaths && r.tempFilePaths[0]
              if (path) { this.localAvatar = path; this.profilePreview = path }
            } catch (e) {}
          }
        })
      } catch (e) {}
    },
    async saveProfile() {
      if (this.savingProfile) return
      const validation = validateProfileName(this.profile.name)
      if (validation) { uni.showToast({ title: validation, icon: 'none' }); return }
      this.savingProfile = true
      try {
        await run(async () => {
          const payload = { name: this.profile.name.trim(), avatar_path: this.profile.avatar_path }
          if (this.localAvatar) {
            const uploaded = await uploadImage(this.localAvatar)
            payload.avatar_path = (uploaded && uploaded.path) || null
          }
          await request('/api/me/profile', { method: 'PUT', data: payload })
        }, '资料已保存')
        const authoritative = await request('/api/me')
        this.me = authoritative
        uni.setStorageSync('dacook_user', authoritative)
        this.showProfile = false
      } catch (e) {
        // run already showed error
      } finally {
        this.savingProfile = false
      }
    },
    changePin() {
      let old = ''
      try {
        uni.showModal({
          title: '输入原密码', editable: true, placeholderText: '6 位数字',
          success: (r) => {
            try {
              if (!r || !r.confirm) return
              old = String(r.content || '')
              const oldError = validatePin(old)
              if (oldError) { uni.showToast({ title: oldError, icon: 'none' }); return }
              uni.showModal({
                title: '输入新密码', editable: true, placeholderText: '6 位数字',
                success: async (n) => {
                  try {
                    if (!n || !n.confirm) return
                    const next = String(n.content || '')
                    const nextError = validatePin(next)
                    if (nextError) { uni.showToast({ title: nextError, icon: 'none' }); return }
                    await run(() => request('/api/me/pin', { method: 'PUT', data: { old_pin: old, new_pin: next } }), '密码已修改')
                  } catch (e) {}
                }
              })
            } catch (e) {}
          }
        })
      } catch (e) {}
    },
    editServer() {
      try {
        uni.showModal({
          title: '后端地址', editable: true, placeholderText: apiBase(),
          success: (r) => {
            try {
              if (!r || !r.confirm) return
              if (!setApiBase(r.content)) { uni.showToast({ title: '请输入有效的服务器地址', icon: 'none' }); return }
              clearSession()
              uni.reLaunch({ url: '/pages/login/index' })
            } catch (e) { uni.showToast({ title: (e && e.message) || '服务器设置失败', icon: 'none' }) }
          }
        })
      } catch (e) {}
    },
    logout() {
      if (this.loggingOut) return
      try {
        uni.showModal({
          title: '确认退出登录？',
          success: async (r) => {
            try {
              if (!r || !r.confirm) return
              this.loggingOut = true
              try { await request('/api/auth/logout', { method: 'POST' }) } catch (e) {}
              clearSession()
              uni.reLaunch({ url: '/pages/login/index' })
            } catch (e) {} finally {
              this.loggingOut = false
            }
          }
        })
      } catch (e) {}
    }
  }
}
</script>
<style scoped>.profile{display:flex;flex-direction:row;align-items:center}.profile-meta{flex:1;display:flex;flex-direction:column}.name{font-size:38rpx;font-weight:800;margin-right:15rpx}.menu{margin-top:46rpx;padding:8rpx 28rpx}.menu-row{min-height:116rpx;display:flex;flex-direction:row;align-items:center;border-bottom:1px solid #edf0ed;font-size:30rpx;padding:0 12rpx}.menu-row:last-child{border:0}.menu-icon{width:58rpx;height:58rpx;border-radius:18rpx;background:#e7f4e9;color:#43a367;display:flex;flex-direction:row;align-items:center;justify-content:center;margin-right:20rpx}.menu-arrow{margin-left:auto}.logout{color:#d95353}.avatar-edit{display:flex;flex-direction:column;align-items:center;color:#43a367;margin:30rpx}.modal-actions{display:flex;flex-direction:row;justify-content:flex-end}.modal-actions .btn{margin-left:18rpx}.state{padding:28rpx;margin-top:20rpx}.state .btn{margin-top:18rpx}</style>
