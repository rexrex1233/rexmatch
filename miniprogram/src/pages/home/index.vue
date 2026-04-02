<template>
  <view class="page">
    <!-- 导航栏 -->
    <view class="nav" :style="{ paddingTop: statusBarHeight + 'px' }">
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

    <!-- 固定全屏卡片 -->
    <view
      class="card"
      v-if="currentCard && !loading"
      :style="cardStyle"
      @touchstart="onTouchStart"
      @touchmove="onTouchMove"
      @touchend="onTouchEnd"
      @tap="goDetail"
    >
      <!-- 滑动标签 -->
      <view class="swipe-tag like-tag" :style="{ opacity: likeOp }"><text>LIKE</text></view>
      <view class="swipe-tag nope-tag" :style="{ opacity: nopeOp }"><text>NOPE</text></view>

      <!-- 背景图 / 无照片降级 -->
      <image v-if="hasRealPhoto" class="card-bg" :src="currentCard.avatar_url" mode="aspectFill" />
      <view v-else class="card-bg-fallback">
        <view class="fb-ring">
          <image class="fb-avatar" :src="currentCard.avatar_url || defaultAvatar" mode="aspectFill" />
        </view>
      </view>

      <!-- 渐变遮罩 -->
      <view class="card-overlay"></view>

      <!-- 照片数量 -->
      <view class="photo-num" v-if="currentCard.photos?.length > 1">
        <text>📷 {{ currentCard.photos.length }}</text>
      </view>

      <!-- 菜单 -->
      <view class="card-menu" @tap.stop="showActionSheet"><text>···</text></view>

      <!-- 底部信息 -->
      <view class="card-info">
        <view class="info-top">
          <text class="info-name">{{ currentCard.nickname }}</text>
          <view class="info-age" v-if="currentCard.age"><text>{{ currentCard.age }}</text></view>
          <view class="info-online" v-if="currentCard.is_online"><text>在线</text></view>
        </view>

        <view class="info-tags">
          <view class="itag" v-if="currentCard.education"><text>{{ currentCard.education }}</text></view>
          <view class="itag" v-if="currentCard.city"><text>📍 {{ currentCard.city }}</text></view>
          <view class="itag" v-if="currentCard.occupation"><text>💼 {{ currentCard.occupation }}</text></view>
        </view>

        <text class="info-bio" v-if="currentCard.bio">{{ currentCard.bio }}</text>

        <!-- 兴趣标签 -->
        <view class="info-interests" v-if="currentCard.interests?.length">
          <view class="interest" v-for="(t, i) in currentCard.interests.slice(0, 5)" :key="i"><text>{{ t }}</text></view>
          <view class="interest more" v-if="currentCard.interests.length > 5"><text>+{{ currentCard.interests.length - 5 }}</text></view>
        </view>

        <!-- 契合度 -->
        <view class="info-compat" v-if="currentCard.compatibility && currentCard.compatibility.score > 0">
          <text class="compat-icon">♥</text>
          <text class="compat-txt">{{ currentCard.compatibility.score }} 项契合</text>
        </view>

        <text class="info-hint">点击查看详情</text>
      </view>
    </view>

    <!-- 空状态 -->
    <view class="empty" v-if="!currentCard && !loading">
      <view class="empty-ring"><text>💫</text></view>
      <text class="empty-t">暂时没有更多推荐</text>
      <text class="empty-s">完善资料或调整偏好获得更多推荐</text>
      <view class="empty-btn" @tap="goEditProfile"><text>完善资料</text></view>
    </view>

    <!-- 底部操作栏 -->
    <view class="bar" v-if="currentCard && !loading">
      <view class="bar-btn skip" @tap.stop="animateSkip"><text class="bar-ico">✕</text></view>
      <view class="bar-btn like" @tap.stop="animateLike"><text class="bar-ico">♥</text></view>
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
const isAnimating = ref(false)
const dailyRemaining = ref(-1)
const dailyLimit = ref(10)

const hasRealPhoto = computed(() => {
  const url = currentCard.value?.avatar_url || ''
  return url && !url.includes('dicebear') && !url.includes('svg')
})

const touchStartX = ref(0)
const touchStartY = ref(0)
const isSwiping = ref(false)
const cardOffsetX = ref(0)
const cardRotate = ref(0)
const cardOpacity = ref(1)
const THRESHOLD = 80

const likeOp = computed(() => Math.min(Math.max(cardOffsetX.value / THRESHOLD, 0), 1))
const nopeOp = computed(() => Math.min(Math.max(-cardOffsetX.value / THRESHOLD, 0), 1))
const cardStyle = computed(() => {
  if (cardOffsetX.value === 0 && cardOpacity.value === 1) return ''
  return `transform:translateX(${cardOffsetX.value}px) rotate(${cardRotate.value}deg);opacity:${cardOpacity.value};transition:${isSwiping.value ? 'none' : 'all .3s cubic-bezier(.4,0,.2,1)'};`
})

