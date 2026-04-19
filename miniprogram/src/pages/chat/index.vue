<template>
  <view class="chat-page">
    <!-- 顶部栏 -->
    <view class="top-bar-container" :class="{ 'immersive-mode': searchFocused || searchKeyword }">
      <view class="top-bar">
        <view class="search-bar" :class="{ searching: searchKeyword }">
          <view class="search-inner" :class="{ active: searchFocused }">
            <text class="search-icon">🔍</text>
            <input
              class="search-input"
              v-model="searchKeyword"
              placeholder="搜索联系人或消息"
              placeholder-class="search-ph"
              confirm-type="search"
              @focus="searchFocused = true"
              @blur="searchFocused = false"
              @input="onSearchInput"
              @confirm="doSearch"
            />
            <text v-if="searchKeyword" class="search-clear" @tap="clearSearch">✕</text>
          </view>
        </view>
        
        <view class="cancel-btn-wrap" v-if="searchFocused || searchKeyword">
          <text class="cancel-btn" @tap="cancelSearch">取消</text>
        </view>
        
        <view v-if="!searchKeyword && !searchFocused" class="batch-btn" @tap="toggleBatchMode">
          <text class="batch-btn-text">{{ batchMode ? '取消' : '管理' }}</text>
        </view>
      </view>
    </view>

    <!-- 沉浸式搜索半透明遮罩 -->
    <view class="search-overlay" v-if="searchFocused && !searchKeyword" @touchmove.stop @tap="cancelSearch"></view>

    <!-- 骨架屏 -->
    <view class="skeleton" v-if="loading && matches.length === 0 && chats.length === 0">
      <view class="sk-match-section">
        <view class="sk-label shimmer"></view>
        <view class="sk-match-row">
          <view class="sk-match-item" v-for="i in 4" :key="i">
            <view class="sk-match-avatar shimmer"></view>
            <view class="sk-match-name shimmer"></view>
          </view>
        </view>
      </view>
      <view class="sk-chat-list">
        <view class="sk-chat-item" v-for="i in 5" :key="i">
          <view class="sk-chat-avatar shimmer"></view>
          <view class="sk-chat-body">
            <view class="sk-chat-name shimmer"></view>
            <view class="sk-chat-msg shimmer"></view>
          </view>
        </view>
      </view>
    </view>

    <!-- 搜索结果面板 -->
    <scroll-view scroll-y class="content-scroll" v-if="searchKeyword && !searching">
      <!-- 联系人命中 -->
      <view v-if="searchResult.contacts.length">
        <view class="section-header">
          <text class="section-header-text">匹配的好友</text>
        </view>
        <view class="chat-list">
          <view class="chat-item" v-for="item in searchResult.contacts" :key="'c-' + item.match_id"
            @tap="goChat(item.match_id, item.partner_nickname)">
            <view class="chat-avatar-wrap">
              <image class="chat-avatar" :src="item.partner_avatar || defaultAvatar" mode="aspectFill" />
            </view>
            <view class="chat-body">
              <view class="chat-top-row">
                <!-- 昵称高亮 -->
                <view class="chat-name-row">
                  <text
                    v-for="(seg, i) in highlight(item.partner_nickname, searchKeyword)"
                    :key="i"
                    :class="['chat-name', seg.match ? 'hl' : '']"
                  >{{ seg.text }}</text>
                </view>
              </view>
              <text class="chat-preview">联系人</text>
            </view>
          </view>
        </view>
      </view>

      <!-- 消息命中 -->
      <view v-if="searchResult.messages.length">
        <view class="section-header">
          <text class="section-header-text">聊天记录</text>
        </view>
        <view class="chat-list">
          <view class="chat-item" v-for="item in searchResult.messages" :key="'m-' + item.message_id"
            @tap="goChatMsg(item.match_id, item.partner_nickname, item.message_id)">
            <view class="chat-avatar-wrap">
              <image class="chat-avatar" :src="item.partner_avatar || defaultAvatar" mode="aspectFill" />
            </view>
            <view class="chat-body">
              <view class="chat-top-row">
                <text class="chat-name">{{ item.partner_nickname }}</text>
                <text class="chat-time">{{ formatTime(item.message_at) }}</text>
              </view>
              <!-- 消息内容高亮 -->
              <view class="chat-preview-row">
                <text
                  v-for="(seg, i) in highlight(item.message_content, searchKeyword)"
                  :key="i"
                  :class="['chat-preview', seg.match ? 'hl' : '']"
                >{{ seg.text }}</text>
              </view>
            </view>
          </view>
        </view>
      </view>

      <!-- 空状态 -->
      <view class="empty-state"
        v-if="!searchResult.contacts.length && !searchResult.messages.length">
        <view class="empty-circle"><text class="empty-icon">🔍</text></view>
        <text class="empty-title">没有找到相关内容</text>
      </view>
    </scroll-view>

    <!-- 内容区域 -->
    <scroll-view
      scroll-y
      class="content-scroll"
      v-if="!searchKeyword && (!loading || matches.length > 0 || chats.length > 0)"
      refresher-enabled
      :refresher-triggered="refreshing"
      @refresherrefresh="onRefresh"
    >
      <!-- 新匹配横向列表 -->
      <view class="match-section" v-if="matches.length && !batchMode">
        <text class="section-label">新匹配</text>
        <scroll-view scroll-x class="match-scroll" :show-scrollbar="false">
          <view class="match-list-inner">
            <view class="match-card" v-for="m in matches" :key="m.match_id"
              @tap="goChat(m.match_id, m.partner_nickname)">
              <view class="match-avatar-ring">
                <image class="match-avatar" :src="m.partner_avatar || defaultAvatar" mode="aspectFill" />
              </view>
              <text class="match-nick">{{ m.partner_nickname }}</text>
            </view>
          </view>
        </scroll-view>
      </view>

      <!-- 消息列表 -->
      <view class="msg-section" v-if="chats.length">
        <text class="section-label" style="padding: 0 32rpx;" v-if="!batchMode">消息</text>
        <!-- 批量模式标头 -->
        <view class="batch-header" v-if="batchMode">
          <text class="batch-header-text">
            {{ selectedIds.size > 0 ? `已选 ${selectedIds.size} 个` : '选择要管理的对话' }}
          </text>
          <!-- 沉默时间筛选条 -->
          <scroll-view scroll-x class="inactive-filter-bar" :show-scrollbar="false">
            <view class="inactive-filter-inner">
              <view
                v-for="opt in inactiveFilterOptions"
                :key="opt.value"
                :class="['inactive-chip', inactiveFilter === opt.value ? 'chip-active' : '']"
                @tap="setInactiveFilter(opt.value)"
              >
                <text class="inactive-chip-text">{{ opt.label }}</text>
              </view>
            </view>
          </scroll-view>
        </view>
        <view class="chat-list">
          <view
            class="chat-item"
            v-for="chat in displayedChats"
            :key="chat.match_id"
            @tap="onChatTap(chat)"
            @longpress="onChatLongPress(chat)"
          >
            <!-- 批量模式复选框 -->
            <view v-if="batchMode" class="checkbox-wrap">
              <view :class="['checkbox', selectedIds.has(chat.match_id) ? 'checked' : '']">
                <text v-if="selectedIds.has(chat.match_id)" class="checkbox-check">✓</text>
              </view>
            </view>
            <view class="chat-avatar-wrap">
              <image class="chat-avatar" :src="chat.partner_avatar || defaultAvatar" mode="aspectFill" />
              <view class="online-dot" v-if="chat.is_online && !batchMode"></view>
              <view class="unread-dot" v-if="chat.unread_count > 0 && !batchMode">
                <text class="unread-num">{{ chat.unread_count > 99 ? '99+' : chat.unread_count }}</text>
              </view>
            </view>
            <view class="chat-body">
              <view class="chat-top-row">
                <text class="chat-name">{{ chat.partner_nickname }}</text>
                <text class="chat-time" v-if="!batchMode">{{ formatTime(chat.last_message_at) }}</text>
              </view>
              <text class="chat-preview">{{ chat.last_message || '还没聊过，快去打个招呼吧' }}</text>
            </view>
          </view>
        </view>
      </view>

      <!-- 空状态 -->
      <view class="empty-state" v-if="!loading && chats.length === 0 && matches.length === 0">
        <view class="empty-circle">
          <text class="empty-icon">💬</text>
        </view>
        <text class="empty-title">还没有匹配和消息</text>
        <text class="empty-desc">去首页划一划，遇见心仪的TA</text>
      </view>
    </scroll-view>

    <!-- 批量操作底栏 -->
    <view class="batch-action-bar" v-if="batchMode">
      <view class="batch-action-row">
        <view
          :class="['batch-action-btn', 'flex-1', selectedIds.size > 0 ? 'danger' : 'disabled']"
          @tap="batchUnmatch"
        >
          <text class="batch-action-text">
            解除匹配{{ selectedIds.size > 0 ? ` (${selectedIds.size})` : '' }}
          </text>
        </view>
        <view
          :class="['batch-action-btn', 'flex-1', 'recycle', selectedIds.size > 0 ? 'recycle-active' : 'disabled']"
          @tap="batchInactiveUnmatch"
        >
          <text class="batch-action-text">清理放回推荐池</text>
        </view>
      </view>
    </view>
  </view>
