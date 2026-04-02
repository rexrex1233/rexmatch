<script setup lang="ts">
import { onLaunch } from '@dcloudio/uni-app'
import { useUserStore } from './stores/user'

onLaunch(() => {
  const userStore = useUserStore()
  userStore.checkLogin()
})
</script>

<style>
page {
  background-color: #f7f8fa;
  font-family: -apple-system, BlinkMacSystemFont, 'PingFang SC', 'Helvetica Neue', 'Segoe UI', Roboto, sans-serif;
  -webkit-font-smoothing: antialiased;
}

/* H5 桌面端：限制最大宽度，居中显示为手机模拟框 */
/* #ifdef H5 */
uni-page-body,
uni-page-wrapper {
  max-width: 480px;
  margin: 0 auto;
  position: relative;
}

@media (min-width: 500px) {
  page {
    background-color: #e8eaed;
  }
  uni-page-body,
  uni-page-wrapper {
    box-shadow: 0 0 40px rgba(0,0,0,0.08);
    background: #f7f8fa;
    min-height: 100vh;
  }
}
/* #endif */
</style>
