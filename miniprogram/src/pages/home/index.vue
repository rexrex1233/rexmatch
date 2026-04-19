<template>
  <view class="page">
    <!-- 苹果风格大标题导航栏 -->
    <view class="nav" :style="{ paddingTop: statusBarHeight + 'px' }" :class="{ 'nav-hidden': showDetail }">
      <view class="nav-content">
        <text class="nav-title">推荐</text>
        <view class="nav-right">
          <view class="glass-circle guide-btn" @tap="openGuide">
            <text class="guide-btn-icon">?</text>
          </view>
          <view class="glass-pill" v-if="dailyRemaining >= 0">
            <text class="quota-heart">💖</text>
            <text class="quota-num">{{ dailyRemaining }}</text>
          </view>
          <view class="glass-circle" @tap="showFilterPanel = true">
            <text class="nav-icon">⊜</text>
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
      
      <!-- 背面的下一张叠放卡片 -->
      <view class="card next-card" :style="nextCardStyle" v-if="nextCard">
        <image class="hero-bg blur-bg" :src="nextCardAvatar" mode="aspectFill" />
        <view class="hero-fade" pointer-events="none"></view>
      </view>

      <view
        class="card active-card"
        :class="{ 'is-expanded': showDetail }"
        :style="cardStyle"
      >
        <!-- 拦截层：解决微信小程序 scroll-view 吞噬手势的终极方案 -->
        <view class="gesture-mask" v-if="!showDetail"
          @touchstart="onHeroTouchStart"
          @touchmove.stop="onHeroTouchMove"
          @touchend="onHeroTouchEnd"
        >
          <!-- 触控区搬迁至遮罩层 -->
          <view class="tap-zones">
            <view class="t-left" @tap.stop="prevPhoto"></view>
            <view class="t-center" @tap.stop="toggleDetail"></view>
            <view class="t-right" @tap.stop="nextPhoto"></view>
          </view>
        </view>

        <!-- 滚动视图 (展开时可滚动) -->
        <scroll-view 
          class="card-scroll" 
          :scroll-y="showDetail" 
          :show-scrollbar="false"
        >
          <!-- 英雄区域 (照片墙与绝赞分段指示器) -->
          <view class="hero-area">
            <!-- 动态渲染单张封面，比 swiper 具有更高的响应度 -->
            <transition name="fade-photo">
              <image :key="currentPhotoIndex" class="hero-bg" :src="displayPhotos[currentPhotoIndex]?.url" mode="aspectFill" />
            </transition>
            
            <!-- Instagram 风格分段指示器 -->
            <view class="story-indicators" v-if="displayPhotos.length > 1">
              <view class="s-dash" v-for="(_, i) in displayPhotos" :key="i" :class="{ 's-active': i === currentPhotoIndex }"></view>
            </view>
            
            <!-- 触控区已被提炼至上方的 gesture-mask 层 -->
            
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

            <!-- 极简中文滑动气泡 -->
            <view class="action-feedback like-feedback" :style="{ opacity: likeOp, transform: `scale(${0.8 + likeOp * 0.2})` }">
              <view class="f-icon">❤️</view><text>喜欢</text>
            </view>
            <view class="action-feedback nope-feedback" :style="{ opacity: nopeOp, transform: `scale(${0.8 + nopeOp * 0.2})` }">
              <view class="f-icon">✖</view><text>无感</text>
            </view>
            
            <!-- 展开时照片左右切换区 -->
            <view v-if="showDetail && displayPhotos.length > 1" class="detail-photo-nav">
              <view class="detail-nav-left" @tap.stop="prevPhoto"></view>
              <view class="detail-nav-right" @tap.stop="nextPhoto"></view>
            </view>

            <!-- 展开时的毛玻璃关闭按钮 -->
            <view class="close-btn glass-morphism" v-if="showDetail" @tap.stop="toggleDetail" :style="{ top: (statusBarHeight + 10) + 'px' }">
              <text class="close-icon">∨</text>
            </view>

            <!-- 右上角更多按钮 -->
            <view class="more-btn glass-morphism" @tap.stop="showMoreMenu = true">
              <text class="more-dots">•••</text>
            </view>
          </view>

          <!-- 资料内容区 -->
          <view 
            class="profile-body" 
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

              
              <view class="detail-bottom-space"></view>
            </view>

          </view>
        </scroll-view>

        <!-- 手势检测层：覆盖资料区域，在 scroll-view 外可正常捕获手势 -->
        <view class="gesture-zone" v-if="!showDetail"
          @touchstart="onHeroTouchStart"
          @touchmove.stop="onHeroTouchMove"
          @touchend="onHeroTouchEnd"
          @tap="toggleDetail">
          <view class="gesture-hint-strip">
            <view class="expand-hint glass-morphism-light">
              <text>上滑查看详细资料</text>
            </view>
          </view>
        </view>
      </view>
      
      <!-- 右侧悬浮操作栏 (Apple SVGs converted to Data URI for miniprogram compatibility) -->
      <view class="right-actions" :class="{'actions-expanded': showDetail}">
        <view class="r-btn r-gift" @tap.stop="handleGift">
          <image style="width: 44rpx; height: 44rpx;" src="data:image/svg+xml;charset=utf-8,%3Csvg%20xmlns%3D%22http%3A%2F%2Fwww.w3.org%2F2000%2Fsvg%22%20width%3D%2224%22%20height%3D%2224%22%20viewBox%3D%220%200%2024%2024%22%20fill%3D%22none%22%20stroke%3D%22%23FF9500%22%20stroke-width%3D%222.5%22%20stroke-linecap%3D%22round%22%20stroke-linejoin%3D%22round%22%3E%3Cpath%20d%3D%22M20%2012v10H4V12%22%2F%3E%3Cpath%20d%3D%22M2%207h20v5H2z%22%2F%3E%3Cline%20x1%3D%2212%22%20y1%3D%2222%22%20x2%3D%2212%22%20y2%3D%227%22%2F%3E%3Cpath%20d%3D%22M12%207H7.5a2.5%202.5%200%200%201%200-5C11%202%2012%207%2012%207z%22%2F%3E%3Cpath%20d%3D%22M12%207h4.5a2.5%202.5%200%200%200%200-5C13%202%2012%207%2012%207z%22%2F%3E%3C%2Fsvg%3E" />
        </view>
        <view class="r-btn r-like" @tap.stop="animateLike">
          <image style="width: 56rpx; height: 56rpx;" src="data:image/svg+xml;charset=utf-8,%3Csvg%20xmlns%3D%22http%3A%2F%2Fwww.w3.org%2F2000%2Fsvg%22%20width%3D%2232%22%20height%3D%2232%22%20viewBox%3D%220%200%2024%2024%22%20fill%3D%22%23FFFFFF%22%20stroke%3D%22%23FFFFFF%22%20stroke-width%3D%222%22%20stroke-linecap%3D%22round%22%20stroke-linejoin%3D%22round%22%3E%3Cpath%20d%3D%22M20.84%204.61a5.5%205.5%200%200%200-7.78%200L12%205.67l-1.06-1.06a5.5%205.5%200%200%200-7.78%207.78l1.06%201.06L12%2021.23l7.78-7.78%201.06-1.06a5.5%205.5%200%200%200%200-7.78z%22%3E%3C%2Fpath%3E%3C%2Fsvg%3E" />
        </view>
        <view class="r-btn r-later" @tap.stop="handleLater">
          <image style="width: 44rpx; height: 44rpx;" src="data:image/svg+xml;charset=utf-8,%3Csvg%20xmlns%3D%22http%3A%2F%2Fwww.w3.org%2F2000%2Fsvg%22%20width%3D%2224%22%20height%3D%2224%22%20viewBox%3D%220%200%2024%2024%22%20fill%3D%22none%22%20stroke%3D%22%23007AFF%22%20stroke-width%3D%222.5%22%20stroke-linecap%3D%22round%22%20stroke-linejoin%3D%22round%22%3E%3Cpolygon%20points%3D%2212%202%2015.09%208.26%2022%209.27%2017%2014.14%2018.18%2021.02%2012%2017.77%205.82%2021.02%207%2014.14%202%209.27%208.91%208.26%2012%202%22%3E%3C%2Fpolygon%3E%3C%2Fsvg%3E" />
        </view>
        <view class="r-btn r-nope" @tap.stop="animateSkip">
          <image style="width: 40rpx; height: 40rpx;" src="data:image/svg+xml;charset=utf-8,%3Csvg%20xmlns%3D%22http%3A%2F%2Fwww.w3.org%2F2000%2Fsvg%22%20width%3D%2224%22%20height%3D%2224%22%20viewBox%3D%220%200%2024%2024%22%20fill%3D%22none%22%20stroke%3D%22%231C1C1E%22%20stroke-width%3D%223%22%20stroke-linecap%3D%22round%22%20stroke-linejoin%3D%22round%22%3E%3Cline%20x1%3D%2218%22%20y1%3D%226%22%20x2%3D%226%22%20y2%3D%2218%22%3E%3C%2Fline%3E%3Cline%20x1%3D%226%22%20y1%3D%226%22%20x2%3D%2218%22%20y2%3D%2218%22%3E%3C%2Fline%3E%3C%2Fsvg%3E" />
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

    <MatchModal :visible="showMatchModal" :matchId="matchedId || 0" @close="closeMatchModal" @go-chat="goToChat" />

    <!-- 更多操作菜单 -->
    <view class="mask" v-if="showMoreMenu" @tap="showMoreMenu = false">
      <view class="sheet more-sheet" @tap.stop>
        <view class="sheet-handle"></view>
        <text class="more-sheet-name">{{ currentCard?.nickname }}</text>
        <view class="more-options">
          <view class="more-opt" @tap="handleShare">
            <text class="mo-icon">↗</text>
            <text class="mo-label">分享给朋友</text>
          </view>
          <view class="more-divider"></view>
          <view class="more-opt" @tap="reportAndClose">
            <text class="mo-label-red">举报该用户</text>
          </view>
          <view class="more-opt" @tap="blockAndClose">
            <text class="mo-label-red">拉黑该用户</text>
          </view>
        </view>
        <view class="more-cancel" @tap="showMoreMenu = false">
          <text>取消</text>
        </view>
      </view>
    </view>

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

  <!-- 新手引导 -->
  <view class="guide-overlay" v-if="showGuide" @tap="nextGuide">
    <view class="guide-card" @tap.stop>

      <!-- 步骤指示点 -->
      <view class="guide-dots">
        <view class="g-dot" :class="{ active: guideStep === 0 }"></view>
        <view class="g-dot" :class="{ active: guideStep === 1 }"></view>
        <view class="g-dot" :class="{ active: guideStep === 2 }"></view>
      </view>

      <!-- 步骤 0: 卡片操作 -->
      <view class="guide-step" v-if="guideStep === 0">
        <text class="guide-emoji">💕</text>
        <text class="guide-title">欢迎来到推荐</text>
        <text class="guide-subtitle">为你精选匹配的人，每天更新</text>
        <view class="guide-rows">
          <view class="guide-row">
            <view class="guide-row-icon"><text>👈</text></view>
            <view class="guide-row-text">
              <text class="gr-name">上一张照片</text>
              <text class="gr-hint">点击卡片左侧区域</text>
            </view>
          </view>
          <view class="guide-row">
            <view class="guide-row-icon"><text>👉</text></view>
            <view class="guide-row-text">
              <text class="gr-name">下一张照片</text>
              <text class="gr-hint">点击卡片右侧区域</text>
            </view>
          </view>
          <view class="guide-row">
            <view class="guide-row-icon"><text>☝️</text></view>
            <view class="guide-row-text">
              <text class="gr-name">查看详细资料</text>
              <text class="gr-hint">点击或上滑卡片底部</text>
            </view>
          </view>
        </view>
      </view>

      <!-- 步骤 1: 右侧按钮 -->
      <view class="guide-step" v-if="guideStep === 1">
        <text class="guide-emoji">✨</text>
        <text class="guide-title">快捷操作</text>
        <text class="guide-subtitle">右侧悬浮按钮，一键操作</text>
        <view class="guide-actions">
          <view class="guide-action-row">
            <view class="ga-btn ga-gift"><text class="ga-icon-text">🎁</text></view>
            <view class="ga-info">
              <text class="ga-name">送礼物</text>
              <text class="ga-hint">即将上线</text>
            </view>
          </view>
          <view class="guide-action-row">
            <view class="ga-btn ga-like"><text class="ga-icon-text">❤️</text></view>
            <view class="ga-info">
              <text class="ga-name">喜欢</text>
              <text class="ga-hint">双方互相喜欢即匹配</text>
            </view>
          </view>
          <view class="guide-action-row">
            <view class="ga-btn ga-later"><text class="ga-icon-text">🔖</text></view>
            <view class="ga-info">
              <text class="ga-name">稍后再看</text>
              <text class="ga-hint">收藏感兴趣的人</text>
            </view>
          </view>
          <view class="guide-action-row">
            <view class="ga-btn ga-nope-btn"><text class="ga-nope">✕</text></view>
            <view class="ga-info">
              <text class="ga-name">跳过</text>
              <text class="ga-hint">不感兴趣，换下一位</text>
            </view>
          </view>
        </view>
      </view>

      <!-- 步骤 2: 出发 -->
      <view class="guide-step" v-if="guideStep === 2">
        <text class="guide-emoji">🚀</text>
        <text class="guide-title">一切就绪</text>
        <text class="guide-subtitle">完善资料可大幅提升匹配率</text>
        <view class="guide-tip-box">
          <text class="guide-tip">💡 上传真实照片 + 填写兴趣标签，匹配率提升 85%</text>
        </view>
      </view>

      <view class="guide-next-btn" @tap="nextGuide">
        <text>{{ guideStep < 2 ? '继续 →' : '开始匹配 →' }}</text>
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
const currentPhotoIndex = ref(0)
const isAnimating = ref(false)
const showDetail = ref(false)
const dailyRemaining = ref(-1)

