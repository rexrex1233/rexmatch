<template>
  <view class="page">
    <!-- 导航栏 -->
    <view class="nav" :style="{ paddingTop: statusBarHeight + 'px' }" v-show="!showDetail">
      <text class="nav-title">推荐</text>
      <view class="nav-right">
        <view class="like-quota" v-if="dailyRemaining >= 0">
          <text class="quota-heart">♥</text>
          <text class="quota-num">{{ dailyRemaining }}</text>
        </view>
        <view class="nav-btn" @tap="showFilterPanel = true"><text>⚙</text></view>
      </view>
    </view>

    <!-- 骨架屏 -->
    <view class="sk" v-if="loading">
      <view class="sk-card shimmer"></view>
    </view>

    <!-- 卡片容器 -->
    <view class="card-wrap" v-if="currentCard && !loading">
      <view
        class="card"
        :class="{ 'is-expanded': showDetail }"
        :style="cardStyle"
      >
        <!-- 滚动视图 (展开时可滚动) -->
        <scroll-view 
          class="card-scroll" 
          :scroll-y="showDetail" 
          :show-scrollbar="false"
        >
          <!-- 英雄区域 (照片 + 渐变) -->
          <view 
            class="hero-area" 
            @touchstart="onHeroTouchStart"
            @touchmove="onHeroTouchMove"
            @touchend="onHeroTouchEnd"
            @tap="!showDetail && toggleDetail()"
          >
            <image class="hero-bg" :src="currentCard.photos?.[0]?.url || currentCard.avatar_url || defaultAvatar" mode="aspectFill" />
            <view class="hero-fade"></view>
            
            <!-- 用户头部信息 (悬浮在渐变上) -->
            <view class="hero-user-info">
              <image class="hu-avatar" :src="currentCard.avatar_url || defaultAvatar" mode="aspectFill" />
              <view class="hu-details">
                <view class="hu-name-row">
                  <text class="hu-name">{{ currentCard.nickname }}</text>
                  <view class="hu-verified"><text>✔</text></view>
                </view>
                <view class="hu-meta">
                  <view class="online-dot" v-if="currentCard.is_online"></view>
                  <text v-if="currentCard.is_online">在线</text>
                  <text class="divider" v-if="currentCard.is_online">|</text>
                  <text v-if="currentCard.age">{{ currentCard.age }}岁</text>
                  <text class="divider" v-if="currentCard.age && currentCard.city">·</text>
                  <text class="text-ellipsis" style="max-width: 180rpx;" v-if="currentCard.city">{{ currentCard.city }}</text>
                </view>
              </view>
            </view>

            <!-- 滑动标签 -->
            <view class="swipe-tag like-tag" :style="{ opacity: likeOp }"><text>LIKE</text></view>
            <view class="swipe-tag nope-tag" :style="{ opacity: nopeOp }"><text>NOPE</text></view>
            
            <!-- 展开时的关闭按钮 -->
            <view class="close-btn" v-if="showDetail" @tap.stop="toggleDetail" :style="{ top: (statusBarHeight + 10) + 'px' }">
              <text class="cb-icon">↓</text>
            </view>
          </view>

          <!-- 资料内容区 (纯白背景) -->
          <view class="profile-body" @tap="!showDetail && toggleDetail()">
            
            <!-- 契合度推荐 -->
            <view class="pb-section pb-compat" v-if="currentCard.compatibility && currentCard.compatibility.score > 0">
              <text class="compat-text">根据你的偏好 </text>
              <text class="compat-highlight">{{ currentCard.compatibility.shared_interests?.join('、') || '多个共同点' }}</text>
              <text class="compat-text"> 推荐</text>
            </view>

            <!-- 兴趣标签 -->
            <view class="pb-section pb-tags" v-if="currentCard.interests?.length">
              <view 
                class="tag-capsule" 
                :class="i < 3 ? 'gradient-tag' : 'plain-tag'" 
                v-for="(t, i) in currentCard.interests" 
                :key="i"
              >
                <text class="tag-icon" v-if="i === 0 && i < 3">🎯</text>
                <text class="tag-icon" v-if="i === 1 && i < 3">✨</text>
                <text class="tag-icon" v-if="i === 2 && i < 3">🌿</text>
                <text>{{ t }}</text>
              </view>
            </view>

            <!-- 关于我 -->
            <view class="pb-section pb-bio" v-if="currentCard.bio">
              <text class="section-title">关于我</text>
              <text class="bio-text" :class="{'line-clamp-3': !showDetail}">{{ currentCard.bio }}</text>
            </view>

            <!-- 详细资料 (展开后显示) -->
            <view class="pb-extended" v-if="showDetail">
              
              <!-- 基础信息 -->
              <view class="d-card">
                <text class="d-title">基础资料</text>
                <view class="d-grid">
                  <view class="d-item" v-if="currentCard.height"><text class="d-icon">📏</text><text>{{ currentCard.height }} cm</text></view>
                  <view class="d-item" v-if="currentCard.education"><text class="d-icon">🎓</text><text>{{ currentCard.education }}</text></view>
                  <view class="d-item" v-if="currentCard.occupation"><text class="d-icon">💼</text><text>{{ currentCard.occupation }}</text></view>
                  <view class="d-item" v-if="currentCard.city"><text class="d-icon">📍</text><text>{{ currentCard.city }}</text></view>
                  <view class="d-item" v-if="currentCard.gender === 1"><text class="d-icon">♂</text><text>男生</text></view>
                  <view class="d-item" v-if="currentCard.gender === 2"><text class="d-icon">♀</text><text>女生</text></view>
                </view>
              </view>

              <!-- 相册 -->
              <view class="d-card" v-if="currentCard.photos?.length > 1">
                <text class="d-title">生活相册</text>
                <view class="d-photos">
                  <image 
                    class="d-photo" 
                    v-for="(p, i) in currentCard.photos" 
                    :key="i" 
                    :src="p.url" 
                    mode="aspectFill" 
                    @tap.stop="previewPhotos(i)"
                  />
                </view>
              </view>

              <!-- 举报拉黑 -->
              <view class="d-actions-link">
                <text class="d-link" @tap.stop="reportUser">举报该用户</text>
                <text class="d-divider">|</text>
                <text class="d-link" @tap.stop="blockUser">拉黑该用户</text>
              </view>
              
              <view class="detail-bottom-space"></view>
            </view>

          </view>
        </scroll-view>

        <!-- 未展开时的渐变遮罩提示 -->
        <view class="body-fade-out" v-if="!showDetail" @tap="toggleDetail">
          <view class="expand-hint">
            <text>点击或上滑查看详细资料</text>
            <text class="arrow-down">⌄</text>
          </view>
        </view>
      </view>
      
      <!-- 右侧悬浮操作栏 -->
      <view class="right-actions" :class="{'actions-expanded': showDetail}">
        <!-- Gift Button -->
        <view class="r-btn gift" @tap.stop="handleGift">
          <text class="r-icon">🌸</text>
        </view>
        <!-- Like Button -->
        <view class="r-btn like" @tap.stop="animateLike">
          <text class="r-icon">❤️</text>
        </view>
        <!-- Later Button -->
        <view class="r-btn later" @tap.stop="handleLater">
          <text class="r-icon">💤</text>
        </view>
        <!-- Nope Button -->
        <view class="r-btn nope" @tap.stop="animateSkip">
          <text class="r-icon">✖</text>
        </view>
      </view>

    </view>

    <!-- 空状态 -->
    <view class="empty" v-if="!currentCard && !loading">
      <view class="empty-ring"><text>💫</text></view>
      <text class="empty-t">暂时没有更多推荐</text>
      <text class="empty-s">完善资料或调整偏好获得更多推荐</text>
      <view class="empty-btn" @tap="goEditProfile"><text>完善资料</text></view>
    </view>

    <MatchModal :visible="showMatchModal" @close="closeMatchModal" @chat="goToChat" />

    <!-- 筛选 -->
    <view class="mask" v-if="showFilterPanel" @tap="showFilterPanel = false">
      <view class="sheet" @tap.stop>
        <view class="sheet-top"><text class="sh">筛选条件</text><text class="sr" @tap="resetFilters">重置</text></view>
        <view class="sg"><text class="sl">性别</text><view class="sc-row">
          <view :class="['sc',{on:filterGender===null}]" @tap="filterGender=null"><text>不限</text></view>
          <view :class="['sc',{on:filterGender===1}]" @tap="filterGender=1"><text>男</text></view>
          <view :class="['sc',{on:filterGender===2}]" @tap="filterGender=2"><text>女</text></view>
        </view></view>
        <view class="sg"><text class="sl">年龄</text><view class="sc-row">
          <view :class="['sc',{on:filterAge===null}]" @tap="filterAge=null"><text>不限</text></view>
          <view :class="['sc',{on:filterAge===`18-25`}]" @tap="filterAge='18-25'"><text>18-25</text></view>
          <view :class="['sc',{on:filterAge===`25-30`}]" @tap="filterAge='25-30'"><text>25-30</text></view>
          <view :class="['sc',{on:filterAge===`30-40`}]" @tap="filterAge='30-40'"><text>30-40</text></view>
        </view></view>
        <view class="sa"><view class="sbtn" @tap="applyFilters"><text>确定</text></view></view>
      </view>
    </view>
  </view>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { onShow } from '@dcloudio/uni-app'
