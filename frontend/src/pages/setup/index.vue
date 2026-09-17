<template>
  <view class="page no-tab setup">
    <view class="brand">🌱</view>
    <text class="title">欢迎来到干饭厨子</text>
    <text class="subtle intro">{{ step === 1 ? '先告诉我你的家庭和昵称' : '设置一个 6 位数字密码' }}</text>
    <view v-if="step===1" class="form">
      <view class="form-group"><text class="label">家庭名称</text><input v-model="familyName" class="input" maxlength="20" placeholder="例如：温馨小家" /></view>
      <view class="form-group"><text class="label">你的昵称</text><input v-model="name" class="input" maxlength="12" placeholder="怎么称呼你" /></view>
      <button class="btn block" :disabled="submitting" @tap="next">下一步</button>
    </view>
    <view v-else class="form"><PinPad v-model="pin" :disabled="submitting" @complete="submit"/><button class="btn ghost block" :disabled="submitting" @tap="step=1;pin=''">返回修改资料</button></view>
    <text class="server" @tap="editServer">服务器：{{ base }}</text>
  </view>
</template>
<script>
import PinPad from '../../components/PinPad.vue'
import { apiBase, request, run, setApiBase, setSession } from '../../api/client'

export default {
  components: { PinPad },
  data() {
    return { step: 1, familyName: '', name: '', pin: '', submitting: false, base: apiBase() }
  },
  methods: {
    next() {
      this.familyName = this.familyName.trim()
      this.name = this.name.trim()
      if (!this.familyName) return uni.showToast({ title: '请填写家庭名称', icon: 'none' })
      if (!this.name) return uni.showToast({ title: '请填写昵称', icon: 'none' })
      this.step = 2
    },
    async submit(value) {
      if (this.submitting) return
      this.submitting = true
      try {
        const data = await run(() => request('/api/auth/setup', { method: 'POST', data: { family_name: this.familyName, name: this.name, pin: value } }))
        setSession(data)
        uni.reLaunch({ url: '/pages/home/index' })
      } catch (e) {
        this.pin = ''
      } finally {
        this.submitting = false
      }
    },
    editServer() {
      uni.showModal({
        title: '后端地址', editable: true, placeholderText: this.base,
        success: r => {
          try {
            if (!r.confirm) return
            if (!setApiBase(r.content)) return uni.showToast({ title: '请输入有效的服务器地址', icon: 'none' })
            uni.reLaunch({ url: '/pages/setup/index' })
          } catch (error) {
            uni.showToast({ title: error.message || '服务器设置失败', icon: 'none' })
          }
        }
      })
    }
  }
}
</script>
<style scoped>.setup{display:flex;flex-direction:column;align-items:center;padding-top:160rpx}.brand{width:150rpx;height:150rpx;border-radius:48rpx;background:white;display:flex;flex-direction:row;align-items:center;justify-content:center;font-size:65rpx;box-shadow:0 8rpx 30rpx rgba(39,91,57,.1);margin-bottom:30rpx}.intro{margin:14rpx 0 50rpx}.form{width:100%;max-width:620rpx}.server{margin-top:60rpx;color:#93a097;font-size:22rpx;max-width:90%;word-break:break-all}</style>
