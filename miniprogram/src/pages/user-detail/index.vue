<template>
  <view class="detail-page">
    <!-- 自定义导航栏 -->
    <view class="nav-bar" :style="{ paddingTop: statusBarHeight + 'px' }">
      <view class="nav-back" @tap="goBack">
        <text class="back-icon">‹</text>
      </view>
      <text class="nav-title">{{ user?.nickname || '' }}</text>
      <view class="nav-more" @tap="showActionSheet">
        <text>···</text>
      </view>
    </view>

    <!-- 骨架屏 -->
    <view class="skeleton" v-if="loading">
      <view class="sk-hero shimmer"></view>
      <view class="sk-row">
        <view class="sk-avatar shimmer"></view>
        <view class="sk-lines">
          <view class="sk-line w60 shimmer"></view>
          <view class="sk-line w40 shimmer"></view>
        </view>
      </view>
      <view class="sk-card shimmer"></view>
    </view>

    <scroll-view scroll-y class="content-scroll" v-if="user && !loading">
      <!-- 大图 -->
      <view class="hero-section" @tap="previewPhotos(0)">
        <image class="hero-img" :src="user.avatar_url || defaultAvatar" mode="aspectFill" />
        <view class="hero-gradient"></view>
        <view class="photo-count" v-if="allPhotos.length > 1">
          <text>1/{{ allPhotos.length }}</text>
        </view>
      </view>

      <!-- 头像+信息 -->
      <view class="user-header">
        <view class="avatar-row">
          <image class="user-avatar" :src="user.avatar_url || defaultAvatar" mode="aspectFill" />
          <view class="name-area">
            <text class="user-name">{{ user.nickname }}</text>
            <view class="meta-line">
              <text class="meta-text" v-if="user.age">{{ user.age }}岁</text>
              <text class="meta-dot" v-if="user.age && user.city">·</text>
              <text class="meta-text" v-if="user.city">{{ user.city }}</text>
            </view>
          </view>
        </view>
      </view>

      <!-- 简介 -->
      <view class="bio-card" v-if="user.bio">
        <text class="bio-quote">"</text>
        <text class="bio-text">{{ user.bio }}</text>
      </view>

      <!-- 基本信息 -->
      <view class="info-card">
        <text class="card-label">基本资料</text>
        <view class="info-grid">
          <view class="info-item" v-if="user.education">
            <text class="info-icon">🎓</text>
            <text class="info-val">{{ user.education }}</text>
          </view>
          <view class="info-item" v-if="user.occupation">
            <text class="info-icon">💼</text>
            <text class="info-val">{{ user.occupation }}</text>
          </view>
          <view class="info-item" v-if="user.city">
            <text class="info-icon">📍</text>
            <text class="info-val">{{ user.city }}</text>
          </view>
          <view class="info-item" v-if="user.height">
            <text class="info-icon">📏</text>
            <text class="info-val">{{ user.height }}cm</text>
          </view>
        </view>
      </view>

      <!-- 兴趣 -->
      <view class="info-card" v-if="user.interests?.length">
        <text class="card-label">兴趣爱好</text>
        <view class="tag-wall">
          <view class="tag-item" v-for="(tag, idx) in user.interests" :key="idx">
            <text>{{ tag.name || tag }}</text>
          </view>
        </view>
      </view>

      <!-- 更多照片 -->
      <view class="info-card" v-if="allPhotos.length > 0">
        <text class="card-label">照片</text>
        <view class="photo-grid">
          <image
            class="grid-photo"
            v-for="(p, idx) in allPhotos"
            :key="idx"
            :src="p"
            mode="aspectFill"
            @tap="previewPhotos(idx)"
          />
        </view>
      </view>

      <view class="bottom-spacer"></view>
    </scroll-view>

    <!-- 底部操作栏 -->
    <view class="action-bar" v-if="user && !loading">
      <view class="action-btn-bar skip" @tap="handleSkip">
        <text class="action-text">跳过</text>
      </view>
      <view class="action-btn-bar like" @tap="handleLike">
        <text class="action-icon-text">♥</text>
        <text class="action-text-w">喜欢</text>
      </view>
    </view>
  </view>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { onLoad } from '@dcloudio/uni-app'
import { userApi, matchApi, reportApi } from '../../api'