function prevPhoto() {
  if (currentPhotoIndex.value > 0) {
    currentPhotoIndex.value--
  }
}

function nextPhoto() {
  if (currentPhotoIndex.value < displayPhotos.value.length - 1) {
    currentPhotoIndex.value++
  } else {
    toggleDetail()
  }
}

const dailyLimit = ref(10)

const touchStartX = ref(0)
const touchStartY = ref(0)
const isSwiping = ref(false)
const cardOffsetX = ref(0)
const cardOffsetY = ref(0)
const cardRotate = ref(0)
const cardRotateY = ref(0)
const cardOpacity = ref(1)
const THRESHOLD = 80

const nextCard = computed(() => currentIndex.value + 1 < cards.value.length ? cards.value[currentIndex.value + 1] : null)
const nextCardAvatar = computed(() => {
  if (!nextCard.value) return defaultAvatar
  if (nextCard.value.all_photos?.length > 0) return nextCard.value.all_photos[0].url
  if (nextCard.value.photos?.length > 0) {
    const p = nextCard.value.photos[0]
    return typeof p === 'string' ? p : p.url
  }
  return nextCard.value.avatar_url || defaultAvatar
})

const likeOp = computed(() => Math.min(Math.max(cardOffsetX.value / THRESHOLD, 0), 1))
const nopeOp = computed(() => Math.min(Math.max(-cardOffsetX.value / THRESHOLD, 0), 1))

