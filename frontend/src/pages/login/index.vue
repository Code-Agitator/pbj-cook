<template>
  <view class="page no-tab login">
    <view class="logo">🍳</view>
    <text class="title">{{ settings.family_name || '我家' }}开饭啦</text>
    <text class="subtle intro">{{
        selected ? '输入 6 位密码' : mode === 'login' ? '选择你的头像' : '新成员加入家庭'
      }}
    </text>
    <view v-if="settings.registration_open&&!selected" class="segment">
      <view :class="{on:mode==='login'}" @tap="switchMode('login')">登录</view>
      <view :class="{on:mode==='register'}" @tap="switchMode('register')">注册</view>
    </view>
    <view v-if="mode==='login'&&!selected" class="members">
      <view v-for="m in members" :key="m.id" class="member card" @tap="pickMember(m)">
        <Avatar :name="m.name" :src="assetUrl(m.avatar_path)" :size="100"/>
        <text>{{ m.name }}</text>
      </view>
    </view>
    <view v-if="mode==='login'&&selected" class="pin-panel">
      <text class="back" @tap="goBack">‹ 换个成员</text>
      <Avatar :name="selected.name" :src="assetUrl(selected.avatar_path)" :size="126"/>
      <text class="member-name">{{ selected.name }}</text>
      <PinPad v-model="pin" :disabled="submitting" @complete="loginNow"/>
    </view>
    <view v-if="mode==='register'" class="register"><input v-model="name" class="input" maxlength="12"
                                                           placeholder="你的昵称"/><input v-if="settings.has_join_code"
                                                                                          v-model="joinCode"
                                                                                          class="input"
                                                                                          placeholder="注册口令"/>
      <PinPad v-model="pin" :disabled="submitting" @complete="registerNow"/>
    </view>
    <text class="server" @tap="editServer">连接设置</text>
  </view>
</template>
<script>
import Avatar from '../../components/Avatar.vue'
import PinPad from '../../components/PinPad.vue'
import {apiBase, assetUrl, bootstrap, clearSession, request, run, setApiBase, setSession} from '../../api/client'

export default {
  components: { Avatar, PinPad },
  created() {
    this.assetUrl = assetUrl
  },
  data() {
    return {
      members: [],
      settings: {},
      selected: null,
      mode: 'login',
      pin: '',
      name: '',
      joinCode: '',
      submitting: false
    }
  },
  mounted() {
    this.init()
  },
  methods: {
    async init() {
      try {
        const data = await bootstrap({redirectOnUnauthorized: false})
        if (data.setup_needed) return uni.reLaunch({url: '/pages/setup/index'})
        this.members = data.members
        this.settings = data.settings
      } catch (e) {
        uni.showToast({title: e.message || '无法连接服务器', icon: 'none'})
      }
    },
    switchMode(v) {
      this.mode = v
      this.pin = ''
      this.selected = null
    },
    pickMember(m) {
      this.selected = m
      this.pin = ''
    },
    goBack() {
      this.selected = null
      this.pin = ''
    },
    async loginNow(v) {
      if (this.submitting || !this.selected) return
      this.submitting = true
      try {
        const data = await run(() => request('/api/auth/login', {
          method: 'POST',
          data: {name: this.selected.name.trim(), pin: v},
          redirectOnUnauthorized: false
        }))
        setSession(data)
        uni.reLaunch({url: '/pages/home/index'})
      } catch (e) {
        this.pin = ''
      } finally {
        this.submitting = false
      }
    },
    async registerNow(v) {
      if (this.submitting) return
      this.name = this.name.trim()
      this.joinCode = this.joinCode.trim()
      if (!this.name) {
        this.pin = ''
        return uni.showToast({title: '请填写昵称', icon: 'none'})
      }
      this.submitting = true
      try {
        const data = await run(() => request('/api/auth/register', {
          method: 'POST',
          data: {name: this.name, pin: v, join_code: this.joinCode},
          redirectOnUnauthorized: false
        }))
        setSession(data)
        uni.reLaunch({url: '/pages/home/index'})
      } catch (e) {
        this.pin = ''
      } finally {
        this.submitting = false
      }
    },
    editServer() {
      uni.showModal({
        title: '后端地址', editable: true, placeholderText: apiBase(), success: r => {
          try {
            if (!r.confirm) return
            if (!setApiBase(r.content)) return uni.showToast({title: '请输入有效的服务器地址', icon: 'none'})
            clearSession()
            uni.reLaunch({url: '/pages/login/index'})
          } catch (error) {
            uni.showToast({title: error.message || '服务器设置失败', icon: 'none'})
          }
        }
      })
    }
  }
}
</script>
<style scoped>.login {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding-top: 105rpx
}

.logo {
  width: 140rpx;
  height: 140rpx;
  border-radius: 42rpx;
  background: #e5f3e9;
  display: flex;
  flex-direction: row;
  align-items: center;
  justify-content: center;
  font-size: 62rpx;
  margin-bottom: 28rpx
}

.intro {
  margin: 12rpx 0 36rpx
}

.segment {
  display: flex;
  flex-direction: row;
  width: 430rpx;
  padding: 8rpx;
  border-radius: 38rpx;
  background: #e7ebe7;
  margin-bottom: 38rpx
}

.segment view {
  flex: 1;
  text-align: center;
  padding: 18rpx;
  border-radius: 30rpx;
  color: #68756e
}

.segment .on {
  background: #fff;
  color: #43a367;
  box-shadow: 0 4rpx 12rpx rgba(40, 50, 44, .12)
}

.members {
  width: 100%;
  display: flex;
  flex-direction: row;
  flex-wrap: wrap
}

.member {
  width: 30%;
  margin: 0 1.5% 18rpx;
  padding: 24rpx 10rpx;
  display: flex;
  align-items: center;
  flex-direction: column;
  font-size: 25rpx
}

.pin-panel, .register {
  width: 100%;
  max-width: 600rpx;
  display: flex;
  flex-direction: column;
  align-items: center
}

.member-name {
  font-weight: 700;
  font-size: 32rpx;
  margin-bottom: 18rpx
}

.register .input {
  margin-bottom: 12rpx
}

.server {
  margin-top: 50rpx;
  color: #96a299;
  font-size: 23rpx
}</style>
