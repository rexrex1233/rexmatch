/**
 * 统一请求封装 - 自动携带 token、统一错误处理
 * API 地址通过 VITE_API_BASE_URL 环境变量配置
 */

// #ifdef H5
const BASE_URL = (import.meta as any).env?.VITE_API_BASE_URL || '/api/v1'
// #endif
// #ifndef H5
const BASE_URL = 'https://your-app.onrender.com/api/v1'
// #endif

interface RequestOptions {
  url: string
  method?: 'GET' | 'POST' | 'PUT' | 'DELETE'
  data?: any
  header?: Record<string, string>
  needAuth?: boolean
}

interface ApiResponse<T = any> {
  code: number
  message: string
  data: T
}

function getToken(): string {
  return uni.getStorageSync('access_token') || ''
}

export function request<T = any>(options: RequestOptions): Promise<ApiResponse<T>> {
  const { url, method = 'GET', data, header = {}, needAuth = true } = options

  if (needAuth) {
    const token = getToken()
    if (token) {
      header['Authorization'] = `Bearer ${token}`
    }
  }

  return new Promise((resolve, reject) => {
    uni.request({
      url: `${BASE_URL}${url}`,
      method,
      data,
      header: {
        'Content-Type': 'application/json',
        ...header,
      },
      success(res) {
        const statusCode = res.statusCode
        const responseData = res.data as ApiResponse<T>

        if (statusCode === 401) {
          uni.removeStorageSync('access_token')
          uni.reLaunch({ url: '/pages/login/index' })
          reject(new Error('登录已过期'))
          return
        }

        if (statusCode >= 200 && statusCode < 300 && responseData.code === 0) {
          resolve(responseData)
        } else {
          const errMsg = responseData?.message || `请求失败(${statusCode})`
          uni.showToast({ title: errMsg, icon: 'none' })
          reject(new Error(errMsg))
        }
      },
      fail(err) {
        uni.showToast({ title: '网络连接失败', icon: 'none' })
        reject(err)
      },
    })
  })
}

export const api = {
  get: <T = any>(url: string, data?: any) => request<T>({ url, method: 'GET', data }),
  post: <T = any>(url: string, data?: any) => request<T>({ url, method: 'POST', data }),
  put: <T = any>(url: string, data?: any) => request<T>({ url, method: 'PUT', data }),
  del: <T = any>(url: string, data?: any) => request<T>({ url, method: 'DELETE', data }),
}

export { BASE_URL }