</template>

<script setup lang="ts">
import { ref, reactive, computed } from 'vue'
import { onShow } from '@dcloudio/uni-app'
import { chatApi, matchApi } from '../../api'

const defaultAvatar = 'https://api.dicebear.com/7.x/avataaars/svg?seed=default'
const loading = ref(false)
const refreshing = ref(false)
const matches = ref<any[]>([])
const chats = ref<any[]>([])

// 搜索
const searchKeyword = ref('')
const searchFocused = ref(false)
const searchResult = ref<{ contacts: any[]; messages: any[] }>({ contacts: [], messages: [] })
const searching = ref(false)
let searchTimer: any = null

// 批量模式
const batchMode = ref(false)
const selectedIds = reactive(new Set<number>())

// 沉默时间筛选
const inactiveFilter = ref<number | null>(null) // 天数，null = 全部
const inactiveFilterOptions = [
  { label: '全部', value: null },
  { label: '7天未聊', value: 7 },
  { label: '15天未聊', value: 15 },
  { label: '1个月', value: 30 },
  { label: '更久', value: 60 },
]

function setInactiveFilter(value: number | null) {
  inactiveFilter.value = value
  selectedIds.clear()
}

// 根据沉默筛选过滤会话列表
const displayedChats = computed(() => {
  if (!batchMode.value || inactiveFilter.value === null) return chats.value
  const cutoff = Date.now() - inactiveFilter.value * 24 * 60 * 60 * 1000
  return chats.value.filter((c: any) => {
    // 从未聊过 或 最后消息时间超过筛选天数
    if (!c.last_message_at) return true
    return new Date(c.last_message_at).getTime() < cutoff
  })
})

