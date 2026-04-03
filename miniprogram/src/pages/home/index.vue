<template>
  <view class="page">
    <!-- 苹果风格大标题导航栏 -->
    <view class="nav" :style="{ paddingTop: statusBarHeight + 'px' }" :class="{ 'nav-hidden': showDetail }">
      <view class="nav-content">
        <text class="nav-title">推荐</text>
        <view class="nav-right">
          <view class="glass-pill" v-if="dailyRemaining >= 0">
            <text class="quota-heart">💖</text>
            <text class="quota-num">{{ dailyRemaining }}</text>
          </view>
          <view class="glass-circle" @tap="showFilterPanel = true">
            <!-- 苹果风格筛选图标 -->
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#000" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
              <line x1="4" y1="21" x2="4" y2="14"></line><line x1="4" y1="10" x2="4" y2="3"></line>
              <line x1="12" y1="21" x2="12" y2="12"></line><line x1="12" y1="8" x2="12" y2="3"></line>
              <line x1="20" y1="21" x2="20" y2="16"></line><line x1="20" y1="12" x2="20" y2="3"></line>
              <line x1="1" y1="14" x2="7" y2="14"></line><line x1="9" y1="8" x2="15" y2="8"></line><line x1="17" y1="16" x2="23" y2="16"></line>
            </svg>
          </view>
        </view>
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
          <!-- 英雄区域 (Swiper 照片墙 + 毛玻璃渐变) -->
          <view class="hero-area">
            <swiper 
              class="hero-swiper" 
              :indicator-dots="displayPhotos.length > 1" 
              indicator-color="rgba(255,255,255,0.4)" 
              indicator-active-color="#FFFFFF"
              :current="0"
            >
              <swiper-item v-for="(photo, i) in displayPhotos" :key="i" @tap="!showDetail && toggleDetail()">
                <image class="hero-bg" :src="photo.url" mode="aspectFill" />
              </swiper-item>
            </swiper>
            
            <!-- 底部柔和阴影，保证文字可读性 -->
            <view class="hero-fade" pointer-events="none"></view>
            
            <!-- 用户头部信息 (悬浮在渐变上) -->
            <view class="hero-user-info">
              <view class="hu-avatar-container">
                <image class="hu-avatar" :src="currentCard.avatar_url || defaultAvatar" mode="aspectFill" />
                <view class="hu-online-badge" v-if="currentCard.is_online"></view>
              </view>
              
              <view class="hu-details">
                <view class="hu-name-row">
                  <text class="hu-name">{{ currentCard.nickname }}</text>
                  <view class="hu-verified"><text>✓</text></view>
                </view>
                
                <!-- 苹果毛玻璃信息胶囊 -->
                <view class="hu-meta glass-morphism">
                  <text v-if="currentCard.age">{{ currentCard.age }}岁</text>
                  <text class="divider" v-if="currentCard.age && currentCard.city">·</text>
                  <text class="text-ellipsis" style="max-width: 200rpx;" v-if="currentCard.city">{{ currentCard.city }}</text>
                  <text class="divider" v-if="currentCard.city && currentCard.education">·</text>
                  <text v-if="currentCard.education">{{ currentCard.education }}</text>
                </view>
              </view>
            </view>

            <!-- 滑动标签 (保持高对比度) -->
            <view class="swipe-tag like-tag" :style="{ opacity: likeOp }"><text>LIKE</text></view>
            <view class="swipe-tag nope-tag" :style="{ opacity: nopeOp }"><text>NOPE</text></view>
            
            <!-- 展开时的毛玻璃关闭按钮 -->
            <view class="close-btn glass-morphism" v-if="showDetail" @tap.stop="toggleDetail" :style="{ top: (statusBarHeight + 10) + 'px' }">
              <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#000" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"><polyline points="6 9 12 15 18 9"></polyline></svg>
            </view>
          </view>

          <!-- 资料内容区 -->
          <view 
            class="profile-body" 
            @touchstart="onHeroTouchStart"
            @touchmove="onHeroTouchMove"
            @touchend="onHeroTouchEnd"
            @tap="!showDetail && toggleDetail()"
          >
            
            <!-- 契合度推荐 (Apple 风格强调文本层级) -->
            <view class="pb-section pb-compat" v-if="currentCard.compatibility && currentCard.compatibility.score > 0">
              <text class="compat-icon">✨</text>
              <view class="compat-text-group">
                <text class="compat-title">高度契合</text>
                <text class="compat-desc">基于你们共同喜欢的 {{ currentCard.compatibility.shared_interests?.join('、') || '多个特质' }}</text>
              </view>
            </view>

            <!-- 兴趣标签 (柔和圆润胶囊) -->
            <view class="pb-section pb-tags" v-if="currentCard.interests?.length">
              <view 
                class="tag-capsule" 
                :class="i < 3 ? 'tag-primary' : 'tag-secondary'" 
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
              <text class="apple-section-title">关于我</text>
              <text class="bio-text" :class="{'line-clamp-3': !showDetail}">{{ currentCard.bio }}</text>
            </view>

            <!-- 详细资料 (展开后显示) -->
            <view class="pb-extended" v-if="showDetail">
              
              <!-- 基础信息 (大圆角卡片) -->
              <view class="apple-card">
                <text class="apple-section-title">基础资料</text>
                <view class="d-grid">
                  <view class="d-item" v-if="currentCard.height"><text class="d-icon">📏</text><text>{{ currentCard.height }} cm</text></view>
                  <view class="d-item" v-if="currentCard.education"><text class="d-icon">🎓</text><text>{{ currentCard.education }}</text></view>
                  <view class="d-item" v-if="currentCard.occupation"><text class="d-icon">💼</text><text>{{ currentCard.occupation }}</text></view>
                  <view class="d-item" v-if="currentCard.city"><text class="d-icon">📍</text><text>{{ currentCard.city }}</text></view>
                  <view class="d-item" v-if="currentCard.gender === 1"><text class="d-icon">♂</text><text>男生</text></view>
                  <view class="d-item" v-if="currentCard.gender === 2"><text class="d-icon">♀</text><text>女生</text></view>
                </view>
              </view>

              <!-- 相册 (无缝圆角边缘) -->
              <view class="apple-card" v-if="displayPhotos.length > 1">
                <text class="apple-section-title">生活相册</text>
                <view class="d-photos">
                  <image 
                    class="d-photo" 
                    v-for="(p, i) in displayPhotos" 
                    :key="i" 
                    :src="p.url" 
                    mode="aspectFill" 
                    @tap.stop="previewPhotos(i)"
                  />
                </view>
              </view>

              <!-- 举报拉黑 (Apple 风格 Destructive 按钮) -->
              <view class="d-actions-link">
                <text class="d-link destructive" @tap.stop="reportUser">举报该用户</text>
                <text class="d-link destructive" @tap.stop="blockUser">拉黑该用户</text>
              </view>
              
              <view class="detail-bottom-space"></view>
            </view>

          </view>
        </scroll-view>

        <!-- 未展开时的向上滑动指示 -->
        <view class="body-fade-out" v-if="!showDetail" @tap="toggleDetail">
          <view class="expand-hint glass-morphism-light">
            <text>上滑查看详细资料</text>
          </view>
        </view>
      </view>
      
      <!-- 右侧悬浮操作栏 (Apple Glassmorphism + SVGs) -->
      <view class="right-actions" :class="{'actions-expanded': showDetail}">
        <!-- Gift -->
        <view class="r-btn glass-morphism" @tap.stop="handleGift">
          <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#FF9500" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><polyline points="20 12 20 22 4 22 4 12"></polyline><rect x="2" y="7" width="20" height="5"></rect><line x1="12" y1="22" x2="12" y2="7"></line><path d="M12 7H7.5a2.5 2.5 0 0 1 0-5C11 2 12 7 12 7z"></path><path d="M12 7h4.5a2.5 2.5 0 0 0 0-5C13 2 12 7 12 7z"></path></svg>
        </view>
        <!-- Like -->
        <view class="r-btn glass-morphism like primary-pop" @tap.stop="animateLike">
          <svg width="34" height="34" viewBox="0 0 24 24" fill="#FF2D55" stroke="#FF2D55" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><path d="M20.84 4.61a5.5 5.5 0 0 0-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 0 0-7.78 7.78l1.06 1.06L12 21.23l7.78-7.78 1.06-1.06a5.5 5.5 0 0 0 0-7.78z"></path></svg>
        </view>
        <!-- Later (Bookmark style) -->
        <view class="r-btn glass-morphism" @tap.stop="handleLater">
          <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#007AFF" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><path d="M19 21l-7-5-7 5V5a2 2 0 0 1 2-2h10a2 2 0 0 1 2 2z"></path></svg>
        </view>
        <!-- Nope (Cross) -->
        <view class="r-btn glass-morphism" @tap.stop="animateSkip">
          <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#8E8E93" stroke-width="3.5" stroke-linecap="round" stroke-linejoin="round"><line x1="18" y1="6" x2="6" y2="18"></line><line x1="6" y1="6" x2="18" y2="18"></line></svg>
        </view>
      </view>

    </view>

    <!-- 空状态 -->
    <view class="empty" v-if="!currentCard && !loading">
      <view class="empty-ring"><text>✨</text></view>
      <text class="empty-t">暂无推荐</text>
      <text class="empty-s">你已经看完了所有的推荐，调整偏好或稍后再来吧</text>
      <view class="apple-btn" @tap="goEditProfile"><text>完善资料</text></view>
    </view>

    <MatchModal :visible="showMatchModal" @close="closeMatchModal" @chat="goToChat" />

    <!-- 筛选 (Apple Bottom Sheet Style, Added ScrollView for Fix) -->
    <view class="mask" v-if="showFilterPanel" @tap="showFilterPanel = false">
      <view class="sheet" @tap.stop>
        <view class="sheet-handle"></view>
        <view class="sheet-top">
          <text class="sh">偏好设置</text>
          <text class="sr" @tap="resetFilters">重置</text>
        </view>
        <scroll-view scroll-y class="sheet-scroll" :show-scrollbar="false">
          <view class="sg">
            <text class="sl">希望认识</text>
            <view class="sc-row">
              <view :class="['sc',{on:filterGender===null}]" @tap="filterGender=null"><text>不限</text></view>
              <view :class="['sc',{on:filterGender===1}]" @tap="filterGender=1"><text>男生</text></view>
              <view :class="['sc',{on:filterGender===2}]" @tap="filterGender=2"><text>女生</text></view>
            </view>
          </view>
          <view class="sg">
            <text class="sl">年龄范围</text>
            <view class="sc-row">
              <view :class="['sc',{on:filterAge===null}]" @tap="filterAge=null"><text>不限</text></view>
              <view :class="['sc',{on:filterAge===`18-25`}]" @tap="filterAge='18-25'"><text>18-25</text></view>
              <view :class="['sc',{on:filterAge===`25-30`}]" @tap="filterAge='25-30'"><text>25-30</text></view>
              <view :class="['sc',{on:filterAge===`30-40`}]" @tap="filterAge='30-40'"><text>30-40</text></view>
            </view>
          </view>
          <view class="sa">
            <view class="apple-btn primary" @tap="applyFilters"><text>完成</text></view>
          </view>
        </scroll-view>
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

