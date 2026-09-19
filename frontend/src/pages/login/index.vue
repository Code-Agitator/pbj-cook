<template>
  <view class="page no-tab login">
    <view class="auth-mark">PBJ-Cook</view>
    <text class="title">{{ settings.family_name || '我家' }} 开饭啦！</text>
    <text class="subtle intro">{{ selected ? '输入 6 位密码' : mode === 'login' ? '选择你的身份' : '新成员加入家庭' }}
    </text>
    <view v-if="settings.registration_open&&!selected" class="segment">
      <button :class="{on:mode==='login'}" @tap="switchMode('login')">登录</button>
      <button :class="{on:mode==='register'}" @tap="switchMode('register')">注册</button>
    </view>
    <view v-if="mode==='login'&&!selected" class="members">
      <button v-for="member in members" :key="member.id" class="member" @tap="pickMember(member)">
        <Avatar :name="member.name" :src="assetUrl(member.avatar_path)" :size="92"/>
        <text>{{ member.name }}</text>
      </button>
    </view>
    <view v-if="mode==='login'&&selected" class="pin-panel">
      <button class="back-member" @tap="goBack">‹ 换个成员</button>
      <Avatar :name="selected.name" :src="assetUrl(selected.avatar_path)" :size="118"/>
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
  </view>
</template>
<script setup lang="js">
import {onMounted, ref} from 'vue';
import Avatar from '../../components/Avatar.vue';
import PinPad from '../../components/PinPad.vue';
import {assetUrl, bootstrap, request, run, setSession} from '../../api/client'

const members = ref([]), settings = ref({}), selected = ref(null), mode = ref('login'), pin = ref(''), name = ref(''),
    joinCode = ref(''), submitting = ref(false)

async function init() {
  try {
    const data = await bootstrap({redirectOnUnauthorized: false});
    if (data.setup_needed) return uni.reLaunch({url: '/pages/setup/index'});
    members.value = Array.isArray(data.members) ? data.members : [];
    settings.value = data.settings || {}
  } catch (error) {
    uni.showToast({title: error?.message || '无法连接服务器', icon: 'none'})
  }
}

function switchMode(value) {
  mode.value = value;
  pin.value = '';
  selected.value = null
}

function pickMember(member) {
  selected.value = member;
  pin.value = ''
}

function goBack() {
  selected.value = null;
  pin.value = ''
}

async function loginNow(value) {
  if (submitting.value || !selected.value) return;
  submitting.value = true;
  try {
    const data = await run(() => request('/api/auth/login', {
      method: 'POST',
      data: {name: selected.value.name.trim(), pin: value},
      redirectOnUnauthorized: false
    }));
    setSession(data);
    uni.reLaunch({url: '/pages/home/index'})
  } catch {
    pin.value = ''
  } finally {
    submitting.value = false
  }
}

async function registerNow(value) {
  if (submitting.value) return;
  name.value = name.value.trim();
  joinCode.value = joinCode.value.trim();
  if (!name.value) {
    pin.value = '';
    return uni.showToast({title: '请填写昵称', icon: 'none'})
  }
  submitting.value = true;
  try {
    const data = await run(() => request('/api/auth/register', {
      method: 'POST',
      data: {name: name.value, pin: value, join_code: joinCode.value},
      redirectOnUnauthorized: false
    }));
    setSession(data);
    uni.reLaunch({url: '/pages/home/index'})
  } catch {
    pin.value = ''
  } finally {
    submitting.value = false
  }
}

onMounted(init)
</script>
<style scoped>.login {
  display: flex;
  padding-top: 96rpx;
  align-items: center;
  flex-direction: column
}

.auth-mark {
  display: flex;
  padding: 12rpx;
  margin-bottom: 26rpx;
  align-items: center;
  justify-content: center;
  border: 1px solid var(--theme-border-subtle);
  border-radius: 18rpx;
  background: var(--theme-bg-surface);
  color: var(--theme-text-action);
  font-family: "Songti SC", "STSong", "Noto Serif CJK SC", serif;
  font-size: 50rpx
}

.intro {
  margin: 10rpx 0 38rpx
}

.segment {
  display: grid;
  width: 420rpx;
  margin-bottom: 38rpx;
  padding: 5rpx;
  grid-template-columns:1fr 1fr;
  border-radius: 10rpx
}

.segment button {
  min-height: 66rpx;
  background: transparent;
  color: var(--theme-text-secondary);
  font-size: 25rpx
}

.segment button.on {
  background: var(--theme-action-primary);
  color: var(--theme-action-on-primary);
  border-radius: 7rpx
}

.members {
  display: grid;
  width: 100%;
  max-width: 650rpx;
  grid-template-columns:repeat(3, minmax(0, 1fr));
  gap: 14rpx
}

.member {
  display: flex;
  min-height: 166rpx;
  padding: 20rpx 12rpx;
  align-items: center;
  flex-direction: column;
  border: 1px solid var(--theme-border-subtle);
  border-radius: 10rpx;
  background: var(--theme-bg-surface);
  color: var(--theme-text-primary);
  font-size: 24rpx
}

.member text {
  margin-top: 10rpx
}

.pin-panel, .register {
  display: flex;
  width: 100%;
  max-width: 560rpx;
  align-items: center;
  flex-direction: column
}

.back-member {
  align-self: flex-start;
  min-height: 60rpx;
  padding: 0;
  background: transparent;
  color: var(--theme-text-secondary)
}

.member-name {
  margin: 12rpx 0 22rpx;
  font-size: 30rpx;
  font-weight: 650
}

.register .input {
  margin-bottom: 14rpx
}

.register .pin-wrap {
  margin-top: 24rpx
}

</style>
