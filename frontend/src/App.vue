<script setup lang="js">
import { onMounted } from 'vue'
import { bootstrap, token } from './api/client'
import { bootstrapRedirectRoute } from './utils/app'
onMounted(async () => {
  try {
    const data = await bootstrap({ redirectOnUnauthorized: false })
    const pages = typeof getCurrentPages === 'function' ? getCurrentPages() : []
    const route = pages[pages.length - 1]?.route || ''
    const redirect = bootstrapRedirectRoute({ setupNeeded: data.setup_needed, authenticated: Boolean(token()), route })
    if (redirect) uni.reLaunch({ url: redirect })
  } catch { uni.showToast({ title: '无法连接服务器', icon: 'none' }) }
})

</script>