import { discoverApi, matchApi, reportApi } from '../../api/index'
import MatchModal from '../../components/MatchModal.vue'

const statusBarHeight = ref(0)
const loading = ref(false)
const cards = ref<any[]>([])
const currentIndex = ref(0)
const showMatchModal = ref(false)
const matchedId = ref<number | null>(null)
const defaultAvatar = 'https://api.dicebear.com/7.x/avataaars/svg?seed=default'
const currentCard = ref<any>(null)
const showFilterPanel = ref(false)
const filterGender = ref<number | null>(null)
const filterAge = ref<string | null>(null)

// 动画与交互状态
const isAnimating = ref(false)
const showDetail = ref(false)
const dailyRemaining = ref(-1)
const dailyLimit = ref(10)

const touchStartX = ref(0)
const touchStartY = ref(0)
const isSwiping = ref(false)
const cardOffsetX = ref(0)
const cardOffsetY = ref(0)
const cardRotate = ref(0)
const cardOpacity = ref(1)
const THRESHOLD = 80

const likeOp = computed(() => Math.min(Math.max(cardOffsetX.value / THRESHOLD, 0), 1))
const nopeOp = computed(() => Math.min(Math.max(-cardOffsetX.value / THRESHOLD, 0), 1))
const cardStyle = computed(() => {
  if (cardOffsetX.value === 0 && cardOffsetY.value === 0 && cardOpacity.value === 1 && !showDetail.value) return ''
  return `transform:translate(${cardOffsetX.value}px, ${cardOffsetY.value}px) rotate(${cardRotate.value}deg);opacity:${cardOpacity.value};transition:${isSwiping.value ? 'none' : 'all .4s cubic-bezier(0.2, 0.8, 0.2, 1)'};`
})

