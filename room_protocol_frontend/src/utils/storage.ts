/**
 * Safe localStorage utility functions
 * Provides SSR compatibility and error handling
 */

/**
 * Check if localStorage is available
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
    console.warn('localStorage is not available:', error);
    return false;
  }
};

/**
 * Safely get localStorage item
 */
export const safeGetItem = (key: string): string | null => {
  if (!isLocalStorageAvailable()) {
    return null;
  }

  try {
    return window.localStorage.getItem(key);
  } catch (error) {
    console.warn(`Failed to get localStorage item [${key}]:`, error);
    return null;
  }
};

/**
 * Safely set localStorage item
 */
export const safeSetItem = (key: string, value: string): boolean => {
  if (!isLocalStorageAvailable()) {
    return false;
  }

  try {
    window.localStorage.setItem(key, value);
    return true;
  } catch (error) {
    console.warn(`Failed to set localStorage item [${key}]:`, error);
    return false;
  }
};

/**
 * Safely remove localStorage item
 */
export const safeRemoveItem = (key: string): boolean => {
  if (!isLocalStorageAvailable()) {
    return false;
  }

  try {
    window.localStorage.removeItem(key);
    return true;
  } catch (error) {
    console.warn(`Failed to remove localStorage item [${key}]:`, error);
    return false;
  }
};

/**
 * Safely get JSON object
 */
export const safeGetJSON = <T>(key: string, defaultValue: T): T => {
  const item = safeGetItem(key);
  if (!item) {
    return defaultValue;
  }

  try {
    return JSON.parse(item) as T;
  } catch (error) {
    console.warn(`Failed to parse JSON [${key}]:`, error);
    return defaultValue;
  }
};

/**
 * Safely set JSON object
 */
export const safeSetJSON = <T>(key: string, value: T): boolean => {
  try {
    const jsonString = JSON.stringify(value);
    return safeSetItem(key, jsonString);
  } catch (error) {
    console.warn(`Failed to serialize JSON [${key}]:`, error);
    return false;
  }
};

/**
 * Batch clear localStorage items
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
 * Get localStorage usage statistics
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
    console.warn('Failed to get storage statistics:', error);
    return {
      available: false,
      itemCount: 0,
      estimatedSize: 0,
    };
  }
};