const displayPhotos = computed(() => {
  if (!currentCard.value) return []
  if (currentCard.value.all_photos && currentCard.value.all_photos.length > 0) {
    return currentCard.value.all_photos
  }
  if (currentCard.value.photos && currentCard.value.photos.length > 0) {
    return currentCard.value.photos.map((p: any) => typeof p === 'string' ? {url: p} : p)
  }
  return [{ url: currentCard.value.avatar_url || defaultAvatar }]
})

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
  // 苹果风格的弹性过渡动画 (Spring-like transition)
  const transition = isSwiping.value ? 'none' : 'all 0.5s cubic-bezier(0.32, 0.72, 0, 1)'
  return `transform:translate(${cardOffsetX.value}px, ${cardOffsetY.value}px) rotate(${cardRotate.value}deg) scale(${isSwiping.value ? 0.98 : 1}); opacity:${cardOpacity.value}; transition:${transition};`
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
  
  // 上滑超过一定距离，展开详情 (增加一点阻尼感)
  if (!isSwiping.value && dy < -40 && Math.abs(dy) > Math.abs(dx)) {
    toggleDetail()
    return
  }

  if (!isSwiping.value && Math.abs(dx) > 10 && Math.abs(dx) > Math.abs(dy)) {
    isSwiping.value = true
  }
  if (isSwiping.value) { 
    // 加入阻尼效果，让滑动感觉更有重量
    const dampening = 0.8
    cardOffsetX.value = dx * dampening
    cardRotate.value = (dx * 0.03) * dampening
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
  setTimeout(() => { handleLike(); resetCard() }, 400) // 延长一点以配合 spring 动画
}