onMounted(() => {
  statusBarHeight.value = uni.getSystemInfoSync().statusBarHeight || 44
  loadRecommendations()
  fetchDailyLikes()
})

onShow(() => { 
  if (!loading.value && cards.value.length === 0) loadRecommendations() 
})

// === 详情展开/收起 ===
function toggleDetail() {
  if (isSwiping.value || isAnimating.value) return
  showDetail.value = !showDetail.value
}

// === 滑动交互 ===
function onHeroTouchStart(e: any) {
  if (showDetail.value || isAnimating.value) return
  touchStartX.value = e.touches[0].clientX
  touchStartY.value = e.touches[0].clientY
  isSwiping.value = false
}

function onHeroTouchMove(e: any) {
  if (showDetail.value || isAnimating.value) return
  const dx = e.touches[0].clientX - touchStartX.value
  const dy = e.touches[0].clientY - touchStartY.value
  
  // 上滑超过一定距离，展开详情
  if (!isSwiping.value && dy < -30 && Math.abs(dy) > Math.abs(dx)) {
    toggleDetail()
    return
  }

  if (!isSwiping.value && Math.abs(dx) > 10 && Math.abs(dx) > Math.abs(dy)) {
    isSwiping.value = true
  }
  if (isSwiping.value) { 
    cardOffsetX.value = dx
    cardRotate.value = dx * 0.04 
  }
}