// 主卡片样式
const cardStyle = computed(() => {
  if (cardOffsetX.value === 0 && cardOffsetY.value === 0 && cardOpacity.value === 1 && !showDetail.value) return 'z-index: 2;'
  const transition = isSwiping.value ? 'none' : 'all 0.5s cubic-bezier(0.32, 0.72, 0, 1)'
  return `z-index: 2; transform:translate(${cardOffsetX.value}px, ${cardOffsetY.value}px) rotateZ(${cardRotate.value}deg) rotateY(${cardRotateY.value}deg) scale(${isSwiping.value ? 0.98 : 1}); opacity:${cardOpacity.value}; transition:${transition};`
})

// 背景叠堆卡片样式 (跟随滑动拉近和清晰)
const nextCardStyle = computed(() => {
  const progress = Math.min(Math.abs(cardOffsetX.value) / 150, 1)
  const scale = 0.94 + (0.06 * progress)
  const ty = 40 - (40 * progress)
  const blur = 6 - (6 * progress)
  const transition = isSwiping.value ? 'none' : 'all 0.5s cubic-bezier(0.32, 0.72, 0, 1)'
  return `z-index: 1; transform: scale(${scale}) translateY(${ty}rpx); filter: blur(${blur}px); opacity: ${0.6 + (0.4*progress)}; transition: ${transition};`
})

