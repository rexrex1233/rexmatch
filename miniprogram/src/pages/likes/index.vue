<template>
  <view class="likes-page">
    <view class="likes-header">
      <text class="likes-title">喜欢</text>
      <text class="likes-count" v-if="likes.length">{{ likes.length }} 人喜欢了你</text>
    </view>

    <!-- 骨架屏 -->
    <view class="skeleton-grid" v-if="loading && likes.length === 0">
      <view class="sk-card" v-for="i in 4" :key="i">
        <view class="sk-img shimmer"></view>
        <view class="sk-info">
          <view class="sk-name shimmer"></view>
          <view class="sk-meta shimmer"></view>
        </view>
      </view>
    </view>

    <!-- 双列网格（支持下拉刷新） -->
    <scroll-view
      scroll-y
      class="likes-scroll"
      v-if="!loading || likes.length > 0"
      refresher-enabled
      :refresher-triggered="refreshing"
      @refresherrefresh="onRefresh"
    >
      <view class="likes-grid" v-if="likes.length">
        <view class="like-card" v-for="user in likes" :key="user.user_id" @tap="viewUser(user.user_id)">
          <view class="like-img-wrap">
            <image class="like-photo" :src="user.avatar_url || defaultAvatar" mode="aspectFill" />
            <view class="like-overlay"></view>
            <view class="like-info">
              <text class="like-name">{{ user.nickname }}</text>
              <view class="like-meta">
                <text class="like-age" v-if="user.age">{{ user.age }}岁</text>
                <text class="like-city" v-if="user.city">{{ user.city }}</text>
              </view>
            </view>
            <view class="like-badge">
              <text class="like-heart">♥</text>
            </view>
          </view>
        </view>
      </view>

      <!-- 空状态 -->
      <view class="empty-state" v-if="!loading && likes.length === 0">
        <view class="empty-circle">
          <text class="empty-emoji">💝</text>
        </view>
        <text class="empty-title">还没有人喜欢你</text>
        <text class="empty-desc">完善资料，让更多人看到你</text>
      </view>
    </scroll-view>
  </view>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { onShow } from '@dcloudio/uni-app'
import { matchApi } from '../../api'

const defaultAvatar = 'https://api.dicebear.com/7.x/avataaars/svg?seed=default'
const likes = ref<any[]>([])
const loading = ref(false)
const refreshing = ref(false)

onShow(() => {
  loadLikes()
})

async function loadLikes() {
  loading.value = true
  try {
    const res = await matchApi.getLikesReceived()
    likes.value = res.data || []
    if (likes.value.length > 0) {
      uni.setTabBarBadge({ index: 1, text: String(likes.value.length) })
    } else {
      uni.removeTabBarBadge({ index: 1 })
    }
  } catch (e) {
    console.error('加载失败', e)
  } finally {
    loading.value = false
    refreshing.value = false
  }
}

async function onRefresh() {
  refreshing.value = true
  await loadLikes()
}

function viewUser(userId: number) {
  uni.navigateTo({ url: `/pages/user-detail/index?userId=${userId}` })
}
</script>

<style scoped>
.likes-page { min-height: 100vh; background: #f7f8fa; }
.likes-header { padding: 24rpx 32rpx 16rpx; background: #fff; }
.likes-title { font-size: 40rpx; font-weight: 800; color: #1a1a1a; display: block; margin-bottom: 8rpx; }
.likes-count { font-size: 26rpx; color: #ff6b81; font-weight: 500; }

/* ---- 骨架屏 ---- */
.skeleton-grid { display: flex; flex-wrap: wrap; padding: 16rpx; gap: 12rpx; }
.sk-card { width: calc(50% - 6rpx); border-radius: 20rpx; overflow: hidden; background: #fff; }
.sk-img { width: 100%; height: 420rpx; background: #e8e8e8; }
.sk-info { padding: 16rpx 20rpx; }
.sk-name { height: 28rpx; width: 60%; border-radius: 14rpx; background: #e0e0e0; margin-bottom: 12rpx; }
.sk-meta { height: 24rpx; width: 40%; border-radius: 12rpx; background: #e0e0e0; }

@keyframes shimmer {
  0% { background-position: -200% 0; }
  100% { background-position: 200% 0; }
}
.shimmer {
  background: linear-gradient(90deg, #e8e8e8 25%, #f5f5f5 50%, #e8e8e8 75%) !important;
  background-size: 200% 100% !important;
  animation: shimmer 1.5s infinite;
}

/* ---- 滚动区域 ---- */
.likes-scroll { height: calc(100vh - 120rpx); }

/* ---- 双列网格 ---- */
.likes-grid { display: flex; flex-wrap: wrap; padding: 16rpx; gap: 12rpx; }
.like-card { width: calc(50% - 6rpx); border-radius: 20rpx; overflow: hidden; box-shadow: 0 4rpx 16rpx rgba(0,0,0,0.08); }
.like-img-wrap { position: relative; width: 100%; height: 420rpx; }
.like-photo { width: 100%; height: 100%; }
.like-overlay { position: absolute; bottom: 0; left: 0; right: 0; height: 55%; background: linear-gradient(0deg, rgba(0,0,0,0.6) 0%, transparent 100%); }
.like-info { position: absolute; bottom: 0; left: 0; right: 0; padding: 20rpx; z-index: 2; }
.like-name { font-size: 30rpx; font-weight: 700; color: #fff; display: block; margin-bottom: 4rpx; }
.like-meta { display: flex; gap: 10rpx; }
.like-age { font-size: 24rpx; color: rgba(255,255,255,0.85); }
.like-city { font-size: 24rpx; color: rgba(255,255,255,0.7); }
.like-badge { position: absolute; top: 16rpx; right: 16rpx; width: 52rpx; height: 52rpx; border-radius: 50%; background: linear-gradient(135deg, #ff6b81, #ff4757); display: flex; align-items: center; justify-content: center; box-shadow: 0 4rpx 12rpx rgba(255,71,87,0.4); }
.like-heart { font-size: 28rpx; color: #fff; }

/* ---- 空状态 ---- */
.empty-state { display: flex; flex-direction: column; align-items: center; padding-top: 240rpx; }
.empty-circle { width: 140rpx; height: 140rpx; border-radius: 50%; background: linear-gradient(135deg, #fff0f3, #ffe0e6); display: flex; align-items: center; justify-content: center; margin-bottom: 28rpx; }
.empty-emoji { font-size: 56rpx; }
.empty-title { font-size: 32rpx; font-weight: 700; color: #1a1a1a; margin-bottom: 12rpx; }
.empty-desc { font-size: 26rpx; color: #b3b3b3; }
</style>