function onHeroTouchEnd() {
  if (!isSwiping.value) { 
    cardOffsetX.value = 0
    cardRotate.value = 0
    return 
  }
  isSwiping.value = false
  if (cardOffsetX.value > THRESHOLD) animateLike()
  else if (cardOffsetX.value < -THRESHOLD) animateSkip()
  else { 
    cardOffsetX.value = 0
    cardRotate.value = 0 
  }
}

// === 动画执行 ===
function animateLike() { 
  if (isAnimating.value) return
  isAnimating.value = true
  showDetail.value = false
  cardOffsetX.value = 500
  cardRotate.value = 15
  cardOpacity.value = 0
  setTimeout(() => { handleLike(); resetCard() }, 300) 
}

function animateSkip() { 
  if (isAnimating.value) return
  isAnimating.value = true
  showDetail.value = false
  cardOffsetX.value = -500
  cardRotate.value = -15
  cardOpacity.value = 0
  setTimeout(() => { handleSkip(); resetCard() }, 300) 
}

function handleLater() {
  if (isAnimating.value) return
  isAnimating.value = true
  showDetail.value = false
  cardOffsetY.value = 800 // 向下滑出屏幕
  cardOpacity.value = 0
  setTimeout(() => {
    // 仅本地跳过，不调后端接口，下次请求还会回来
    currentIndex.value++
    showNext()
    resetCard()
  }, 300)
}

function handleGift() {
  uni.showToast({ title: '礼物功能即将上线，敬请期待', icon: 'none' })
}

function resetCard() { 
  isSwiping.value = true
  cardOffsetX.value = 0
  cardOffsetY.value = 0
  cardRotate.value = 0
  cardOpacity.value = 1
  setTimeout(() => { 
    isSwiping.value = false
    isAnimating.value = false 
  }, 50) 
}

// === 业务逻辑 ===
async function loadRecommendations() {
  loading.value = true
  try {
    const p: any = {}
    if (filterGender.value) p.gender = filterGender.value
    if (filterAge.value) { const [a, b] = filterAge.value.split('-').map(Number); p.min_age = a; p.max_age = b }
    const res = await discoverApi.getRecommendations(p)
    cards.value = res.data || []
    currentIndex.value = 0
    showNext()
  } catch (e) { console.error(e) } finally { loading.value = false }
}

function showNext() { 
  currentCard.value = currentIndex.value < cards.value.length ? cards.value[currentIndex.value] : null 
}

async function fetchDailyLikes() {
  try {
    const r = await matchApi.getDailyLikes()
    dailyRemaining.value = r.data.remaining
    dailyLimit.value = r.data.limit
  } catch {}
}