onMounted(() => {
  statusBarHeight.value = uni.getSystemInfoSync().statusBarHeight || 44
  loadRecommendations()
  fetchDailyLikes()
})
onShow(() => { if (!loading.value && cards.value.length === 0) loadRecommendations() })

function onTouchStart(e: any) {
  if (isAnimating.value) return
  touchStartX.value = e.touches[0].clientX
  touchStartY.value = e.touches[0].clientY
  isSwiping.value = false
}
function onTouchMove(e: any) {
  if (isAnimating.value) return
  const dx = e.touches[0].clientX - touchStartX.value
  const dy = e.touches[0].clientY - touchStartY.value
  if (!isSwiping.value && Math.abs(dx) > 10 && Math.abs(dx) > Math.abs(dy)) isSwiping.value = true
  if (isSwiping.value) { cardOffsetX.value = dx; cardRotate.value = dx * 0.04 }
}
function onTouchEnd() {
  if (!isSwiping.value) { cardOffsetX.value = 0; cardRotate.value = 0; return }
  isSwiping.value = false
  if (cardOffsetX.value > THRESHOLD) animateLike()
  else if (cardOffsetX.value < -THRESHOLD) animateSkip()
  else { cardOffsetX.value = 0; cardRotate.value = 0 }
}

function animateLike() { if (isAnimating.value) return; isAnimating.value = true; isSwiping.value = false; cardOffsetX.value = 500; cardRotate.value = 15; cardOpacity.value = 0; setTimeout(() => { handleLike(); resetCard() }, 300) }
function animateSkip() { if (isAnimating.value) return; isAnimating.value = true; isSwiping.value = false; cardOffsetX.value = -500; cardRotate.value = -15; cardOpacity.value = 0; setTimeout(() => { handleSkip(); resetCard() }, 300) }
function resetCard() { isSwiping.value = true; cardOffsetX.value = 0; cardRotate.value = 0; cardOpacity.value = 1; setTimeout(() => { isSwiping.value = false; isAnimating.value = false }, 50) }

async function loadRecommendations() {
  loading.value = true
  try {
    const p: any = {}
    if (filterGender.value) p.gender = filterGender.value
    if (filterAge.value) { const [a, b] = filterAge.value.split('-').map(Number); p.min_age = a; p.max_age = b }
    const res = await discoverApi.getRecommendations(p)
    cards.value = res.data || []; currentIndex.value = 0; showNext()
  } catch (e) { console.error(e) } finally { loading.value = false }
}

function showNext() { currentCard.value = currentIndex.value < cards.value.length ? cards.value[currentIndex.value] : null }

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
    uni.showToast({ title: `今日 ${dailyLimit.value} 次喜欢已用完，明天再来`, icon: 'none', duration: 2500 })
    return
  }
  try {
    const r = await matchApi.swipe(currentCard.value.user_id, true)
    if (dailyRemaining.value > 0) dailyRemaining.value--
    if (r.data.is_match) { matchedId.value = r.data.match_id; showMatchModal.value = true }
    currentIndex.value++; showNext()
  } catch (e: any) {
    if (e?.statusCode === 429 || e?.message?.includes('上限')) {
      dailyRemaining.value = 0
      uni.showToast({ title: '今日喜欢次数已用完', icon: 'none' })
    }
  }
}
async function handleSkip() {
  if (!currentCard.value) return
  try { await matchApi.swipe(currentCard.value.user_id, false); currentIndex.value++; showNext() } catch {}
}

function goDetail() {
  if (isSwiping.value || isAnimating.value || !currentCard.value) return
  uni.navigateTo({ url: `/pages/user-detail/index?userId=${currentCard.value.user_id}` })
}

function showActionSheet() {
  const uid = currentCard.value?.user_id
  if (!uid) return
  uni.showActionSheet({ itemList: ['举报该用户', '拉黑该用户'], success(res) {
    if (res.tapIndex === 0) uni.showModal({ title: '举报用户', content: '确定举报？', confirmColor: '#ff4757', success(r) { if (r.confirm) reportApi.submit(uid, '不当行为').then(() => { uni.showToast({ title: '已举报', icon: 'success' }); currentIndex.value++; showNext() }) } })
    else uni.showModal({ title: '拉黑用户', content: '拉黑后不再看到对方', confirmColor: '#ff4757', success(r) { if (r.confirm) reportApi.block(uid).then(() => { uni.showToast({ title: '已拉黑', icon: 'success' }); currentIndex.value++; showNext() }) } })
  }})
}