function animateSkip() { 
  if (isAnimating.value) return
  isAnimating.value = true
  showDetail.value = false
  cardOffsetX.value = -500
  cardRotate.value = -15
  cardOpacity.value = 0
  setTimeout(() => { handleSkip(); resetCard() }, 400) 
}

function handleLater() {
  if (isAnimating.value) return
  isAnimating.value = true
  showDetail.value = false
  cardOffsetY.value = 800 // 向下滑出屏幕
  cardOpacity.value = 0
  setTimeout(() => {
    currentIndex.value++
    showNext()
    resetCard()
  }, 400)
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
    uni.showToast({ title: `今日喜欢额度已用完`, icon: 'none', duration: 2500 })
    return
  }
  let isMatch = false
  try {
    const r = await matchApi.swipe(currentCard.value.user_id, true)
    if (dailyRemaining.value > 0) dailyRemaining.value--
    if (r.data.is_match) { 
      matchedId.value = r.data.match_id
      showMatchModal.value = true 
      isMatch = true
    }
  } catch (e: any) {
    if (e?.statusCode === 429 || e?.message?.includes('上限')) {
      dailyRemaining.value = 0
      uni.showToast({ title: '今日喜欢次数已用完', icon: 'none' })
      return // 阻止卡片滑走
    }
  }
  currentIndex.value++
  showNext()
}

