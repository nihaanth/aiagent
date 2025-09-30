/**
 * Polyfills for React Native iOS compatibility
 * Import this file at the top of App.js
 */

// Fix for _domainNameToDomainMap error on iOS
if (typeof global !== 'undefined') {

  // Fix domain mapping issue that causes ReferenceError
  if (!global._domainNameToDomainMap) {
    global._domainNameToDomainMap = new Map();
  }

  // Polyfill for URL constructor using available package
  try {
    if (!global.URL) {
      const { URL } = require('whatwg-url-without-unicode');
      global.URL = URL;
    }
  } catch (e) {
    // Fallback URL implementation for iOS
    global.URL = class URL {
      constructor(url, base) {
        this.href = url || '';
        this.origin = '';
        this.protocol = '';
        this.hostname = '';
        this.pathname = '';
        this.search = '';
        this.hash = '';
      }
    };
  }

  // URLSearchParams polyfill
  try {
    if (!global.URLSearchParams) {
      const { URLSearchParams } = require('whatwg-url-without-unicode');
      global.URLSearchParams = URLSearchParams;
    }
  } catch (e) {
    // Fallback URLSearchParams for iOS
    global.URLSearchParams = class URLSearchParams {
      constructor() {
        this.params = new Map();
      }
      get(key) { return this.params.get(key); }
      set(key, value) { this.params.set(key, value); }
      has(key) { return this.params.has(key); }
      delete(key) { this.params.delete(key); }
    };
  }

  // XMLHttpRequest domain handling polyfills
  if (!global._domainToASCII) {
    global._domainToASCII = function(domain) {
      return domain && domain.toString ? domain.toString() : '';
    };
  }

  if (!global._domainToUnicode) {
    global._domainToUnicode = function(domain) {
      return domain && domain.toString ? domain.toString() : '';
    };
  }

  // FormData polyfill for React Native
  if (!global.FormData) {
    try {
      global.FormData = require('react-native/Libraries/Network/FormData');
    } catch (e) {
      // Fallback FormData
      global.FormData = class FormData {
        constructor() {
          this.data = new Map();
        }
        append(key, value) { this.data.set(key, value); }
        get(key) { return this.data.get(key); }
        has(key) { return this.data.has(key); }
      };
    }
  }

  // Fetch polyfill if needed
  if (!global.fetch) {
    try {
      require('whatwg-fetch');
    } catch (e) {
      // Fetch will be provided by React Native
    }
  }
}

// Console polyfill for debugging
if (typeof console === 'undefined') {
  global.console = {
    log: () => {},
    warn: () => {},
    error: () => {},
    info: () => {},
    debug: () => {},
  };
}

console.log('✅ iOS networking polyfills loaded successfully');