async function handleLike() {
  if (!currentCard.value) return
  if (dailyRemaining.value === 0) {
    uni.showToast({ title: `今日 ${dailyLimit.value} 次喜欢已用完`, icon: 'none', duration: 2500 })
    return
  }
  try {
    const r = await matchApi.swipe(currentCard.value.user_id, true)
    if (dailyRemaining.value > 0) dailyRemaining.value--
    if (r.data.is_match) { 
      matchedId.value = r.data.match_id
      showMatchModal.value = true 
    }
    currentIndex.value++
    showNext()
  } catch (e: any) {
    if (e?.statusCode === 429 || e?.message?.includes('上限')) {
      dailyRemaining.value = 0
      uni.showToast({ title: '今日喜欢次数已用完', icon: 'none' })
    }
  }
}

async function handleSkip() {
  if (!currentCard.value) return
  try { 
    await matchApi.swipe(currentCard.value.user_id, false)
    currentIndex.value++
    showNext() 
  } catch {}
}

function reportUser() {
  const uid = currentCard.value?.user_id
  if (!uid) return
  uni.showModal({ 
    title: '举报用户', content: '确定举报？', confirmColor: '#ff4757', 
    success(r) { 
      if (r.confirm) {
        reportApi.submit(uid, '不当行为').then(() => { 
          uni.showToast({ title: '已举报', icon: 'success' })
          animateSkip()
        }) 
      } 
    } 
  })
}

function blockUser() {
  const uid = currentCard.value?.user_id
  if (!uid) return
  uni.showModal({ 
    title: '拉黑用户', content: '拉黑后不再看到对方', confirmColor: '#ff4757', 
    success(r) { 
      if (r.confirm) {
        reportApi.block(uid).then(() => { 
          uni.showToast({ title: '已拉黑', icon: 'success' })
          animateSkip()
        }) 
      } 
    } 
  })
}

function previewPhotos(i: number) { 
  const u = currentCard.value?.photos?.map((p:any) => p.url) || []
  if (u.length) uni.previewImage({ urls: u, current: u[i] || u[0] }) 
}

function closeMatchModal() { showMatchModal.value = false }
function goToChat() { 
  showMatchModal.value = false
  if (matchedId.value) uni.navigateTo({ url: `/pages/chat-detail/index?matchId=${matchedId.value}` }) 
}
function goEditProfile() { uni.navigateTo({ url: '/pages/edit-profile/index' }) }
function resetFilters() { filterGender.value = null; filterAge.value = null }
function applyFilters() { showFilterPanel.value = false; loadRecommendations() }
</script>

<style scoped>
.page { 
  height: 100vh; 
  background: #fdfdfd; 
  display: flex; 
  flex-direction: column; 
  overflow: hidden; 
  box-sizing: border-box; 
  padding-bottom: calc(env(safe-area-inset-bottom) + 100rpx); 
}
/* #ifdef H5 */
.page { padding-bottom: 50px; }
/* #endif */