async function handleSkip() {
  if (!currentCard.value) return
  try { 
    await matchApi.swipe(currentCard.value.user_id, false)
  } catch {}
  currentIndex.value++
  showNext() 
}

function reportUser() {
  const uid = currentCard.value?.user_id
  if (!uid) return
  uni.showModal({ 
    title: '举报', content: '确定举报该用户？', confirmColor: '#FF3B30', 
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
    title: '拉黑', content: '拉黑后将不再向您推荐此人', confirmColor: '#FF3B30', 
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
  const u = displayPhotos.value.map(p => p.url)
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
/* 全局页面背景：Apple Secondary System Background */
.page { 
  height: 100vh; 
  background: #F2F2F7; 
  display: flex; 
  flex-direction: column; 
  overflow: hidden; 
  box-sizing: border-box; 
  padding-bottom: calc(env(safe-area-inset-bottom) + 100rpx); 
  font-family: -apple-system, BlinkMacSystemFont, "SF Pro Text", "Helvetica Neue", Helvetica, Arial, sans-serif;
}
/* #ifdef H5 */
.page { padding-bottom: 50px; }
/* #endif */

/* ====== 毛玻璃通用样式 (Apple Glassmorphism) ====== */
.glass-morphism {
  background: rgba(255, 255, 255, 0.65);
  backdrop-filter: blur(24px);
  -webkit-backdrop-filter: blur(24px);
  border: 0.5px solid rgba(255, 255, 255, 0.4);
}
.glass-morphism-light {
  background: rgba(255, 255, 255, 0.3);
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
  border: 0.5px solid rgba(255, 255, 255, 0.2);
}

/* ====== 顶部导航栏 (Apple Large Title) ====== */
.nav { 
  padding: 0 32rpx 16rpx; 
  position: relative; 
  z-index: 10; 
  flex-shrink: 0; 
  transition: opacity 0.3s, transform 0.3s;
}
.nav-hidden { opacity: 0; transform: translateY(-20rpx); pointer-events: none; }
.nav-content { display: flex; align-items: flex-end; justify-content: space-between; height: 88rpx; }
.nav-title { font-size: 64rpx; font-weight: 800; color: #000000; letter-spacing: -2rpx; line-height: 1; }
.nav-right { display: flex; align-items: center; gap: 16rpx; margin-bottom: 4rpx; }

.glass-pill { 
  display: flex; align-items: center; gap: 8rpx; padding: 12rpx 24rpx; 
  border-radius: 40rpx; 
  background: #FFFFFF; 
  box-shadow: 0 4rpx 12rpx rgba(0,0,0,0.04);
}
.quota-heart { font-size: 24rpx; }
.quota-num { font-size: 26rpx; color: #000; font-weight: 700; font-variant-numeric: tabular-nums; }

.glass-circle { 
  width: 64rpx; height: 64rpx; 
  border-radius: 50%; 
  background: #FFFFFF; 
  box-shadow: 0 4rpx 12rpx rgba(0,0,0,0.04); 
  display: flex; align-items: center; justify-content: center; 
}

/* ====== 卡片容器与主卡片 (Large Squircles) ====== */
.card-wrap {
  flex: 1;
  position: relative;
  z-index: 5;
  padding: 0 16rpx; /* 外层留白 */
}

.card { 
  position: absolute;
  top: 0; left: 16rpx; right: 16rpx; bottom: 16rpx;
  border-radius: 48rpx; /* Apple 风格的大圆角 */
  background: #FFFFFF;
  overflow: hidden; 
  will-change: transform, opacity; 
  box-shadow: 0 16rpx 48rpx rgba(0,0,0,0.06), 0 2rpx 8rpx rgba(0,0,0,0.04); /* 弥散多重阴影 */
}
.card.is-expanded {
  top: -88rpx; /* 盖住导航栏 */
  left: 0; right: 0; bottom: -100rpx; 
  border-radius: 0;
  z-index: 100;
}
/* #ifdef H5 */
.card.is-expanded { bottom: -50px; }
/* #endif */

.card-scroll { width: 100%; height: 100%; }

/* ====== 英雄区域 (照片) ====== */
.hero-area {
  position: relative;
  width: 100%;
  height: 60vh;
  background: #E5E5EA; /* 骨架加载时的颜色 */
  transition: height 0.5s cubic-bezier(0.32, 0.72, 0, 1);
  overflow: hidden;
}
.card.is-expanded .hero-area {
  height: 65vh;
}
.hero-swiper { width: 100%; height: 100%; }
.hero-bg { position: absolute; top: 0; left: 0; width: 100%; height: 100%; }
.hero-fade { 
  position: absolute; bottom: 0; left: 0; right: 0; height: 360rpx; 
  background: linear-gradient(to bottom, rgba(0,0,0,0) 0%, rgba(0,0,0,0.4) 50%, rgba(0,0,0,0.7) 100%); 
  pointer-events: none; 
}

/* ====== 用户头部信息 (悬浮毛玻璃) ====== */
.hero-user-info {
  position: absolute;
  bottom: 40rpx;
  left: 32rpx;
  right: 32rpx;
  display: flex;
  align-items: center;
  gap: 24rpx;
  z-index: 10;
}
.hu-avatar-container { position: relative; flex-shrink: 0; }
.hu-avatar {
  width: 140rpx; height: 140rpx;
  border-radius: 50%;
  border: 4rpx solid #FFFFFF;
  background: #FFFFFF;
}
.hu-online-badge {
  position: absolute; bottom: 8rpx; right: 8rpx;
  width: 24rpx; height: 24rpx;
  border-radius: 50%;
  background: #34C759; /* Apple Green */
  border: 4rpx solid #FFFFFF;
}

.hu-details { flex: 1; display: flex; flex-direction: column; justify-content: center; }
.hu-name-row { display: flex; align-items: center; gap: 12rpx; margin-bottom: 12rpx; }
.hu-name { font-size: 52rpx; font-weight: 800; color: #FFFFFF; letter-spacing: 1rpx; text-shadow: 0 4rpx 16rpx rgba(0,0,0,0.2); }
.hu-verified { 
  width: 36rpx; height: 36rpx; border-radius: 50%; background: #007AFF; color: #FFFFFF; 
  display: flex; align-items: center; justify-content: center; 
}
.hu-verified text { font-size: 22rpx; font-weight: 800; }

.hu-meta { 
  display: inline-flex; align-items: center; 
  padding: 12rpx 28rpx; border-radius: 32rpx; gap: 12rpx; 
}
.hu-meta text { color: #1C1C1E; font-size: 24rpx; font-weight: 600; }
.divider { color: rgba(0,0,0,0.3) !important; font-size: 24rpx; }
.text-ellipsis { white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }

/* ====== 悬浮滑动标签 ====== */
.swipe-tag { position: absolute; top: 120rpx; z-index: 50; padding: 12rpx 40rpx; border-radius: 16rpx; border: 8rpx solid; font-size: 64rpx; font-weight: 900; letter-spacing: 4rpx; pointer-events: none; }
.like-tag { left: 40rpx; color: #34C759; border-color: #34C759; transform: rotate(-15deg); }
.nope-tag { right: 40rpx; color: #FF3B30; border-color: #FF3B30; transform: rotate(15deg); }

.close-btn {
  position: absolute;
  right: 32rpx;
  width: 72rpx; height: 72rpx;
  border-radius: 50%;
  display: flex; align-items: center; justify-content: center;
  z-index: 20;
}

/* ====== 资料内容区 ====== */
.profile-body {
  background: #FFFFFF;
  padding: 40rpx 140rpx 80rpx 32rpx; /* 右侧留白给悬浮按钮 */
  min-height: 40vh;
}

.pb-section { margin-bottom: 40rpx; }

/* 契合度 */
.pb-compat { 
  display: flex; align-items: flex-start; gap: 16rpx;
  padding: 24rpx; background: #FFF5F7; border-radius: 24rpx; 
}
.compat-icon { font-size: 32rpx; margin-top: 4rpx; }
.compat-text-group { display: flex; flex-direction: column; gap: 6rpx; }
.compat-title { font-size: 28rpx; color: #FF2D55; font-weight: 700; }
.compat-desc { font-size: 26rpx; color: #FF2D55; opacity: 0.8; line-height: 1.4; }

/* 兴趣标签 */
.pb-tags { display: flex; flex-wrap: wrap; gap: 16rpx; }
.tag-capsule {
  padding: 14rpx 32rpx; border-radius: 40rpx; font-size: 26rpx; font-weight: 600; 
  display: inline-flex; align-items: center; gap: 10rpx;
}
.tag-primary {
  background: linear-gradient(135deg, #FF2D55, #FF375F); color: #FFFFFF; 
  box-shadow: 0 4rpx 12rpx rgba(255,45,85,0.25);
}
.tag-secondary { background: #F2F2F7; color: #1C1C1E; }
.tag-icon { font-size: 26rpx; }

/* 关于我与标题 */
.apple-section-title { font-size: 34rpx; color: #000000; font-weight: 700; margin-bottom: 20rpx; display: block; letter-spacing: -0.5rpx; }
.bio-text { font-size: 30rpx; color: #3A3A3C; line-height: 1.6; font-weight: 400; }
.line-clamp-3 { display: -webkit-box; -webkit-line-clamp: 3; -webkit-box-orient: vertical; overflow: hidden; }

/* ====== 详细资料 (展开后) ====== */
.pb-extended {
  margin-top: 48rpx;
  margin-right: -108rpx; /* 抵消右侧留白，让卡片占满宽度 */
}
.apple-card {
  background: #F2F2F7;
  margin-bottom: 32rpx;
  padding: 32rpx;
  border-radius: 32rpx;
}
.d-grid { display: flex; flex-wrap: wrap; gap: 16rpx; }
.d-item { padding: 14rpx 28rpx; background: #FFFFFF; border-radius: 32rpx; font-size: 26rpx; color: #1C1C1E; font-weight: 500; display: flex; gap: 12rpx; box-shadow: 0 2rpx 8rpx rgba(0,0,0,0.02); }

.d-photos { display: flex; flex-wrap: wrap; gap: 16rpx; }
.d-photo { width: calc(33.33% - 11rpx); height: 240rpx; border-radius: 24rpx; }

/* Destructive Actions */
.d-actions-link { display: flex; flex-direction: column; align-items: center; gap: 32rpx; margin-top: 80rpx; margin-bottom: 60rpx; padding-right: 108rpx; }
.d-link { font-size: 30rpx; font-weight: 600; padding: 20rpx 0; }
.destructive { color: #FF3B30; }
.detail-bottom-space { height: 120rpx; }

/* ====== 向上滑动指示 ====== */
.body-fade-out {
  position: absolute;
  bottom: 0; left: 0; right: 0;
  height: 140rpx;
  background: linear-gradient(to bottom, rgba(255,255,255,0) 0%, rgba(255,255,255,1) 80%);
  display: flex; align-items: flex-end; justify-content: center;
  padding-bottom: 24rpx;
  z-index: 20;
}
.expand-hint { 
  padding: 12rpx 32rpx; border-radius: 40rpx; 
}
.expand-hint text { font-size: 24rpx; color: #1C1C1E; font-weight: 600; }

/* ====== 右侧悬浮操作栏 (Apple Layout & SVG Icons) ====== */
.right-actions {
  position: absolute;
  right: 24rpx;
  bottom: 200rpx;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 32rpx;
  z-index: 100;
  transition: all 0.4s cubic-bezier(0.32, 0.72, 0, 1);
}
.right-actions.actions-expanded {
  bottom: 100rpx;
  transform: scale(0.9);
  opacity: 0.5;
}
.r-btn {
  width: 96rpx; height: 96rpx;
  border-radius: 50%;
  display: flex; align-items: center; justify-content: center;
  transition: transform 0.2s cubic-bezier(0.25, 0.1, 0.25, 1);
  box-shadow: 0 8rpx 32rpx rgba(0,0,0,0.1);
}
.r-btn:active { transform: scale(0.85); }
.r-btn.like { width: 120rpx; height: 120rpx; margin: 10rpx 0; } 
.primary-pop { border: 2rpx solid #FF2D55; }

/* ====== 骨架与空状态 ====== */
.sk { flex: 1; margin: 0 16rpx 16rpx; border-radius: 48rpx; overflow: hidden; }
.sk-card { width: 100%; height: 100%; }
@keyframes shimmer { 0%{background-position:-200% 0} 100%{background-position:200% 0} }
.shimmer { background: linear-gradient(90deg,#E5E5EA 25%,#F2F2F7 50%,#E5E5EA 75%); background-size: 200% 100%; animation: shimmer 1.4s infinite; }

.empty { flex: 1; display: flex; flex-direction: column; align-items: center; justify-content: center; padding: 0 60rpx; background: #F2F2F7; }
.empty-ring { width: 160rpx; height: 160rpx; border-radius: 50%; background: #FFFFFF; box-shadow: 0 16rpx 48rpx rgba(0,0,0,0.06); display: flex; align-items: center; justify-content: center; margin-bottom: 40rpx; font-size: 64rpx; }
.empty-t { font-size: 40rpx; font-weight: 800; color: #000; margin-bottom: 16rpx; letter-spacing: -0.5rpx; }
.empty-s { font-size: 30rpx; color: #8E8E93; margin-bottom: 60rpx; text-align: center; line-height: 1.5; }
.apple-btn { padding: 28rpx 80rpx; border-radius: 60rpx; background: #000000; color: #FFFFFF; font-size: 32rpx; font-weight: 700; box-shadow: 0 16rpx 32rpx rgba(0,0,0,0.15); transition: transform 0.2s; }
.apple-btn:active { transform: scale(0.95); }
.apple-btn.primary { background: #FF2D55; width: 100%; text-align: center; box-shadow: 0 16rpx 32rpx rgba(255,45,85,0.3); }

/* ====== 苹果底部弹窗 (Bottom Sheet) ====== */
.mask { position: fixed; top: 0; left: 0; right: 0; bottom: 0; background: rgba(0,0,0,0.4); z-index: 200; display: flex; align-items: flex-end; }
.sheet { width: 100%; background: #FFFFFF; border-radius: 48rpx 48rpx 0 0; padding: 24rpx 40rpx calc(40rpx + env(safe-area-inset-bottom)); position: relative; }
/* #ifdef H5 */
.sheet { padding-bottom: calc(80px + env(safe-area-inset-bottom)); }
/* #endif */
.sheet-scroll { max-height: 60vh; }
.sheet-handle { width: 80rpx; height: 10rpx; border-radius: 10rpx; background: #E5E5EA; margin: 0 auto 32rpx; }
.sheet-top { display: flex; justify-content: space-between; align-items: center; margin-bottom: 48rpx; }
.sh { font-size: 40rpx; font-weight: 800; color: #000000; }
.sr { font-size: 32rpx; color: #FF2D55; font-weight: 600; }
.sg { margin-bottom: 40rpx; }
.sl { font-size: 30rpx; color: #000000; margin-bottom: 24rpx; display: block; font-weight: 700; }
.sc-row { display: flex; gap: 20rpx; flex-wrap: wrap; }
.sc { padding: 16rpx 40rpx; border-radius: 40rpx; background: #F2F2F7; font-size: 30rpx; color: #1C1C1E; font-weight: 600; }
.sc.on { background: #000000; color: #FFFFFF; }
.sa { padding-top: 32rpx; padding-bottom: 20rpx; }
</style>