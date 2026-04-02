<template>
  <view class="profile-page">
    <!-- 头部卡片 -->
    <view class="profile-hero">
      <view class="hero-bg"></view>
      <view class="hero-content">
        <view class="avatar-container">
          <image
            class="hero-avatar"
            :src="avatarUrl || defaultAvatar"
            mode="aspectFill"
          />
          <view class="verified-badge" v-if="profile?.is_verified">
            <text>✓</text>
          </view>
        </view>
        <text class="hero-name">{{ profile?.nickname || '未设置昵称' }}</text>
        <view class="hero-meta">
          <text class="meta-chip" v-if="profile?.age">{{ profile.age }}岁</text>
          <text class="meta-chip" v-if="profile?.city">{{ profile.city }}</text>
          <text class="meta-chip" v-if="profile?.occupation">{{ profile.occupation }}</text>
        </view>
        <text class="hero-bio" v-if="profile?.bio">{{ profile.bio }}</text>
      </view>
    </view>

    <!-- 资料完整度提示 -->
    <view class="complete-banner" v-if="completeness < 100" @tap="goEditProfile">
      <view class="complete-left">
        <view class="complete-ring">
          <text class="complete-pct">{{ completeness }}%</text>
        </view>
        <view class="complete-info">
          <text class="complete-title">资料完善度 {{ completeness }}%</text>
          <text class="complete-hint">完善资料获得更多曝光</text>
        </view>
      </view>
      <text class="complete-arrow">去完善 ›</text>
    </view>

    <!-- 统计信息 -->
    <view class="stats-card">
      <view class="stat-item">
        <text class="stat-num">{{ profile?.match_count || 0 }}</text>
        <text class="stat-label">匹配</text>
      </view>
      <view class="stat-divider"></view>
      <view class="stat-item">
        <text class="stat-num">{{ profile?.like_count || 0 }}</text>
        <text class="stat-label">被喜欢</text>
      </view>
      <view class="stat-divider"></view>
      <view class="stat-item">
        <text class="stat-num">{{ (profile?.interests || []).length }}</text>
        <text class="stat-label">兴趣</text>
      </view>
    </view>

    <!-- 菜单 -->
    <view class="menu-card">
      <view class="menu-item" @tap="goEditProfile">
        <view class="menu-left">
          <view class="menu-icon-wrap pink">
            <text class="menu-emoji">✏️</text>
          </view>
          <text class="menu-label">编辑资料</text>
        </view>
        <text class="menu-arrow">›</text>
      </view>
      <view class="menu-item" @tap="goMatches">
        <view class="menu-left">
          <view class="menu-icon-wrap purple">
            <text class="menu-emoji">💕</text>
          </view>
          <text class="menu-label">我的匹配</text>
        </view>
        <text class="menu-arrow">›</text>
      </view>
      <view class="menu-item" @tap="goPreferences">
        <view class="menu-left">
          <view class="menu-icon-wrap orange">
            <text class="menu-emoji">🎯</text>
          </view>
          <text class="menu-label">择偶偏好</text>
        </view>
        <text class="menu-arrow">›</text>
      </view>
    </view>

    <view class="menu-card">
      <view class="menu-item" @tap="goPrivacy">
        <view class="menu-left">
          <view class="menu-icon-wrap blue">
            <text class="menu-emoji">🔒</text>
          </view>
          <text class="menu-label">隐私设置</text>
        </view>
        <text class="menu-arrow">›</text>
      </view>
      <view class="menu-item" @tap="goAbout">
        <view class="menu-left">
          <view class="menu-icon-wrap gray">
            <text class="menu-emoji">ℹ️</text>
          </view>
          <text class="menu-label">关于 RexMatch</text>
        </view>
        <text class="menu-version">v0.1.0</text>
      </view>
    </view>

    <!-- 退出 -->
    <view class="logout-area">
      <view class="logout-btn" @tap="handleLogout">
        <text class="logout-text">退出登录</text>
      </view>
    </view>
  </view>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { onShow } from '@dcloudio/uni-app'
import { useUserStore } from '../../stores/user'

const userStore = useUserStore()
const defaultAvatar = 'https://api.dicebear.com/7.x/avataaars/svg?seed=default'

const profile = computed(() => userStore.profile)
const avatarUrl = computed(() => {
  const photos = profile.value?.photos || []
  const avatar = photos.find((p: any) => p.is_avatar)
  return avatar?.url || photos[0]?.url || null
})
const completeness = computed(() => {
  const p = profile.value
  if (!p) return 0
  let score = 0
  const checks = [
    p.nickname, p.gender, p.birthday, p.city, p.bio,
    p.education, p.occupation, (p.photos?.length > 0),
    (p.interests?.length > 0),
  ]
  checks.forEach(v => { if (v) score += 1 })
  return Math.round((score / checks.length) * 100)
})

onShow(() => {
  userStore.fetchProfile()
})

function goEditProfile() {
  uni.navigateTo({ url: '/pages/edit-profile/index' })
}

function goMatches() {
  uni.switchTab({ url: '/pages/chat/index' })
}

function goPreferences() {
  uni.navigateTo({ url: '/pages/preferences/index' })
}

function goPrivacy() {
  uni.navigateTo({ url: '/pages/privacy/index' })
}

function goAbout() {
  uni.navigateTo({ url: '/pages/about/index' })
}

function handleLogout() {
  uni.showModal({
    title: '确认退出',
    content: '确定要退出登录吗？',
    confirmColor: '#ff4757',
    success(res) {
      if (res.confirm) {
        userStore.logout()
      }
    },
  })
}
</script>