const statusBarHeight = ref(0)
const userId = ref(0)
const user = ref<any>(null)
const loading = ref(false)
const defaultAvatar = 'https://api.dicebear.com/7.x/avataaars/svg?seed=default'

const allPhotos = computed(() => {
  if (!user.value) return []
  const photos = user.value.photos || []
  return photos.map((p: any) => p.url || p).filter(Boolean)
})

onLoad((options: any) => {
  userId.value = Number(options.userId)
})

onMounted(async () => {
  const sysInfo = uni.getSystemInfoSync()
  statusBarHeight.value = sysInfo.statusBarHeight || 44
  await loadUser()
})

async function loadUser() {
  loading.value = true
  try {
    const res = await userApi.getUserProfile(userId.value)
    user.value = res.data
  } catch (e) {
    console.error('加载用户失败', e)
  } finally {
    loading.value = false
  }
}

function previewPhotos(idx: number) {
  const urls = allPhotos.value
  if (urls.length === 0) return
  uni.previewImage({ urls, current: urls[idx] || urls[0] })
}

function goBack() { uni.navigateBack() }

function showActionSheet() {
  uni.showActionSheet({
    itemList: ['举报该用户', '拉黑该用户'],
    success(res) {
      if (res.tapIndex === 0) {
        uni.showModal({
          title: '举报用户', content: '确定要举报该用户吗？', confirmColor: '#ff4757',
          success(r) {
            if (r.confirm) reportApi.submit(userId.value, '不当行为')
              .then(() => { uni.showToast({ title: '举报已提交', icon: 'success' }); uni.navigateBack() })
          },
        })
      } else if (res.tapIndex === 1) {
        uni.showModal({
          title: '拉黑用户', content: '拉黑后将不再看到对方，确定吗？', confirmColor: '#ff4757',
          success(r) {
            if (r.confirm) reportApi.block(userId.value)
              .then(() => { uni.showToast({ title: '已拉黑', icon: 'success' }); uni.navigateBack() })
          },
        })
      }
    },
  })
}

async function handleLike() {
  try {
    const res = await matchApi.swipe(userId.value, true)
    if (res.data.is_match) {
      uni.showToast({ title: '配对成功!', icon: 'success' })
    } else {
      uni.showToast({ title: '已喜欢', icon: 'success' })
    }
    setTimeout(() => uni.navigateBack(), 1000)
  } catch (e: any) {
    uni.showToast({ title: e?.message || '操作失败', icon: 'none' })
  }
}

async function handleSkip() {
  try {
    await matchApi.swipe(userId.value, false)
    uni.navigateBack()
  } catch (e: any) {
    uni.showToast({ title: e?.message || '操作失败', icon: 'none' })
  }
}
</script>