function toggleBatchMode() {
  batchMode.value = !batchMode.value
  if (!batchMode.value) {
    selectedIds.clear()
    inactiveFilter.value = null
  }
}

function onChatTap(chat: any) {
  if (batchMode.value) {
    if (selectedIds.has(chat.match_id)) selectedIds.delete(chat.match_id)
    else selectedIds.add(chat.match_id)
    return
  }
  goChat(chat.match_id, chat.partner_nickname)
}

function onChatLongPress(chat: any) {
  if (batchMode.value) return
  uni.showActionSheet({
    itemList: ['解除匹配'],
    success(res) {
      if (res.tapIndex === 0) confirmUnmatch(chat)
    }
  })
}

function confirmUnmatch(chat: any) {
  uni.showModal({
    title: '解除匹配',
    content: `确认解除与「${chat.partner_nickname}」的匹配吗？此操作不可撤销`,
    confirmText: '解除',
    confirmColor: '#ff4757',
    success(res) {
      if (res.confirm) doUnmatch([chat.match_id])
    }
  })
}

async function doUnmatch(matchIds: number[]) {
  try {
    if (matchIds.length === 1) {
      await matchApi.unmatch(matchIds[0])
    } else {
      await matchApi.batchUnmatch(matchIds)
    }
    chats.value = chats.value.filter(c => !matchIds.includes(c.match_id))
    matches.value = matches.value.filter(m => !matchIds.includes(m.match_id))
    selectedIds.clear()
    if (batchMode.value) batchMode.value = false
    uni.showToast({ title: '已解除匹配', icon: 'success' })
  } catch {
    uni.showToast({ title: '操作失败', icon: 'none' })
  }
}