function previewPhotos(i: number) { const u = currentCard.value?.photos || []; if (u.length) uni.previewImage({ urls: u, current: u[i] || u[0] }) }
function closeMatchModal() { showMatchModal.value = false }
function goToChat() { showMatchModal.value = false; if (matchedId.value) uni.navigateTo({ url: `/pages/chat-detail/index?matchId=${matchedId.value}` }) }
function goEditProfile() { uni.navigateTo({ url: '/pages/edit-profile/index' }) }
function resetFilters() { filterGender.value = null; filterAge.value = null }
function applyFilters() { showFilterPanel.value = false; loadRecommendations() }
</script>

<style scoped>
.page { height: 100vh; background: #111; display: flex; flex-direction: column; overflow: hidden; box-sizing: border-box; padding-bottom: calc(env(safe-area-inset-bottom) + 100rpx); }
/* #ifdef H5 */
.page { padding-bottom: 50px; }
/* #endif */

/* 导航 */
.nav { display: flex; align-items: center; justify-content: space-between; height: 88rpx; padding: 0 32rpx; background: #fff; position: relative; z-index: 10; flex-shrink: 0; }
.nav-title { font-size: 36rpx; font-weight: 800; color: #1a1a1a; }
.nav-right { display: flex; align-items: center; gap: 16rpx; }
.like-quota { display: flex; align-items: center; gap: 4rpx; padding: 6rpx 18rpx; border-radius: 20rpx; background: rgba(255,107,129,0.1); }
.quota-heart { font-size: 22rpx; color: #ff6b81; }
.quota-num { font-size: 24rpx; color: #ff4757; font-weight: 700; }
.nav-btn { width: 56rpx; height: 56rpx; border-radius: 50%; background: #f5f5f5; display: flex; align-items: center; justify-content: center; font-size: 26rpx; color: #888; }

/* 骨架 */
.sk { flex: 1; margin: 16rpx; border-radius: 24rpx; overflow: hidden; }
.sk-card { width: 100%; height: 100%; }
@keyframes shimmer { 0%{background-position:-200% 0} 100%{background-position:200% 0} }
.shimmer { background: linear-gradient(90deg,#222 25%,#333 50%,#222 75%); background-size: 200% 100%; animation: shimmer 1.4s infinite; }

/* 卡片 - 固定全屏 */
.card { flex: 1; margin: 12rpx 16rpx; border-radius: 24rpx; position: relative; overflow: hidden; will-change: transform, opacity; }
.card-bg { position: absolute; top: 0; left: 0; width: 100%; height: 100%; }

/* 无照片降级 */
.card-bg-fallback { position: absolute; top: 0; left: 0; width: 100%; height: 100%; background: linear-gradient(160deg, #667eea 0%, #764ba2 50%, #f093fb 100%); display: flex; align-items: center; justify-content: center; }
.fb-ring { width: 240rpx; height: 240rpx; border-radius: 50%; padding: 8rpx; background: rgba(255,255,255,0.25); }
.fb-avatar { width: 100%; height: 100%; border-radius: 50%; }

/* 遮罩 */
.card-overlay { position: absolute; bottom: 0; left: 0; right: 0; height: 65%; background: linear-gradient(0deg, rgba(0,0,0,0.7) 0%, rgba(0,0,0,0.3) 50%, transparent 100%); z-index: 2; pointer-events: none; }

.photo-num { position: absolute; top: 20rpx; left: 20rpx; padding: 6rpx 16rpx; border-radius: 16rpx; background: rgba(0,0,0,0.45); font-size: 22rpx; color: #fff; z-index: 5; }
.card-menu { position: absolute; top: 20rpx; right: 20rpx; width: 56rpx; height: 56rpx; border-radius: 50%; background: rgba(0,0,0,0.35); display: flex; align-items: center; justify-content: center; color: #fff; font-size: 28rpx; font-weight: bold; z-index: 5; }

/* 滑动标签 */
.swipe-tag { position: absolute; top: 50%; margin-top: -60rpx; z-index: 10; padding: 10rpx 36rpx; border-radius: 12rpx; border: 6rpx solid; font-size: 48rpx; font-weight: 900; letter-spacing: 4rpx; pointer-events: none; }
.like-tag { left: 40rpx; color: #07c160; border-color: #07c160; transform: rotate(-15deg); }
.nope-tag { right: 40rpx; color: #ff4757; border-color: #ff4757; transform: rotate(15deg); }

/* 底部信息 */
.card-info { position: absolute; bottom: 0; left: 0; right: 0; padding: 0 32rpx 32rpx; z-index: 3; }

.info-top { display: flex; align-items: center; gap: 14rpx; margin-bottom: 12rpx; }
.info-name { font-size: 44rpx; font-weight: 800; color: #fff; }
.info-age { width: 56rpx; height: 56rpx; border-radius: 50%; background: rgba(255,107,129,0.85); display: flex; align-items: center; justify-content: center; font-size: 24rpx; color: #fff; font-weight: 700; }
.info-online { padding: 4rpx 16rpx; border-radius: 16rpx; background: rgba(7,193,96,0.85); font-size: 20rpx; color: #fff; font-weight: 600; }

.info-tags { display: flex; flex-wrap: wrap; gap: 10rpx; margin-bottom: 14rpx; }
.itag { padding: 6rpx 18rpx; border-radius: 16rpx; background: rgba(255,255,255,0.2); backdrop-filter: blur(4px); font-size: 22rpx; color: rgba(255,255,255,0.9); }

.info-bio { font-size: 26rpx; color: rgba(255,255,255,0.8); line-height: 1.6; display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden; margin-bottom: 14rpx; display: block; }

.info-interests { display: flex; flex-wrap: wrap; gap: 8rpx; margin-bottom: 14rpx; }
.interest { padding: 6rpx 16rpx; border-radius: 14rpx; background: rgba(255,255,255,0.15); font-size: 22rpx; color: rgba(255,255,255,0.85); }
.interest.more { background: rgba(255,107,129,0.5); }

.info-compat { display: flex; align-items: center; gap: 8rpx; margin-bottom: 12rpx; }
.compat-icon { font-size: 22rpx; color: #ff6b81; }
.compat-txt { font-size: 24rpx; color: #ff6b81; font-weight: 600; }

.info-hint { font-size: 22rpx; color: rgba(255,255,255,0.4); text-align: center; display: block; }

/* 底部操作栏 */
.bar { flex-shrink: 0; display: flex; justify-content: center; gap: 80rpx; padding: 16rpx 0 20rpx; background: #fff; }
.bar-btn { width: 108rpx; height: 108rpx; border-radius: 50%; display: flex; align-items: center; justify-content: center; transition: transform 0.15s; }
.bar-btn:active { transform: scale(0.88); }
.bar-btn.skip { background: #fff; border: 3rpx solid #e8e8e8; box-shadow: 0 2rpx 12rpx rgba(0,0,0,0.06); }
.bar-btn.skip .bar-ico { font-size: 40rpx; color: #ccc; }
.bar-btn.like { background: linear-gradient(135deg, #ff6b81, #ff4757); box-shadow: 0 6rpx 24rpx rgba(255,71,87,0.35); }
.bar-btn.like .bar-ico { font-size: 44rpx; color: #fff; }

/* 空状态 */
.empty { flex: 1; display: flex; flex-direction: column; align-items: center; justify-content: center; padding: 0 60rpx; background: #f7f8fa; }
.empty-ring { width: 140rpx; height: 140rpx; border-radius: 50%; background: linear-gradient(135deg, #fff0f3, #ffe0e6); display: flex; align-items: center; justify-content: center; margin-bottom: 28rpx; font-size: 56rpx; }
.empty-t { font-size: 32rpx; font-weight: 700; color: #1a1a1a; margin-bottom: 10rpx; }
.empty-s { font-size: 26rpx; color: #b3b3b3; margin-bottom: 36rpx; text-align: center; }
.empty-btn { padding: 20rpx 56rpx; border-radius: 40rpx; background: linear-gradient(135deg, #ff6b81, #ff4757); box-shadow: 0 8rpx 24rpx rgba(255,71,87,0.3); color: #fff; font-size: 28rpx; font-weight: 600; }

/* 筛选 */
.mask { position: fixed; top: 0; left: 0; right: 0; bottom: 0; background: rgba(0,0,0,0.4); z-index: 200; display: flex; align-items: flex-end; }
.sheet { width: 100%; background: #fff; border-radius: 24rpx 24rpx 0 0; padding: 28rpx 32rpx calc(28rpx + env(safe-area-inset-bottom)); }
.sheet-top { display: flex; justify-content: space-between; align-items: center; margin-bottom: 28rpx; }
.sh { font-size: 30rpx; font-weight: 700; color: #1a1a1a; }
.sr { font-size: 26rpx; color: #ff6b81; }
.sg { margin-bottom: 24rpx; }
.sl { font-size: 24rpx; color: #999; margin-bottom: 14rpx; display: block; }
.sc-row { display: flex; gap: 14rpx; flex-wrap: wrap; }
.sc { padding: 12rpx 28rpx; border-radius: 28rpx; background: #f0f1f5; font-size: 26rpx; color: #666; }
.sc.on { background: rgba(255,107,129,0.1); color: #ff4757; font-weight: 600; }
.sa { padding-top: 12rpx; }
.sbtn { width: 100%; height: 84rpx; background: linear-gradient(135deg, #ff6b81, #ff4757); border-radius: 42rpx; display: flex; align-items: center; justify-content: center; color: #fff; font-size: 30rpx; font-weight: 600; }
</style>