<style scoped>
.detail-page { min-height: 100vh; background: #f7f8fa; }
.nav-bar { display: flex; align-items: center; justify-content: space-between; height: 88rpx; padding: 0 24rpx; background: #fff; position: relative; z-index: 10; }
.nav-back { width: 64rpx; height: 64rpx; display: flex; align-items: center; justify-content: center; }
.back-icon { font-size: 48rpx; color: #333; font-weight: 300; }
.nav-title { font-size: 32rpx; font-weight: 600; color: #1a1a1a; }
.nav-more { width: 64rpx; height: 64rpx; display: flex; align-items: center; justify-content: center; font-size: 28rpx; color: #666; font-weight: bold; letter-spacing: 2rpx; }

/* ---- 骨架屏 ---- */
.skeleton { padding: 0; }
.sk-hero { width: 100%; height: 480rpx; background: #e8e8e8; }
.sk-row { display: flex; gap: 20rpx; padding: 0 32rpx; margin-top: -60rpx; position: relative; z-index: 2; }
.sk-avatar { width: 130rpx; height: 130rpx; border-radius: 50%; border: 6rpx solid #fff; flex-shrink: 0; }
.sk-lines { flex: 1; padding-top: 60rpx; display: flex; flex-direction: column; gap: 14rpx; }
.sk-line { height: 26rpx; border-radius: 13rpx; background: #e0e0e0; }
.sk-line.w60 { width: 60%; }
.sk-line.w40 { width: 40%; }
.sk-card { height: 160rpx; margin: 20rpx 24rpx; border-radius: 20rpx; background: #e8e8e8; }

@keyframes shimmer {
  0% { background-position: -200% 0; }
  100% { background-position: 200% 0; }
}
.shimmer {
  background: linear-gradient(90deg, #e8e8e8 25%, #f5f5f5 50%, #e8e8e8 75%) !important;
  background-size: 200% 100% !important;
  animation: shimmer 1.5s infinite;
}

.content-scroll { height: calc(100vh - 88rpx - 140rpx); }

.hero-section { position: relative; height: 480rpx; }
.hero-img { width: 100%; height: 100%; }
.hero-gradient { position: absolute; bottom: 0; left: 0; right: 0; height: 40%; background: linear-gradient(0deg, #f7f8fa 0%, transparent 100%); }
.photo-count { position: absolute; top: 24rpx; left: 24rpx; padding: 6rpx 16rpx; border-radius: 16rpx; background: rgba(0,0,0,0.4); font-size: 22rpx; color: #fff; }

.user-header { margin-top: -70rpx; padding: 0 32rpx 16rpx; position: relative; z-index: 5; }
.avatar-row { display: flex; align-items: flex-end; gap: 20rpx; }
.user-avatar { width: 130rpx; height: 130rpx; border-radius: 50%; border: 6rpx solid #fff; box-shadow: 0 4rpx 16rpx rgba(0,0,0,0.1); }
.name-area { padding-bottom: 8rpx; }
.user-name { font-size: 36rpx; font-weight: 800; color: #1a1a1a; display: block; margin-bottom: 4rpx; }
.meta-line { display: flex; align-items: center; gap: 8rpx; }
.meta-text { font-size: 26rpx; color: #999; }
.meta-dot { font-size: 26rpx; color: #ccc; }

.bio-card { margin: 16rpx 24rpx; padding: 24rpx 28rpx; background: #fff; border-radius: 20rpx; box-shadow: 0 2rpx 12rpx rgba(0,0,0,0.04); position: relative; }
.bio-quote { font-size: 56rpx; color: #ffe0e3; font-weight: 800; position: absolute; top: 4rpx; left: 16rpx; }
.bio-text { font-size: 28rpx; color: #333; line-height: 1.7; padding-left: 28rpx; }

.info-card { margin: 16rpx 24rpx; padding: 24rpx 28rpx; background: #fff; border-radius: 20rpx; box-shadow: 0 2rpx 12rpx rgba(0,0,0,0.04); }
.card-label { font-size: 28rpx; color: #999; font-weight: 600; margin-bottom: 16rpx; display: block; }
.info-grid { display: flex; flex-wrap: wrap; gap: 12rpx; }
.info-item { display: flex; align-items: center; gap: 8rpx; padding: 12rpx 20rpx; background: #f7f8fa; border-radius: 12rpx; }
.info-icon { font-size: 22rpx; }
.info-val { font-size: 26rpx; color: #333; }
.tag-wall { display: flex; flex-wrap: wrap; gap: 12rpx; }
.tag-item { padding: 10rpx 24rpx; border-radius: 28rpx; background: rgba(255,107,129,0.08); font-size: 26rpx; color: #ff6b81; }

.photo-grid { display: flex; flex-wrap: wrap; gap: 12rpx; }
.grid-photo { width: calc(33.33% - 8rpx); height: 200rpx; border-radius: 12rpx; }
.bottom-spacer { height: 40rpx; }

.action-bar { position: fixed; bottom: 0; left: 0; right: 0; display: flex; gap: 24rpx; padding: 20rpx 32rpx; padding-bottom: calc(20rpx + env(safe-area-inset-bottom)); background: #fff; border-top: 1rpx solid #f0f1f5; z-index: 50; }
.action-btn-bar { flex: 1; height: 88rpx; border-radius: 44rpx; display: flex; align-items: center; justify-content: center; gap: 8rpx; }
.action-btn-bar.skip { background: #f0f1f5; }
.action-btn-bar.skip .action-text { font-size: 30rpx; color: #999; font-weight: 500; }
.action-btn-bar.like { background: linear-gradient(135deg, #ff6b81, #ff4757); box-shadow: 0 6rpx 20rpx rgba(255,71,87,0.3); }
.action-icon-text { font-size: 28rpx; color: #fff; }
.action-text-w { font-size: 30rpx; color: #fff; font-weight: 600; }
</style>