function batchUnmatch() {
  if (selectedIds.size === 0) return
  const ids = Array.from(selectedIds)
  uni.showModal({
    title: '批量解除匹配',
    content: `确认解除选中的 ${ids.length} 个匹配吗？此操作不可撤销`,
    confirmText: '解除',
    confirmColor: '#ff4757',
    success(res) {
      if (res.confirm) doUnmatch(ids)
    }
  })
}

async function batchInactiveUnmatch() {
  if (selectedIds.size === 0) return
  const ids = Array.from(selectedIds)
  uni.showModal({
    title: '清理沉默匹配',
    content: `将解除选中的 ${ids.length} 个沉默匹配，这些人将有机会再次出现在你的推荐页（排位稍靠后）。`,
    confirmText: '清理',
    confirmColor: '#ff6b81',
    success: async (res) => {
      if (!res.confirm) return
      try {
        await matchApi.inactiveUnmatchBatch(ids)
        chats.value = chats.value.filter((c: any) => !ids.includes(c.match_id))
        matches.value = matches.value.filter((m: any) => !ids.includes(m.match_id))
        selectedIds.clear()
        batchMode.value = false
        inactiveFilter.value = null
        uni.showToast({ title: '已清理，他们将重回推荐池', icon: 'none', duration: 2500 })
      } catch {
        uni.showToast({ title: '操作失败', icon: 'none' })
      }
    }
  })
}

// 搜索逻辑
function onSearchInput() {
  if (searchTimer) clearTimeout(searchTimer)
  if (!searchKeyword.value.trim()) {
    searchResult.value = { contacts: [], messages: [] }
    return
  }
  searchTimer = setTimeout(() => doSearch(), 400)
}

async function doSearch() {
  const kw = searchKeyword.value.trim()
  if (!kw) return
  searching.value = true
  try {
    const res = await chatApi.searchChats(kw)
    searchResult.value = res.data || { contacts: [], messages: [] }
  } catch {
    searchResult.value = { contacts: [], messages: [] }
  } finally {
    searching.value = false
  }
}

function clearSearch() {
  searchKeyword.value = ''
  searchResult.value = { contacts: [], messages: [] }
}

function cancelSearch() {
  searchFocused.value = false
  searchKeyword.value = ''
  searchResult.value = { contacts: [], messages: [] }
  uni.hideKeyboard()
}

// 关键词高亮分词
function highlight(text: string, keyword: string): { text: string; match: boolean }[] {
  if (!keyword || !text) return [{ text, match: false }]
  const escaped = keyword.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')
  const parts = text.split(new RegExp(`(${escaped})`, 'gi'))
  return parts.filter(p => p).map(p => ({
    text: p,
    match: p.toLowerCase() === keyword.toLowerCase(),
  }))
}

onShow(() => {
  if (!batchMode.value) loadData()
})

