/**
 * 用户状态管理
 */
import { defineStore } from 'pinia'
import { ref } from 'vue'
import { authApi, userApi } from '../api'

export const useUserStore = defineStore('user', () => {
  const token = ref('')
  const isLoggedIn = ref(false)
  const profile = ref<any>(null)

  function checkLogin() {
    const savedToken = uni.getStorageSync('access_token')
    if (savedToken) {
      token.value = savedToken
      isLoggedIn.value = true
      fetchProfile()
    } else {
      uni.reLaunch({ url: '/pages/login/index' })
    }
  }

  async function wxLogin() {
    // #ifdef H5
    await h5TestLogin()
    return
    // #endif

    // #ifndef H5
    return new Promise<void>((resolve, reject) => {
      uni.login({
        provider: 'weixin',
        success: async (loginRes) => {
          try {
            await handleLoginResponse(loginRes.code)
            resolve()
          } catch (e) {
            reject(e)
          }
        },
        fail: (err) => {
          uni.showToast({ title: '微信登录失败', icon: 'none' })
          reject(err)
        },
      })
    })
    // #endif
  }

  async function h5TestLogin() {
    const testCode = 'h5_test_' + Date.now()
    await handleLoginResponse(testCode)
  }

  async function handleLoginResponse(code: string) {
    const res = await authApi.wxLogin(code)
    token.value = res.data.access_token
    isLoggedIn.value = true
    uni.setStorageSync('access_token', res.data.access_token)

    await fetchProfile()

    if (res.data.is_new_user) {
      uni.redirectTo({ url: '/pages/onboarding/index' })
    } else {
      uni.switchTab({ url: '/pages/home/index' })
    }
  }

  async function fetchProfile() {
    try {
      const res = await userApi.getMyProfile()
      profile.value = res.data
    } catch (e) {
      console.error('获取资料失败', e)
    }
  }

  function logout() {
    token.value = ''
    isLoggedIn.value = false
    profile.value = null
    uni.removeStorageSync('access_token')
    uni.reLaunch({ url: '/pages/login/index' })
  }

  return {
    token,
    isLoggedIn,
    profile,
    checkLogin,
    wxLogin,
    fetchProfile,
    logout,
  }
})
