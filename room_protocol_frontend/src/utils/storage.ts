/**
 * 安全的localStorage工具函数
 * 提供SSR兼容性和错误处理
 */

/**
 * 检查localStorage是否可用
 */
export const isLocalStorageAvailable = (): boolean => {
  if (typeof window === 'undefined') {
    return false;
  }
  
  try {
    const testKey = '__localStorage_test__';
    window.localStorage.setItem(testKey, 'test');
    window.localStorage.removeItem(testKey);
    return true;
  } catch (error) {
    console.warn('localStorage不可用:', error);
    return false;
  }
};

/**
 * 安全地获取localStorage项
 */
export const safeGetItem = (key: string): string | null => {
  if (!isLocalStorageAvailable()) {
    return null;
  }
  
  try {
    return window.localStorage.getItem(key);
  } catch (error) {
    console.warn(`获取localStorage项失败 [${key}]:`, error);
    return null;
  }
};

/**
 * 安全地设置localStorage项
 */
export const safeSetItem = (key: string, value: string): boolean => {
  if (!isLocalStorageAvailable()) {
    return false;
  }
  
  try {
    window.localStorage.setItem(key, value);
    return true;
  } catch (error) {
    console.warn(`设置localStorage项失败 [${key}]:`, error);
    return false;
  }
};

/**
 * 安全地移除localStorage项
 */
export const safeRemoveItem = (key: string): boolean => {
  if (!isLocalStorageAvailable()) {
    return false;
  }
  
  try {
    window.localStorage.removeItem(key);
    return true;
  } catch (error) {
    console.warn(`移除localStorage项失败 [${key}]:`, error);
    return false;
  }
};

/**
 * 安全地获取JSON对象
 */
export const safeGetJSON = <T>(key: string, defaultValue: T): T => {
  const item = safeGetItem(key);
  if (!item) {
    return defaultValue;
  }
  
  try {
    return JSON.parse(item) as T;
  } catch (error) {
    console.warn(`解析JSON失败 [${key}]:`, error);
    return defaultValue;
  }
};

/**
 * 安全地设置JSON对象
 */
export const safeSetJSON = <T>(key: string, value: T): boolean => {
  try {
    const jsonString = JSON.stringify(value);
    return safeSetItem(key, jsonString);
  } catch (error) {
    console.warn(`序列化JSON失败 [${key}]:`, error);
    return false;
  }
};

/**
 * 批量清理localStorage项
 */
export const safeClearItems = (keys: string[]): number => {
  if (!isLocalStorageAvailable()) {
    return 0;
  }
  
  let clearedCount = 0;
  for (const key of keys) {
    if (safeRemoveItem(key)) {
      clearedCount++;
    }
  }
  
  return clearedCount;
};

/**
 * 获取localStorage使用情况统计
 */
export const getStorageStats = (): {
  available: boolean;
  itemCount: number;
  estimatedSize: number;
} => {
  if (!isLocalStorageAvailable()) {
    return {
      available: false,
      itemCount: 0,
      estimatedSize: 0,
    };
  }
  
  try {
    const storage = window.localStorage;
    let estimatedSize = 0;
    
    for (let i = 0; i < storage.length; i++) {
      const key = storage.key(i);
      if (key) {
        const value = storage.getItem(key);
        estimatedSize += key.length + (value?.length || 0);
      }
    }
    
    return {
      available: true,
      itemCount: storage.length,
      estimatedSize,
    };
  } catch (error) {
    console.warn('获取存储统计失败:', error);
    return {
      available: false,
      itemCount: 0,
      estimatedSize: 0,
    };
  }
};