async function loadData() {
  loading.value = true
  try {
    const [matchRes, chatRes] = await Promise.all([
      matchApi.getMatchList(),
      chatApi.getChatList(),
    ])
    matches.value = matchRes.data || []
    chats.value = chatRes.data || []
    const totalUnread = chats.value.reduce((sum: number, c: any) => sum + (c.unread_count || 0), 0)
    if (totalUnread > 0) {
      uni.setTabBarBadge({ index: 2, text: String(totalUnread > 99 ? '99+' : totalUnread) })
    } else {
      uni.removeTabBarBadge({ index: 2 })
    }
  } finally {
    loading.value = false
    refreshing.value = false
  }
}

async function onRefresh() {
  refreshing.value = true
  await loadData()
}

function goChat(matchId: number, nickname: string) {
  uni.navigateTo({
    url: `/pages/chat-detail/index?matchId=${matchId}&nickname=${encodeURIComponent(nickname)}`,
  })
}

function goChatMsg(matchId: number, nickname: string, messageId: number) {
  uni.navigateTo({
    url: `/pages/chat-detail/index?matchId=${matchId}&nickname=${encodeURIComponent(nickname)}&scrollToMsgId=${messageId}`,
  })
}

function formatTime(timeStr: string | null): string {
  if (!timeStr) return ''
  const d = new Date(timeStr)
  const now = new Date()
  const diff = now.getTime() - d.getTime()
  if (diff < 60000) return '刚刚'
  if (diff < 3600000) return `${Math.floor(diff / 60000)}分钟前`
  if (diff < 86400000) return `${Math.floor(diff / 3600000)}小时前`
  return `${d.getMonth() + 1}/${d.getDate()}`
}
</script>