/* 导航 */
.nav { display: flex; align-items: center; justify-content: space-between; height: 88rpx; padding: 0 32rpx; position: relative; z-index: 10; flex-shrink: 0; }
.nav-title { font-size: 40rpx; font-weight: 800; color: #1a1a1a; letter-spacing: 2rpx; }
.nav-right { display: flex; align-items: center; gap: 20rpx; }
.like-quota { display: flex; align-items: center; gap: 6rpx; padding: 8rpx 20rpx; border-radius: 30rpx; background: #fff; box-shadow: 0 4rpx 12rpx rgba(0,0,0,0.05); }
.quota-heart { font-size: 24rpx; color: #ff4757; }
.quota-num { font-size: 26rpx; color: #1a1a1a; font-weight: 700; }
.nav-btn { width: 60rpx; height: 60rpx; border-radius: 50%; background: #fff; box-shadow: 0 4rpx 12rpx rgba(0,0,0,0.05); display: flex; align-items: center; justify-content: center; font-size: 30rpx; color: #1a1a1a; }

/* 卡片容器 */
.card-wrap {
  flex: 1;
  position: relative;
  z-index: 5;
}

/* 主卡片 */
.card { 
  position: absolute;
  top: 12rpx; left: 16rpx; right: 16rpx; bottom: 12rpx;
  border-radius: 40rpx; 
  background: #fff;
  overflow: hidden; 
  will-change: transform, opacity; 
  box-shadow: 0 12rpx 40rpx rgba(0,0,0,0.08);
}
.card.is-expanded {
  top: 0; left: 0; right: 0; bottom: -100rpx; /* 盖住 tabbar */
  border-radius: 0;
  z-index: 100;
}
/* #ifdef H5 */
.card.is-expanded { bottom: -50px; }
/* #endif */

.card-scroll {
  width: 100%;
  height: 100%;
}

/* 英雄区域 (照片) */
.hero-area {
  position: relative;
  width: 100%;
  height: 55vh;
  background: #f7f8fa;
  transition: height 0.4s cubic-bezier(0.2, 0.8, 0.2, 1);
  overflow: hidden;
}
.card.is-expanded .hero-area {
  height: 60vh;
}
.hero-bg { 
  position: absolute; top: 0; left: 0; width: 100%; height: 100%; 
}
.hero-fade { 
  position: absolute; bottom: -2rpx; left: 0; right: 0; height: 280rpx; 
  background: linear-gradient(to bottom, rgba(255,255,255,0) 0%, rgba(255,255,255,1) 100%); 
  pointer-events: none; 
}

/* 用户头部信息 (悬浮) */
.hero-user-info {
  position: absolute;
  bottom: 24rpx;
  left: 32rpx;
  right: 32rpx;
  display: flex;
  align-items: center;
  gap: 24rpx;
  z-index: 10;
}
.hu-avatar {
  width: 160rpx;
  height: 160rpx;
  border-radius: 50%;
  border: 6rpx solid #fff;
  box-shadow: 0 4rpx 16rpx rgba(0,0,0,0.1);
  flex-shrink: 0;
  background: #fff;
}
.hu-details {
  flex: 1;
  display: flex;
  flex-direction: column;
  justify-content: center;
}
.hu-name-row { display: flex; align-items: center; gap: 12rpx; margin-bottom: 12rpx; }
.hu-name { font-size: 44rpx; font-weight: 800; color: #1a1a1a; }
.hu-verified { 
  width: 32rpx; height: 32rpx; border-radius: 50%; background: #1890ff; color: #fff; 
  display: flex; align-items: center; justify-content: center; 
}
.hu-verified text { font-size: 20rpx; font-weight: bold; }

.hu-meta { 
  display: inline-flex; align-items: center; background: rgba(0,0,0,0.45); 
  backdrop-filter: blur(10px); padding: 10rpx 24rpx; border-radius: 30rpx; gap: 10rpx; 
}
.hu-meta text { color: #fff; font-size: 24rpx; font-weight: 500; }
.online-dot { width: 14rpx; height: 14rpx; border-radius: 50%; background: #07c160; }
.divider { color: rgba(255,255,255,0.6); font-size: 20rpx; margin: 0 4rpx; }
.text-ellipsis { white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }

/* 悬浮标签 */
.swipe-tag { position: absolute; top: 120rpx; z-index: 50; padding: 12rpx 36rpx; border-radius: 16rpx; border: 8rpx solid; font-size: 56rpx; font-weight: 900; letter-spacing: 4rpx; pointer-events: none; }
.like-tag { left: 40rpx; color: #ff4757; border-color: #ff4757; transform: rotate(-15deg); }
.nope-tag { right: 40rpx; color: #1a1a1a; border-color: #1a1a1a; transform: rotate(15deg); }

.close-btn {
  position: absolute;
  right: 32rpx;
  width: 80rpx; height: 80rpx;
  border-radius: 50%;
  background: rgba(255,255,255,0.5);
  backdrop-filter: blur(10px);
  display: flex; align-items: center; justify-content: center;
  z-index: 20;
}
.cb-icon { font-size: 40rpx; color: #333; font-weight: bold; }


/* 资料内容区 */
.profile-body {
  background: #ffffff;
  padding: 10rpx 140rpx 60rpx 40rpx; /* right padding leaves space for floating actions */
  min-height: 40vh;
}

.pb-section { margin-bottom: 32rpx; }
.pb-compat { line-height: 1.5; }
.compat-text { font-size: 26rpx; color: #999; }
.compat-highlight { font-size: 26rpx; color: #ff4757; font-weight: 700; margin: 0 4rpx; }

.pb-tags { display: flex; flex-wrap: wrap; gap: 16rpx; }
.tag-capsule {
  padding: 12rpx 32rpx; border-radius: 40rpx; font-size: 26rpx; font-weight: 500; 
  display: inline-flex; align-items: center; gap: 8rpx;
}
.gradient-tag {
  background: linear-gradient(135deg, #ff6b81, #ff4757); color: #fff; 
  box-shadow: 0 4rpx 12rpx rgba(255,107,129,0.3);
}
.plain-tag { background: #f4f6f8; color: #666; }
.tag-icon { font-size: 24rpx; }

.section-title { font-size: 26rpx; color: #999; font-weight: 600; margin-bottom: 16rpx; display: block; }
.bio-text { font-size: 30rpx; color: #333; line-height: 1.6; }
.line-clamp-3 { display: -webkit-box; -webkit-line-clamp: 3; -webkit-box-orient: vertical; overflow: hidden; }

/* 详细资料 */
.pb-extended {
  margin-top: 40rpx;
  margin-right: -100rpx; /* compensate for the profile-body right padding to make cards full width */
}
.d-card {
  background: #fdfdfd;
  margin-bottom: 32rpx;
  padding: 32rpx;
  border-radius: 24rpx;
  border: 1rpx solid #f0f0f0;
}
.d-title { font-size: 28rpx; font-weight: 800; color: #1a1a1a; margin-bottom: 24rpx; display: block; }
.d-grid { display: flex; flex-wrap: wrap; gap: 16rpx; }
.d-item { padding: 12rpx 28rpx; background: #f4f6f8; border-radius: 30rpx; font-size: 26rpx; color: #333; font-weight: 500; display: flex; gap: 12rpx; }
.d-icon { color: #888; }

.d-photos { display: flex; flex-wrap: wrap; gap: 16rpx; }
.d-photo { width: calc(33.33% - 11rpx); height: 220rpx; border-radius: 16rpx; }

.d-actions-link { display: flex; justify-content: center; gap: 32rpx; margin-top: 60rpx; margin-bottom: 40rpx; padding-right: 100rpx; }
.d-link { font-size: 26rpx; color: #999; font-weight: 500; }
.d-divider { color: #dce0e5; }
.detail-bottom-space { height: 120rpx; }

/* 未展开时的渐变遮罩提示 */
.body-fade-out {
  position: absolute;
  bottom: 0; left: 0; right: 0;
  height: 160rpx;
  background: linear-gradient(to bottom, rgba(255,255,255,0) 0%, rgba(255,255,255,1) 80%);
  display: flex; align-items: flex-end; justify-content: center;
  padding-bottom: 20rpx;
  z-index: 20;
  border-radius: 0 0 40rpx 40rpx;
}
.expand-hint { display: flex; flex-direction: column; align-items: center; opacity: 0.5; gap: 2rpx; }
.expand-hint text { font-size: 24rpx; color: #1a1a1a; font-weight: 600; letter-spacing: 2rpx; }
.arrow-down { font-size: 28rpx; font-weight: bold; animation: bounce 1.5s infinite; }
@keyframes bounce { 0%, 100% { transform: translateY(0); } 50% { transform: translateY(-8rpx); } }

/* 右侧悬浮操作栏 */
.right-actions {
  position: absolute;
  right: 24rpx;
  bottom: 180rpx;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 32rpx;
  z-index: 100;
  transition: all 0.3s;
}
.right-actions.actions-expanded {
  bottom: 100rpx;
}
.r-btn {
  width: 90rpx; height: 90rpx;
  border-radius: 50%;
  background: rgba(255,255,255,0.95);
  backdrop-filter: blur(10px);
  box-shadow: 0 8rpx 24rpx rgba(0,0,0,0.12);
  display: flex; align-items: center; justify-content: center;
  transition: transform 0.2s;
}
.r-btn:active { transform: scale(0.85); }
.r-btn.like { width: 110rpx; height: 110rpx; } /* Like 更大一点 */
.r-btn.gift .r-icon { font-size: 40rpx; }
.r-btn.like .r-icon { font-size: 50rpx; margin-top: 4rpx; }
.r-btn.later .r-icon { font-size: 36rpx; }
.r-btn.nope .r-icon { color: #888; font-size: 32rpx; font-weight: bold; }


/* 骨架与空状态 */
.sk { flex: 1; margin: 12rpx 16rpx; border-radius: 32rpx; overflow: hidden; }
.sk-card { width: 100%; height: 100%; }
@keyframes shimmer { 0%{background-position:-200% 0} 100%{background-position:200% 0} }
.shimmer { background: linear-gradient(90deg,#e8e8e8 25%,#f5f5f5 50%,#e8e8e8 75%); background-size: 200% 100%; animation: shimmer 1.4s infinite; }

.empty { flex: 1; display: flex; flex-direction: column; align-items: center; justify-content: center; padding: 0 60rpx; background: #fdfdfd; }
.empty-ring { width: 160rpx; height: 160rpx; border-radius: 50%; background: #fff; box-shadow: 0 12rpx 32rpx rgba(0,0,0,0.05); display: flex; align-items: center; justify-content: center; margin-bottom: 32rpx; font-size: 64rpx; }
.empty-t { font-size: 36rpx; font-weight: 800; color: #1a1a1a; margin-bottom: 12rpx; }
.empty-s { font-size: 28rpx; color: #999; margin-bottom: 48rpx; text-align: center; }
.empty-btn { padding: 24rpx 64rpx; border-radius: 48rpx; background: #1a1a1a; color: #fff; font-size: 30rpx; font-weight: 600; box-shadow: 0 12rpx 24rpx rgba(0,0,0,0.15); }

/* 筛选 */
.mask { position: fixed; top: 0; left: 0; right: 0; bottom: 0; background: rgba(0,0,0,0.4); z-index: 200; display: flex; align-items: flex-end; }
.sheet { width: 100%; background: #fff; border-radius: 32rpx 32rpx 0 0; padding: 40rpx 40rpx calc(40rpx + env(safe-area-inset-bottom)); }
.sheet-top { display: flex; justify-content: space-between; align-items: center; margin-bottom: 40rpx; }
.sh { font-size: 36rpx; font-weight: 800; color: #1a1a1a; }
.sr { font-size: 28rpx; color: #999; font-weight: 500; }
.sg { margin-bottom: 32rpx; }
.sl { font-size: 26rpx; color: #888; margin-bottom: 20rpx; display: block; font-weight: 500; }
.sc-row { display: flex; gap: 20rpx; flex-wrap: wrap; }
.sc { padding: 14rpx 36rpx; border-radius: 40rpx; background: #f0f2f5; font-size: 28rpx; color: #555; font-weight: 500; }
.sc.on { background: #1a1a1a; color: #fff; }
.sa { padding-top: 20rpx; }
.sbtn { width: 100%; height: 96rpx; background: #1a1a1a; border-radius: 48rpx; display: flex; align-items: center; justify-content: center; color: #fff; font-size: 32rpx; font-weight: 600; }
</style>