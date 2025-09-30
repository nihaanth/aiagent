/**
 * Minimal polyfills for React Native iOS compatibility
 * Import this file at the top of App.js
 */

// Fix for _domainNameToDomainMap error on iOS
if (typeof global !== 'undefined') {
  // Fix domain mapping issue that causes ReferenceError
  if (!global._domainNameToDomainMap) {
    global._domainNameToDomainMap = new Map();
  }

  // Basic URL polyfill for iOS
  if (!global.URL) {
    global.URL = class URL {
      constructor(url, base) {
        this.href = url || '';
        this.origin = '';
        this.protocol = '';
        this.hostname = '';
        this.pathname = '';
        this.search = '';
        this.hash = '';

        if (url) {
          try {
            const parts = url.split('://');
            if (parts.length > 1) {
              this.protocol = parts[0] + ':';
              const remaining = parts[1];
              const hostPath = remaining.split('/');
              this.hostname = hostPath[0];
              this.origin = this.protocol + '//' + this.hostname;
              this.pathname = '/' + hostPath.slice(1).join('/');
            }
          } catch (e) {
            // Fallback for malformed URLs
          }
        }
      }
    };
  }

  // URLSearchParams polyfill for iOS
  if (!global.URLSearchParams) {
    global.URLSearchParams = class URLSearchParams {
      constructor(init) {
        this.params = new Map();
        if (typeof init === 'string') {
          const pairs = init.replace(/^\?/, '').split('&');
          pairs.forEach(pair => {
            const [key, value] = pair.split('=');
            if (key) {
              this.params.set(decodeURIComponent(key), decodeURIComponent(value || ''));
            }
          });
        }
      }
      get(key) { return this.params.get(key); }
      set(key, value) { this.params.set(key, value); }
      has(key) { return this.params.has(key); }
      delete(key) { this.params.delete(key); }
      toString() {
        const pairs = [];
        this.params.forEach((value, key) => {
          pairs.push(encodeURIComponent(key) + '=' + encodeURIComponent(value));
        });
        return pairs.join('&');
      }
    };
  }

  // Domain handling polyfills for XMLHttpRequest
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

  // Basic FormData polyfill for React Native
  if (!global.FormData) {
    global.FormData = class FormData {
      constructor() {
        this.data = new Map();
      }
      append(key, value) { this.data.set(key, value); }
      get(key) { return this.data.get(key); }
      has(key) { return this.data.has(key); }
      delete(key) { this.data.delete(key); }
    };
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

console.log('✅ Minimal iOS networking polyfills loaded successfully');