<style scoped>
.chat-page { min-height: 100vh; background: #f7f8fa; }

/* ---- 顶部栏与沉浸式搜索 ---- */
.top-bar-container {
  background: #fff;
  transition: all 0.3s cubic-bezier(0.25, 0.1, 0.25, 1);
  position: relative;
  z-index: 100;
}
.top-bar-container.immersive-mode {
  padding-bottom: 8rpx;
  box-shadow: 0 4rpx 16rpx rgba(0,0,0,0.04);
}
.top-bar { display: flex; align-items: center; padding: 16rpx 32rpx 12rpx; gap: 16rpx; }
.search-bar { flex: 1; transition: flex 0.3s cubic-bezier(0.25, 0.1, 0.25, 1); }
.search-inner { display: flex; align-items: center; gap: 12rpx; background: #f0f1f5; border-radius: 36rpx; padding: 16rpx 28rpx; transition: background 0.2s; }
.search-inner.active { background: #e8e9ee; }
.search-icon { font-size: 28rpx; flex-shrink: 0; }
.search-input { flex: 1; font-size: 26rpx; color: #1a1a1a; height: 44rpx; }
.search-ph { color: #b3b3b3; }
.search-clear { font-size: 24rpx; color: #b3b3b3; padding: 4rpx 8rpx; flex-shrink: 0; }

.cancel-btn-wrap {
  overflow: hidden;
  animation: slideInCancel 0.3s cubic-bezier(0.25, 0.1, 0.25, 1) forwards;
  display: flex; align-items: center; justify-content: center;
}
.cancel-btn { font-size: 30rpx; color: #1a1a1a; padding: 10rpx 0 10rpx 16rpx; white-space: nowrap; }

@keyframes slideInCancel {
  from { width: 0; opacity: 0; transform: translateX(20rpx); }
  to { width: 70rpx; opacity: 1; transform: translateX(0); }
}

.search-overlay {
  position: fixed; top: 120rpx; left: 0; right: 0; bottom: 0;
  background: rgba(0, 0, 0, 0.3);
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
  z-index: 90;
  animation: fadeIn 0.3s cubic-bezier(0.25, 0.1, 0.25, 1) forwards;
}

@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

.batch-btn { flex-shrink: 0; padding: 8rpx 4rpx; }
.batch-btn-text { font-size: 28rpx; color: #1a1a1a; font-weight: 600; }

/* ---- 搜索结果分组标头 ---- */
.section-header { padding: 20rpx 32rpx 8rpx; background: #f7f8fa; }
.section-header-text { font-size: 22rpx; color: #999; font-weight: 600; text-transform: uppercase; letter-spacing: 2rpx; }

/* 高亮文字 */
.hl { color: #ff6b81; font-weight: 700; }
.chat-name-row { display: flex; flex-wrap: wrap; }
.chat-preview-row { display: flex; flex-wrap: wrap; overflow: hidden; max-height: 40rpx; }

/* ---- 骨架屏 ---- */
.skeleton { padding: 0; }
.sk-match-section { background: #fff; padding: 24rpx 32rpx 20rpx; margin-bottom: 16rpx; }
.sk-label { width: 100rpx; height: 24rpx; border-radius: 12rpx; margin-bottom: 20rpx; }
.sk-match-row { display: flex; gap: 28rpx; }
.sk-match-item { display: flex; flex-direction: column; align-items: center; gap: 10rpx; }
.sk-match-avatar { width: 108rpx; height: 108rpx; border-radius: 50%; }
.sk-match-name { width: 80rpx; height: 20rpx; border-radius: 10rpx; }
.sk-chat-list { background: #fff; padding: 24rpx 32rpx; }
.sk-chat-item { display: flex; align-items: center; gap: 20rpx; padding: 20rpx 0; border-bottom: 1rpx solid #f5f6f8; }
.sk-chat-avatar { width: 100rpx; height: 100rpx; border-radius: 50%; flex-shrink: 0; }
.sk-chat-body { flex: 1; }
.sk-chat-name { width: 40%; height: 28rpx; border-radius: 14rpx; margin-bottom: 12rpx; }
.sk-chat-msg { width: 70%; height: 24rpx; border-radius: 12rpx; }

@keyframes shimmer {
  0% { background-position: -200% 0; }
  100% { background-position: 200% 0; }
}
.shimmer {
  background: linear-gradient(90deg, #e8e8e8 25%, #f5f5f5 50%, #e8e8e8 75%);
  background-size: 200% 100%;
  animation: shimmer 1.5s infinite;
}

.content-scroll { height: calc(100vh - 88rpx - env(safe-area-inset-bottom)); }

/* ---- 新匹配 ---- */
.match-section { background: #fff; padding: 24rpx 0 20rpx; margin-bottom: 16rpx; }
.section-label { font-size: 26rpx; color: #999; font-weight: 600; margin-bottom: 20rpx; display: block; padding-left: 32rpx; text-transform: uppercase; letter-spacing: 2rpx; }
.match-scroll { white-space: nowrap; padding-left: 32rpx; }
.match-list-inner { display: inline-flex; gap: 28rpx; padding-right: 32rpx; }
.match-card { display: flex; flex-direction: column; align-items: center; width: 120rpx; }
.match-avatar-ring { width: 108rpx; height: 108rpx; border-radius: 50%; padding: 4rpx; background: linear-gradient(135deg, #ff6b81, #ff4757, #ffa502); margin-bottom: 10rpx; }
.match-avatar { width: 100%; height: 100%; border-radius: 50%; border: 4rpx solid #fff; }
.match-nick { font-size: 22rpx; color: #333; width: 120rpx; text-align: center; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }

/* ---- 消息列表 ---- */
.msg-section { background: #fff; padding-top: 24rpx; }
.chat-list { padding: 0 32rpx; }
.chat-item { display: flex; align-items: center; padding: 24rpx 0; border-bottom: 1rpx solid #f5f6f8; }
.chat-item:last-child { border-bottom: none; }
.chat-avatar-wrap { position: relative; margin-right: 24rpx; flex-shrink: 0; }
.chat-avatar { width: 100rpx; height: 100rpx; border-radius: 50%; }
.online-dot { position: absolute; bottom: 4rpx; right: 4rpx; width: 20rpx; height: 20rpx; border-radius: 50%; background: #07c160; border: 4rpx solid #fff; }
.unread-dot { position: absolute; top: -6rpx; right: -6rpx; background: #ff4757; border-radius: 24rpx; padding: 2rpx 12rpx; min-width: 32rpx; text-align: center; border: 3rpx solid #fff; }
.unread-num { color: #fff; font-size: 20rpx; font-weight: 600; }
.chat-body { flex: 1; overflow: hidden; }
.chat-top-row { display: flex; justify-content: space-between; align-items: center; margin-bottom: 10rpx; }
.chat-name { font-size: 30rpx; font-weight: 600; color: #1a1a1a; }
.chat-time { font-size: 22rpx; color: #ccc; flex-shrink: 0; }
.chat-preview { font-size: 26rpx; color: #999; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; display: block; }

/* ---- 批量模式 ---- */
.batch-header { padding: 16rpx 32rpx 12rpx; }
.batch-header-text { font-size: 26rpx; color: #999; }
.checkbox-wrap { margin-right: 20rpx; flex-shrink: 0; }
.checkbox { width: 44rpx; height: 44rpx; border-radius: 50%; border: 3rpx solid #ddd; display: flex; align-items: center; justify-content: center; transition: all 0.2s; }
.checkbox.checked { background: #ff4757; border-color: #ff4757; }
.checkbox-check { font-size: 24rpx; color: #fff; font-weight: 700; }

/* 沉默筛选条 */
.inactive-filter-bar { margin-top: 12rpx; white-space: nowrap; }
.inactive-filter-inner { display: inline-flex; gap: 12rpx; padding: 4rpx 0 8rpx; }
.inactive-chip {
  display: inline-flex; align-items: center; justify-content: center;
  padding: 10rpx 28rpx; border-radius: 32rpx;
  border: 2rpx solid #e5e5ea; background: #f7f8fa;
  transition: all 0.2s;
}
.inactive-chip.chip-active { background: linear-gradient(135deg, #ff6b81, #ff4757); border-color: transparent; }
.inactive-chip-text { font-size: 24rpx; color: #666; }
.inactive-chip.chip-active .inactive-chip-text { color: #fff; font-weight: 600; }

/* 批量操作底栏 */
.batch-action-bar {
  position: fixed; bottom: 0; left: 0; right: 0;
  padding: 16rpx 32rpx;
  padding-bottom: calc(16rpx + env(safe-area-inset-bottom));
  background: #fff;
  border-top: 1rpx solid #f0f1f5;
}
.batch-action-row { display: flex; gap: 16rpx; }
.batch-action-btn {
  height: 88rpx; border-radius: 44rpx;
  display: flex; align-items: center; justify-content: center;
  transition: opacity 0.2s;
}
.flex-1 { flex: 1; }
.batch-action-btn.danger { background: linear-gradient(135deg, #ff6b81, #ff4757); }
.batch-action-btn.recycle-active { background: linear-gradient(135deg, #5856d6, #007aff); }
.batch-action-btn.disabled { background: #e0e0e0; }
.batch-action-text { font-size: 28rpx; font-weight: 700; color: #fff; }

/* ---- 空状态 ---- */
.empty-state { display: flex; flex-direction: column; align-items: center; padding-top: 240rpx; }
.empty-circle { width: 140rpx; height: 140rpx; border-radius: 50%; background: linear-gradient(135deg, #fff0f3, #ffe0e6); display: flex; align-items: center; justify-content: center; margin-bottom: 28rpx; }
.empty-icon { font-size: 56rpx; }
.empty-title { font-size: 32rpx; font-weight: 700; color: #1a1a1a; margin-bottom: 12rpx; }
.empty-desc { font-size: 26rpx; color: #b3b3b3; }
</style>
