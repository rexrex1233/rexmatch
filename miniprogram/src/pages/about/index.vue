<template>
  <view class="about-page">
    <!-- Logo + 版本 -->
    <view class="hero">
      <view class="logo-ring">
        <text class="logo-text">R</text>
      </view>
      <text class="app-name">RexMatch</text>
      <text class="app-version">Version {{ version }}</text>
    </view>

    <!-- 功能亮点 -->
    <view class="card">
      <view class="feature-row" v-for="(f, i) in features" :key="i">
        <view :class="['f-icon', f.color]"><text>{{ f.icon }}</text></view>
        <view class="f-desc">
          <text class="f-title">{{ f.title }}</text>
          <text class="f-hint">{{ f.hint }}</text>
        </view>
      </view>
    </view>

    <!-- 协议链接 -->
    <view class="card">
      <view class="link-row" @tap="showAgreement('用户协议')">
        <text class="link-label">用户协议</text>
        <text class="link-arrow">›</text>
      </view>
      <view class="link-row" @tap="showAgreement('隐私政策')">
        <text class="link-label">隐私政策</text>
        <text class="link-arrow">›</text>
      </view>
      <view class="link-row" @tap="showAgreement('社区规范')">
        <text class="link-label">社区规范</text>
        <text class="link-arrow">›</text>
      </view>
    </view>

    <!-- 底部声明 -->
    <view class="footer">
      <text class="footer-text">Made with ♥ by Rex</text>
      <text class="footer-copy">© 2026 RexMatch. All rights reserved.</text>
    </view>
  </view>
</template>

<script setup lang="ts">
import { ref } from 'vue'

const version = ref('0.1.0')

const features = [
  { icon: '🎯', title: '智能推荐', hint: '基于兴趣和偏好的个性化匹配算法', color: 'pink' },
  { icon: '💬', title: '实时聊天', hint: 'WebSocket 即时通讯，消息秒达', color: 'blue' },
  { icon: '🛡', title: '安全可靠', hint: '举报拉黑机制保护你的使用体验', color: 'green' },
  { icon: '📱', title: '跨平台', hint: '小程序 + H5 多端适配', color: 'purple' },
]

function showAgreement(title: string) {
  uni.showModal({
    title,
    content: `${title}正在完善中，上线前会提供完整的${title}文档。`,
    showCancel: false,
    confirmText: '我知道了',
    confirmColor: '#ff6b81',
  })
}
</script>

<style scoped>
.about-page { min-height: 100vh; background: #f7f8fa; padding-bottom: calc(60rpx + env(safe-area-inset-bottom)); }

.hero { display: flex; flex-direction: column; align-items: center; padding: 80rpx 0 48rpx; }
.logo-ring { width: 140rpx; height: 140rpx; border-radius: 32rpx; background: linear-gradient(135deg, #ff6b81, #ff4757); display: flex; align-items: center; justify-content: center; margin-bottom: 24rpx; box-shadow: 0 12rpx 40rpx rgba(255,71,87,0.3); }
.logo-text { font-size: 64rpx; color: #fff; font-weight: 900; font-style: italic; }
.app-name { font-size: 40rpx; font-weight: 800; color: #1a1a1a; margin-bottom: 8rpx; }
.app-version { font-size: 26rpx; color: #b3b3b3; }

.card { background: #fff; margin: 24rpx; border-radius: 24rpx; overflow: hidden; box-shadow: 0 2rpx 12rpx rgba(0,0,0,0.04); }

.feature-row { display: flex; align-items: flex-start; gap: 20rpx; padding: 24rpx 32rpx; border-bottom: 1rpx solid #f5f6f8; }
.feature-row:last-child { border-bottom: none; }
.f-icon { width: 64rpx; height: 64rpx; border-radius: 16rpx; display: flex; align-items: center; justify-content: center; flex-shrink: 0; font-size: 28rpx; }
.f-icon.pink { background: rgba(255,107,129,0.1); }
.f-icon.blue { background: rgba(116,185,255,0.1); }
.f-icon.green { background: rgba(7,193,96,0.1); }
.f-icon.purple { background: rgba(162,155,254,0.1); }
.f-desc { display: flex; flex-direction: column; }
.f-title { font-size: 28rpx; color: #1a1a1a; font-weight: 600; }
.f-hint { font-size: 24rpx; color: #999; margin-top: 4rpx; }

.link-row { display: flex; align-items: center; justify-content: space-between; padding: 30rpx 32rpx; border-bottom: 1rpx solid #f5f6f8; }
.link-row:last-child { border-bottom: none; }
.link-label { font-size: 30rpx; color: #1a1a1a; }
.link-arrow { font-size: 36rpx; color: #ccc; }

.footer { display: flex; flex-direction: column; align-items: center; padding: 60rpx 0 20rpx; }
.footer-text { font-size: 26rpx; color: #ff6b81; font-weight: 600; margin-bottom: 8rpx; }
.footer-copy { font-size: 22rpx; color: #ccc; }
</style>
