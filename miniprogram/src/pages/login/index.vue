<template>
  <view class="login-page">
    <!-- 装饰背景 -->
    <view class="bg-decor">
      <view class="decor-circle c1"></view>
      <view class="decor-circle c2"></view>
      <view class="decor-circle c3"></view>
    </view>

    <!-- Logo区域 -->
    <view class="logo-section">
      <view class="logo-ring">
        <view class="logo-inner">
          <text class="logo-icon">💕</text>
        </view>
      </view>
      <text class="app-name">RexMatch</text>
      <text class="app-slogan">遇见对的人，从这里开始</text>
    </view>

    <!-- 功能亮点 -->
    <view class="features">
      <view class="feature-item">
        <text class="feature-icon">🎯</text>
        <text class="feature-text">智能匹配</text>
      </view>
      <view class="feature-dot"></view>
      <view class="feature-item">
        <text class="feature-icon">🔒</text>
        <text class="feature-text">安全可靠</text>
      </view>
      <view class="feature-dot"></view>
      <view class="feature-item">
        <text class="feature-icon">💬</text>
        <text class="feature-text">即时聊天</text>
      </view>
    </view>

    <!-- 登录按钮区 -->
    <view class="login-section">
      <button class="login-btn" @tap="handleLogin" :loading="loggingIn">
        <text class="btn-icon" v-if="!loggingIn">💚</text>
        <text class="btn-label">微信一键登录</text>
      </button>
      <text class="agreement">
        登录即表示同意
        <text class="link">《用户协议》</text>
        和
        <text class="link">《隐私政策》</text>
      </text>
    </view>
  </view>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useUserStore } from '../../stores/user'

const userStore = useUserStore()
const loggingIn = ref(false)

async function handleLogin() {
  if (loggingIn.value) return
  loggingIn.value = true
  try {
    await userStore.wxLogin()
  } catch (e) {
    console.error('登录失败', e)
  } finally {
    loggingIn.value = false
  }
}
</script>

<style scoped>
.login-page {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  align-items: center;
  background: linear-gradient(165deg, #fff5f7 0%, #ffffff 40%, #f8f0ff 100%);
  padding: 0 48rpx;
  position: relative;
  overflow: hidden;
}

/* ---- 装饰圆 ---- */
.bg-decor {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  pointer-events: none;
}

.decor-circle {
  position: absolute;
  border-radius: 50%;
  opacity: 0.15;
}

.c1 {
  width: 400rpx;
  height: 400rpx;
  background: #ff6b81;
  top: -120rpx;
  right: -100rpx;
}

.c2 {
  width: 300rpx;
  height: 300rpx;
  background: #a29bfe;
  bottom: 200rpx;
  left: -140rpx;
}

.c3 {
  width: 200rpx;
  height: 200rpx;
  background: #ffa502;
  top: 300rpx;
  right: -80rpx;
}

/* ---- Logo ---- */
.logo-section {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding-top: 200rpx;
  z-index: 1;
}

.logo-ring {
  width: 180rpx;
  height: 180rpx;
  border-radius: 50%;
  background: linear-gradient(135deg, rgba(255,107,129,0.15), rgba(255,71,87,0.08));
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 36rpx;
}

.logo-inner {
  width: 130rpx;
  height: 130rpx;
  border-radius: 50%;
  background: linear-gradient(135deg, #ff6b81, #ff4757);
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 12rpx 40rpx rgba(255, 107, 129, 0.4);
}

.logo-icon {
  font-size: 56rpx;
}

.app-name {
  font-size: 56rpx;
  font-weight: 800;
  color: #1a1a1a;
  letter-spacing: 4rpx;
  margin-bottom: 12rpx;
}

.app-slogan {
  font-size: 28rpx;
  color: #999;
  letter-spacing: 2rpx;
}

/* ---- 功能亮点 ---- */
.features {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 24rpx;
  z-index: 1;
}

.feature-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8rpx;
}

.feature-icon {
  font-size: 40rpx;
}

.feature-text {
  font-size: 24rpx;
  color: #666;
  font-weight: 500;
}

.feature-dot {
  width: 8rpx;
  height: 8rpx;
  border-radius: 50%;
  background: #ddd;
  margin-bottom: 20rpx;
}

/* ---- 登录区 ---- */
.login-section {
  width: 100%;
  padding-bottom: 100rpx;
  z-index: 1;
}

.login-btn {
  width: 100%;
  height: 100rpx;
  background: linear-gradient(135deg, #07c160, #06ad56);
  border-radius: 50rpx;
  display: flex;
  flex-direction: row;
  align-items: center;
  justify-content: center;
  gap: 12rpx;
  border: none;
  box-shadow: 0 8rpx 32rpx rgba(7, 193, 96, 0.35);
}

.login-btn::after {
  border: none;
}

.btn-icon {
  font-size: 36rpx;
}

.btn-label {
  color: #fff;
  font-size: 32rpx;
  font-weight: 600;
  letter-spacing: 2rpx;
}

.agreement {
  display: block;
  text-align: center;
  font-size: 22rpx;
  color: #bbb;
  margin-top: 28rpx;
  line-height: 1.8;
}

.link {
  color: #ff6b81;
}
</style>
