/**
 * API 接口定义
 */
import { api, BASE_URL } from './request'

/** 认证 */
export const authApi = {
  wxLogin: (code: string) => api.post('/auth/wx-login', { code }),
}

/** 用户资料 */
export const userApi = {
  getMyProfile: () => api.get('/users/me'),
  getUserProfile: (userId: number) => api.get(`/users/${userId}`),
  updateProfile: (data: any) => api.put('/users/me', data),
  uploadPhoto: (filePath: string, isAvatar = false): Promise<any> => {
    return new Promise((resolve, reject) => {
      const token = uni.getStorageSync('access_token') || ''
      uni.uploadFile({
        url: `${BASE_URL}/upload/photo?is_avatar=${isAvatar}`,
        filePath,
        name: 'file',
        header: { Authorization: `Bearer ${token}` },
        success(res) {
          const data = JSON.parse(res.data)
          if (data.code === 0) resolve(data)
          else reject(new Error(data.message))
        },
        fail: reject,
      })
    })
  },
  deletePhoto: (photoId: number) => api.del(`/users/me/photos/${photoId}`),
  getAllInterests: () => api.get('/users/interests/all'),
  addCustomInterest: (name: string, category: string = '自定义') => 
    api.post('/users/interests/custom', { name, category }),
  getPreferences: () => api.get('/users/me/preferences'),
  updatePreferences: (data: any) => api.put('/users/me/preferences', data),
}

/** 发现/推荐 */
export const discoverApi = {
  getRecommendations: (params?: any) => api.get('/discover/recommend', params),
}

/** 匹配 */
export const matchApi = {
  swipe: (targetUserId: number, isLike: boolean) =>
    api.post('/match/swipe', { target_user_id: targetUserId, is_like: isLike }),
  getMatchList: () => api.get('/match/list'),
  unmatch: (matchId: number) => api.post(`/match/${matchId}/unmatch`),
  batchUnmatch: (matchIds: number[]) => api.post('/match/unmatch-batch', { match_ids: matchIds }),
  inactiveUnmatchBatch: (matchIds: number[]) => api.post('/match/inactive-unmatch-batch', { match_ids: matchIds }),
  getLikesReceived: () => api.get('/match/likes-received'),
  getDailyLikes: () => api.get('/match/daily-likes'),
  addBookmark: (targetUserId: number) => api.post(`/match/bookmark/${targetUserId}`),
  removeBookmark: (targetUserId: number) => api.del(`/match/bookmark/${targetUserId}`),
  getBookmarks: () => api.get('/match/bookmarks'),
}

/** 聊天 */
export const chatApi = {
  getChatList: () => api.get('/chat/list'),
  getMessages: (matchId: number, page = 1) =>
    api.get(`/chat/${matchId}/messages?page=${page}`),
  sendMessage: (matchId: number, content: string, msgType = 'text', replyToId?: number) =>
    api.post('/chat/send', { match_id: matchId, content, msg_type: msgType, ...(replyToId ? { reply_to_id: replyToId } : {}) }),
  recallMessage: (messageId: number) => api.post(`/chat/${messageId}/recall`),
  searchChats: (q: string) => api.get(`/chat/search?q=${encodeURIComponent(q)}`),
}

/** 用户昵称查重 */
export const checkNickname = (nickname: string) =>
  api.get(`/users/check-nickname?nickname=${encodeURIComponent(nickname)}`)

/** 举报 */
export const reportApi = {
  submit: (reportedUserId: number, reason: string, detail?: string) =>
    api.post('/report/submit', { reported_user_id: reportedUserId, reason, detail }),
  block: (blockedUserId: number) =>
    api.post('/report/block', { blocked_user_id: blockedUserId }),
  unblock: (userId: number) => api.post(`/report/unblock/${userId}`),
  getBlockList: () => api.get('/report/block-list'),
}