const showGuide = ref(false)
const guideStep = ref(0)

function openGuide() {
  guideStep.value = 0
  showGuide.value = true
}

function nextGuide() {
  if (guideStep.value < 2) {
    guideStep.value++
  } else {
    showGuide.value = false
    uni.setStorageSync('home_guide_seen', '1')
  }
}

onMounted(() => {
  statusBarHeight.value = uni.getSystemInfoSync().statusBarHeight || 44
  loadRecommendations()
  fetchDailyLikes()
  if (!uni.getStorageSync('home_guide_seen')) {
    setTimeout(() => { showGuide.value = true }, 800)
  }
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
  
  // 上滑超过一定距离，展开详情 (dy负数代表向上)
  if (!isSwiping.value && dy < -40 && Math.abs(dy) > Math.abs(dx)) {
    toggleDetail()
    // 防止连续触发
    touchStartY.value = e.touches[0].clientY 
    return
  }

  if (!isSwiping.value && Math.abs(dx) > 10 && Math.abs(dx) > Math.abs(dy)) {
    isSwiping.value = true
  }
  if (isSwiping.value) { 
    // 加入阻尼效果与真实的 3D 重力翻转感
    const dampening = 0.8
    cardOffsetX.value = dx * dampening
    cardRotate.value = (dx * 0.03) * dampening
    cardRotateY.value = (dx * 0.08) * dampening 
  }
}

function onHeroTouchEnd() {
  if (!isSwiping.value) { 
    cardOffsetX.value = 0
    cardRotate.value = 0
    cardRotateY.value = 0
    return 
  }
  isSwiping.value = false
  if (cardOffsetX.value > THRESHOLD) animateLike()
  else if (cardOffsetX.value < -THRESHOLD) animateSkip()
  else { 
    cardOffsetX.value = 0
    cardRotate.value = 0 
    cardRotateY.value = 0
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

async function handleLater() {
  if (isAnimating.value) return
  isAnimating.value = true
  showDetail.value = false
  cardOffsetY.value = 800
  cardOpacity.value = 0
  const uid = currentCard.value?.user_id
  setTimeout(async () => {
    currentIndex.value++
    showNext()
    resetCard()
    if (uid) {
      try { await matchApi.addBookmark(uid) } catch {}
    }
  }, 400)
}

function handleGift() {
  uni.showToast({ title: '礼物功能即将上线，敬请期待', icon: 'none' })
}

function resetCard() { 
  isSwiping.value = true
  currentPhotoIndex.value = 0
  cardOffsetX.value = 0
  cardOffsetY.value = 0
  cardRotate.value = 0
  cardRotateY.value = 0
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

const showMoreMenu = ref(false)

function handleShare() {
  showMoreMenu.value = false
  uni.showToast({ title: '分享功能即将上线', icon: 'none' })
}

function handleLaterAndClose() {
  showMoreMenu.value = false
  handleLater()
}

function reportAndClose() {
  showMoreMenu.value = false
  reportUser()
}

function blockAndClose() {
  showMoreMenu.value = false
  blockUser()
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
function goToChat(matchId?: number) {
  showMatchModal.value = false
  const id = matchId || matchedId.value
  if (id) uni.navigateTo({ url: `/pages/chat-detail/index?matchId=${id}` })
}
function goEditProfile() { uni.navigateTo({ url: '/pages/edit-profile/index' }) }
function resetFilters() { filterGender.value = null; filterAge.value = null }
function applyFilters() { showFilterPanel.value = false; loadRecommendations() }

const expandTouchStartY = ref(0)
function onExpandTouchStart(e: any) {
  expandTouchStartY.value = e.touches[0].clientY
}
function onExpandTouchMove(e: any) {
  const dy = e.touches[0].clientY - expandTouchStartY.value
  if (dy < -30) toggleDetail()
}
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
  perspective: 1200px; /* 激活 3D 景深 */
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

.next-card { pointer-events: none; }
.blur-bg { filter: brightness(0.8); }

.card-scroll { width: 100%; height: 100%; }

/* 专门阻断 scroll-view 吞手势的超级透明层 */
.gesture-mask {
  position: absolute; top: 0; left: 0; width: 100%; height: 100%; z-index: 20;
}

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

/* 相册墙替换逻辑 */
.fade-photo-enter-active, .fade-photo-leave-active { transition: opacity 0.3s; }
.fade-photo-enter-from, .fade-photo-leave-to { opacity: 0; }
.hero-bg { position: absolute; top: 0; left: 0; width: 100%; height: 100%; }

.story-indicators { position: absolute; top: 16rpx; left: 16rpx; right: 16rpx; display: flex; gap: 8rpx; z-index: 30; }
.s-dash { flex: 1; height: 6rpx; border-radius: 4rpx; background: rgba(255,255,255,0.4); }
.s-dash.s-active { background: #FFFFFF; box-shadow: 0 2rpx 8rpx rgba(0,0,0,0.5); }

.tap-zones { position: absolute; top: 40rpx; bottom: 360rpx; left: 0; right: 0; display: flex; z-index: 25; }
.t-left { width: 40%; }
.t-center { width: 20%; }
.t-right { width: 40%; }

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

/* ====== 渐变气泡滑动提示 (Action Feedback) ====== */
.action-feedback {
  position: absolute; top: 120rpx;
  display: flex; flex-direction: column; align-items: center; justify-content: center;
  width: 160rpx; height: 160rpx;
  border-radius: 50%;
  pointer-events: none; z-index: 50;
  backdrop-filter: blur(20px); -webkit-backdrop-filter: blur(20px);
}
.action-feedback text { font-size: 26rpx; font-weight: 800; margin-top: 12rpx; letter-spacing: 2rpx; }
.f-icon { font-size: 64rpx; line-height: 1; }

.like-feedback { 
  left: 60rpx; background: rgba(255,45,85,0.15); border: 2rpx solid rgba(255,45,85,0.4); 
  color: #FF2D55; text-shadow: 0 2rpx 8rpx rgba(255,45,85,0.3);
}
.nope-feedback { 
  right: 60rpx; background: rgba(28,28,30,0.15); border: 2rpx solid rgba(0,0,0,0.2); 
  color: #1C1C1E; text-shadow: 0 2rpx 8rpx rgba(255,255,255,0.5);
}

.detail-photo-nav {
  position: absolute;
  top: 0; left: 0; right: 0;
  height: 100%;
  display: flex;
  pointer-events: none;
  z-index: 5;
}
.detail-nav-left, .detail-nav-right {
  flex: 1;
  height: 100%;
  pointer-events: auto;
}

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

/* ====== 手势检测层（覆盖整个资料区，scroll-view 外） ====== */
.gesture-zone {
  position: absolute;
  bottom: 0; left: 0; right: 0;
  height: 45vh;
  z-index: 20;
}
.gesture-hint-strip {
  position: absolute;
  bottom: 0; left: 0; right: 0;
  height: 140rpx;
  background: linear-gradient(to bottom, rgba(255,255,255,0) 0%, rgba(255,255,255,1) 80%);
  display: flex; align-items: flex-end; justify-content: center;
  padding-bottom: 24rpx;
}
.expand-hint { padding: 12rpx 32rpx; border-radius: 40rpx; }
.expand-hint text { font-size: 24rpx; color: #1C1C1E; font-weight: 600; }

/* ====== 右侧悬浮操作栏 (Apple Layout & SVG Icons) ====== */
.right-actions {
  position: absolute; right: 20rpx; bottom: 220rpx;
  display: flex; flex-direction: column; align-items: center; gap: 24rpx;
  z-index: 100; transition: all 0.4s cubic-bezier(0.32, 0.72, 0, 1);
}
.right-actions.actions-expanded {
  bottom: 120rpx; transform: scale(0.9); opacity: 0.5;
}
.r-btn {
  width: 84rpx; height: 84rpx; border-radius: 50%;
  display: flex; align-items: center; justify-content: center;
  transition: transform 0.2s cubic-bezier(0.25, 0.1, 0.25, 1), box-shadow 0.2s ease;
  background: linear-gradient(135deg, rgba(250,250,255,0.95), rgba(230,230,235,0.85));
  backdrop-filter: blur(24px); -webkit-backdrop-filter: blur(24px);
  box-shadow: 
    -2rpx -2rpx 8rpx rgba(255, 255, 255, 1) inset, 
    4rpx 4rpx 10rpx rgba(0, 0, 0, 0.1) inset,
    0 12rpx 24rpx rgba(0, 0, 0, 0.15),
    0 4rpx 8rpx rgba(0, 0, 0, 0.08); /* 3D Glass Layering */
  border: 1rpx solid rgba(255, 255, 255, 0.9);
}
.r-btn:active { 
  transform: scale(0.85); 
  box-shadow: -2rpx -2rpx 8rpx rgba(255, 255, 255, 0.8) inset, 4rpx 4rpx 14rpx rgba(0, 0, 0, 0.2) inset, 0 4rpx 12rpx rgba(0, 0, 0, 0.1); 
}
.r-btn image { filter: drop-shadow(0 4rpx 6rpx rgba(0,0,0,0.15)); }

/* The Like button is bigger and distinct, 3D Ruby Red */
.r-btn.r-like { 
  width: 104rpx; height: 104rpx; margin: 6rpx 0; 
  background: linear-gradient(135deg, #FF6B8B, #FF2D55); 
  box-shadow: 
    -2rpx -2rpx 12rpx rgba(255, 200, 215, 0.9) inset, 
    4rpx 4rpx 14rpx rgba(180, 0, 30, 0.6) inset,
    0 16rpx 40rpx rgba(255, 45, 85, 0.4),
    0 6rpx 12rpx rgba(255, 45, 85, 0.2); 
  border: 1rpx solid rgba(255, 140, 160, 0.7);
}
.r-btn.r-like:active { 
  box-shadow: -2rpx -2rpx 8rpx rgba(255, 200, 215, 0.8) inset, 4rpx 4rpx 16rpx rgba(180, 0, 30, 0.7) inset, 0 8rpx 20rpx rgba(255, 45, 85, 0.3); 
}
.r-btn.r-like image { filter: drop-shadow(0 6rpx 10rpx rgba(180, 0, 30, 0.7)); }
.nav-icon { font-size: 36rpx; color: #000; line-height: 1; }

/* ====== 右上角更多按钮 ====== */
.more-btn {
  position: absolute;
  top: 24rpx; right: 24rpx;
  width: 64rpx; height: 64rpx;
  border-radius: 50%;
  z-index: 30;
  display: flex; align-items: center; justify-content: center;
}
.more-dots { font-size: 22rpx; color: #fff; letter-spacing: 2rpx; font-weight: 700; line-height: 1; text-shadow: 0 1px 4px rgba(0,0,0,0.4); }

/* ====== 更多菜单 ====== */
.more-sheet { padding-bottom: calc(40rpx + env(safe-area-inset-bottom)); }
.more-sheet-name { font-size: 28rpx; color: #8E8E93; font-weight: 500; text-align: center; display: block; margin-bottom: 32rpx; }
.more-options { background: #F2F2F7; border-radius: 28rpx; overflow: hidden; margin-bottom: 16rpx; }
.more-opt { display: flex; align-items: center; gap: 20rpx; padding: 36rpx 40rpx; background: #fff; border-bottom: 1rpx solid #F2F2F7; }
.more-opt:last-child { border-bottom: none; }
.mo-icon { font-size: 36rpx; width: 48rpx; text-align: center; }
.mo-label { font-size: 32rpx; color: #1C1C1E; font-weight: 500; }
.mo-label-red { font-size: 32rpx; color: #FF3B30; font-weight: 500; }
.more-divider { height: 12rpx; background: #F2F2F7; }
.more-cancel {
  background: #fff; border-radius: 28rpx;
  padding: 36rpx; text-align: center;
}
.more-cancel text { font-size: 32rpx; color: #1C1C1E; font-weight: 600; }
.guide-btn-icon { font-size: 30rpx; font-weight: 800; color: #000; line-height: 1; }
.close-icon { font-size: 40rpx; color: #000; font-weight: 700; line-height: 1; }

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

/* ====== 新手引导 ====== */
.guide-overlay {
  position: fixed;
  top: 0; left: 0; right: 0; bottom: 0;
  background: rgba(0, 0, 0, 0.78);
  z-index: 999;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 0 40rpx;
}
.guide-card {
  width: 100%;
  background: rgba(255, 255, 255, 0.96);
  backdrop-filter: blur(40px);
  -webkit-backdrop-filter: blur(40px);
  border-radius: 48rpx;
  padding: 56rpx 48rpx 48rpx;
  box-shadow: 0 32rpx 80rpx rgba(0,0,0,0.3);
}
.guide-dots {
  display: flex; gap: 12rpx; justify-content: center; margin-bottom: 48rpx;
}
.g-dot {
  width: 14rpx; height: 14rpx; border-radius: 50%;
  background: #E5E5EA;
  transition: all 0.3s;
}
.g-dot.active { width: 40rpx; border-radius: 8rpx; background: #000; }
.guide-step { display: flex; flex-direction: column; align-items: center; }
.guide-emoji { font-size: 96rpx; margin-bottom: 24rpx; }
.guide-title { font-size: 52rpx; font-weight: 800; color: #000; letter-spacing: -1rpx; margin-bottom: 12rpx; }
.guide-subtitle { font-size: 28rpx; color: #8E8E93; font-weight: 500; margin-bottom: 48rpx; text-align: center; }

/* 步骤 0：操作行 */
.guide-rows { width: 100%; display: flex; flex-direction: column; gap: 24rpx; }
.guide-row { display: flex; align-items: center; gap: 24rpx; background: #F2F2F7; padding: 28rpx 32rpx; border-radius: 28rpx; }
.guide-row-icon { width: 64rpx; height: 64rpx; display: flex; align-items: center; justify-content: center; font-size: 40rpx; }
.gr-name { font-size: 30rpx; font-weight: 700; color: #000; display: block; }
.gr-hint { font-size: 24rpx; color: #8E8E93; display: block; margin-top: 4rpx; }

/* 步骤 1：操作按钮列表 */
.guide-actions { width: 100%; display: flex; flex-direction: column; gap: 20rpx; }
.guide-action-row { display: flex; align-items: center; gap: 24rpx; }
.ga-btn {
  width: 88rpx; height: 88rpx; border-radius: 50%;
  background: rgba(255,255,255,0.85);
  backdrop-filter: blur(20px);
  box-shadow: 0 8rpx 24rpx rgba(0,0,0,0.10);
  border: 1rpx solid rgba(255,255,255,0.6);
  display: flex; align-items: center; justify-content: center;
  flex-shrink: 0;
}
.ga-icon-text { font-size: 36rpx; line-height: 1; }
.ga-btn.ga-like { background: rgba(255, 45, 85, 0.12); box-shadow: 0 8rpx 24rpx rgba(255,45,85,0.15); }
.ga-btn.ga-later { background: rgba(90, 200, 250, 0.12); }
.ga-btn.ga-nope-btn { background: rgba(142,142,147,0.10); }
.ga-nope { font-size: 32rpx; color: #8E8E93; font-weight: 700; }
.ga-name { font-size: 30rpx; font-weight: 700; color: #000; display: block; }
.ga-hint { font-size: 24rpx; color: #8E8E93; display: block; margin-top: 4rpx; }

/* 步骤 2：提示框 */
.guide-tip-box {
  background: #F2F2F7; border-radius: 28rpx;
  padding: 28rpx 32rpx; width: 100%;
}
.guide-tip { font-size: 28rpx; color: #3C3C43; line-height: 1.6; font-weight: 500; }

/* 下一步按钮 */
.guide-next-btn {
  margin-top: 48rpx;
  height: 100rpx; border-radius: 50rpx;
  background: #000;
  display: flex; align-items: center; justify-content: center;
  box-shadow: 0 12rpx 32rpx rgba(0,0,0,0.15);
}
.guide-next-btn text { font-size: 32rpx; font-weight: 700; color: #fff; letter-spacing: 1rpx; }
</style>