<script>
import { bootstrap, token } from './api/client'
import { bootstrapRedirectRoute } from './utils/app'

export default {
  async onLaunch() {
    try {
      const data = await bootstrap({ redirectOnUnauthorized: false })
      const pages = getCurrentPages()
      const route = pages[pages.length - 1]?.route || ''
      const redirect = bootstrapRedirectRoute({ setupNeeded: data.setup_needed, authenticated: Boolean(token()), route })
      if (redirect) uni.reLaunch({ url: redirect })
    } catch (error) {
      uni.showToast({ title: '无法连接服务器', icon: 'none' })
    }
  }
}
</script>

<style>
page { background: #f5f8f5; color: #1d2a22; }
</style>