<style scoped>
.profile-page {
  min-height: 100vh;
  background: #f7f8fa;
}

/* ---- 头部 ---- */
.profile-hero {
  position: relative;
  padding-bottom: 40rpx;
}

.hero-bg {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 320rpx;
  background: linear-gradient(165deg, #ff6b81 0%, #ff4757 50%, #ff6348 100%);
  border-radius: 0 0 48rpx 48rpx;
}

.hero-content {
  position: relative;
  z-index: 2;
  display: flex;
  flex-direction: column;
  align-items: center;
  padding-top: 100rpx;
}

.avatar-container {
  position: relative;
  margin-bottom: 20rpx;
}

.hero-avatar {
  width: 180rpx;
  height: 180rpx;
  border-radius: 50%;
  border: 8rpx solid #fff;
  box-shadow: 0 8rpx 32rpx rgba(0, 0, 0, 0.15);
}

.verified-badge {
  position: absolute;
  bottom: 8rpx;
  right: 8rpx;
  width: 44rpx;
  height: 44rpx;
  border-radius: 50%;
  background: #07c160;
  display: flex;
  align-items: center;
  justify-content: center;
  border: 4rpx solid #fff;
  color: #fff;
  font-size: 24rpx;
  font-weight: bold;
}

.hero-name {
  font-size: 40rpx;
  font-weight: 800;
  color: #1a1a1a;
  margin-bottom: 12rpx;
}

.hero-meta {
  display: flex;
  gap: 12rpx;
  margin-bottom: 16rpx;
}

.meta-chip {
  padding: 8rpx 20rpx;
  background: #f0f1f5;
  border-radius: 20rpx;
  font-size: 24rpx;
  color: #666;
}

.hero-bio {
  font-size: 26rpx;
  color: #999;
  text-align: center;
  padding: 0 60rpx;
  line-height: 1.6;
}

/* ---- 资料完整度 ---- */
.complete-banner { display: flex; align-items: center; justify-content: space-between; margin: 20rpx 24rpx; padding: 24rpx 28rpx; background: linear-gradient(135deg, #fff0f3, #fef4e8); border-radius: 24rpx; box-shadow: 0 2rpx 12rpx rgba(0,0,0,0.04); }
.complete-left { display: flex; align-items: center; gap: 20rpx; }
.complete-ring { width: 72rpx; height: 72rpx; border-radius: 50%; background: linear-gradient(135deg, #ff6b81, #ffa502); display: flex; align-items: center; justify-content: center; }
.complete-pct { font-size: 22rpx; color: #fff; font-weight: 800; }
.complete-info { display: flex; flex-direction: column; }
.complete-title { font-size: 28rpx; color: #1a1a1a; font-weight: 600; }
.complete-hint { font-size: 22rpx; color: #999; margin-top: 4rpx; }
.complete-arrow { font-size: 26rpx; color: #ff6b81; font-weight: 600; }

/* ---- 统计 ---- */
.stats-card {
  display: flex;
  align-items: center;
  justify-content: space-around;
  background: #fff;
  margin: 20rpx 24rpx;
  border-radius: 24rpx;
  padding: 32rpx 0;
  box-shadow: 0 2rpx 12rpx rgba(0, 0, 0, 0.04);
}

.stat-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  flex: 1;
}

.stat-num {
  font-size: 40rpx;
  font-weight: 800;
  color: #1a1a1a;
  margin-bottom: 4rpx;
}

.stat-label {
  font-size: 24rpx;
  color: #b3b3b3;
}

.stat-divider {
  width: 1rpx;
  height: 48rpx;
  background: #f0f1f5;
}

/* ---- 菜单 ---- */
.menu-card {
  background: #fff;
  margin: 20rpx 24rpx;
  border-radius: 24rpx;
  overflow: hidden;
  box-shadow: 0 2rpx 12rpx rgba(0, 0, 0, 0.04);
}

.menu-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 28rpx 32rpx;
  border-bottom: 1rpx solid #f5f6f8;
}

.menu-item:last-child {
  border-bottom: none;
}

.menu-left {
  display: flex;
  align-items: center;
  gap: 20rpx;
}

.menu-icon-wrap {
  width: 64rpx;
  height: 64rpx;
  border-radius: 16rpx;
  display: flex;
  align-items: center;
  justify-content: center;
}

.menu-icon-wrap.pink { background: rgba(255,107,129,0.1); }
.menu-icon-wrap.purple { background: rgba(162,155,254,0.1); }
.menu-icon-wrap.orange { background: rgba(255,165,2,0.1); }
.menu-icon-wrap.blue { background: rgba(116,185,255,0.1); }
.menu-icon-wrap.gray { background: rgba(178,190,195,0.1); }

.menu-emoji {
  font-size: 28rpx;
}

.menu-label {
  font-size: 30rpx;
  color: #1a1a1a;
  font-weight: 500;
}

.menu-arrow {
  font-size: 36rpx;
  color: #ccc;
}

.menu-version {
  font-size: 26rpx;
  color: #ccc;
}

/* ---- 退出 ---- */
.logout-area {
  padding: 40rpx 24rpx 80rpx;
}

.logout-btn {
  width: 100%;
  height: 88rpx;
  background: #fff;
  border: 2rpx solid #ffe0e3;
  border-radius: 44rpx;
  display: flex;
  align-items: center;
  justify-content: center;
}

.logout-text {
  font-size: 30rpx;
  color: #ff4757;
  font-weight: 500;
}
</style>
